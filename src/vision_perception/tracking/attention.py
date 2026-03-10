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
    Smoothed attention state machine for child engagement monitoring.

    Designed for neurodiverse children — uses hysteresis so brief head
    movements do not trigger distraction alerts. A child must consistently
    look away for ~0.5s before DISTRACTED is reported.
    """

    def __init__(self):
        self._state: str = "UNKNOWN"
        self._candidate: str = "UNKNOWN"
        self._candidate_frames: int = 0
        self._distraction_frames: int = 0
        log.info(
            f"AttentionTracker v1.0 initialised "
            f"(focus_confirm={FOCUS_CONFIRM_FRAMES}, "
            f"distract_confirm={DISTRACT_CONFIRM_FRAMES})"
        )

    def update(self, presence: bool, looking_at_screen: bool) -> tuple:
        """
        Call once per frame.

        Args:
            presence:         True if a face is detected in the frame.
            looking_at_screen: True if head pose indicates child is looking at screen.

        Returns:
            (attentionState: str, distractionFrames: int)
        """
        # ── Absence path ──────────────────────────────────────────
        if not presence:
            self._state = "ABSENT"
            self._candidate = "UNKNOWN"
            self._candidate_frames = 0
            self._distraction_frames = 0
            return self._state, 0

        # ── Candidate state ───────────────────────────────────────
        candidate = "FOCUSED" if looking_at_screen else "DISTRACTED"

        if candidate == self._candidate:
            self._candidate_frames += 1
        else:
            # Reset streak on direction change
            self._candidate = candidate
            self._candidate_frames = 1

        # ── Threshold check ───────────────────────────────────────
        threshold = (
            FOCUS_CONFIRM_FRAMES
            if candidate == "FOCUSED"
            else DISTRACT_CONFIRM_FRAMES
        )

        if self._candidate_frames >= threshold:
            if self._state != candidate:
                log.info({
                    "msg": "AttentionTracker state transition",
                    "from": self._state,
                    "to": candidate,
                    "confirmed_after_frames": self._candidate_frames,
                })
            self._state = candidate

        # ── Distraction frame counter ─────────────────────────────
        if self._state == "DISTRACTED":
            self._distraction_frames += 1
        else:
            self._distraction_frames = 0

        return self._state, self._distraction_frames

    @property
    def state(self) -> str:
        """Current confirmed attention state."""
        return self._state

    def reset(self) -> None:
        """Reset all state — call on soft restart."""
        self._state = "UNKNOWN"
        self._candidate = "UNKNOWN"
        self._candidate_frames = 0
        self._distraction_frames = 0
        log.info("AttentionTracker reset")
