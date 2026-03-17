"""
LaRa Session Summary Layer (Section 5, lara_memory_architecture_full_v2.md)

Generates a structured, non-narrative summary of the current session.
Injected into the LLM prompt above the rolling history buffer to give
the LLM full awareness of session-level progress without storing transcripts.

Summary is STRUCTURED (deterministic format) and NEVER narrative.
Replaces older raw turns when buffer approaches 75% capacity.

Example output:
  [Session State]
  Concept: counting | Difficulty: 2/5
  Stability trend: improving | Frustration events: 1 | Recovery events: 1
  Reinforcement style: calm_validation
  Turn: 7 | Mastery baseline: 2
"""

import logging


def generate_session_summary(session, learning_manager=None, reinforcement_manager=None) -> str:
    """
    Build a structured session summary string for LLM context injection.

    Args:
        session: SessionState instance
        learning_manager: LearningProgressManager instance (optional)
        reinforcement_manager: ReinforcementAdaptationManager instance (optional)

    Returns:
        A compact, deterministic summary string. Empty string if no session.
    """
    if session is None:
        return ""

    # Compute stability trend
    if session.consecutive_stability >= 2:
        trend = "improving"
    elif session.consecutive_frustration >= 2:
        trend = "declining"
    else:
        trend = "stable"

    # Concept
    concept = session.current_concept or "general"
    difficulty = session.current_difficulty
    turn = session.turn_count

    # Mastery baseline from learning manager
    mastery = "unknown"
    if learning_manager:
        try:
            mastery = str(learning_manager.get_mastery_level(concept))
        except Exception:
            mastery = "unknown"

    # Reinforcement style
    r_style = "calm_validation"
    if reinforcement_manager:
        try:
            r_style = reinforcement_manager.current_style
        except Exception:
            r_style = "calm_validation"

    # Build structured one-liner summary (compact, no narrative)
    lines = [
        "[Session State]",
        f"Concept: {concept} | Difficulty: {difficulty}/5 | Turn: {turn}",
        f"Stability trend: {trend} | Frustration streak: {session.consecutive_frustration} | Stability streak: {session.consecutive_stability}",
        f"Reinforcement: {r_style} | Mastery: {mastery}/5",
    ]

    summary = "\n".join(lines)
    logging.debug(f"[SessionSummary] Generated: {trend} | D{difficulty} | T{turn}")
    return summary


def export_session_summary(summary: str, session_id: str) -> None:
    """
    Appends the deterministic summary to a persistent text log for this session.
    
    Args:
        summary: The generated summary string.
        session_id: The ID of the current session.
    """
    if not summary or not session_id:
        return
        
    try:
        from src.core.runtime_paths import get_sessions_dir
        import os
        import time
        
        sessions_dir = get_sessions_dir()
        log_path = os.path.join(sessions_dir, f"session_{session_id}_summary.txt")
        
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- {ts} ---\n")
            f.write(summary + "\n")
    except Exception as e:
        logging.error(f"[SessionSummary] Failed to export to disk: {e}")
