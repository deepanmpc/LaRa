"""
LaRa User Memory (Phase 2)
Local SQLite database for persistent user profiles, learning progress,
and aggregated emotional metrics.

Design rules (from memory_architecture.md):
- All storage local (SQLite file)
- No raw transcripts stored
- No emotional narratives
- No identity-level labels
- Emotional metrics are aggregated counts with decay
- LLM cannot write to this directly — only deterministic managers
"""

import os
import time
import sqlite3
import logging
import threading
from dataclasses import dataclass
from typing import Optional

try:
    from config_loader import CONFIG as _CONFIG
    _DB_OVERRIDE    = _CONFIG.memory.db_filename
    _DECAY_FACTOR   = _CONFIG.memory.emotional_decay_factor
except Exception:
    _DB_OVERRIDE    = None
    _DECAY_FACTOR   = 0.95


# Database file location (local to project)
DB_DIR  = os.path.dirname(os.path.abspath(__file__))
_db_file = _DB_OVERRIDE if _DB_OVERRIDE else "lara_memory.db"
DB_PATH = os.path.join(DB_DIR, _db_file)

# Emotional metric decay
METRIC_DECAY_FACTOR    = _DECAY_FACTOR
DECAY_INTERVAL_SECONDS = 24 * 60 * 60  # 24 hours


@dataclass
class UserProfile:
    """Persistent user preferences."""
    user_id: str
    baseline_instruction_depth: int = 2   # 1=simple, 2=normal, 3=detailed
    preferred_topics: str = ""            # Comma-separated
    preferred_tts_speed: float = 0.9      # Kokoro speed


@dataclass
class LearningProgress:
    """Per-concept mastery tracking."""
    user_id: str
    concept_name: str
    mastery_level: int = 0          # 0-5 scale
    highest_success_level: int = 0
    attempt_count: int = 0
    last_success_timestamp: float = 0.0


@dataclass
class EmotionalMetrics:
    """Aggregated emotional counts per concept. No narratives."""
    user_id: str
    concept_name: str
    frustration_count: int = 0
    recovery_count: int = 0
    neutral_stability_count: int = 0
    last_updated: float = 0.0


