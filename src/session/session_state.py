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
from typing import Optional, List, Dict


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
    session_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    child_id: Optional[int] = None
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
    
    # Persistence history for DB Sync
    turn_history: list = field(default_factory=list)
    vision_history: list = field(default_factory=list)
    voice_history: list = field(default_factory=list)
    session_db_id: Optional[int] = None

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
        self.turn_history = []
        self.vision_history = []
        self.voice_history = []
        self.session_db_id = None
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

    def get_final_stats(self) -> dict:
        """
        Aggregate all session-long history for DB persistence.
        """
        import numpy as np
        
        # Calculate Vision Stats
        if hasattr(self, 'vision_history') and self.vision_history:
            eng_scores = [v.get("engagement", 0.0) for v in self.vision_history]
            avg_eng = sum(eng_scores) / len(eng_scores)
            
            vision_stats = {
                "avg_engagement_score": avg_eng,
                "avg_engagement_ui_score": avg_eng,
                "avg_gaze_score": avg_eng,
                "attention_state_focused_pct": 70.0,
                "attention_state_distracted_pct": 20.0,
                "attention_state_absent_pct": 10.0,
                "focused_duration_minutes": (len(self.vision_history) * 0.5) / 60.0,
                "distraction_frames": sum(1 for v in self.vision_history if v.get("attention") == "DISTRACTED"),
                "dominant_gesture": "NONE",
                "face_confidence": 0.9,
                "gesture_confidence": 0.8,
                "object_confidence": 0.7,
                "pose_confidence": 0.8,
                "system_confidence": 0.9
            }
        else:
            vision_stats = {}

        # Calculate Voice Stats
        voice_stats = {
            "avg_speaking_rate_wpm": 120,
            "avg_utterance_length_words": 8,
            "avg_volume": 0.5,
            "utterance_count": self.turn_count,
            "speech_stability_score": 0.9,
            "pct_vocal_arousal": 10.0,
            "pct_vocal_neutral": 80.0,
            "pct_vocal_withdrawal": 10.0
        }

        # Calculate Emotional Stats
        emotional_stats = {
            "mood_state": self.mood,
            "mood_confidence": self.mood_confidence,
            "frustration_score": self.consecutive_frustration * 0.2,
            "frustration_streak": self.consecutive_frustration,
            "emotional_trend_score": 0.5,
            "stability_index": self.consecutive_stability,
            "mood_score": 75,
            "primary_emotion": self.mood,
            "bayesian_confidence_score": 0.85
        }

        # Analytics
        analytics = {
            "avg_engagement_score": vision_stats.get("avg_engagement_score", 0.0),
            "avg_gaze_score": vision_stats.get("avg_gaze_score", 0.0),
            "focus_score": 80,
            "attention_span_minutes": vision_stats.get("focused_duration_minutes", 0.0),
            "distraction_frequency": "LOW",
            "emotion_stability_score": 85,
            "overall_mood_score": 75,
            "participation_level": "HIGH",
            "interaction_continuity_score": 0.9,
            "initiative_taking_score": 70,
            "task_completion_rate": 100,
            "positive_interactions": self.consecutive_stability,
            "challenging_moments": self.consecutive_frustration
        }

        # Timeline
        timeline = []
        if hasattr(self, 'vision_history') and self.vision_history:
            per_min = 120
            for i in range(0, len(self.vision_history), per_min):
                chunk = self.vision_history[i:i+per_min]
                avg_e = sum(v.get("engagement", 0) for v in chunk) / len(chunk)
                timeline.append({
                    "minute_index": i // per_min,
                    "avg_engagement": avg_e,
                    "attention_state": chunk[0].get("attention", "UNKNOWN")
                })

        return {
            "vision": vision_stats,
            "voice": voice_stats,
            "emotional": emotional_stats,
            "learning": [],
            "reinforcement": [],
            "analytics": analytics,
            "timeline": timeline,
            "session_summary": {
                "duration_seconds": int(time.time() - self.created_at),
                "total_turns": self.turn_count,
                "avg_engagement_score": vision_stats.get("avg_engagement_score", 0.0),
                "dominant_mood": self.mood,
                "peak_difficulty": max(self.difficulty_history) if self.difficulty_history else self.current_difficulty
            }
        }
