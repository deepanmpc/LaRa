"""
Tests for PerceptionEngine core logic (no camera required).
v2.2 compatible: update() returns (score, ui_score) tuple.
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


# ── State machine tests ──────────────────────────────────────

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


# ── PerceptionOutput dataclass tests ────────────────────────────

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
    assert isinstance(d["detectedObjects"], list)  # tuple → list for JSON

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


# ── Engagement tracker tests ─────────────────────────────────

def test_engagement_returns_tuple():
    """v2.2: update() must return (score, ui_score) tuple."""
    t = EngagementTracker()
    result = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    assert isinstance(result, tuple)
    assert len(result) == 2
    score, ui_score = result
    assert 0.0 <= score <= 1.0
    assert 0.0 <= ui_score <= 1.0

def test_engagement_all_active():
    t = EngagementTracker()
    score = None
    for _ in range(20):
        score, _ = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    assert score > 0.9

def test_engagement_all_inactive():
    t = EngagementTracker()
    score = None
    for _ in range(20):
        score, _ = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    assert score < 0.05

def test_engagement_fast_decay():
    """When face absent, score should collapse quickly."""
    t = EngagementTracker()
    # Build up a high score
    for _ in range(20):
        t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    # Now disappear for 15 frames
    for _ in range(15):
        score, _ = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    # At 0.7^15 ≈ 0.005, the score should be very low
    assert score < 0.05

def test_engagement_ui_score_slower_than_internal():
    """UI score should remain higher than internal score on absence."""
    t = EngagementTracker()
    for _ in range(20):
        t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    # Disappear for 5 frames
    for _ in range(5):
        score, ui_score = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    # UI score decays at 0.95 vs internal 0.7 — UI should be higher
    assert ui_score >= score

def test_engagement_gaze_gates_gesture():
    """Gesture should not contribute if not looking at screen."""
    t1 = EngagementTracker()
    t2 = EngagementTracker()
    for _ in range(20):
        s1, _ = t1.update(face_present=True, looking_at_screen=False, gesture="OPEN_PALM")
        s2, _ = t2.update(face_present=True, looking_at_screen=False, gesture="NONE")
    # With gesture gated by gaze, both scores should be equal
    assert s1 == s2

def test_engagement_labels():
    t = EngagementTracker()
    assert t.label(0.9) == "Highly Engaged"
    assert t.label(0.5) == "Moderately Engaged"
    assert t.label(0.2) == "Frequently Distracted"


# ── Memory tracking tests ────────────────────────────────────

def test_memory_peak_tracking():
    state = PerceptionState()
    # Simulate 3 sessions with increasing peaks
    mb = state.sample_memory()
    assert mb > 0
    state.record_session_peak()
    # Peak fragmentation needs 3 windows — should be False initially
    assert state.peak_leak_suspected() is False

def test_stall_count_resets_on_set_running():
    state = PerceptionState()
    state.stall_count = 7
    state.set_running()
    assert state.stall_count == 0

# ── Parallel Execution tests ──────────────────────────────────
from unittest.mock import patch

@patch('core.engine.FaceDetector')
@patch('core.engine.HandDetector')
@patch('core.engine.ObjectDetector')
def test_engine_executor_parallel(mock_obj, mock_hand, mock_face):
    from core.engine import PerceptionEngine
    engine = PerceptionEngine()
    assert hasattr(engine, '_executor')
    engine.stop()

