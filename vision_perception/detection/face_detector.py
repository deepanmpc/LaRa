"""
LaRa Vision Perception — Face Detector
MediaPipe face detection + OpenCV solvePnP head-pose estimation.
Outputs: presence, lookingAtScreen, raw yaw/pitch for the engagement tracker.
"""

from collections import deque
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# 3-D model reference points for head pose (generic human skull)
_MODEL_POINTS = np.array([
    (0.0,    0.0,    0.0),     # Nose tip
    (0.0,   -330.0, -65.0),    # Chin
    (-225.0, 170.0, -135.0),   # Left eye corner
    (225.0,  170.0, -135.0),   # Right eye corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0,  -150.0, -125.0),  # Right mouth corner
], dtype=np.float64)


class FaceDetector:
    """
    Runs MediaPipe FaceMesh to:
      1. Detect face presence.
      2. Estimate head pose (yaw, pitch) via solvePnP.
      3. Classify gaze as lookingAtScreen based on config thresholds.

    Head pose output is smoothed over a rolling buffer.
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
        log.info("FaceDetector initialised (MediaPipe FaceMesh)")

    def process(self, frame: np.ndarray) -> dict:
        """
        Args:
            frame: BGR uint8 numpy array.
        Returns:
            dict with keys: presence (bool), yaw (float), pitch (float),
                            lookingAtScreen (bool)
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {"presence": False, "yaw": 0.0, "pitch": 0.0, "lookingAtScreen": False}

        lm = results.multi_face_landmarks[0].landmark
        yaw, pitch = self._estimate_head_pose(lm, w, h)

        # Smooth via buffer
        self._yaw_buf.append(yaw)
        self._pitch_buf.append(pitch)
        yaw_s = float(np.mean(self._yaw_buf))
        pitch_s = float(np.mean(self._pitch_buf))

        looking = (
            abs(yaw_s) < vision_config.GAZE_YAW_THRESHOLD
            and abs(pitch_s) < vision_config.GAZE_PITCH_THRESHOLD
        )

        return {
            "presence": True,
            "yaw": round(yaw_s, 2),
            "pitch": round(pitch_s, 2),
            "lookingAtScreen": looking,
        }

    # ── Internal ────────────────────────────────────────────────

    def _estimate_head_pose(self, landmarks, w: int, h: int) -> Tuple[float, float]:
        """Returns (yaw_deg, pitch_deg) from solvePnP."""
        # Use 6-landmark subset: nose tip, chin, eye corners, mouth corners
        indices = [1, 152, 263, 33, 287, 57]
        image_points = np.array([
            (landmarks[i].x * w, landmarks[i].y * h) for i in indices
        ], dtype=np.float64)

        focal = w
        cam_matrix = np.array([
            [focal, 0,     w / 2],
            [0,     focal, h / 2],
            [0,     0,     1    ],
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1))

        ok, rvec, tvec = cv2.solvePnP(
            _MODEL_POINTS, image_points, cam_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not ok:
            return 0.0, 0.0

        rot_mat, _ = cv2.Rodrigues(rvec)
        _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(
            np.hstack([rot_mat, tvec])
        )
        pitch = float(euler[0])
        yaw   = float(euler[1])
        return yaw, pitch

    def close(self) -> None:
        self._face_mesh.close()
