import sys
import os
import pytest
import time
from unittest.mock import MagicMock

# Setup paths
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from core.state import PerceptionState, EngineState, PerceptionOutput, PerceptionSkipReason

def test_initial_state():
    state = PerceptionState()
    assert state.engine_state == EngineState.STOPPED
    assert state.error_message == ""
    assert state.stall_count == 0
    assert state.fps == 0.0
    assert state.latest.timestamp == 0.0

def test_setters():
    state = PerceptionState()
    state.set_running()
    assert state.engine_state == EngineState.RUNNING
    assert state.stall_count == 0
    
    state.set_error("test error")
    assert state.engine_state == EngineState.ERROR
    assert state.error_message == "test error"
    
    state.set_stopped()
    assert state.engine_state == EngineState.STOPPED

def test_stall_counting():
    state = PerceptionState()
    assert state.stall_count == 0
    state.increment_stall()
    assert state.stall_count == 1
    state.increment_stall()
    assert state.stall_count == 2
    state.set_running()
    assert state.stall_count == 0

def test_fps_calculation():
    state = PerceptionState()
    # Mock window start to 1 second ago
    state._fps_window_start = time.time() - 1.05
    for _ in range(30):
        state.tick()
    # tick() updates fps when elapsed >= 1.0
    assert 25 <= state.fps <= 35

def test_memory_sampling_and_slope():
    state = PerceptionState()
    # Sample 1
    state._proc.memory_info = MagicMock(return_value=MagicMock(rss=100 * 1024 * 1024))
    state.sample_memory()
    assert state.memory_mb == 100.0
    
    # Sample 2 (10 seconds later, 110MB)
    state._proc.memory_info = MagicMock(return_value=MagicMock(rss=110 * 1024 * 1024))
    with MagicMock() as mock_time:
        mock_time.return_value = time.time() + 10.0
        with MagicMock(side_effect=[time.time(), time.time() + 10.0]) as mock_t:
            # We need to manually manipulate the internal samples for testing slope reliably
            state._memory_samples = [(time.time(), 100.0), (time.time() + 10.0, 110.0)]
            state._update_slope()
            # Slope = (110 - 100) / 10 = 1.0 MB/s
            assert state.memory_growth_rate_mb_per_sec() == 1.0

def test_peak_leak_detection():
    state = PerceptionState()
    # 3 increasing peaks
    state._session_peaks = [100.0, 120.0, 150.0]
    assert state.peak_leak_suspected() is True
    
    # Not strictly increasing
    state._session_peaks = [100.0, 150.0, 120.0]
    assert state.peak_leak_suspected() is False

def test_publish_latest():
    state = PerceptionState()
    out = PerceptionOutput(presence=True, engagementScore=0.9, timestamp=100.0)
    state.publish(out)
    assert state.latest.presence is True
    assert state.latest.engagementScore == 0.9
    assert state.latest.timestamp == 100.0
