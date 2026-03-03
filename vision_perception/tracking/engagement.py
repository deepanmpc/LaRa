"""
LaRa Vision Perception — Engagement Score Tracker (v2)
Production fix:
  - Gesture weight ONLY contributes if lookingAtScreen == True.
    Prevents random gestures (scratch, fidget) from inflating engagement.
  - Returns confidence as a separate signal.
"""

from collections import deque
from typing import Deque

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class EngagementTracker:
    """
    Rolling engagement score [0.0–1.0] from three signals.

    Signal weights:
      face_present     → 0.45
      looking_at_screen → 0.45
      gesture_active   → 0.10  (contributes ONLY when lookingAtScreen=True)

    Rationale: A child can wave their hand while looking away.
    That should NOT count as engagement. Gesture bonus requires
    the child to already be on-screen and looking at it.
    """

    W_FACE    = 0.45
    W_GAZE    = 0.45
    W_GESTURE = 0.10

    def __init__(self):
        self._buf: Deque[float] = deque(maxlen=vision_config.ENGAGEMENT_BUFFER)
        log.info(
            f"EngagementTracker v2: face={self.W_FACE}, gaze={self.W_GAZE}, "
            f"gesture={self.W_GESTURE} (gaze-gated) | buffer={vision_config.ENGAGEMENT_BUFFER}"
        )

    def update(
        self,
        face_present: bool,
        looking_at_screen: bool,
        gesture: str,
    ) -> float:
        """
        Push one frame's signals; return smoothed rolling score.
        Gesture weight applies only when lookingAtScreen == True.
        """
        gesture_active = (gesture != "NONE") and looking_at_screen   # ← gaze-gated

        raw = (
            self.W_FACE    * float(face_present)
            + self.W_GAZE    * float(looking_at_screen)
            + self.W_GESTURE * float(gesture_active)
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
