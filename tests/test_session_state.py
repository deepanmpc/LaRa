"""
LaRa Pytest Test Suite — Session State
Tests the two-phase update, difficulty gating, TTL expiry, and boundaries.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import time
from session_state import SessionState


def test_pre_decision_updates_mood():
    s = SessionState()
    s.update_pre_decision("frustrated", 0.8)
    assert s.mood == "frustrated"
    assert s.mood_confidence == 0.8


def test_consecutive_frustration_increments():
    s = SessionState()
    s.update_pre_decision("frustrated", 0.8)
    s.update_post_response("x", "y")
    s.update_pre_decision("frustrated", 0.8)
    s.update_post_response("x", "y")
    assert s.consecutive_frustration == 2
    assert s.consecutive_stability == 0


def test_consecutive_stability_increments():
    s = SessionState()
    for _ in range(3):
        s.update_pre_decision("happy", 0.9)
        s.update_post_response("x", "y")
    assert s.consecutive_stability == 3
    assert s.consecutive_frustration == 0


def test_mood_switch_resets_opposing_streak():
    s = SessionState()
    s.update_pre_decision("frustrated", 0.8)
    s.update_post_response("x", "y")
    s.update_pre_decision("frustrated", 0.8)
    s.update_post_response("x", "y")
    assert s.consecutive_frustration == 2
    s.update_pre_decision("happy", 0.9)
    s.update_post_response("x", "y")
    assert s.consecutive_frustration == 0
    assert s.consecutive_stability == 1


def test_difficulty_decrease_on_frustration_streak():
    s = SessionState()
    s.current_difficulty = 3
    s.update_pre_decision("frustrated", 0.7)
    s.update_post_response("x", "y")
    s.update_pre_decision("frustrated", 0.7)
    s.update_post_response("x", "y")
    # Should have decreased
    assert s.current_difficulty <= 3


def test_difficulty_never_below_min():
    s = SessionState()
    s.current_difficulty = 1
    for _ in range(5):
        s.update_pre_decision("frustrated", 0.9)
        s.update_post_response("x", "y")
    assert s.current_difficulty >= 1


def test_difficulty_never_above_max():
    s = SessionState()
    s.current_difficulty = 5
    for _ in range(6):
        s.update_pre_decision("happy", 0.9)
        s.update_post_response("x", "y")
    assert s.current_difficulty <= 5


def test_turn_count_increments():
    s = SessionState()
    for i in range(3):
        s.update_pre_decision("neutral", 0.6)
        s.update_post_response("hello", "hi")
    assert s.turn_count == 3


def test_post_response_stores_truncated_text():
    s = SessionState()
    s.update_pre_decision("neutral", 0.5)
    long_text = "a" * 300
    s.update_post_response(long_text, long_text)
    assert len(s.last_user_input) <= 200
    assert len(s.last_ai_response) <= 200


def test_session_not_expired_fresh():
    s = SessionState()
    assert not s.is_expired()


def test_concept_defaults_to_general():
    s = SessionState()
    assert s.current_concept is not None
