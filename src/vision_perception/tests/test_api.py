"""
Tests for the FastAPI routes (no camera, engine mocked).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import app after path is set
    import app as vision_app
    from core.state import perception_state, EngineState
    # Reset state before each test
    perception_state.set_stopped()
    return TestClient(vision_app.app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_status_stopped(client):
    r = client.get("/status")
    assert r.status_code == 200
    data = r.json()
    assert data["state"] == "STOPPED"
    assert data["fps"] == 0.0


def test_latest_when_stopped_raises_503(client):
    r = client.get("/latest")
    assert r.status_code == 503


def test_stop_when_stopped(client):
    r = client.post("/stop")
    assert r.status_code == 200
    assert r.json()["status"] == "already_stopped"


def test_start_mocked(client):
    """Verify /start sets engine to RUNNING without opening a real camera."""
    from core.state import perception_state, EngineState
    import app as vision_app

    with patch.object(vision_app._engine, "start", lambda: perception_state.set_running()):
        r = client.post("/start")
        assert r.status_code == 200
        assert r.json()["state"] == "RUNNING"


def test_latest_when_running(client):
    """Verify /latest returns the cached frame when engine is running."""
    from core.state import perception_state
    import app as vision_app

    perception_state.set_running()
    perception_state.latest = {
        "presence": True,
        "faceVerified": False,
        "lookingAtScreen": True,
        "engagementScore": 0.85,
        "gesture": "OPEN_PALM",
        "detectedObjects": ["cup"],
        "timestamp": 1234567890.0,
    }

    r = client.get("/latest")
    assert r.status_code == 200
    data = r.json()
    assert data["presence"] is True
    assert data["gesture"] == "OPEN_PALM"
    assert data["engagementScore"] == 0.85
