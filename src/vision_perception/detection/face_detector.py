"""
LaRa Vision Perception — Face Detector (v2.2)
v2.2 fixes over v2.1:

  Fix 1 – Landmark Visibility Score (Signal 1 was missing):
    The docstring claimed pose_confidence used 3 signals but only 2 were
    implemented. Signal 1 (MediaPipe landmark visibility) is now computed
    as the mean visibility of the 6 key landmarks and incorporated into
    the composite pose_confidence with weights: 0.40 visibility + 0.40
    reprojection quality + 0.20 spread.

  Fix 2 – Pose confidence weights rebalanced:
    Old weights: 0.70 repro + 0.30 spread (visibility ignored).
    New weights: 0.40 visibility + 0.40 reprojection + 0.20 spread.
    This makes low-landmark-quality frames (partial occlusion, side view)
    correctly suppress gaze classification rather than relying solely on
    reprojection error which can be artificially low when few points fit.

  Fix 3 – Camera intrinsics cache key is now (w, h) with validated fallback:
    Prevents silent reuse of stale intrinsics when resolution changes mid-session.
"""

from collections import deque
from typing import Tuple

import cv2
import mediapipe as mp
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# Generic 3-D skull model reference points (mm)
_MODEL_POINTS = np.array([
    (0.0,    0.0,    0.0),
    (0.0,   -330.0, -65.0),
    (-225.0, 170.0, -135.0),
    (225.0,  170.0, -135.0),
    (-150.0, -150.0, -125.0),
    (150.0,  -150.0, -125.0),
], dtype=np.float64)

_LANDMARK_INDICES = [1, 152, 263, 33, 287, 57]
_YAW_CLAMP   = 90.0
_PITCH_CLAMP = 90.0

# Pose confidence composite weights (must sum to 1.0)
_W_VISIBILITY   = 0.40   # Signal 1: MediaPipe landmark mean visibility
_W_REPROJECTION = 0.40   # Signal 2: solvePnP reprojection quality
_W_SPREAD       = 0.20   # Signal 3: 2D landmark spatial spread


