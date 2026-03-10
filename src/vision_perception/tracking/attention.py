"""
LaRa Vision Perception — Attention State Tracker
Converts raw lookingAtScreen bool into a stable, smoothed attention state.

States:
  FOCUSED     — child is looking at screen, sustained
  DISTRACTED  — child is present but not looking at screen
  ABSENT      — face not detected

Uses minimum duration thresholds to avoid flickering between states.
"""

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# Minimum consecutive frames before state transition is accepted
# At 15fps: 5 frames = ~0.33s, 15 frames = ~1s
FOCUS_CONFIRM_FRAMES    = 5   # Must look at screen for N frames to become FOCUSED
DISTRACT_CONFIRM_FRAMES = 8   # Must look away for N frames to become DISTRACTED


class AttentionTracker:
    """
    Smoothed attention state machine.
    Prevents rapid flickering between FOCUSED / DISTRACTED.
    """

    def __init__(self):
        self._state: str = "UNKNOWN"
        self._candidate: str = "UNKNOWN"
        self._candidate_frames: int = 0
        self._distraction_frames: int = 0  # Total consecutive off-screen frames
        log.info("AttentionTracker initialised")

    def update(self, presence: bool, looking_at_screen: bool) -> tuple[str, int]:
        """
        Returns (attentionState: str, distractionFrames: int).
        """
        if not presence:
            self._state = "ABSENT"
            self._distraction_frames = 0
            self._candidate_frames = 0
            return self._state, 0

        candidate = "FOCUSED" if looking_at_screen else "DISTRACTED"

        if candidate == self._candidate:
            self._candidate_frames += 1
        else:
            self._candidate = candidate
            self._candidate_frames = 1

        # Confirm threshold depends on which direction we're transitioning
        threshold = FOCUS_CONFIRM_FRAMES if candidate == "FOCUSED" else DISTRACT_CONFIRM_FRAMES

        if self._candidate_frames >= threshold:
            if self._state != candidate:
                log.info(f"AttentionTracker: {self._state} → {candidate}")
            self._state = candidate

        # Track distraction duration
        if self._state == "DISTRACTED":
            self._distraction_frames += 1
        else:
            self._distraction_frames = 0

        return self._state, self._distraction_frames

    def reset(self) -> None:
        self.__init__()
