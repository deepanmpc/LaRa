"""
Tests for PerceptionEngine core logic (no camera required).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from core.state import PerceptionState, EngineState, perception_state
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
    import time
    state = PerceptionState()
    for _ in range(20):
        state.tick()
    # FPS starts at 0 until 1 second passes; just ensure no crash
    assert state.fps >= 0.0


# ── Engagement tracker tests ──────────────────────────────────

def test_engagement_all_active():
    t = EngagementTracker()
    score = None
    for _ in range(20):
        score = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    assert score > 0.9  # Expected ≈1.0 when fully filled


def test_engagement_all_inactive():
    t = EngagementTracker()
    score = None
    for _ in range(20):
        score = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    assert score < 0.05  # Expected ≈0.0


def test_engagement_labels():
    t = EngagementTracker()
    assert t.label(0.9) == "Highly Engaged"
    assert t.label(0.5) == "Moderately Engaged"
    assert t.label(0.2) == "Frequently Distracted"


def test_engagement_buffer_rollover():
    """Scores before buffer fills should still return a valid float."""
    t = EngagementTracker()
    score = t.update(True, True, "NONE")
    assert 0.0 <= score <= 1.0
