"""
Tests for the FastAPI routes (no camera, engine mocked).
v2.2 compatible: uses PerceptionOutput dataclass for state seeding.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    import app as vision_app
    from core.state import perception_state
    perception_state.set_stopped()
    return TestClient(vision_app.app)


# ── Health & basic routes ────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["service"] == "lara-vision-perception"


def test_status_stopped(client):
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == "STOPPED"
    assert data["fps"] == 0.0
    assert "memory_mb" in data
    assert "stall_count" in data
    assert "yolo_interval" in data


def test_status_new_fields_present(client):
    """v2.2: status must include peak memory and fragmentation fields."""
    r = client.get("/status")
    data = r.json()
    assert "memory_growth_rate_mb_per_sec" in data
    assert "memory_leak_suspected" in data
    assert "current_peak_mb" in data
    assert "peak_fragmentation_suspected" in data


def test_latest_when_stopped_raises_503(client):
    r = client.get("/latest")
    assert r.status_code == 503


def test_stop_when_stopped(client):
    r = client.post("/stop")
    assert r.status_code == 200
    assert r.json()["status"] == "already_stopped"


# ── Mocked engine start ──────────────────────────────────────

def test_start_mocked(client):
    """Verify /start sets engine to RUNNING without opening a real camera."""
    from core.state import perception_state
    import app as vision_app

    with patch.object(vision_app._engine, "start", lambda: perception_state.set_running()):
        r = client.post("/start")
        assert r.status_code == 200
        assert r.json()["state"] == "RUNNING"


def test_start_already_running(client):
    """Calling /start when already running should return already_running."""
    from core.state import perception_state
    import app as vision_app

    with patch.object(vision_app._engine, "start", lambda: perception_state.set_running()):
        client.post("/start")
        r = client.post("/start")
        assert r.json()["status"] == "already_running"


# ── Latest endpoint ──────────────────────────────────────────

def test_latest_when_running_returns_correct_shape(client):
    """Verify /latest returns the v2.2 schema when engine is running."""
    from core.state import perception_state, PerceptionOutput, PerceptionSkipReason, PerceptionConfidence
    import app as vision_app

    perception_state.set_running()

    # Publish a known PerceptionOutput dataclass
    out = PerceptionOutput(
        presence=True,
        faceVerified=False,
        lookingAtScreen=True,
        engagementScore=0.85,
        engagementScoreUI=0.91,
        gesture="OPEN_PALM",
        detectedObjects=("book",),
        skipped=PerceptionSkipReason(),
        confidence=PerceptionConfidence(face=0.9, gesture=0.88, objects=0.7, pose=0.82),
        systemConfidence=0.7,
        timestamp=1234567890.0,
    )
    perception_state.publish(out)

    r = client.get("/latest")
    assert r.status_code == 200
    data = r.json()

    # Core fields
    assert data["presence"] is True
    assert data["gesture"] == "OPEN_PALM"
    assert data["engagementScore"] == 0.85
    assert "attentionState" in data
    assert "distractionFrames" in data
    assert data["attentionState"] == "UNKNOWN"  # default
    assert data["distractionFrames"] == 0

    # v2.2 new fields
    assert data["engagementScoreUI"] == 0.91
    assert data["systemConfidence"] == 0.7
    assert "skipped" in data
    assert data["skipped"]["quality"] is False
    assert data["skipped"]["camera_drop"] is False
    assert "confidence" in data
    assert data["confidence"]["pose"] == 0.82

    # Objects should be a list (tuple serialised by to_dict)
    assert isinstance(data["detectedObjects"], list)
    assert "book" in data["detectedObjects"]


def test_latest_skip_reason_quality(client):
    """When quality gate fires, skipped.quality should be True."""
    from core.state import perception_state, PerceptionOutput, PerceptionSkipReason
    import app as vision_app

    perception_state.set_running()
    out = PerceptionOutput(
        presence=True,
        engagementScore=0.7,
        skipped=PerceptionSkipReason(quality=True),
        timestamp=9999.0,
    )
    perception_state.publish(out)

    r = client.get("/latest")
    assert r.status_code == 200
    data = r.json()
    assert data["skipped"]["quality"] is True
    # Stable data should be preserved (not zeroed)
    assert data["engagementScore"] == 0.7
