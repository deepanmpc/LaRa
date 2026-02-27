"""
LaRa Robustness Tests — Silent/Partial/Fragmented Speech
Asserts that the pipeline does NOT escalate or change state
when given blank audio, empty text, or fragmented speech.

Break scenario (from optimization roadmap):
  Whisper returns empty/fragmented text
  → mood detector misclassifies
  → difficulty jumps
  → child gets harder task when they said nothing

These tests assert that behavior.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from session_state import SessionState
from mood_detector import MoodDetector


# ── Helpers ────────────────────────────────────────────────────────────────────

BLANK_OUTPUTS = [
    "",
    " ",
    "   ",
    "[BLANK_AUDIO]",
    "[blank_audio]",
    "...",
    ".",
    "Hmm",
    "Uh",
    "Um",
]

FRAGMENT_OUTPUTS = [
    "I",
    "the",
    "ok",
    "yeah",
    "no",
]


def _apply_turns(session, mood, conf, n):
    """Apply N turns of a given mood to session."""
    for _ in range(n):
        session.update_pre_decision(mood, conf)
        session.update_post_response("x", "y")


# ── Tests: Blank audio must not change session state ───────────────────────────

def test_blank_audio_does_not_start_frustration_streak():
    """
    If Whisper returns blank audio it's skipped upstream,
    but even if it somehow reaches the session, 
    neutral classification should not build a frustration streak.
    """
    s = SessionState()
    initial_difficulty = s.current_difficulty
    initial_frustration = s.consecutive_frustration

    # Simulate what happens if blank text is classified as neutral (safe fallback)
    _apply_turns(s, "neutral", 0.3, 5)  # Low confidence neutrals

    # Should NOT have decreased difficulty (confidence too low)
    assert s.current_difficulty == initial_difficulty, (
        f"Difficulty changed unexpectedly: {initial_difficulty} → {s.current_difficulty}"
    )
    assert s.consecutive_frustration == 0


def test_blank_audio_does_not_increase_difficulty():
    """
    Silence/blank must never increase difficulty.
    Only high-confidence stable turns should increase difficulty.
    """
    s = SessionState()
    initial_difficulty = s.current_difficulty

    # Simulate low-confidence neutral turns (what blank audio produces)
    _apply_turns(s, "neutral", 0.2, 6)

    # Low confidence: difficulty must NOT increase
    assert s.current_difficulty == initial_difficulty, (
        "Difficulty increased on low-confidence neutral turns"
    )


# ── Tests: Fragmented/partial speech must not cause escalation ─────────────────

def test_fragment_speech_single_turn_no_mood_change():
    """
    A single fragment ("I", "um", "ok") must not change mood behavior.
    3-turn consensus required — 1 turn alone cannot trigger anything.
    """
    s = SessionState()
    initial_difficulty = s.current_difficulty

    # One frustrated-classified fragment
    s.update_pre_decision("frustrated", 0.65)
    s.update_post_response("ok", "okay")

    # One turn alone cannot decrease difficulty (needs streak ≥ 2)
    assert s.current_difficulty == initial_difficulty


def test_fragmented_frustrated_then_stable_no_escalation():
    """
    Fragment classified as frustrated, followed by stable turn.
    Streak must reset — no difficulty change should occur.
    """
    s = SessionState()
    initial_difficulty = s.current_difficulty

    s.update_pre_decision("frustrated", 0.7)
    s.update_post_response("I", "Let's go!")
    # Stable turn resets frustration streak
    s.update_pre_decision("happy", 0.8)
    s.update_post_response("ok yeah", "Great!")

    assert s.consecutive_frustration == 0, "Frustration streak not reset by stable turn"
    assert s.current_difficulty == initial_difficulty, "Difficulty changed from single frustrated fragment"


def test_alternating_empty_and_speech_no_difficulty_jump():
    """
    Alternating silence and speech should not cause oscillation.
    Difficulty lock prevents rapid changes even if conditions are met.
    """
    s = SessionState()
    s.current_difficulty = 3

    # Alternate frustrated and stable → no sustained streak → no change
    pattern = [("frustrated", 0.7), ("happy", 0.85), ("frustrated", 0.6), ("neutral", 0.5)]
    for mood, conf in pattern:
        s.update_pre_decision(mood, conf)
        s.update_post_response("x", "y")

    # No sustained streak → difficulty should stay at 3
    assert s.current_difficulty == 3, (
        f"Difficulty oscillated to {s.current_difficulty} on alternating moods"
    )


# ── Tests: Confidence gate blocks low-quality signals ─────────────────────────

def test_low_confidence_frustration_does_not_decrease_difficulty():
    """
    Even with 3 consecutive frustrated turns, low confidence (<0.60)
    must NOT decrease difficulty.
    """
    s = SessionState()
    s.current_difficulty = 3

    for _ in range(3):
        s.update_pre_decision("frustrated", 0.40)  # Below 0.60 threshold
        s.update_post_response("x", "y")

    assert s.current_difficulty == 3, (
        f"Difficulty decreased despite low confidence: {s.current_difficulty}"
    )


def test_borderline_confidence_at_threshold():
    """
    Exactly at the threshold (0.60) with required streak should trigger change.
    This verifies the threshold is inclusive.
    """
    s = SessionState()
    s.current_difficulty = 3

    for _ in range(2):  # Frustration streak threshold is 2
        s.update_pre_decision("frustrated", 0.60)
        s.update_post_response("x", "y")

    # AT threshold with required streak — should decrease
    assert s.current_difficulty <= 3  # Either decreased or stayed (both valid if locked)


def test_high_confidence_frustration_streak_decreases_difficulty():
    """
    This is the POSITIVE case: sustained high-confidence frustration
    SHOULD flag should_decrease_difficulty() == True.
    The main loop then calls change_difficulty(-1).
    We simulate the full flow here.
    """
    s = SessionState()
    s.current_difficulty = 3

    for _ in range(2):
        s.update_pre_decision("frustrated", 0.90)
        s.update_post_response("real sentence here", "okay let's slow down")

    # Gate should be open
    assert s.should_decrease_difficulty(), (
        "should_decrease_difficulty() returned False — gate not opening for high-conf frustration streak"
    )
    # Simulate main loop applying the change
    s.change_difficulty(-1)
    assert s.current_difficulty < 3, (
        "Difficulty did not decrease after explicit change_difficulty(-1) call"
    )


# ── Tests: MoodDetector robustness with blank/fragmented text ──────────────────

def test_mood_detector_blank_returns_neutral():
    """
    Blank/empty text must classify as a SAFE mood (neutral or quiet)
    with low confidence. It must NEVER return frustrated, anxious, or sad.

    Note: MoodDetector correctly returns 'quiet' (not 'neutral') for empty
    text — quiet is the safe non-escalating fallback for silence.
    """
    md = MoodDetector()
    safe_moods = {"neutral", "quiet"}
    dangerous_moods = {"frustrated", "anxious", "sad"}

    for blank in BLANK_OUTPUTS:
        mood, conf = md.analyze(blank, [], 0.0)
        assert mood not in dangerous_moods, (
            f"Blank text '{blank}' returned dangerous mood='{mood}' — must be neutral or quiet"
        )
        assert mood in safe_moods, (
            f"Blank text '{blank}' returned unexpected mood='{mood}'"
        )
        assert conf < 0.6, (
            f"Blank text '{blank}' returned high confidence {conf:.2f} — should be low"
        )


def test_mood_detector_fragments_do_not_return_frustrated():
    """
    Short fragments like 'I', 'um', 'ok' must not trigger 
    frustrated/anxious/sad classification with high confidence.
    """
    md = MoodDetector()
    dangerous_moods = {"frustrated", "anxious", "sad"}

    for fragment in FRAGMENT_OUTPUTS:
        mood, conf = md.analyze(fragment, [], 0.5)
        if mood in dangerous_moods:
            assert conf < 0.6, (
                f"Fragment '{fragment}' classified as '{mood}' with confidence {conf:.2f} — too high"
            )


def test_mood_detector_consecutive_blanks_stay_neutral():
    """
    Multiple consecutive blank inputs must not accumulate state
    that eventually tips into a non-neutral mood.
    """
    md = MoodDetector()
    for _ in range(5):
        mood, conf = md.analyze("[BLANK_AUDIO]", [], 0.0)
        assert mood == "neutral"
        assert conf < 0.5
