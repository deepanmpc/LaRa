"""
LaRa Vision Perception — Engagement Score Tracker
Combines face presence, gaze stability, and head-pose smoothness
into a single rolling engagement float [0.0 – 1.0].
"""

from collections import deque
from typing import Deque

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class EngagementTracker:
    """
    Maintains a rolling buffer of per-frame engagement signals and
    produces a smoothed score without recomputing from scratch each frame.

    Signals:
      - face_present   (bool)  → 0.4 weight
      - looking_at_screen (bool) → 0.4 weight
      - gesture_active (bool)  → 0.2 weight  (any non-NONE gesture)
    """

    WEIGHTS = {
        "face": 0.4,
        "gaze": 0.4,
        "gesture": 0.2,
    }

    def __init__(self):
        self._buf: Deque[float] = deque(maxlen=vision_config.ENGAGEMENT_BUFFER)
        log.info(f"EngagementTracker initialised (buffer={vision_config.ENGAGEMENT_BUFFER})")

    def update(
        self,
        face_present: bool,
        looking_at_screen: bool,
        gesture: str,
    ) -> float:
        """
        Push one frame's signals into the buffer and return smoothed score.
        """
        raw = (
            self.WEIGHTS["face"] * float(face_present)
            + self.WEIGHTS["gaze"] * float(looking_at_screen)
            + self.WEIGHTS["gesture"] * float(gesture != "NONE")
        )
        self._buf.append(raw)
        score = sum(self._buf) / len(self._buf)
        return round(score, 4)

    def label(self, score: float) -> str:
        """Returns the caregiver-facing engagement label."""
        if score >= vision_config.ENGAGEMENT_THRESHOLDS["high"]:
            return "Highly Engaged"
        elif score >= vision_config.ENGAGEMENT_THRESHOLDS["medium"]:
            return "Moderately Engaged"
        return "Frequently Distracted"
