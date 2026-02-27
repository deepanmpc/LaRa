"""
LaRa Edge Case Tests — Mood Detection Layer
Covers: 2.1 Mixed Sentiment, 2.2 Extended Oscillation (10 alternating turns)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from session_state import SessionState
from mood_detector import MoodDetector


# ── 2.1 Mixed Sentiment ────────────────────────────────────────────────────────

MIXED_SENTENCES = [
    "I like this but it's kind of hard.",
    "It's okay but I'm not sure about it.",
    "I love the colors but the shapes are confusing.",
    "This is fun but I don't understand the last part.",
    "I liked it before but now it's harder.",
]


def test_mixed_sentiment_not_fully_frustrated():
    """
    Mixed positive-negative sentences must not return frustrated
    with high confidence. Should produce neutral or moderate mood.
    """
    md = MoodDetector()
    for sentence in MIXED_SENTENCES:
        mood, conf = md.analyze(sentence, [], 1.5)
        if mood == "frustrated":
            assert conf < 0.7, (
                f"Mixed sentence '{sentence}' → frustrated conf={conf:.2f} — too high for mixed input"
            )


def test_mixed_sentiment_does_not_drop_difficulty():
    """
    A single mixed-sentiment turn must not trigger a difficulty decrease.
    """
    s = SessionState()
    initial = s.current_difficulty

    # Classify as frustrated (worst case) but single turn
    s.update_pre_decision("frustrated", 0.55)
    s.update_post_response("I like this but it's hard", "Great job! Let's slow down a bit.")

    assert not s.should_decrease_difficulty(), (
        "Single mixed-sentiment turn triggered difficulty decrease"
    )
    assert s.current_difficulty == initial


def test_mixed_sentiment_smoothing_over_3_turns():
    """
    3-turn smoothing window: one mixed turn surrounded by stable turns
    must not classify overall as frustrated.
    """
    md = MoodDetector()

    md.analyze("I like learning with you!", [], 1.5)         # stable
    md.analyze("I like this but it's hard", [], 1.5)         # mixed
    mood, conf = md.analyze("Okay, let's keep going!", [], 1.5)  # stable

    # After smoothing, should NOT be stuck on frustrated
    assert mood != "frustrated" or conf < 0.6, (
        f"Smoothing failed: 1 mixed turn in 3 stable turns → mood={mood} conf={conf:.2f}"
    )


# ── 2.2 Extended Oscillation (10 alternating turns) ───────────────────────────

def test_10_alternating_turns_no_difficulty_thrash():
    """
    10 alternating happy/frustrated turns at high confidence must
    NOT cause difficulty oscillation.
    Streak threshold requires 2 CONSECUTIVE same-mood turns.
    Alternating pattern never meets the streak requirement.
    """
    s = SessionState()
    s.current_difficulty = 3
    changes = 0

    pattern = ["happy", "frustrated"] * 5  # 10 alternating turns
    prev_diff = s.current_difficulty

    for i, mood in enumerate(pattern):
        conf = 0.85
        s.update_pre_decision(mood, conf)
        s.update_post_response(f"turn {i}", f"response {i}")

        if s.current_difficulty != prev_diff:
            changes += 1
            prev_diff = s.current_difficulty

    assert changes == 0, (
        f"Difficulty changed {changes} times during 10 alternating moods — thrashing detected"
    )


def test_oscillation_consecutive_streak_still_works():
    """
    After alternating, a genuine 2-turn frustration streak should still
    open the gate — verify the mechanism is not stuck.
    """
    s = SessionState()
    s.current_difficulty = 3

    # Alternate first to "confuse" system
    for mood in ["happy", "frustrated", "happy"]:
        s.update_pre_decision(mood, 0.8)
        s.update_post_response("x", "y")

    # Now genuine streak
    s.update_pre_decision("frustrated", 0.9)
    s.update_post_response("x", "y")
    s.update_pre_decision("frustrated", 0.9)
    s.update_post_response("x", "y")

    assert s.should_decrease_difficulty(), (
        "Genuine 2-turn frustration streak after oscillation did not open gate"
    )


def test_20_neutral_turns_no_difficulty_change():
    """
    20 consecutive neutral turns at low-medium confidence
    must NEVER increase difficulty (needs stability streak, not neutrals).
    """
    s = SessionState()
    initial = s.current_difficulty

    for _ in range(20):
        s.update_pre_decision("neutral", 0.45)
        s.update_post_response("hmm", "okay")

    assert s.current_difficulty == initial, (
        f"20 neutral turns changed difficulty from {initial} to {s.current_difficulty}"
    )
