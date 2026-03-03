"""
LaRa Vision Perception — Face Detector (v2.1)
v2.1 upgrade: Full pose confidence layer.

pose_confidence is computed from 3 signals:
  1. MediaPipe landmark visibility score (mean of 6 key landmarks)
  2. solvePnP reprojection error (pixel distance — lower = better)
  3. Landmark spread quality (spatial coverage in frame)

If pose_confidence < POSE_CONFIDENCE_MIN → lookingAtScreen forced False.
pose_confidence is returned in the output dict for the confidence sub-object.
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


class FaceDetector:
    """
    MediaPipe FaceMesh + calibrated solvePnP head pose + pose confidence.
    """

    def __init__(self):
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._yaw_buf: deque = deque(maxlen=vision_config.HEAD_POSE_BUFFER)
        self._pitch_buf: deque = deque(maxlen=vision_config.HEAD_POSE_BUFFER)
        self._last_valid_yaw:   float = 0.0
        self._last_valid_pitch: float = 0.0
        self._cam_cache: dict = {}
        log.info("FaceDetector v2.1 initialised (pose confidence layer active)")

    def process(self, frame: np.ndarray) -> dict:
        """
        Returns:
            presence (bool), yaw (float), pitch (float),
            lookingAtScreen (bool), confidence (float), pose_confidence (float)
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {
                "presence": False, "yaw": 0.0, "pitch": 0.0,
                "lookingAtScreen": False,
                "confidence": 0.0,
                "pose_confidence": 0.0,
            }

        lm = results.multi_face_landmarks[0].landmark

        # ── solvePnP + reprojection error ─────────────────────────
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

        # ── Landmark spread quality ───────────────────────────────
        pts = np.array([(lm[i].x * w, lm[i].y * h) for i in _LANDMARK_INDICES])
        spread = float(np.std(pts))   # Higher spread = better coverage
        spread_score = min(1.0, spread / 80.0)  # Normalise; 80px std = full score

        # ── Composite pose_confidence ─────────────────────────────
        # Signal 1: reprojection quality (lower err = higher score)
        repro_score = float(np.clip(
            1.0 - reprojection_err / (vision_config.POSE_REPROJECTION_THRESHOLD * 2),
            0.0, 1.0,
        ))

        # Signal 2: spatial spread
        pose_confidence = round(
            0.70 * repro_score + 0.30 * spread_score,
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
            (max(0.0, 1.0 - abs(yaw_s) / _YAW_CLAMP) + max(0.0, 1.0 - abs(pitch_s) / _PITCH_CLAMP)) / 2.0,
            3,
        )

        return {
            "presence": True,
            "yaw": round(yaw_s, 2),
            "pitch": round(pitch_s, 2),
            "lookingAtScreen": looking,
            "confidence": face_conf,
            "pose_confidence": pose_confidence,
        }

    # ── Camera intrinsics ─────────────────────────────────────────

    def _get_camera_matrix(self, w: int, h: int) -> np.ndarray:
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
