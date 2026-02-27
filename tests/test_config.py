"""
LaRa Pytest Test Suite — Config Loader
Tests that config loads correctly and validates required sections.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from config_loader import CONFIG


def test_config_loads():
    assert CONFIG is not None


def test_config_llm_model():
    assert hasattr(CONFIG.llm, 'model_name')
    assert isinstance(CONFIG.llm.model_name, str)
    assert len(CONFIG.llm.model_name) > 0


def test_config_audio_values():
    assert CONFIG.audio.sample_rate == 16000
    assert CONFIG.audio.frame_duration_ms in (10, 20, 30)
    assert 0 <= CONFIG.audio.vad_mode <= 3


def test_config_session_difficulty():
    assert CONFIG.session.min_difficulty == 1
    assert CONFIG.session.max_difficulty == 5
    assert CONFIG.session.min_difficulty < CONFIG.session.max_difficulty


def test_config_llm_temperature_safe():
    # Must be deterministic — never above 0.3
    assert CONFIG.llm.temperature <= 0.3


def test_config_reinforcement_threshold():
    assert 0 < CONFIG.reinforcement.improvement_threshold < 1.0


def test_config_vector_memory_similarity():
    assert 0 < CONFIG.vector_memory.min_similarity_score < 1.0


def test_config_app_has_wake_word():
    assert hasattr(CONFIG.app, 'wake_word')
    assert isinstance(CONFIG.app.wake_word, str)
