"""
LaRa Child Preference Memory
Detects and stores what the child likes, dislikes, and cares about.
Uses these preferences to personalize LLM responses.

Examples:
  "I like dinosaurs" → stores like: dinosaurs
  "I don't like spiders" → stores dislike: spiders
  "My favorite color is blue" → stores like: blue (color)
  "I love playing with blocks" → stores like: playing with blocks
  "I hate math" → stores dislike: math

Rules (from system_invariants.md):
- Store structured data only (topic + sentiment)
- No emotional labeling
- No narrative storage
- LLM receives preferences as context, not instructions
- Preferences are additive — never override existing ones
- Maximum 20 preferences per user (prevent unbounded growth)
"""

import re
import time
import logging
from dataclasses import dataclass
from typing import Optional


MAX_PREFERENCES_PER_USER = 20
MAX_TOPIC_LENGTH = 50


@dataclass
class Preference:
    """A single structured preference."""
    topic: str          # What (e.g., "dinosaurs", "blue", "math")
    sentiment: str      # "like" or "dislike"
    timestamp: float    # When it was detected


# --- Regex Patterns for Preference Detection ---
# Positive patterns (likes)
LIKE_PATTERNS = [
    r"\bi (?:really )?(?:like|love|enjoy|want)(?: to)? (.+?)(?:\.|!|$)",
    r"\bmy (?:favorite|favourite) (?:\w+ )?is (.+?)(?:\.|!|$)",
    r"\bi (?:really )?(?:like|love|enjoy) (.+?)(?:\.|!|$)",
    r"\b(.+?) (?:is|are) (?:my )?(?:favorite|favourite|the best)(?:\.|!|$)",
    r"\bi think (.+?) (?:is|are) (?:cool|fun|great|awesome|amazing|nice)(?:\.|!|$)",
]

# Negative patterns (dislikes)
DISLIKE_PATTERNS = [
    r"\bi (?:don'?t|do not) (?:really )?(?:like|want|enjoy) (.+?)(?:\.|!|$)",
    r"\bi (?:hate|dislike) (.+?)(?:\.|!|$)",
    r"\b(.+?) (?:is|are) (?:scary|boring|yucky|bad|mean|stupid|gross)(?:\.|!|$)",
    r"\bi(?:'m| am) (?:scared|afraid) of (.+?)(?:\.|!|$)",
    r"\bi (?:don'?t|do not) want (.+?)(?:\.|!|$)",
]


def _clean_topic(raw: str) -> Optional[str]:
    """Clean and validate an extracted topic string."""
    topic = raw.strip().lower()
    # Remove common filler words at the start
    topic = re.sub(r"^(a |an |the |some |to |that |this |it |when )", "", topic)
    topic = topic.strip()
    
    # Reject if too short, too long, or just noise
    if len(topic) < 2 or len(topic) > MAX_TOPIC_LENGTH:
        return None
    if topic in ("it", "that", "this", "them", "those", "something", "anything", "everything"):
        return None
    
    return topic


def extract_preferences(text: str) -> list[Preference]:
    """
    Extract likes/dislikes from user text.
    Returns a list of Preference objects (may be empty).
    """
    text_lower = text.lower().strip()
    if len(text_lower) < 5:
        return []
    
    results = []
    now = time.time()
    
    # Check dislike patterns first (they're more specific with "don't like")
    for pattern in DISLIKE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            topic = _clean_topic(match.group(1))
            if topic:
                results.append(Preference(topic=topic, sentiment="dislike", timestamp=now))
    
    # Check like patterns (skip if we already found a dislike for same text)
    if not results:
        for pattern in LIKE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                topic = _clean_topic(match.group(1))
                if topic:
                    results.append(Preference(topic=topic, sentiment="like", timestamp=now))
                    break  # One like per utterance is enough
    
    for p in results:
        logging.info(f"[Preference] Detected: {p.sentiment} → {p.topic}")
    
    return results


