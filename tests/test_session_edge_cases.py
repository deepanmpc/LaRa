"""
LaRa Edge Case Tests — Session State Layer
Covers: 3.3 Session Expiry Boundary, off-by-one expiry
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import pytest
from unittest.mock import patch
from session_state import SessionState, SESSION_TTL_SECONDS


# ── 3.3 Session Expiry Boundary ────────────────────────────────────────────────

def test_fresh_session_not_expired():
    """Newly created session must not be expired."""
    s = SessionState()
    assert not s.is_expired()


def test_session_expired_at_24h():
    """
    Session created exactly 24h ago must be expired.
    Uses mock time to avoid a real 24-hour wait.
    """
    s = SessionState()
    # Move created_at back by exactly TTL seconds
    s.created_at = time.time() - SESSION_TTL_SECONDS
    assert s.is_expired(), "Session should be expired at exactly TTL boundary"


def test_session_not_expired_before_24h():
    """
    Session created 1 second short of TTL must NOT be expired.
    Verifies off-by-one: (TTL - 1) should still be valid.
    """
    s = SessionState()
    s.created_at = time.time() - (SESSION_TTL_SECONDS - 1)
    assert not s.is_expired(), (
        f"Session flagged expired at TTL-1s — off-by-one error"
    )


def test_session_expired_past_24h():
    """
    Session created longer than 24h ago must be expired.
    """
    s = SessionState()
    s.created_at = time.time() - (SESSION_TTL_SECONDS + 3600)  # +1h past TTL
    assert s.is_expired()


def test_newly_created_session_ttl_is_correct():
    """
    Verify SESSION_TTL_SECONDS is exactly 86400 (24 hours).
    Guards against accidental modifications to the constant.
    """
    assert SESSION_TTL_SECONDS == 86400, (
        f"SESSION_TTL_SECONDS is {SESSION_TTL_SECONDS}, expected 86400 (24h)"
    )


def test_session_state_consistent_after_expiry():
    """
    An expired session must still return consistent state (no crash).
    The caller may choose to reset it, but the object should be stable.
    """
    s = SessionState()
    s.created_at = time.time() - (SESSION_TTL_SECONDS + 1)

    # Should not raise
    assert s.is_expired()
    assert s.current_difficulty >= 1
    assert s.turn_count >= 0
    assert s.consecutive_frustration >= 0


def test_session_expiry_not_affected_by_updates():
    """
    Making updates to session state must not reset the creation timestamp.
    Expiry is based on session creation, not last activity.
    """
    s = SessionState()
    original_created_at = s.created_at

    for _ in range(10):
        s.update_pre_decision("happy", 0.8)
        s.update_post_response("x", "y")

    assert s.created_at == original_created_at, (
        "Updates incorrectly changed session created_at — expiry will be wrong"
    )
