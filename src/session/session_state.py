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
import json
import os
import threading
from dataclasses import dataclass, field, fields


# Configuration access
try:
    from src.core.config_loader import CONFIG
    _SES_CFG = CONFIG.session
    MAX_STORED_TEXT = _SES_CFG.max_stored_text_chars
    SESSION_TTL_SECONDS = _SES_CFG.ttl_hours * 3600
    MIN_DIFFICULTY = _SES_CFG.min_difficulty
    MAX_DIFFICULTY = _SES_CFG.max_difficulty
    DEFAULT_DIFFICULTY = 2 # Usually fixed
    DIFFICULTY_LOCK_TURNS = _SES_CFG.difficulty_lock_turns
    FRUSTRATION_TURNS_FOR_DECREASE = _SES_CFG.frustration_streak_threshold
    STABILITY_TURNS_FOR_INCREASE = _SES_CFG.stability_streak_threshold
    MOOD_CONFIDENCE_FOR_DIFFICULTY = _SES_CFG.mood_confidence_threshold
except Exception:
    MAX_STORED_TEXT = 200
    SESSION_TTL_SECONDS = 24 * 3600
    MIN_DIFFICULTY = 1
    MAX_DIFFICULTY = 5
    DEFAULT_DIFFICULTY = 2
    DIFFICULTY_LOCK_TURNS = 2
    FRUSTRATION_TURNS_FOR_DECREASE = 2
    STABILITY_TURNS_FOR_INCREASE = 3
    MOOD_CONFIDENCE_FOR_DIFFICULTY = 0.6


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
    
    # Phase 4 extensions
    difficulty_history: list = field(default_factory=list)
    last_3_input_lengths: list = field(default_factory=list)

    # Live vision state
    vision_presence: bool = False
    vision_attention: str = "UNKNOWN"
    vision_engagement: float = 0.0
    vision_gesture: str = "NONE"
    vision_timestamp: float = 0.0
    vision_lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)
    
    def reset(self):
        """Reset session state to clean defaults while keeping object instance."""
        self.session_id = str(uuid.uuid4())[:8]
        self.created_at = time.time()
        self.turn_count = 0
        self.current_concept = ""
        self.current_difficulty = DEFAULT_DIFFICULTY
        self.consecutive_frustration = 0
        self.consecutive_stability = 0
        self.last_user_input = ""
        self.last_ai_response = ""
        self.mood = "neutral"
        self.mood_confidence = 0.0
        self.difficulty_locked_turns = 0
        self.difficulty_history = []
        self.last_3_input_lengths = []
        with self.vision_lock:
            self.vision_presence = False
            self.vision_attention = "UNKNOWN"
            self.vision_engagement = 0.0
            self.vision_gesture = "NONE"
            self.vision_timestamp = 0.0
        logging.info(f"[Session] Reset complete. New ID: {self.session_id}")

    def is_expired(self) -> bool:
        """Check if session has exceeded TTL."""
        if (time.time() - self.created_at) > SESSION_TTL_SECONDS:
            # Enforce expiration limit by resetting
            self.reset()
            return True
        return False
    
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
        
        # Track difficulty trajectory (last 3)
        self.difficulty_history.append(self.current_difficulty)
        self.difficulty_history = self.difficulty_history[-3:]
        
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
        
        # Track engagement via input length
        input_len = len(user_input) if user_input else 0
        self.last_3_input_lengths.append(input_len)
        self.last_3_input_lengths = self.last_3_input_lengths[-3:]
        
        logging.info(
            f"[Session] Turn {self.turn_count} complete | "
            f"Difficulty: {self.current_difficulty} | "
            f"Locked: {self.difficulty_locked_turns > 0}"
        )
        self.save_to_disk()
    
    def save_to_disk(self):
        """
        Debounced disk persistence — coalesces rapid writes to at most once per 2s.
        Spawns a timer on first call; subsequent calls within the window just set
        the pending flag. The timer fires and writes once, then resets.
        """
        self._save_pending = True
        if not hasattr(self, '_save_timer') or self._save_timer is None or not self._save_timer.is_alive():
            self._save_timer = threading.Timer(2.0, self._debounced_save)
            self._save_timer.daemon = True
            self._save_timer.start()

    def _debounced_save(self):
        """Internal: called by the debounce timer to flush pending state."""
        if not getattr(self, '_save_pending', False):
            return
        self._save_pending = False
        try:
            from src.core.runtime_paths import get_sessions_dir
            sessions_dir = get_sessions_dir()
            state_file = os.path.join(sessions_dir, f"session_{self.session_id}_state.json")
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self._serialize(), f, indent=2)
        except Exception as e:
            logging.error(f"[Session] Failed to persist state to disk: {e}")

    def flush_to_disk(self):
        """
        Immediate disk write — call on session end to ensure final state is persisted.
        Cancels any pending debounce timer.
        """
        if hasattr(self, '_save_timer') and self._save_timer is not None:
            self._save_timer.cancel()
            self._save_timer = None
        self._save_pending = False
        try:
            from src.core.runtime_paths import get_sessions_dir
            sessions_dir = get_sessions_dir()
            state_file = os.path.join(sessions_dir, f"session_{self.session_id}_state.json")
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(self._serialize(), f, indent=2)
            logging.info(f"[Session] Final state flushed to {state_file}")
        except Exception as e:
            logging.error(f"[Session] Failed to flush state to disk: {e}")

    def _serialize(self) -> dict:
        data = {}
        with self.vision_lock:
            for item in fields(self):
                if item.name == "vision_lock":
                    continue
                data[item.name] = getattr(self, item.name)
        return data

    def get_vision_snapshot(self) -> dict:
        with self.vision_lock:
            return {
                "presence": self.vision_presence,
                "attention": self.vision_attention,
                "engagement": self.vision_engagement,
                "gesture": self.vision_gesture,
                "timestamp": self.vision_timestamp,
            }
            
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
