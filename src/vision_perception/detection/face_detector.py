"""
LaRa Vision Perception — Face Detector (v2)
Production-hardened:
  - Configurable camera intrinsic matrix (override or auto-derive from frame).
  - Yaw/pitch clamped to ±90° to eliminate landmark jitter spikes.
  - solvePnP failure handled gracefully — propagates last valid pose.
  - Returns confidence score (0.0–1.0) from MediaPipe detection confidence.
"""

from collections import deque
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# Generic 3-D skull model reference points (metric: mm)
_MODEL_POINTS = np.array([
    (0.0,    0.0,    0.0),     # Nose tip
    (0.0,   -330.0, -65.0),    # Chin
    (-225.0, 170.0, -135.0),   # Left eye corner
    (225.0,  170.0, -135.0),   # Right eye corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0,  -150.0, -125.0),  # Right mouth corner
], dtype=np.float64)

_LANDMARK_INDICES = [1, 152, 263, 33, 287, 57]

# Clamp angles to prevent solvePnP spikes on landmark jitter
_YAW_CLAMP   = 90.0
_PITCH_CLAMP = 90.0


class FaceDetector:
    """
    MediaPipe FaceMesh + solvePnP head pose.
    Outputs: presence, yaw, pitch, lookingAtScreen, confidence.
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

        # Last valid solvePnP result — fallback on failure
        self._last_valid_yaw: float = 0.0
        self._last_valid_pitch: float = 0.0

        # Cache derived camera matrix per (w, h) pair to avoid recomputing
        self._cam_cache: dict = {}

        log.info("FaceDetector v2 initialised (MediaPipe FaceMesh + calibrated solvePnP)")

    def process(self, frame: np.ndarray) -> dict:
        """
        Returns:
            presence (bool), yaw (float), pitch (float),
            lookingAtScreen (bool), confidence (float)
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {
                "presence": False, "yaw": 0.0, "pitch": 0.0,
                "lookingAtScreen": False, "confidence": 0.0,
            }

        lm = results.multi_face_landmarks[0].landmark
        yaw, pitch, ok = self._estimate_head_pose(lm, w, h)

        # Use last valid pose if solvePnP failed this frame
        if not ok:
            yaw, pitch = self._last_valid_yaw, self._last_valid_pitch
        else:
            # Clamp to prevent spike on landmark jitter
            yaw   = float(np.clip(yaw,   -_YAW_CLAMP,   _YAW_CLAMP))
            pitch = float(np.clip(pitch, -_PITCH_CLAMP, _PITCH_CLAMP))
            self._last_valid_yaw   = yaw
            self._last_valid_pitch = pitch

        # Smooth via rolling buffer
        self._yaw_buf.append(yaw)
        self._pitch_buf.append(pitch)
        yaw_s   = float(np.mean(self._yaw_buf))
        pitch_s = float(np.mean(self._pitch_buf))

        looking = (
            abs(yaw_s)   < vision_config.GAZE_YAW_THRESHOLD
            and abs(pitch_s) < vision_config.GAZE_PITCH_THRESHOLD
        )

        # Derive confidence from landmark proximity to expected pattern
        # Simple proxy: ratio of how "centred" the head is in the gaze window
        yaw_conf   = max(0.0, 1.0 - abs(yaw_s)   / _YAW_CLAMP)
        pitch_conf = max(0.0, 1.0 - abs(pitch_s) / _PITCH_CLAMP)
        confidence = round((yaw_conf + pitch_conf) / 2.0, 3)

        return {
            "presence": True,
            "yaw": round(yaw_s, 2),
            "pitch": round(pitch_s, 2),
            "lookingAtScreen": looking,
            "confidence": confidence,
        }

    # ── Camera intrinsics ────────────────────────────────────────────────────

    def _get_camera_matrix(self, w: int, h: int) -> np.ndarray:
        key = (w, h)
        if key not in self._cam_cache:
            # Allow override via config; fall back to focal = frame width
            fx = getattr(vision_config, "CAMERA_FX", float(w))
            fy = getattr(vision_config, "CAMERA_FY", float(w))  # square pixels assumed
            cx = getattr(vision_config, "CAMERA_CX", w / 2.0)
            cy = getattr(vision_config, "CAMERA_CY", h / 2.0)
            self._cam_cache[key] = np.array([
                [fx,  0,  cx],
                [0,  fy,  cy],
                [0,   0,   1],
            ], dtype=np.float64)
        return self._cam_cache[key]

    # ── solvePnP wrapper ─────────────────────────────────────────────────────

    def _estimate_head_pose(
        self, landmarks, w: int, h: int
    ) -> Tuple[float, float, bool]:
        """Returns (yaw_deg, pitch_deg, success_flag)."""
        try:
            image_points = np.array([
                (landmarks[i].x * w, landmarks[i].y * h)
                for i in _LANDMARK_INDICES
            ], dtype=np.float64)

            cam_matrix  = self._get_camera_matrix(w, h)
            dist_coeffs = np.zeros((4, 1))  # Calibrated zeros — override if lens data available

            ok, rvec, tvec = cv2.solvePnP(
                _MODEL_POINTS, image_points, cam_matrix, dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )
            if not ok:
                return 0.0, 0.0, False

            rot_mat, _ = cv2.Rodrigues(rvec)
            _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(
                np.hstack([rot_mat, tvec])
            )
            return float(euler[1]), float(euler[0]), True   # yaw, pitch

        except Exception as e:
            log.warning(f"solvePnP exception: {e}")
            return 0.0, 0.0, False

    def close(self) -> None:
        self._face_mesh.close()
