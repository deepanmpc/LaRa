"""
LaRa Learning Progress Manager (Step 2)
Handles mastery tracking independently from difficulty gating.

Rules:
- Difficulty decisions live in DifficultyGate (SessionState)
- Mastery tracking lives HERE
- Never mix emotional logic with mastery updates
- Reads/writes via UserMemoryManager
"""

import time
import logging


class LearningProgressManager:
    """
    Tracks concept mastery independently from emotional/difficulty logic.
    
    Responsibilities:
    - Update attempt counts
    - Update mastery levels (0-5)
    - Track success rate per concept
    - Provide mastery data for difficulty baseline
    
    NOT responsible for:
    - Difficulty decisions (that's DifficultyGate/SessionState)
    - Emotional metrics (that's UserMemoryManager)
    """
    
    def __init__(self, memory_manager):
        """
        Args:
            memory_manager: UserMemoryManager instance for persistence
        """
        self._memory = memory_manager
        self._user_id = None
        logging.info("[LearningProgress] Manager initialized.")
    
    def set_user(self, user_id: str):
        """Set the active user for this session."""
        self._user_id = user_id
    
    def update_attempt(self, concept: str, difficulty: int, success: bool):
        """
        Record a learning attempt outcome.
        
        Args:
            concept: The concept being practiced (e.g., "counting", "colors")
            difficulty: The difficulty level at time of attempt
            success: Whether the child completed/understood the task
        """
        if not self._memory or not self._user_id:
            return
        
        progress = self._memory.record_attempt(self._user_id, concept, success)
        
        logging.info(
            f"[LearningProgress] {concept} | difficulty={difficulty} | "
            f"success={success} | mastery={progress.mastery_level}/5 | "
            f"attempts={progress.attempt_count}"
        )
        
        return progress
    
    def get_mastery_level(self, concept: str) -> int:
        """Get current mastery level for a concept (0-5)."""
        if not self._memory or not self._user_id:
            return 0
        
        progress = self._memory.get_learning_progress(self._user_id, concept)
        return progress.mastery_level
    
    def get_baseline_difficulty(self, concept: str) -> int:
        """
        Suggest a baseline difficulty based on mastery.
        Mastery 0-1 → difficulty 1
        Mastery 2-3 → difficulty 2
        Mastery 4   → difficulty 3
        Mastery 5   → difficulty 4
        """
        mastery = self.get_mastery_level(concept)
        if mastery <= 1:
            return 1
        elif mastery <= 3:
            return 2
        elif mastery == 4:
            return 3
        else:
            return 4
    
    def update_mastery(self, concept: str):
        """
        Recalculate mastery based on recent success pattern.
        Called at session end or significant milestones.
        """
        # Currently mastery is updated per-attempt in record_attempt.
        # This method exists for future batch recalculation if needed.
        pass