class UserMemoryManager:
    """
    Deterministic manager for LaRa's persistent memory.
    
    Rules:
    - Only structured data (counts, levels, timestamps)
    - No raw transcripts
    - No emotional labels or narratives
    - Decay applied to emotional metrics every 24h
    - LLM has no direct access — only this manager writes
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn = None
        self._lock = threading.Lock()   # Prevents concurrent SQLite write corruption
        self._init_db()
        self._apply_startup_decay()
        logging.info(f"[UserMemory] Initialized (db: {os.path.basename(db_path)})")
    
    def _init_db(self):
        """Create tables if they don't exist."""
        self._conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None,   # Autocommit — we manage transactions explicitly
        )
        self._conn.row_factory = sqlite3.Row
        
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                baseline_instruction_depth INTEGER DEFAULT 2,
                preferred_topics TEXT DEFAULT '',
                preferred_tts_speed REAL DEFAULT 0.9
            );
            
            CREATE TABLE IF NOT EXISTS learning_progress (
                user_id TEXT NOT NULL,
                concept_name TEXT NOT NULL,
                mastery_level INTEGER DEFAULT 0,
                highest_success_level INTEGER DEFAULT 0,
                attempt_count INTEGER DEFAULT 0,
                last_success_timestamp REAL DEFAULT 0.0,
                PRIMARY KEY (user_id, concept_name)
            );
            
            CREATE TABLE IF NOT EXISTS emotional_metrics (
                user_id TEXT NOT NULL,
                concept_name TEXT NOT NULL,
                frustration_count INTEGER DEFAULT 0,
                recovery_count INTEGER DEFAULT 0,
                neutral_stability_count INTEGER DEFAULT 0,
                last_updated REAL DEFAULT 0.0,
                PRIMARY KEY (user_id, concept_name)
            );
            
            CREATE TABLE IF NOT EXISTS decay_log (
                id INTEGER PRIMARY KEY,
                last_decay_timestamp REAL DEFAULT 0.0
            );
            
            CREATE TABLE IF NOT EXISTS reinforcement_metrics (
                user_id TEXT PRIMARY KEY,
                preferred_style TEXT DEFAULT 'calm_validation',
                total_events INTEGER DEFAULT 0,
                last_updated REAL DEFAULT 0.0
            );
        """)
        self._conn.commit()
    
    # --- User Profile ---
    
    def get_or_create_user(self, user_id: str) -> UserProfile:
        """Get existing user profile or create a new one."""
        row = self._conn.execute(
            "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
        ).fetchone()
        
        if row:
            return UserProfile(
                user_id=row["user_id"],
                baseline_instruction_depth=row["baseline_instruction_depth"],
                preferred_topics=row["preferred_topics"],
                preferred_tts_speed=row["preferred_tts_speed"]
            )
        
        # Create new user with defaults
        self._conn.execute(
            "INSERT INTO user_profiles (user_id) VALUES (?)", (user_id,)
        )
        self._conn.commit()
        logging.info(f"[UserMemory] Created new user profile: {user_id}")
        return UserProfile(user_id=user_id)
    
    def update_user_preferences(self, user_id: str, **kwargs):
        """Update user preferences (instruction_depth, topics, tts_speed)."""
        allowed = {"baseline_instruction_depth", "preferred_topics", "preferred_tts_speed"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        
        if not updates:
            return
        
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [user_id]
        self._conn.execute(
            f"UPDATE user_profiles SET {set_clause} WHERE user_id = ?", values
        )
        self._conn.commit()
    
    # --- Learning Progress ---
    
    def get_learning_progress(self, user_id: str, concept_name: str) -> LearningProgress:
        """Get learning progress for a concept, creating if needed."""
        row = self._conn.execute(
            "SELECT * FROM learning_progress WHERE user_id = ? AND concept_name = ?",
            (user_id, concept_name)
        ).fetchone()
        
        if row:
            return LearningProgress(
                user_id=row["user_id"],
                concept_name=row["concept_name"],
                mastery_level=row["mastery_level"],
                highest_success_level=row["highest_success_level"],
                attempt_count=row["attempt_count"],
                last_success_timestamp=row["last_success_timestamp"]
            )
        
        # Create new entry
        self._conn.execute(
            "INSERT INTO learning_progress (user_id, concept_name) VALUES (?, ?)",
            (user_id, concept_name)
        )
        self._conn.commit()
        return LearningProgress(user_id=user_id, concept_name=concept_name)
    
    def record_attempt(self, user_id: str, concept_name: str, success: bool):
        """
        Record a learning attempt.
        On success: increment mastery (max 5), update highest level.
        Always: increment attempt count.
        """
        progress = self.get_learning_progress(user_id, concept_name)
        progress.attempt_count += 1
        
        if success:
            progress.mastery_level = min(5, progress.mastery_level + 1)
            progress.highest_success_level = max(
                progress.highest_success_level, progress.mastery_level
            )
            progress.last_success_timestamp = time.time()
        
        with self._lock:
            self._conn.execute("""
                UPDATE learning_progress 
                SET mastery_level = ?, highest_success_level = ?,
                    attempt_count = ?, last_success_timestamp = ?
                WHERE user_id = ? AND concept_name = ?
            """, (
                progress.mastery_level, progress.highest_success_level,
                progress.attempt_count, progress.last_success_timestamp,
                user_id, concept_name
            ))
            self._conn.commit()
        
        logging.info(
            f"[UserMemory] Learning: {concept_name} | "
            f"Mastery: {progress.mastery_level}/5 | "
            f"Attempts: {progress.attempt_count} | "
            f"Success: {success}"
        )
        return progress
    
    # --- Emotional Metrics ---
    
    def record_emotional_metric(self, user_id: str, concept_name: str, mood: str):
        """
        Record an aggregated emotional count for a concept.
        No narratives — only increments counters.
        """
        with self._lock:
            now = time.time()
            self._conn.execute("""
                INSERT OR IGNORE INTO emotional_metrics (user_id, concept_name)
                VALUES (?, ?)
            """, (user_id, concept_name))
            if mood in ("frustrated", "sad"):
                self._conn.execute("""
                    UPDATE emotional_metrics 
                    SET frustration_count = frustration_count + 1, last_updated = ?
                    WHERE user_id = ? AND concept_name = ?
                """, (now, user_id, concept_name))
            elif mood in ("neutral", "happy"):
                self._conn.execute("""
                    UPDATE emotional_metrics 
                    SET neutral_stability_count = neutral_stability_count + 1, last_updated = ?
                    WHERE user_id = ? AND concept_name = ?
                """, (now, user_id, concept_name))
            self._conn.commit()
    
    def record_recovery(self, user_id: str, concept_name: str):
        """Record a recovery event (frustration → stability transition)."""
        with self._lock:
            self._conn.execute("""
                INSERT OR IGNORE INTO emotional_metrics (user_id, concept_name)
                VALUES (?, ?)
            """, (user_id, concept_name))
            self._conn.execute("""
                UPDATE emotional_metrics 
                SET recovery_count = recovery_count + 1, last_updated = ?
                WHERE user_id = ? AND concept_name = ?
            """, (time.time(), user_id, concept_name))
            self._conn.commit()
    
    # --- Decay ---
    
    def _apply_startup_decay(self):
        """
        Apply emotional metric decay on startup.
        Multiplies all counts by METRIC_DECAY_FACTOR for each 24h period
        that has elapsed since the last decay.
        """
        row = self._conn.execute(
            "SELECT last_decay_timestamp FROM decay_log WHERE id = 1"
        ).fetchone()
        
        if row:
            last_decay = row["last_decay_timestamp"]
        else:
            # First run — initialize decay log
            self._conn.execute(
                "INSERT INTO decay_log (id, last_decay_timestamp) VALUES (1, ?)",
                (time.time(),)
            )
            self._conn.commit()
            return
        
        elapsed = time.time() - last_decay
        decay_periods = int(elapsed / DECAY_INTERVAL_SECONDS)
        
        if decay_periods <= 0:
            return
        
        # Apply compound decay
        total_decay = METRIC_DECAY_FACTOR ** decay_periods
        
        self._conn.execute("""
            UPDATE emotional_metrics SET
                frustration_count = CAST(frustration_count * ? AS INTEGER),
                recovery_count = CAST(recovery_count * ? AS INTEGER),
                neutral_stability_count = CAST(neutral_stability_count * ? AS INTEGER)
        """, (total_decay, total_decay, total_decay))
        
        self._conn.execute(
            "UPDATE decay_log SET last_decay_timestamp = ? WHERE id = 1",
            (time.time(),)
        )
        self._conn.commit()
        
        logging.info(
            f"[UserMemory] Applied decay ({decay_periods} periods, "
            f"factor={total_decay:.3f})"
        )
    
    # --- Dashboard Data ---
    
    def get_session_summary(self, user_id: str) -> dict:
        """
        Get structured data for therapist dashboard.
        Returns counts and levels only — no transcripts or labels.
        """
        progress_rows = self._conn.execute(
            "SELECT * FROM learning_progress WHERE user_id = ?", (user_id,)
        ).fetchall()
        
        metrics_rows = self._conn.execute(
            "SELECT * FROM emotional_metrics WHERE user_id = ?", (user_id,)
        ).fetchall()
        
        return {
            "user_id": user_id,
            "learning": [
                {
                    "concept": r["concept_name"],
                    "mastery": r["mastery_level"],
                    "attempts": r["attempt_count"],
                    "highest": r["highest_success_level"]
                }
                for r in progress_rows
            ],
            "emotional_stability": [
                {
                    "concept": r["concept_name"],
                    "frustration_count": r["frustration_count"],
                    "recovery_count": r["recovery_count"],
                    "stability_count": r["neutral_stability_count"]
                }
                for r in metrics_rows
            ]
        }
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
