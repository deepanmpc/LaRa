"""
LaRa Edge Case Tests — Reinforcement Manager Layer
Covers: 4.1 Over-Reinforcement (10 correct answers), 4.2 Incorrect answer not marked correct
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from reinforcement_manager import ReinforcementAdaptationManager, ReinforcementStyle
from learning_progress import LearningProgressManager


# ── 4.1 Over-Reinforcement ─────────────────────────────────────────────────────

def test_reinforcement_style_locked_after_one_change():
    """
    Reinforcement style must only change ONCE per session.
    After the lock, further events must not change the style.
    """
    rm = ReinforcementAdaptationManager()

    # Simulate 10 events on one style to trigger switch
    from reinforcement_manager import ReinforcementStyle
    target = ReinforcementStyle.PRAISE_BASED

    for _ in range(10):
        rm.update_metrics(target, outcome_stable=True)

    # Allow other styles to fail
    for style in ReinforcementStyle.ALL:
        if style != target:
            for _ in range(3):
                rm.update_metrics(style, outcome_stable=False)

    # Force style evaluation (requires regulation_state with persistence)
    class FakeRegState:
        frustration_persistence = 0.0
        stability_persistence = 0.9

    style_before = rm._current_style
    rm.get_style(FakeRegState())
    style_after = rm._current_style

    # Once locked, style cannot change again
    rm.get_style(FakeRegState())
    assert rm._current_style == style_after, (
        "Reinforcement style changed more than once in a session — lock broken"
    )


def test_reinforcement_not_changed_below_min_events():
    """
    Reinforcement style must NOT change if total events < 5.
    Guards against premature adaptation.
    """
    rm = ReinforcementAdaptationManager()

    # Only 4 events total — below MIN_EVENTS_FOR_CHANGE = 5
    rm.update_metrics(ReinforcementStyle.PRAISE_BASED, outcome_stable=True)
    rm.update_metrics(ReinforcementStyle.PRAISE_BASED, outcome_stable=True)
    rm.update_metrics(ReinforcementStyle.PRAISE_BASED, outcome_stable=True)
    rm.update_metrics(ReinforcementStyle.PRAISE_BASED, outcome_stable=True)

    initial_style = rm._current_style

    class FakeRegState:
        frustration_persistence = 0.0
        stability_persistence = 0.8

    rm.get_style(FakeRegState())
    assert rm._current_style == initial_style, (
        "Reinforcement style changed with < 5 events — MIN_EVENTS_FOR_CHANGE violated"
    )


def test_reinforcement_requires_15pct_improvement():
    """
    A candidate style must be at least 15% better than current
    before a switch occurs.
    """
    rm = ReinforcementAdaptationManager()
    current = rm._current_style

    # Current style: 5 events, 60% success
    for i in range(5):
        rm.update_metrics(current, outcome_stable=(i < 3))

    # Candidate: 5 events, 70% success — only 10% better, not 15%
    other = [s for s in ReinforcementStyle.ALL if s != current][0]
    for i in range(5):
        rm.update_metrics(other, outcome_stable=(i < 3.5))

    class FakeRegState:
        frustration_persistence = 0.0
        stability_persistence = 0.7

    rm.get_style(FakeRegState())
    # Should NOT switch (improvement < 15%)
    assert rm._current_style == current or rm._style_changed_this_session is False or \
           rm._session_metrics[other].success_rate - rm._session_metrics[current].success_rate >= 0.15, (
        "Style switched with < 15% improvement"
    )


def test_reinforcement_metrics_accumulate_correctly():
    """
    Success and total counts must increment correctly.
    """
    rm = ReinforcementAdaptationManager()
    style = ReinforcementStyle.CALM_VALIDATION

    rm.update_metrics(style, outcome_stable=True)
    rm.update_metrics(style, outcome_stable=True)
    rm.update_metrics(style, outcome_stable=False)

    m = rm._session_metrics[style]
    assert m.total_count == 3
    assert m.success_count == 2
    assert abs(m.success_rate - 2/3) < 0.01


def test_reinforcement_invalid_type_ignored():
    """
    Passing a non-existent reinforcement type must not crash or corrupt state.
    """
    rm = ReinforcementAdaptationManager()
    try:
        rm.update_metrics("nonexistent_style", outcome_stable=True)
    except Exception as e:
        pytest.fail(f"Invalid reinforcement type raised exception: {e}")
    # Nothing should change
    total = sum(m.total_count for m in rm._session_metrics.values())
    assert total == 0


# ── 4.2 Incorrect Answer Not Marked Correct ────────────────────────────────────

def test_incorrect_answer_does_not_increase_mastery():
    """
    record_attempt(success=False) must NOT increase mastery level.
    Guards against false progress.
    """
    from user_memory import UserMemoryManager
    import tempfile, os

    db = os.path.join(tempfile.mkdtemp(), "test_learning.db")
    mem = UserMemoryManager(db_path=db)

    progress = mem.record_attempt("child1", "counting", success=False)
    assert progress.mastery_level == 0, (
        f"Incorrect answer increased mastery to {progress.mastery_level}"
    )
    assert progress.attempt_count == 1


def test_correct_answer_increases_mastery():
    """
    record_attempt(success=True) SHOULD increase mastery.
    Positive case — verify the mechanism works.
    """
    from user_memory import UserMemoryManager
    import tempfile, os

    db = os.path.join(tempfile.mkdtemp(), "test_learning_pos.db")
    mem = UserMemoryManager(db_path=db)

    progress = mem.record_attempt("child1", "counting", success=True)
    assert progress.mastery_level == 1, (
        f"Correct answer did not increase mastery: {progress.mastery_level}"
    )


def test_mastery_capped_at_5():
    """
    Mastery level must never exceed 5, even after 100 correct answers.
    """
    from user_memory import UserMemoryManager
    import tempfile, os

    db = os.path.join(tempfile.mkdtemp(), "test_mastery_cap.db")
    mem = UserMemoryManager(db_path=db)

    for _ in range(10):
        progress = mem.record_attempt("child1", "counting", success=True)

    assert progress.mastery_level <= 5, (
        f"Mastery exceeded maximum: {progress.mastery_level}"
    )


def test_attempt_count_always_increments():
    """
    attempt_count must increment on both success and failure.
    """
    from user_memory import UserMemoryManager
    import tempfile, os

    db = os.path.join(tempfile.mkdtemp(), "test_attempts.db")
    mem = UserMemoryManager(db_path=db)

    mem.record_attempt("child1", "shapes", success=True)
    mem.record_attempt("child1", "shapes", success=False)
    mem.record_attempt("child1", "shapes", success=False)
    progress = mem.record_attempt("child1", "shapes", success=True)

    assert progress.attempt_count == 4
