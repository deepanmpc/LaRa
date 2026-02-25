"""
LaRa Reinforcement Adaptation Manager (Step 4)
Adapts reinforcement style based on historical response patterns.

Reinforcement Types:
- PRAISE_BASED: "Great job! You did it!"
- ACHIEVEMENT_BASED: "You got 3 right in a row!"
- CALM_VALIDATION: "You are doing well. Let us keep going."
- PLAYFUL_ENCOURAGEMENT: "Wow, that was fun! Want to try another?"

Rules (from implementation_fix_and_reinforcement.md):
- Adapt only after minimum 5 supporting events
- Change style at most once per session
- Lock reinforcement style for remainder of session once changed
- Persist changes only after session ends
- Default to baseline preference if uncertain
- No sudden personality shifts
- No sarcasm or exaggerated praise
"""

import logging
from dataclasses import dataclass, field
from typing import Optional


class ReinforcementStyle:
    """Reinforcement type constants."""
    PRAISE_BASED = "praise_based"
    ACHIEVEMENT_BASED = "achievement_based"
    CALM_VALIDATION = "calm_validation"
    PLAYFUL_ENCOURAGEMENT = "playful_encouragement"
    
    ALL = [PRAISE_BASED, ACHIEVEMENT_BASED, CALM_VALIDATION, PLAYFUL_ENCOURAGEMENT]
    
    # Prompt additions per style (injected into LLM context)
    PROMPTS = {
        PRAISE_BASED: (
            "Use warm praise when the child succeeds. "
            "Example: 'Great job! You did it!' Keep praise genuine and calm."
        ),
        ACHIEVEMENT_BASED: (
            "Acknowledge specific achievements. "
            "Example: 'You got that right! You are getting better at this.' "
            "Focus on observable progress, not personality."
        ),
        CALM_VALIDATION: (
            "Use calm, steady validation. "
            "Example: 'You are doing well. Let us keep going.' "
            "Minimal excitement, maximum steadiness."
        ),
        PLAYFUL_ENCOURAGEMENT: (
            "Use gentle, playful encouragement. "
            "Example: 'That was fun! Want to try one more?' "
            "Keep energy moderate — never hyperactive."
        ),
    }


# Minimum events before reinforcement style can change
MIN_EVENTS_FOR_CHANGE = 5

# Confidence threshold for style adaptation
STYLE_CONFIDENCE_THRESHOLD = 0.6


@dataclass
class ReinforcementMetrics:
    """Tracks effectiveness of each reinforcement type per user."""
    style: str
    success_count: int = 0        # Times followed by stability
    total_count: int = 0          # Times this style was used
    
    @property
    def success_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count


