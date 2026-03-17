"""
LaRa Attention Controller (Phase 3)
Determines token budgets for prompt segments based on current run state.
"""
from typing import Dict

class AttentionController:
    @staticmethod
    def get_budgets(
        is_frustrated: bool,
        rag_active: bool,
        turn_count: int
    ) -> Dict[str, int]:
        """
        Dynamically adjusts token budgets per component based on cognitive load rules.
        """
        # Base budgets (approx tokens)
        budgets = {
            "system": 300,        # Stable, unbreakable
            "strategy": 100,
            "reinforcement": 50,
            "memory": 150,
            "session": 120,
            "history": 200,
            "live_input": 150
        }

        if is_frustrated:
            # Cognitive offload: less history, more focus on immediate clarity
            budgets["history"] = 80
            budgets["memory"] = 50   # Less distracting past stories
            budgets["strategy"] = 150 # Ensure strategy has emphasis

        if rag_active:
            # RAG needs room, squeeze history
            budgets["history"] = min(budgets["history"], 120)

        if turn_count > 15:
            # Aggressive compression for long sessions to prevent context dilution
            budgets["history"] = min(budgets["history"], 100)

        return budgets