class ChildPreferenceManager:
    """
    Manages the child's personal preferences in UserMemory.
    
    Detects, stores, deduplicates, and provides preferences
    for LLM context injection.
    """
    
    def __init__(self, memory_manager):
        """
        Args:
            memory_manager: UserMemoryManager instance
        """
        self._memory = memory_manager
        self._user_id = None
        self._cached_preferences: list[Preference] = []
        self._ensure_table()
        logging.info("[Preference] Manager initialized.")
    
    def _ensure_table(self):
        """Create preferences table if it doesn't exist."""
        if not self._memory or not self._memory._conn:
            return
        self._memory._conn.execute("""
            CREATE TABLE IF NOT EXISTS child_preferences (
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                timestamp REAL DEFAULT 0.0,
                PRIMARY KEY (user_id, topic)
            )
        """)
        self._memory._conn.commit()
    
    def set_user(self, user_id: str):
        """Set active user and load their preferences from DB."""
        self._user_id = user_id
        self._load_preferences()
    
    def _load_preferences(self):
        """Load preferences from SQLite into memory cache."""
        self._cached_preferences = []
        if not self._memory or not self._user_id:
            return
        
        try:
            rows = self._memory._conn.execute(
                "SELECT topic, sentiment, timestamp FROM child_preferences WHERE user_id = ? ORDER BY timestamp DESC",
                (self._user_id,)
            ).fetchall()
            
            for r in rows:
                self._cached_preferences.append(Preference(
                    topic=r["topic"],
                    sentiment=r["sentiment"],
                    timestamp=r["timestamp"]
                ))
            
            if self._cached_preferences:
                logging.info(
                    f"[Preference] Loaded {len(self._cached_preferences)} preferences for {self._user_id}"
                )
        except Exception as e:
            logging.warning(f"[Preference] Failed to load: {e}")
    
    def process_utterance(self, text: str) -> list[Preference]:
        """
        Analyze user text for preference statements.
        New preferences are stored in DB and cached.
        Returns list of newly detected preferences.
        """
        new_prefs = extract_preferences(text)
        
        for pref in new_prefs:
            self._store_preference(pref)
        
        return new_prefs
    
    def _store_preference(self, pref: Preference):
        """Store a preference, deduplicating by topic."""
        if not self._memory or not self._user_id:
            return
        
        # Check if we already have this topic
        existing_topics = {p.topic for p in self._cached_preferences}
        
        if pref.topic in existing_topics:
            # Update sentiment if it changed (e.g., "I like X" → "I don't like X")
            self._memory._conn.execute("""
                UPDATE child_preferences SET sentiment = ?, timestamp = ?
                WHERE user_id = ? AND topic = ?
            """, (pref.sentiment, pref.timestamp, self._user_id, pref.topic))
            self._memory._conn.commit()
            
            # Update cache
            for p in self._cached_preferences:
                if p.topic == pref.topic:
                    p.sentiment = pref.sentiment
                    p.timestamp = pref.timestamp
            
            logging.info(f"[Preference] Updated: {pref.topic} → {pref.sentiment}")
            return
        
        # Enforce max preferences limit
        if len(self._cached_preferences) >= MAX_PREFERENCES_PER_USER:
            # Remove oldest preference
            oldest = min(self._cached_preferences, key=lambda p: p.timestamp)
            self._memory._conn.execute(
                "DELETE FROM child_preferences WHERE user_id = ? AND topic = ?",
                (self._user_id, oldest.topic)
            )
            self._cached_preferences.remove(oldest)
            logging.info(f"[Preference] Evicted oldest: {oldest.topic}")
        
        # Insert new
        self._memory._conn.execute("""
            INSERT OR REPLACE INTO child_preferences (user_id, topic, sentiment, timestamp)
            VALUES (?, ?, ?, ?)
        """, (self._user_id, pref.topic, pref.sentiment, pref.timestamp))
        self._memory._conn.commit()
        self._cached_preferences.append(pref)
        
        logging.info(f"[Preference] Stored: {pref.sentiment} → {pref.topic}")
    
    def get_context_for_llm(self) -> str:
        """
        Build a structured preference context string for the LLM.
        Returns empty string if no preferences are stored.
        
        Format:
          [Child's preferences — use these naturally, do NOT list them:
           Likes: dinosaurs, blue, playing outside
           Dislikes: spiders, loud sounds]
        """
        if not self._cached_preferences:
            return ""
        
        likes = [p.topic for p in self._cached_preferences if p.sentiment == "like"]
        dislikes = [p.topic for p in self._cached_preferences if p.sentiment == "dislike"]
        
        parts = []
        if likes:
            parts.append(f"Likes: {', '.join(likes)}")
        if dislikes:
            parts.append(f"Dislikes: {', '.join(dislikes)}")
        
        if not parts:
            return ""
        
        context = (
            "[Child's preferences — weave these into your responses naturally. "
            "Do NOT list them or say 'I know you like X'. "
            "Instead, use them to choose examples, topics, and references.\n"
            f"{'; '.join(parts)}]"
        )
        
        return context
    
    def get_all_preferences(self) -> list[Preference]:
        """Return all cached preferences."""
        return list(self._cached_preferences)
