"""
LaRa Session State (Phase 1)
In-memory session tracking for conversational continuity.

Tracks:
- Turn count
- Current concept and difficulty
- Consecutive frustration/stability counters
- Last user input and AI response (truncated)
- Current mood and confidence
- Difficulty change cooldown

Design rules (from rules_task_todo.md):
- Stored in RAM only
- Auto-expires after 24 hours
- Never stores emotional narrative
- Never stores raw transcripts long-term
- LLM cannot write to this directly
"""

import time
import uuid
import logging
from dataclasses import dataclass, field


# Maximum characters to store for last input/response (privacy + memory)
MAX_STORED_TEXT = 200

# Session TTL: 24 hours in seconds
SESSION_TTL_SECONDS = 24 * 60 * 60

# Difficulty boundaries
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 5
DEFAULT_DIFFICULTY = 2

# Difficulty lock duration after any change
DIFFICULTY_LOCK_TURNS = 2

# Thresholds for difficulty changes (from adaptive_learning_design.md)
FRUSTRATION_TURNS_FOR_DECREASE = 2   # 2 consecutive frustrated turns → decrease
STABILITY_TURNS_FOR_INCREASE = 3     # 3 consecutive stable turns → increase
MOOD_CONFIDENCE_FOR_DIFFICULTY = 0.6 # Minimum confidence to allow difficulty change


@dataclass
class SessionState:
    """
    In-memory state for the current interaction session.
    
    Provides context for RecoveryStrategy and difficulty gating.
    Auto-expires after 24 hours. Never persists emotional narratives.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: float = field(default_factory=time.time)
    
    # Turn tracking
    turn_count: int = 0
    
    # Task/concept tracking
    current_concept: str = ""
    current_difficulty: int = DEFAULT_DIFFICULTY
    
    # Mood streak counters (for difficulty gating)
    consecutive_frustration: int = 0
    consecutive_stability: int = 0
    
    # Last interaction (truncated for privacy)
    last_user_input: str = ""
    last_ai_response: str = ""
    
    # Current mood snapshot (temporary, not stored long-term)
    mood: str = "neutral"
    mood_confidence: float = 0.0
    
    # Difficulty cooldown (prevents oscillation)
    difficulty_locked_turns: int = 0
    
    def is_expired(self) -> bool:
        """Check if session has exceeded 24h TTL."""
        return (time.time() - self.created_at) > SESSION_TTL_SECONDS
    
    def update_pre_decision(self, mood: str, mood_confidence: float):
        """
        Phase 1 of session update — runs BEFORE DifficultyGate and RecoveryStrategy.
        Updates mood and streak counters so decisions use fresh data.
        
        Do NOT call update_post_response until after LLM response is generated.
        """
        self.mood = mood
        self.mood_confidence = mood_confidence
        
        # Decrement difficulty lock cooldown
        if self.difficulty_locked_turns > 0:
            self.difficulty_locked_turns -= 1
        
        # Update mood streak counters
        self._update_streaks(mood, mood_confidence)
        
        logging.info(
            f"[Session] Pre-decision | "
            f"Mood: {mood} ({mood_confidence:.2f}) | "
            f"Frustration: {self.consecutive_frustration} | "
            f"Stability: {self.consecutive_stability}"
        )
    
    def update_post_response(self, user_input: str, ai_response: str):
        """
        Phase 2 of session update — runs AFTER LLM response is generated.
        Finalizes the turn: increments count, stores truncated text.
        
        Must be called AFTER DifficultyGate and RecoveryStrategy have executed.
        """
        self.turn_count += 1
        self.last_user_input = user_input[:MAX_STORED_TEXT] if user_input else ""
        self.last_ai_response = ai_response[:MAX_STORED_TEXT] if ai_response else ""
        
        logging.info(
            f"[Session] Turn {self.turn_count} complete | "
            f"Difficulty: {self.current_difficulty} | "
            f"Locked: {self.difficulty_locked_turns > 0}"
        )
    
    def _update_streaks(self, mood: str, confidence: float):
        """
        Track consecutive frustration and stability.
        
        Frustrated: mood is 'frustrated' or 'sad' with confidence >= threshold
        Stable: mood is 'neutral' or 'happy' with confidence >= threshold
        
        Any other mood resets both counters.
        """
        if confidence < MOOD_CONFIDENCE_FOR_DIFFICULTY:
            # Low confidence — don't affect streaks
            return
        
        if mood in ("frustrated", "sad"):
            self.consecutive_frustration += 1
            self.consecutive_stability = 0
        elif mood in ("neutral", "happy"):
            self.consecutive_stability += 1
            self.consecutive_frustration = 0
        else:
            # Anxious, quiet, or unknown — reset both (don't escalate uncertainty)
            self.consecutive_frustration = 0
            self.consecutive_stability = 0
    
    def can_change_difficulty(self) -> bool:
        """
        Check if difficulty change is allowed.
        Requires:
        - Difficulty lock expired (cooldown of 2 turns)
        - Mood confidence >= 0.6
        """
        if self.difficulty_locked_turns > 0:
            return False
        if self.mood_confidence < MOOD_CONFIDENCE_FOR_DIFFICULTY:
            return False
        return True
    
    def should_decrease_difficulty(self) -> bool:
        """
        Check if difficulty should decrease.
        Requires 2 consecutive frustrated turns + can_change_difficulty.
        """
        if not self.can_change_difficulty():
            return False
        return self.consecutive_frustration >= FRUSTRATION_TURNS_FOR_DECREASE
    
    def should_increase_difficulty(self) -> bool:
        """
        Check if difficulty should increase.
        Requires 3 consecutive stable turns + can_change_difficulty.
        """
        if not self.can_change_difficulty():
            return False
        return self.consecutive_stability >= STABILITY_TURNS_FOR_INCREASE
    
    def change_difficulty(self, delta: int):
        """
        Apply a difficulty change (+1 or -1).
        Clamps to [MIN_DIFFICULTY, MAX_DIFFICULTY].
        Locks difficulty for DIFFICULTY_LOCK_TURNS after any change.
        Resets streak counters.
        """
        old = self.current_difficulty
        self.current_difficulty = max(
            MIN_DIFFICULTY,
            min(MAX_DIFFICULTY, self.current_difficulty + delta)
        )
        
        if self.current_difficulty != old:
            self.difficulty_locked_turns = DIFFICULTY_LOCK_TURNS
            self.consecutive_frustration = 0
            self.consecutive_stability = 0
            logging.info(
                f"[Session] Difficulty changed: {old} → {self.current_difficulty} "
                f"(locked for {DIFFICULTY_LOCK_TURNS} turns)"
            )
    
    def get_summary(self) -> dict:
        """
        Return a structured summary for logging/dashboard.
        No raw transcripts, no emotional labels.
        """
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "current_difficulty": self.current_difficulty,
            "consecutive_frustration": self.consecutive_frustration,
            "consecutive_stability": self.consecutive_stability,
            "mood": self.mood,
            "mood_confidence": round(self.mood_confidence, 2),
            "difficulty_locked": self.difficulty_locked_turns > 0,
        }
