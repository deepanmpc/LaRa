"""
LaRa Attention Controller (Phase 3)
Dynamically re-allocates token budgets across prompt blocks based on RegulationState.
"""

from dataclasses import dataclass
from src.core.PerformanceMonitor import PerformanceMonitor
from src.core.config_loader import CONFIG

@dataclass
class AttentionProfile:
    budget_history_tokens: int
    budget_memory_tokens: int
    compress_aggressiveness: float

class AttentionController:
    def __init__(self):
        # Load constraints from config if available
        try:
            cfg = CONFIG.cognitive_pipeline
            self.def_hist = getattr(cfg, "history_max_tokens", 200)
            self.def_agg = getattr(cfg, "compress_default_aggressiveness", 0.3)
            self.max_agg = getattr(cfg, "compress_max_aggressiveness", 1.0)
            self.frust_hist = getattr(cfg, "attention_frustrated_history_budget", 80)
            self.rag_hist = getattr(cfg, "attention_rag_history_budget", 100)
            self.rag_mem = getattr(cfg, "attention_rag_memory_budget", 120)
        except Exception:
            self.def_hist = 200
            self.def_agg = 0.3
            self.max_agg = 1.0
            self.frust_hist = 80
            self.rag_hist = 100
            self.rag_mem = 120

    def get_profile(self, regulation_state, turn_count: int, rag_triggered: bool) -> AttentionProfile:
        mood = getattr(regulation_state, "current_mood", "neutral")
        frustration_persistence = getattr(regulation_state, "frustration_persistence", 0.0)
        
        # Rule 1
        if mood in ("frustrated", "sad", "angry") or frustration_persistence > 0.6:
            hist_budget = self.frust_hist
            mem_budget = 40
            
            # Constraints: NEVER set compress_aggressiveness to 1.0 on the very first frustrated turn
            if frustration_persistence > 0.4:
                # The rule specifically says set to 0.8 for frustration.
                # If we scale it or just use 0.8:
                agg = 0.8
            else:
                agg = 0.5 # A moderate step before 0.8/1.0
                
            profile_name = "frustrated"
            
        # Rule 2
        elif rag_triggered:
            hist_budget = self.rag_hist
            mem_budget = self.rag_mem
            agg = 0.6
            profile_name = "rag"
            
        # Default
        else:
            hist_budget = self.def_hist
            mem_budget = 60
            agg = self.def_agg
            profile_name = "default"

        # Rule 3: turn_count > 10
        if turn_count > 10:
            extra_agg = ((turn_count - 10) // 5) * 0.1
            agg = min(self.max_agg, agg + extra_agg)

        # Constraints: NEVER reduce history_block below 60 tokens
        hist_budget = max(60, hist_budget)

        profile = AttentionProfile(
            budget_history_tokens=hist_budget,
            budget_memory_tokens=mem_budget,
            compress_aggressiveness=round(agg, 2)
        )
        
        # Log to PerfMonitor
        perf = PerformanceMonitor.get()
        perf.set_metric("attention_profile", profile_name)
        
        # Instruction requires logging exactly: attention_profile=frustrated history_budget=80 memory_budget=40 aggressiveness=0.8
        # We can just emit via standard logging.
        import logging
        logging.info(f"[Perf] attention_profile={profile_name} history_budget={profile.budget_history_tokens} "
                     f"memory_budget={profile.budget_memory_tokens} aggressiveness={profile.compress_aggressiveness}")

        return profile