class ReinforcementAdaptationManager:
    """
    Adapts reinforcement style based on aggregated outcomes.
    
    Rules:
    - Tracks which reinforcement type correlates with improved stability
    - Uses aggregated success metrics (not single events)
    - Adapts only after minimum 5 events
    - Changes reinforcement style at most once per session
    - Locks style for remainder of session after change
    """
    
    def __init__(self, memory_manager=None):
        """
        Args:
            memory_manager: UserMemoryManager for persistence (optional)
        """
        self._memory = memory_manager
        self._user_id = None
        
        # Per-session tracking
        self._session_metrics: dict[str, ReinforcementMetrics] = {
            style: ReinforcementMetrics(style=style)
            for style in ReinforcementStyle.ALL
        }
        self._current_style = ReinforcementStyle.CALM_VALIDATION  # Safe default
        self._baseline_style = ReinforcementStyle.CALM_VALIDATION
        self._style_changed_this_session = False
        self._style_locked = False
        
        logging.info("[Reinforcement] Manager initialized.")
    
    def set_user(self, user_id: str, baseline_style: Optional[str] = None):
        """Set the active user and load their baseline preference."""
        self._user_id = user_id
        
        if baseline_style and baseline_style in ReinforcementStyle.ALL:
            self._baseline_style = baseline_style
            self._current_style = baseline_style
        
        # Load historical metrics from DB if available
        if self._memory:
            self._load_historical_metrics(user_id)
        
        logging.info(
            f"[Reinforcement] User: {user_id} | "
            f"Baseline: {self._baseline_style}"
        )
    
    def get_style(self, regulation_state) -> str:
        """
        Get the current reinforcement style.
        
        Uses RegulationState to decide if style should adapt.
        Only adapts once per session, only with enough data.
        
        Args:
            regulation_state: RegulationState from compute_regulation_state()
            
        Returns:
            Reinforcement style string
        """
        # If style is locked for this session, return current
        if self._style_locked:
            return self._current_style
        
        # Check if we have enough data to consider adapting
        total_events = sum(m.total_count for m in self._session_metrics.values())
        
        if total_events >= MIN_EVENTS_FOR_CHANGE and not self._style_changed_this_session:
            best_style = self._find_best_style()
            
            if best_style and best_style != self._current_style:
                old = self._current_style
                self._current_style = best_style
                self._style_changed_this_session = True
                self._style_locked = True  # Lock for rest of session
                
                logging.info(
                    f"[Reinforcement] Style adapted: {old} → {best_style} "
                    f"(after {total_events} events)"
                )
        
        return self._current_style
    
    def get_style_prompt(self) -> str:
        """Get the LLM prompt addition for current reinforcement style."""
        return ReinforcementStyle.PROMPTS.get(self._current_style, "")
    
    def update_metrics(self, reinforcement_type: str, outcome_stable: bool):
        """
        Record a reinforcement event outcome.
        
        Args:
            reinforcement_type: Which style was used
            outcome_stable: Whether the child's next turn was stable (neutral/happy)
        """
        if reinforcement_type not in self._session_metrics:
            return
        
        metrics = self._session_metrics[reinforcement_type]
        metrics.total_count += 1
        if outcome_stable:
            metrics.success_count += 1
        
        logging.debug(
            f"[Reinforcement] {reinforcement_type}: "
            f"{metrics.success_count}/{metrics.total_count} "
            f"({metrics.success_rate:.0%} success)"
        )
    
    def _find_best_style(self) -> Optional[str]:
        """
        Find the best reinforcement style based on success rate.
        Only considers styles with >= MIN_EVENTS_FOR_CHANGE uses.
        """
        candidates = [
            m for m in self._session_metrics.values()
            if m.total_count >= 3  # At least 3 uses of this style
        ]
        
        if not candidates:
            return None
        
        best = max(candidates, key=lambda m: m.success_rate)
        
        # Only switch if meaningfully better than current
        current_metrics = self._session_metrics[self._current_style]
        if current_metrics.total_count >= 3:
            improvement = best.success_rate - current_metrics.success_rate
            if improvement < 0.15:  # Need at least 15% improvement
                return None
        
        return best.style
    
    def _load_historical_metrics(self, user_id: str):
        """Load historical reinforcement metrics from UserMemory."""
        if not self._memory:
            return
        
        try:
            row = self._memory._conn.execute(
                "SELECT * FROM reinforcement_metrics WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            
            if row:
                preferred = row["preferred_style"]
                if preferred in ReinforcementStyle.ALL:
                    self._baseline_style = preferred
                    self._current_style = preferred
        except Exception:
            # Table might not exist yet — that's fine
            pass
    
    def persist_session_metrics(self):
        """
        Persist reinforcement metrics to DB at end of session.
        Only called at session end — never during turns.
        """
        if not self._memory or not self._user_id:
            return
        
        try:
            self._memory._conn.execute("""
                INSERT OR REPLACE INTO reinforcement_metrics
                (user_id, preferred_style, total_events, last_updated)
                VALUES (?, ?, ?, ?)
            """, (
                self._user_id,
                self._current_style,
                sum(m.total_count for m in self._session_metrics.values()),
                __import__('time').time()
            ))
            self._memory._conn.commit()
            
            logging.info(
                f"[Reinforcement] Persisted metrics for {self._user_id}: "
                f"style={self._current_style}"
            )
        except Exception as e:
            logging.warning(f"[Reinforcement] Failed to persist: {e}")
