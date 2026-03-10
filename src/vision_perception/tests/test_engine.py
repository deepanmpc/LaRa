"""
Tests for PerceptionEngine core logic (no camera required).
v2.3 compatible: updated for engagement tracker pre-fill removal and
peak_leak_suspected off-by-one fix.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from core.state import (
    PerceptionState, EngineState, perception_state,
    PerceptionOutput, PerceptionSkipReason, PerceptionConfidence,
)
from tracking.engagement import EngagementTracker


# ── State machine tests ──────────────────────────────────────────────────────

def test_initial_state_is_stopped():
    state = PerceptionState()
    assert state.engine_state == EngineState.STOPPED
    assert not state.is_running()


def test_set_running():
    state = PerceptionState()
    state.set_running()
    assert state.engine_state == EngineState.RUNNING
    assert state.is_running()


def test_set_error():
    state = PerceptionState()
    state.set_error("camera disconnected")
    assert state.engine_state == EngineState.ERROR
    assert state.error_message == "camera disconnected"
    assert not state.is_running()


def test_fps_tick():
    state = PerceptionState()
    for _ in range(20):
        state.tick()
    assert state.fps >= 0.0


def test_stall_count_thread_safe_increment():
    """FIX 2 test: increment_stall must atomically increment and return new value."""
    state = PerceptionState()
    assert state.stall_count == 0
    val = state.increment_stall()
    assert val == 1
    assert state.stall_count == 1
    state.increment_stall()
    assert state.stall_count == 2


def test_stall_count_resets_on_set_running():
    state = PerceptionState()
    state.stall_count = 7
    state.set_running()
    assert state.stall_count == 0


# ── PerceptionOutput dataclass tests ─────────────────────────────────────────

def test_output_is_frozen():
    """Frozen dataclass must be immutable."""
    out = PerceptionOutput(presence=True, engagementScore=0.5)
    with pytest.raises(Exception):
        out.presence = False  # must raise FrozenInstanceError


def test_output_to_dict_has_all_keys():
    out = PerceptionOutput(
        presence=True,
        lookingAtScreen=True,
        engagementScore=0.8,
        engagementScoreUI=0.85,
        gesture="THUMBS_UP",
        detectedObjects=("book",),
        systemConfidence=0.75,
        timestamp=1234567890.0,
    )
    d = out.to_dict()
    assert "presence" in d
    assert "engagementScore" in d
    assert "engagementScoreUI" in d
    assert "systemConfidence" in d
    assert "skipped" in d
    assert "confidence" in d
    assert isinstance(d["detectedObjects"], list)


def test_skip_reason_fields():
    skip = PerceptionSkipReason(quality=True)
    assert skip.quality is True
    assert skip.throttle is False
    assert skip.camera_drop is False


def test_publish_and_latest():
    """Atomic swap: latest should always return what was published."""
    state = PerceptionState()
    out = PerceptionOutput(presence=True, engagementScore=0.72, timestamp=9999.0)
    state.publish(out)
    assert state.latest.presence is True
    assert state.latest.engagementScore == 0.72


# ── Engagement tracker tests ──────────────────────────────────────────────────

def test_engagement_returns_tuple():
    """update() must return (score, ui_score) tuple."""
    t = EngagementTracker()
    result = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    assert isinstance(result, tuple)
    assert len(result) == 2
    score, ui_score = result
    assert 0.0 <= score <= 1.0
    assert 0.0 <= ui_score <= 1.0


def test_engagement_full_engagement_reaches_max():
    """FIX 1: full engagement (face + gaze + gesture) should approach 1.0."""
    t = EngagementTracker()
    score = None
    for _ in range(30):
        score, _ = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    # After buffer fills with raw=1.0, score must be very close to 1.0
    assert score >= 0.98, f"Expected ~1.0 for full engagement, got {score}"


def test_engagement_all_inactive():
    t = EngagementTracker()
    score = None
    for _ in range(20):
        score, _ = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    assert score < 0.05


def test_engagement_fast_decay():
    """When face absent, score should collapse quickly."""
    t = EngagementTracker()
    for _ in range(20):
        t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    for _ in range(15):
        score, _ = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    # At 0.7^15 ≈ 0.005, score should be very low
    assert score < 0.05


def test_engagement_ui_score_slower_than_internal():
    """UI score should remain higher than internal score on absence."""
    t = EngagementTracker()
    for _ in range(20):
        t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    for _ in range(5):
        score, ui_score = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    assert ui_score >= score


def test_engagement_gaze_gates_gesture_contribution():
    """
    FIX 1 test: When gaze is absent, gesture should give a small boost (ungated)
    rather than being completely ignored as in v2.2.
    Child looking away + gesture active should score higher than no gesture.
    """
    t1 = EngagementTracker()
    t2 = EngagementTracker()
    for _ in range(20):
        s1, _ = t1.update(face_present=True, looking_at_screen=False, gesture="OPEN_PALM")
        s2, _ = t2.update(face_present=True, looking_at_screen=False, gesture="NONE")
    # With ungated gesture weight, s1 (gesture active) should be slightly higher
    assert s1 > s2, (
        f"Gesture while not looking should give a small boost: s1={s1}, s2={s2}"
    )


def test_engagement_no_pre_fill_drag():
    """
    FIX 2 test: First frame with full engagement should not be dragged to near zero
    by zero pre-fill. Score after first frame should be > 0.5.
    """
    t = EngagementTracker()
    score, _ = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    # Without pre-fill, first frame raw=1.0 → average of [1.0] = 1.0
    assert score > 0.5, f"First-frame score should not be pre-fill-dragged: {score}"


def test_engagement_ui_score_bootstrapped():
    """
    FIX 3 test: UI score on first frame should equal internal score (not be blended with 0.0).
    """
    t = EngagementTracker()
    score, ui_score = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    # On first update, ui_score bootstraps from score (no 0.2 * 0.0 pull)
    assert ui_score == score, (
        f"UI score should bootstrap from internal score on first frame: "
        f"score={score}, ui_score={ui_score}"
    )


def test_engagement_labels():
    t = EngagementTracker()
    assert t.label(0.9) == "Highly Engaged"
    assert t.label(0.5) == "Moderately Engaged"
    assert t.label(0.2) == "Frequently Distracted"


# ── Memory tracking tests ─────────────────────────────────────────────────────

def test_memory_peak_tracking():
    state = PerceptionState()
    mb = state.sample_memory()
    assert mb > 0
    state.record_session_peak()
    assert state.peak_leak_suspected() is False


def test_peak_leak_suspected_off_by_one_fix():
    """
    FIX 1 test: Three strictly increasing peaks should be detected.
    Original code used range(len-3, len-1) and missed the last peak.
    """
    state = PerceptionState()
    # Inject 3 strictly increasing fake peaks
    state._session_peaks = [100.0, 200.0, 300.0]
    assert state.peak_leak_suspected() is True, (
        "Three strictly increasing peaks should trigger fragmentation warning"
    )


def test_peak_leak_not_suspected_with_decreasing_peak():
    state = PerceptionState()
    state._session_peaks = [300.0, 200.0, 100.0]
    assert state.peak_leak_suspected() is False


def test_peak_leak_not_suspected_with_only_two_peaks():
    state = PerceptionState()
    state._session_peaks = [100.0, 200.0]
    assert state.peak_leak_suspected() is False


# ── AttentionTracker tests ────────────────────────────────────────────────────

from tracking.attention import AttentionTracker


def test_attention_initial_state_is_unknown():
    """Fresh tracker must start in UNKNOWN state."""
    t = AttentionTracker()
    assert t.state == "UNKNOWN"


def test_attention_absent_on_no_presence():
    """If face is not present, state must immediately be ABSENT regardless of history."""
    t = AttentionTracker()
    state, frames = t.update(presence=False, looking_at_screen=False)
    assert state == "ABSENT"
    assert frames == 0


def test_attention_absent_clears_distraction_counter():
    """Going absent must reset distractionFrames to 0."""
    t = AttentionTracker()
    # Build up distraction
    for _ in range(20):
        t.update(presence=True, looking_at_screen=False)
    # Then go absent
    state, frames = t.update(presence=False, looking_at_screen=False)
    assert state == "ABSENT"
    assert frames == 0


def test_attention_focused_requires_confirm_threshold():
    """
    FOCUSED must not be reported until FOCUS_CONFIRM_FRAMES consecutive
    looking_at_screen=True frames have been seen.
    Before threshold: state stays UNKNOWN (or previous state).
    At threshold: state becomes FOCUSED.
    """
    from tracking.attention import FOCUS_CONFIRM_FRAMES
    t = AttentionTracker()

    # One frame short of threshold — should NOT be FOCUSED yet
    for i in range(FOCUS_CONFIRM_FRAMES - 1):
        state, _ = t.update(presence=True, looking_at_screen=True)
        assert state != "FOCUSED", (
            f"Should not be FOCUSED before threshold at frame {i+1}"
        )

    # Exactly at threshold — must now be FOCUSED
    state, _ = t.update(presence=True, looking_at_screen=True)
    assert state == "FOCUSED"


def test_attention_distracted_requires_confirm_threshold():
    """
    DISTRACTED must not be reported until DISTRACT_CONFIRM_FRAMES consecutive
    looking_at_screen=False frames have been seen (with presence=True).
    """
    from tracking.attention import DISTRACT_CONFIRM_FRAMES
    t = AttentionTracker()

    # One frame short of threshold
    for i in range(DISTRACT_CONFIRM_FRAMES - 1):
        state, _ = t.update(presence=True, looking_at_screen=False)
        assert state != "DISTRACTED", (
            f"Should not be DISTRACTED before threshold at frame {i+1}"
        )

    # Exactly at threshold — must now be DISTRACTED
    state, _ = t.update(presence=True, looking_at_screen=False)
    assert state == "DISTRACTED"


def test_attention_distraction_frames_count_up():
    """
    distractionFrames must increment by 1 each frame while DISTRACTED.
    """
    from tracking.attention import DISTRACT_CONFIRM_FRAMES
    t = AttentionTracker()

    # Reach DISTRACTED state
    for _ in range(DISTRACT_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=False)

    # Now count up
    for expected in range(1, 6):
        state, frames = t.update(presence=True, looking_at_screen=False)
        assert state == "DISTRACTED"
        assert frames == DISTRACT_CONFIRM_FRAMES + expected, (
            f"Expected distractionFrames={DISTRACT_CONFIRM_FRAMES + expected}, got {frames}"
        )


def test_attention_distraction_frames_reset_on_focused():
    """
    distractionFrames must reset to 0 once state transitions back to FOCUSED.
    """
    from tracking.attention import DISTRACT_CONFIRM_FRAMES, FOCUS_CONFIRM_FRAMES
    t = AttentionTracker()

    # Go DISTRACTED
    for _ in range(DISTRACT_CONFIRM_FRAMES + 5):
        t.update(presence=True, looking_at_screen=False)

    # Go back FOCUSED
    for _ in range(FOCUS_CONFIRM_FRAMES):
        state, frames = t.update(presence=True, looking_at_screen=True)

    assert state == "FOCUSED"
    assert frames == 0


def test_attention_brief_look_away_does_not_trigger_distracted():
    """
    A brief glance away (fewer frames than DISTRACT_CONFIRM_FRAMES) must NOT
    transition to DISTRACTED. This is the hysteresis protection for children
    who briefly turn their heads.
    """
    from tracking.attention import FOCUS_CONFIRM_FRAMES, DISTRACT_CONFIRM_FRAMES
    t = AttentionTracker()

    # Establish FOCUSED
    for _ in range(FOCUS_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=True)
    assert t.state == "FOCUSED"

    # Look away briefly — one fewer than threshold
    for _ in range(DISTRACT_CONFIRM_FRAMES - 1):
        t.update(presence=True, looking_at_screen=False)

    # Must still be FOCUSED
    assert t.state == "FOCUSED", (
        "Brief look-away should not trigger DISTRACTED due to hysteresis"
    )


def test_attention_brief_look_away_then_returns_to_focused():
    """
    After a brief look-away that did NOT trigger DISTRACTED, looking back
    at screen must quickly re-confirm FOCUSED.
    """
    from tracking.attention import FOCUS_CONFIRM_FRAMES, DISTRACT_CONFIRM_FRAMES
    t = AttentionTracker()

    # Establish FOCUSED
    for _ in range(FOCUS_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=True)

    # Brief look-away (not enough to trigger DISTRACTED)
    for _ in range(DISTRACT_CONFIRM_FRAMES - 1):
        t.update(presence=True, looking_at_screen=False)

    # Look back — should re-confirm FOCUSED quickly
    for _ in range(FOCUS_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=True)

    assert t.state == "FOCUSED"


def test_attention_reset_clears_all_state():
    """
    reset() must bring tracker back to UNKNOWN with zero counters,
    as if it was just constructed.
    """
    from tracking.attention import DISTRACT_CONFIRM_FRAMES
    t = AttentionTracker()

    # Build up state
    for _ in range(DISTRACT_CONFIRM_FRAMES + 10):
        t.update(presence=True, looking_at_screen=False)
    assert t.state == "DISTRACTED"

    t.reset()
    assert t.state == "UNKNOWN"
    state, frames = t.update(presence=False, looking_at_screen=False)
    assert state == "ABSENT"
    assert frames == 0


def test_attention_absent_to_focused_full_path():
    """
    Full path: UNKNOWN → ABSENT → FOCUSED.
    Simulates a child sitting down and starting to look at the screen.
    """
    from tracking.attention import FOCUS_CONFIRM_FRAMES
    t = AttentionTracker()

    # No face yet
    state, _ = t.update(presence=False, looking_at_screen=False)
    assert state == "ABSENT"

    # Face appears, looking at screen
    for _ in range(FOCUS_CONFIRM_FRAMES):
        state, _ = t.update(presence=True, looking_at_screen=True)

    assert state == "FOCUSED"


def test_attention_focused_to_distracted_to_focused_cycle():
    """
    Full attention cycle: FOCUSED → DISTRACTED → FOCUSED.
    Simulates a child getting distracted and then re-engaging.
    """
    from tracking.attention import FOCUS_CONFIRM_FRAMES, DISTRACT_CONFIRM_FRAMES
    t = AttentionTracker()

    # Establish FOCUSED
    for _ in range(FOCUS_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=True)
    assert t.state == "FOCUSED"

    # Child looks away long enough
    for _ in range(DISTRACT_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=False)
    assert t.state == "DISTRACTED"

    # Child looks back
    for _ in range(FOCUS_CONFIRM_FRAMES):
        t.update(presence=True, looking_at_screen=True)
    assert t.state == "FOCUSED"


def test_attention_output_in_perception_output():
    """
    PerceptionOutput must contain attentionState and distractionFrames fields
    with correct defaults and correct serialisation via to_dict().
    """
    out = PerceptionOutput(
        presence=True,
        lookingAtScreen=True,
        engagementScore=0.9,
        attentionState="FOCUSED",
        distractionFrames=0,
        timestamp=1234567890.0,
    )
    assert out.attentionState == "FOCUSED"
    assert out.distractionFrames == 0

    d = out.to_dict()
    assert "attentionState" in d
    assert "distractionFrames" in d
    assert d["attentionState"] == "FOCUSED"
    assert d["distractionFrames"] == 0


def test_attention_distracted_output_in_perception_output():
    """
    PerceptionOutput with DISTRACTED state and non-zero distractionFrames
    must serialise correctly.
    """
    out = PerceptionOutput(
        presence=True,
        lookingAtScreen=False,
        engagementScore=0.45,
        attentionState="DISTRACTED",
        distractionFrames=42,
        timestamp=9999.0,
    )
    d = out.to_dict()
    assert d["attentionState"] == "DISTRACTED"
    assert d["distractionFrames"] == 42


def test_attention_default_unknown_in_perception_output():
    """
    Default PerceptionOutput (no fields set) must have UNKNOWN attentionState
    and 0 distractionFrames.
    """
    out = PerceptionOutput()
    assert out.attentionState == "UNKNOWN"
    assert out.distractionFrames == 0