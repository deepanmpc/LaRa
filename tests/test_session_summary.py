"""
LaRa Pytest Test Suite — Session Summary
Tests the structured output format and key fields.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from session_state import SessionState
from session_summary import generate_session_summary


def test_summary_returns_string():
    s = SessionState()
    result = generate_session_summary(s)
    assert isinstance(result, str)
    assert len(result) > 0


def test_summary_contains_concept():
    s = SessionState()
    s.current_concept = "colors"
    result = generate_session_summary(s)
    assert "colors" in result


def test_summary_contains_difficulty():
    s = SessionState()
    s.current_difficulty = 3
    result = generate_session_summary(s)
    assert "3/5" in result


def test_summary_declining_trend():
    s = SessionState()
    s.update_pre_decision("frustrated", 0.8)
    s.update_post_response("x", "y")
    s.update_pre_decision("frustrated", 0.8)
    s.update_post_response("x", "y")
    result = generate_session_summary(s)
    assert "declining" in result


def test_summary_improving_trend():
    s = SessionState()
    for _ in range(3):
        s.update_pre_decision("happy", 0.9)
        s.update_post_response("x", "y")
    result = generate_session_summary(s)
    assert "improving" in result


def test_summary_none_session_returns_empty():
    result = generate_session_summary(None)
    assert result == ""


def test_summary_has_session_state_header():
    s = SessionState()
    result = generate_session_summary(s)
    assert "[Session State]" in result