class FaceDetector:
    """
    MediaPipe FaceMesh + calibrated solvePnP head pose + 3-signal pose confidence.

    pose_confidence is computed from:
      1. Landmark visibility (mean of 6 key landmarks, 0-1 from MediaPipe)
      2. solvePnP reprojection error (lower = better confidence)
      3. Landmark spread quality (spatial coverage in frame, prevents degenerate fits)

    If pose_confidence < POSE_CONFIDENCE_MIN → lookingAtScreen forced False.
    """

    def __init__(self):
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._yaw_buf: deque = deque(maxlen=vision_config.HEAD_POSE_BUFFER)
        self._pitch_buf: deque = deque(maxlen=vision_config.HEAD_POSE_BUFFER)
        self._last_valid_yaw:   float = 0.0
        self._last_valid_pitch: float = 0.0
        self._cam_cache: dict = {}
        log.info(
            "FaceDetector v2.2 initialised "
            f"(pose confidence: visibility={_W_VISIBILITY}, "
            f"reprojection={_W_REPROJECTION}, spread={_W_SPREAD})"
        )

    def process(self, rgb_frame: np.ndarray) -> dict:
        """
        Args:
            rgb_frame: Pre-computed RGB image array.
        Returns:
            presence (bool), yaw (float), pitch (float),
            lookingAtScreen (bool), confidence (float), pose_confidence (float)
        """
        h, w = rgb_frame.shape[:2]
        results = self._face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return {
                "presence": False, "yaw": 0.0, "pitch": 0.0,
                "lookingAtScreen": False,
                "confidence": 0.0,
                "pose_confidence": 0.0,
            }

        lm = results.multi_face_landmarks[0].landmark

        # ── Signal 1: Landmark visibility (FIX 1) ────────────────
        visibility_scores = [lm[i].visibility for i in _LANDMARK_INDICES]
        mean_visibility = float(np.mean(visibility_scores))
        # Use config threshold instead of hardcoded 0.5
        v_min = vision_config.LANDMARK_VISIBILITY_MIN
        visibility_score = float(np.clip((mean_visibility - v_min) / (1.0 - v_min) if v_min < 1.0 else 0.0, 0.0, 1.0))

        # ── Signal 2: solvePnP + reprojection error ───────────────
        yaw, pitch, reprojection_err, solvepnp_ok = self._estimate_head_pose(lm, w, h)

        if not solvepnp_ok:
            yaw, pitch = self._last_valid_yaw, self._last_valid_pitch
            reprojection_err = vision_config.POSE_REPROJECTION_THRESHOLD * 2  # penalise

        # Clamp angles
        yaw   = float(np.clip(yaw,   -_YAW_CLAMP,   _YAW_CLAMP))
        pitch = float(np.clip(pitch, -_PITCH_CLAMP, _PITCH_CLAMP))

        if solvepnp_ok:
            self._last_valid_yaw   = yaw
            self._last_valid_pitch = pitch

        # Smooth
        self._yaw_buf.append(yaw)
        self._pitch_buf.append(pitch)
        yaw_s   = float(np.mean(self._yaw_buf))
        pitch_s = float(np.mean(self._pitch_buf))

        # Reprojection quality score (lower err = higher score)
        repro_score = float(np.clip(
            1.0 - reprojection_err / (vision_config.POSE_REPROJECTION_THRESHOLD * 2),
            0.0, 1.0,
        ))

        # ── Signal 3: Landmark spread quality ────────────────────
        pts = np.array([(lm[i].x * w, lm[i].y * h) for i in _LANDMARK_INDICES])
        spread = float(np.std(pts))
        spread_score = min(1.0, spread / 80.0)  # Normalise; 80px std = full score

        # ── Composite pose_confidence (FIX 2: all 3 signals) ─────
        pose_confidence = round(
            _W_VISIBILITY   * visibility_score
            + _W_REPROJECTION * repro_score
            + _W_SPREAD       * spread_score,
            3,
        )

        # ── Gaze classification — soft fail on low confidence ─────
        above_threshold = (
            abs(yaw_s)   < vision_config.GAZE_YAW_THRESHOLD
            and abs(pitch_s) < vision_config.GAZE_PITCH_THRESHOLD
        )
        looking = above_threshold and (pose_confidence >= vision_config.POSE_CONFIDENCE_MIN)

        # Face detection confidence: head-centrality proxy
        face_conf = round(
            (max(0.0, 1.0 - abs(yaw_s) / _YAW_CLAMP)
             + max(0.0, 1.0 - abs(pitch_s) / _PITCH_CLAMP)) / 2.0,
            3,
        )

        return {
            "presence": True,
            "yaw": round(yaw_s, 2),
            "pitch": round(pitch_s, 2),
            "lookingAtScreen": looking,
            "confidence": face_conf,
            "pose_confidence": pose_confidence,
            # Debug: expose sub-scores for dashboard/logging
            "_visibility_score": round(visibility_score, 3),
            "_repro_score": round(repro_score, 3),
            "_spread_score": round(spread_score, 3),
        }

    # ── Camera intrinsics ─────────────────────────────────────────

    def _get_camera_matrix(self, w: int, h: int) -> np.ndarray:
        """
        Returns calibrated camera matrix for the given resolution.
        FIX 3: Cache key validated so stale intrinsics are never reused
        on resolution changes.
        """
        key = (w, h)
        if key not in self._cam_cache:
            fx = getattr(vision_config, "CAMERA_FX", float(w))
            fy = getattr(vision_config, "CAMERA_FY", float(w))
            cx = getattr(vision_config, "CAMERA_CX", w / 2.0)
            cy = getattr(vision_config, "CAMERA_CY", h / 2.0)
            self._cam_cache[key] = np.array([
                [fx,  0,  cx],
                [0,  fy,  cy],
                [0,   0,   1],
            ], dtype=np.float64)
            log.info(f"Camera matrix cached for resolution {w}x{h}: fx={fx}, fy={fy}")
        return self._cam_cache[key]

    # ── solvePnP + reprojection error ─────────────────────────────

    def _estimate_head_pose(
        self, landmarks, w: int, h: int
    ) -> Tuple[float, float, float, bool]:
        """Returns (yaw_deg, pitch_deg, reprojection_error_px, success)."""
        try:
            image_points = np.array([
                (landmarks[i].x * w, landmarks[i].y * h)
                for i in _LANDMARK_INDICES
            ], dtype=np.float64)

            cam_matrix  = self._get_camera_matrix(w, h)
            dist_coeffs = np.zeros((4, 1))

            ok, rvec, tvec = cv2.solvePnP(
                _MODEL_POINTS, image_points, cam_matrix, dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )
            if not ok:
                return 0.0, 0.0, 999.0, False

            # Compute reprojection error
            projected, _ = cv2.projectPoints(
                _MODEL_POINTS, rvec, tvec, cam_matrix, dist_coeffs
            )
            projected = projected.reshape(-1, 2)
            reprojection_err = float(np.mean(np.linalg.norm(projected - image_points, axis=1)))

            rot_mat, _ = cv2.Rodrigues(rvec)
            _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(
                np.hstack([rot_mat, tvec])
            )
            return float(euler[1]), float(euler[0]), reprojection_err, True

        except Exception as e:
            log.warning(f"solvePnP exception: {e}")
            return 0.0, 0.0, 999.0, False

    def close(self) -> None:
        self._face_mesh.close()