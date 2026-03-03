"""
LaRa Vision Perception — Engagement Score Tracker (v2.2)
v2.2 upgrade: Dual-rate scoring.

Two scores are maintained in parallel:
  - engagementScore    : Fast-decay (0.7/frame on absence). Raw internal signal.
  - engagementScoreUI  : Slow-decay (0.95/frame on absence). Caregiver dashboard signal.

This prevents the robotic precision of the internal score from shocking caregivers
with instant drops. The internal score is used for logic gating; the UI score is
used for display.
"""

from collections import deque
from typing import Deque, Tuple

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class EngagementTracker:
    """
    Dual-track rolling engagement scorer.

    Internal (fast): collapses on absence at ENGAGEMENT_DECAY_RATE_FAST (0.7).
    UI (slow):       collapses at ENGAGEMENT_DECAY_RATE_UI (0.95) for smooth display.

    Both are in [0.0–1.0]. The engine exposes both in PerceptionOutput.
    """

    W_FACE    = 0.45
    W_GAZE    = 0.45
    W_GESTURE = 0.10

    def __init__(self):
        buf_size = vision_config.ENGAGEMENT_BUFFER
        self._buf: Deque[float] = deque(maxlen=buf_size)
        self._current_score: float = 0.0
        self._ui_score:      float = 0.0

        # Pre-fill with zero so the first frame doesn't start at an artificially high mean
        for _ in range(buf_size):
            self._buf.append(0.0)

        log.info(
            f"EngagementTracker v2.2: face={self.W_FACE}, gaze={self.W_GAZE}, "
            f"gesture={self.W_GESTURE} (gaze-gated) | "
            f"decay_fast={vision_config.ENGAGEMENT_DECAY_RATE_FAST} "
            f"decay_ui={vision_config.ENGAGEMENT_DECAY_RATE_UI} | "
            f"buffer={buf_size}"
        )

    def update(
        self,
        face_present: bool,
        looking_at_screen: bool,
        gesture: str,
    ) -> Tuple[float, float]:
        """
        Returns (engagementScore, engagementScoreUI).

        Absence path: both scores decay independently.
        Presence path: both tracks updated from the same raw signal.
        """
        if not face_present:
            # Fast-decay internal track
            self._current_score = round(
                self._current_score * vision_config.ENGAGEMENT_DECAY_RATE_FAST, 4
            )
            self._buf.append(self._current_score)

            # Slow-decay UI track
            self._ui_score = round(
                self._ui_score * vision_config.ENGAGEMENT_DECAY_RATE_UI, 4
            )
            return self._current_score, self._ui_score

        # Normal scoring path (face present)
        gesture_active = (gesture != "NONE") and looking_at_screen
        raw = (
            self.W_FACE    * float(face_present)
            + self.W_GAZE    * float(looking_at_screen)
            + self.W_GESTURE * float(gesture_active)
        )
        self._buf.append(raw)
        self._current_score = round(sum(self._buf) / len(self._buf), 4)

        # UI score: weighted blend of previous UI score and new internal score
        # This makes it trail the internal score smoothly rather than jumping
        self._ui_score = round(0.8 * self._current_score + 0.2 * self._ui_score, 4)
        return self._current_score, self._ui_score

    def label(self, score: float) -> str:
        """Caregiver-facing engagement label."""
        if score >= vision_config.ENGAGEMENT_THRESHOLDS["high"]:
            return "Highly Engaged"
        elif score >= vision_config.ENGAGEMENT_THRESHOLDS["medium"]:
            return "Moderately Engaged"
        return "Frequently Distracted"
