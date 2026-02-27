"""
LaRa Edge Case Tests — Audio & STT Layer
Covers: 1.1 Complete Silence, 1.3 Background Noise, 1.4 Interrupted Speech
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pytest
from session_state import SessionState
from mood_detector import MoodDetector


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_silence_frames(num_frames=30, frame_size=480):
    """Generate zero-RMS audio frames (pure silence)."""
    return [np.zeros(frame_size, dtype=np.float32) for _ in range(num_frames)]


def _make_noise_frames(num_frames=30, frame_size=480, amplitude=0.004):
    """Generate low-amplitude white noise (below RMS gate = 0.005)."""
    rng = np.random.default_rng(42)
    return [
        (rng.random(frame_size).astype(np.float32) * 2 - 1) * amplitude
        for _ in range(num_frames)
    ]


def _make_loud_noise_frames(num_frames=30, frame_size=480, amplitude=0.3):
    """Generate loud white noise (above RMS gate, but non-speech)."""
    rng = np.random.default_rng(99)
    return [
        (rng.random(frame_size).astype(np.float32) * 2 - 1) * amplitude
        for _ in range(num_frames)
    ]


# ── 1.1 Complete Silence ───────────────────────────────────────────────────────

def test_silence_rms_is_zero():
    """Zero-RMS frames must be detectable as silence."""
    frames = _make_silence_frames()
    rms = np.sqrt(np.mean(np.concatenate(frames) ** 2))
    assert rms < 0.001, f"Silence frames have unexpected RMS: {rms}"


def test_silence_mood_unchanged():
    """
    Feeding silence audio to MoodDetector must not change mood
    from its default neutral.
    """
    md = MoodDetector()
    silence = _make_silence_frames()
    initial_mood, _ = md.get_current_mood()

    # Simulate silence being passed as empty text (what STT returns for silence)
    mood, conf = md.analyze("", silence, 0.0)

    assert mood in ("neutral", "quiet"), f"Silence returned mood='{mood}'"
    assert conf < 0.6, f"Silence returned unexpectedly high confidence: {conf}"


def test_silence_session_difficulty_unchanged():
    """
    Repeated silence inputs must not change session difficulty.
    """
    s = SessionState()
    initial = s.current_difficulty

    for _ in range(5):
        s.update_pre_decision("quiet", 0.2)   # What silence yields
        s.update_post_response("", "")         # Empty transcript

    assert s.current_difficulty == initial
    assert s.consecutive_frustration == 0


def test_silence_does_not_crash():
    """Zero-RMS audio pipline must not raise any exception."""
    md = MoodDetector()
    silence = _make_silence_frames()
    try:
        mood, conf = md.analyze("", silence, 0.0)
    except Exception as e:
        pytest.fail(f"MoodDetector crashed on silence: {e}")


# ── 1.3 Background Noise Only ──────────────────────────────────────────────────

def test_background_noise_below_gate_classified_as_quiet():
    """
    Audio below NOISE_GATE_THRESHOLD (0.005 RMS) must produce
    safe neutral/quiet mood with low confidence.
    This simulates the sub-gate noise path.
    """
    md = MoodDetector()
    noise = _make_noise_frames(amplitude=0.003)   # Well below gate

    # Sub-gate noise typically produces empty STT output
    mood, conf = md.analyze("", noise, 0.0)
    assert mood in ("neutral", "quiet")
    assert conf < 0.6


def test_loud_noise_no_dangerous_mood():
    """
    Even loud non-speech noise must not trigger frustrated/sad/anxious.
    Whisper typically returns empty or [BLANK_AUDIO] for pure noise.
    """
    md = MoodDetector()
    noise = _make_loud_noise_frames()

    # Simulate Whisper returning [BLANK_AUDIO] for non-speech audio
    mood, conf = md.analyze("[BLANK_AUDIO]", noise, 0.1)
    assert mood not in ("frustrated", "sad", "anxious"), (
        f"Background noise produced dangerous mood='{mood}'"
    )


def test_noise_does_not_accumulate_frustration_streak():
    """
    Repeated noise inputs must not build a frustration streak.
    """
    s = SessionState()
    initial_frustration = s.consecutive_frustration

    # Simulate 5 noise/blank turns classified as quiet
    for _ in range(5):
        s.update_pre_decision("quiet", 0.2)
        s.update_post_response("", "")

    assert s.consecutive_frustration == initial_frustration


# ── 1.4 Interrupted Speech ─────────────────────────────────────────────────────

def test_interrupted_speech_no_frustration_spike():
    """
    Fragmented transcription ("I don't li—") must not
    produce high-confidence frustration.
    """
    md = MoodDetector()
    fragments = ["I don't li—", "I can'—", "Wai—", "no I—"]

    for frag in fragments:
        mood, conf = md.analyze(frag, [], len(frag.split()) * 0.3)
        if mood == "frustrated":
            assert conf < 0.6, (
                f"Interrupted speech '{frag}' → frustrated with conf={conf:.2f} — too high"
            )


def test_interrupted_speech_single_turn_no_difficulty_change():
    """
    A single interrupted-speech turn must not trigger difficulty change.
    Gate requires a streak of 2+.
    """
    s = SessionState()
    initial = s.current_difficulty

    s.update_pre_decision("frustrated", 0.65)
    s.update_post_response("I don't li—", "Let's try something else.")

    # Single turn — should_decrease_difficulty needs streak >= 2
    assert not s.should_decrease_difficulty() or s.current_difficulty == initial
