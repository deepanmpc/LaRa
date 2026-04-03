import sys
import os
import pytest
import time
import threading
from unittest.mock import MagicMock, patch

# Setup paths
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from core.engine import PerceptionEngine
from core.state import perception_state, EngineState

@pytest.fixture
def engine():
    # Use a fresh singleton state for each test if possible
    perception_state.set_stopped()
    e = PerceptionEngine()
    # Mock components to avoid hardware access
    e._camera = MagicMock()
    e._face = MagicMock()
    e._hand = MagicMock()
    e._objects = MagicMock()
    return e

def test_engine_start_stop(engine):
    with patch('threading.Thread'):
        engine.start()
        assert perception_state.engine_state == EngineState.RUNNING
        assert engine._camera.start.called
        
        engine.stop()
        assert perception_state.engine_state == EngineState.STOPPED
        assert engine._camera.stop.called

def test_pipeline_loop_skip_on_no_frame(engine):
    # Mock get_frame to return None once then stop
    engine._camera.get_frame.return_value = None
    
    # We'll run the loop once manually if we can, but it's a while loop.
    # Instead, we can mock perception_state.is_running to return True then False.
    with patch.object(perception_state, 'is_running', side_effect=[True, False]):
        engine._pipeline_loop()
        
    assert perception_state.latest.skipped.camera_drop is True

def test_watchdog_soft_restart(engine):
    # Setup for soft restart (3 stalls)
    engine._last_tick = time.monotonic() - 10.0 # Force stall
    
    with patch.object(perception_state, 'is_running', side_effect=[True, True, True, False]):
        with patch.object(engine, '_reinit_detectors') as mock_reinit:
            with patch.object(engine, '_spawn_pipeline_thread') as mock_spawn:
                # We need to control the sleep in watchdog
                with patch('time.sleep'):
                    engine._watchdog_loop()
                    assert mock_reinit.called
                    assert mock_spawn.called
                    assert perception_state.stall_count >= 3

def test_make_skip(engine):
    # No last stable
    engine._last_stable = None
    out = engine._make_skip(quality=True)
    assert out.skipped.quality is True
    assert out.presence is False
    
    # With last stable
    from core.state import PerceptionOutput
    engine._last_stable = PerceptionOutput(presence=True, engagementScore=0.8)
    out = engine._make_skip(throttle=True)
    assert out.skipped.throttle is True
    assert out.presence is True
    assert out.engagementScore == 0.8
