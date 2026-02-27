"""
LaRa Regulation State Layer
Computes structured regulation signals from SessionState.

RecoveryStrategy operates on RegulationState, NOT raw mood directly.
This prevents raw mood classifications from directly altering behavior.

RegulationState provides:
- frustration_persistence: how sustained the frustration is (0.0-1.0)
- stability_persistence: how sustained the stability is (0.0-1.0)
- emotional_trend_score: net trend (-1.0 = declining, +1.0 = improving)
"""

import logging
from dataclasses import dataclass


@dataclass
class RegulationState:
    """
    Computed regulation signals derived from SessionState.
    RecoveryStrategy reads this — never raw mood.
    """
    # Persistence scores (0.0 = no streak, 1.0 = max streak)
    frustration_persistence: float = 0.0
    stability_persistence: float = 0.0
    
    # Emotional trend: negative = worsening, positive = improving
    emotional_trend_score: float = 0.0
    
    # Pass-through for strategy selection (but strategy reads persistence, not this)
    current_mood: str = "neutral"
    current_confidence: float = 0.0
    
    # Session context
    turn_count: int = 0
    current_difficulty: int = 2
    difficulty_locked: bool = False


# Maximum streak values for normalization
MAX_FRUSTRATION_STREAK = 5
MAX_STABILITY_STREAK = 5


def compute_regulation_state(session) -> RegulationState:
    """
    Compute RegulationState from SessionState.
    
    This is the ONLY bridge between raw session data and the
    RecoveryStrategy/ReinforcementAdaptation layers.
    
    Args:
        session: SessionState object
        
    Returns:
        RegulationState with normalized persistence scores and trend
    """
    if session is None:
        return RegulationState()
    
    # Normalize streaks to 0.0-1.0 range
    frustration_persistence = min(
        session.consecutive_frustration / MAX_FRUSTRATION_STREAK, 1.0
    )
    stability_persistence = min(
        session.consecutive_stability / MAX_STABILITY_STREAK, 1.0
    )
    
    # Emotional trend: stability pushes positive, frustration pushes negative
    # Range: -1.0 (pure frustration) to +1.0 (pure stability)
    total = session.consecutive_frustration + session.consecutive_stability
    if total > 0:
        trend = (session.consecutive_stability - session.consecutive_frustration) / total
    else:
        trend = 0.0
    
    reg = RegulationState(
        frustration_persistence=frustration_persistence,
        stability_persistence=stability_persistence,
        emotional_trend_score=trend,
        current_mood=session.mood,
        current_confidence=session.mood_confidence,
        turn_count=session.turn_count,
        current_difficulty=session.current_difficulty,
        difficulty_locked=session.difficulty_locked_turns > 0,
    )
    
    logging.debug(
        f"[RegulationState] frustration={frustration_persistence:.2f} "
        f"stability={stability_persistence:.2f} trend={trend:.2f}"
    )
    
    return reg
