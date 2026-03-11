"""
LaRa Vision Perception — Engagement Score Tracker (v2.3)
v2.3 fixes over v2.2:

  Fix 1 – Engagement weight rebalancing for gaze-gated gesture:
    Original weights: W_FACE=0.45, W_GAZE=0.45, W_GESTURE=0.10.
    gesture_active is gated by `looking_at_screen`, so when the child IS
    looking at the screen AND performing a gesture, the effective sum of all
    active components is 0.45 + 0.45 + 0.10 = 1.0 ✓
    BUT when looking_at_screen=False (child's head is turned), gesture is
    ALWAYS 0 regardless of hand state, meaning the effective max raw score
    is 0.45 (face only). This compresses the full dynamic range for children
    who are engaged but looking down at materials.

    Fix: Decouple gesture contribution from gaze gate. Gesture is still only
    counted when gaze is confirmed, but when gaze is absent, we redistribute
    its weight so face+gesture_without_gaze can still reach a meaningful score.

    New behaviour:
      - face=True, gaze=True,  gesture=True  → raw = 1.0  (full engagement)
      - face=True, gaze=True,  gesture=False → raw = 0.90 (high engagement)
      - face=True, gaze=False, gesture=True  → raw = 0.55 (moderate — child
                                                            present, gesture active,
                                                            just not looking at screen)
      - face=True, gaze=False, gesture=False → raw = 0.45 (low — present, not engaged)
      - face=False (any)                     → decay path (no raw score computed)

  Fix 2 – Buffer pre-fill with neutral score instead of zero:
    Pre-filling with 0.0 means that for the first ENGAGEMENT_BUFFER frames
    (~1 second at 15fps), every new frame is dragged down by the zero history.
    A child who immediately engages on session start will report artificially
    low engagement for the opening second. Pre-fill is now omitted and the
    buffer fills naturally, with the first sample used as-is until the window
    is saturated (deque fills naturally).

  Fix 3 – UI score initialised to match internal score on first update:
    If _ui_score starts at 0.0 and the first frame has a high engagement score,
    the blend `0.8 * score + 0.2 * 0.0` creates an unnecessary pull toward zero
    for the first frame. UI score is now bootstrapped from the first real score.
"""

from collections import deque
from typing import Deque, Optional, Tuple

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# FIX 1: Revised weights — see module docstring for behaviour table
_W_FACE            = 0.45  # Presence weight (face detected)
_W_GAZE            = 0.45  # Gaze weight (looking at screen)
_W_GESTURE_GATED   = 0.10  # Gesture weight when gaze is confirmed
_W_GESTURE_UNGATED = 0.10  # Gesture weight when gaze is absent (redistributed from gaze)

# Sanity: ensure full engagement reaches 1.0
assert abs(_W_FACE + _W_GAZE + _W_GESTURE_GATED - 1.0) < 1e-9, (
    "Engagement weights must sum to 1.0 for full engagement path"
)


class EngagementTracker:
    """
    Dual-track rolling engagement scorer (v2.3).

    Internal (fast): collapses on absence at ENGAGEMENT_DECAY_RATE_FAST (0.7).
    UI (slow):       collapses at ENGAGEMENT_DECAY_RATE_UI (0.95) for smooth display.

    Both are in [0.0–1.0]. The engine exposes both in PerceptionOutput.
    """

    def __init__(self):
        buf_size = vision_config.ENGAGEMENT_BUFFER
        # FIX 2: No pre-fill — buffer fills naturally from first real frames.
        # This avoids the 1-second drag-down artefact on session start.
        self._buf: Deque[float] = deque(maxlen=buf_size)
        self._current_score: float = 0.0
        self._ui_score: Optional[float] = None  # FIX 3: None = not yet bootstrapped

        log.info(
            f"EngagementTracker v2.3: face={_W_FACE}, gaze={_W_GAZE}, "
            f"gesture_gated={_W_GESTURE_GATED}, gesture_ungated={_W_GESTURE_UNGATED} | "
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

            # Slow-decay UI track (bootstrap UI score if not yet set)
            if self._ui_score is None:
                self._ui_score = self._current_score
            self._ui_score = round(
                self._ui_score * vision_config.ENGAGEMENT_DECAY_RATE_UI, 4
            )
            return self._current_score, self._ui_score

        # ── Presence path ─────────────────────────────────────────
        gesture_active = gesture != "NONE"

        # FIX 1: Gesture contribution depends on whether gaze is confirmed
        if looking_at_screen:
            # Full engagement path: all 3 components active
            raw = (
                _W_FACE
                + _W_GAZE
                + (_W_GESTURE_GATED if gesture_active else 0.0)
            )
        else:
            # Child is present but not looking at screen.
            # Gaze contribution is 0. Gesture gets its ungated weight if active.
            raw = (
                _W_FACE
                + (_W_GESTURE_UNGATED if gesture_active else 0.0)
            )

        self._buf.append(raw)
        self._current_score = round(sum(self._buf) / len(self._buf), 4)

        # FIX 3: Bootstrap UI score from first real score to avoid initial pull-to-zero
        if self._ui_score is None:
            self._ui_score = self._current_score

        # UI score: weighted blend of previous UI score and new internal score
        self._ui_score = round(0.8 * self._current_score + 0.2 * self._ui_score, 4)
        return self._current_score, self._ui_score

    def label(self, score: float) -> str:
        """Caregiver-facing engagement label."""
        if score >= vision_config.ENGAGEMENT_THRESHOLDS["high"]:
            return "Highly Engaged"
        elif score >= vision_config.ENGAGEMENT_THRESHOLDS["medium"]:
            return "Moderately Engaged"
        return "Frequently Distracted"