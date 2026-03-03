"""
LaRa Vision Perception — Engagement Score Tracker (v2.1)
v2.1 upgrade: Fast decay when presence is False.

When the child leaves the frame, the score doesn't hold at its last value.
Instead it decays multiplicatively each frame by ENGAGEMENT_DECAY_RATE_FAST.
This gives a smooth but aggressive drop, preventing a "ghost engagement"
artifact where the score stays high after the child walks away.
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
      face_present      → 0.45
      looking_at_screen → 0.45
      gesture_active    → 0.10  (ONLY when lookingAtScreen=True)

    Absence decay: if presence=False, current score *= ENGAGEMENT_DECAY_RATE_FAST
    instead of adding to buffer via normal path. This aggressively collapses
    the rolling average without requiring the buffer to fill with zeros.
    """

    W_FACE    = 0.45
    W_GAZE    = 0.45
    W_GESTURE = 0.10

    def __init__(self):
        self._buf: Deque[float] = deque(maxlen=vision_config.ENGAGEMENT_BUFFER)
        self._current_score: float = 0.0
        # Pre-fill buffer with zeros so we don't start at artificially high on first frame
        for _ in range(vision_config.ENGAGEMENT_BUFFER):
            self._buf.append(0.0)

        log.info(
            f"EngagementTracker v2.1: face={self.W_FACE}, gaze={self.W_GAZE}, "
            f"gesture={self.W_GESTURE} (gaze-gated) | "
            f"decay_rate={vision_config.ENGAGEMENT_DECAY_RATE_FAST} | "
            f"buffer={vision_config.ENGAGEMENT_BUFFER}"
        )

    def update(
        self,
        face_present: bool,
        looking_at_screen: bool,
        gesture: str,
    ) -> float:
        """
        Push one frame's signals; return smoothed engagement score.

        If presence is False → apply multiplicative decay to current score
        instead of the normal buffer-append path. This makes absence collapse
        the score rapidly without waiting N frames for the window to clear.
        """
        if not face_present:
            # Fast decay path — collapse directly on the current score
            self._current_score = round(
                self._current_score * vision_config.ENGAGEMENT_DECAY_RATE_FAST, 4
            )
            # Also push the decayed score into the buffer so rolling average
            # converges toward zero gradually
            self._buf.append(self._current_score)
            return self._current_score

        # Normal scoring path
        gesture_active = (gesture != "NONE") and looking_at_screen
        raw = (
            self.W_FACE    * float(face_present)
            + self.W_GAZE    * float(looking_at_screen)
            + self.W_GESTURE * float(gesture_active)
        )
        self._buf.append(raw)
        self._current_score = round(sum(self._buf) / len(self._buf), 4)
        return self._current_score

    def label(self, score: float) -> str:
        """Returns the caregiver-facing engagement label."""
        if score >= vision_config.ENGAGEMENT_THRESHOLDS["high"]:
            return "Highly Engaged"
        elif score >= vision_config.ENGAGEMENT_THRESHOLDS["medium"]:
            return "Moderately Engaged"
        return "Frequently Distracted"
