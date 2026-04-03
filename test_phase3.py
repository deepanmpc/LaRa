import sys, os

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.llm.AttentionController import AttentionController
from dataclasses import dataclass

@dataclass
class DummyRegState:
    current_mood: str = "neutral"
    frustration_persistence: float = 0.0

def test_attention_controller():
    controller = AttentionController()
    
    # Test frustrated
    reg = DummyRegState(current_mood="frustrated", frustration_persistence=0.7)
    prof = controller.get_profile(reg, turn_count=1, rag_triggered=False)
    assert prof.budget_history_tokens == 80, f"Expected 80, got {prof.budget_history_tokens}"
    assert prof.compress_aggressiveness == 0.8, f"Expected 0.8, got {prof.compress_aggressiveness}"
    
    # Test frustration floor limitation if custom config is weird
    controller.frust_hist = 20
    prof2 = controller.get_profile(reg, turn_count=1, rag_triggered=False)
    assert prof2.budget_history_tokens >= 60, "History budget dropped below 60 floor"
    
    print("Phase 3: Unit test passed. Frustrated yields 80, never drops below 60 floor.")

if __name__ == '__main__':
    test_attention_controller()
