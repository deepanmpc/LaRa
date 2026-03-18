import sys, os

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.session.session_state import SessionState
from src.session.session_summary import generate_session_summary

def test_phase4():
    # Setup mock session state
    session = SessionState()
    session.current_concept = "counting"
    session.turn_count = 7
    session.consecutive_frustration = 0
    session.consecutive_stability = 3
    
    # Mocking difficulty trajectory
    session.difficulty_history = [2, 2, 3]
    
    # Mocking engagement proxy lengths
    session.last_3_input_lengths = [20, 25, 30] # Average 25 -> moderate
    
    # Generate summary
    summary = generate_session_summary(session)
    
    print("\n[Output]")
    print(summary)
    
    assert "Difficulty: 2->2->3" in summary, "Difficulty trajectory not formatted correctly."
    assert "Trend: improving (accelerating)" in summary, "Trend velocity not formatted correctly."
    assert "Engagement: moderate" in summary, "Engagement proxy not formatted correctly."
    
    # Test length limitation
    token_len = len(summary) // 4
    assert token_len < 120, f"Session summary token count ({token_len}) exceeds 120."
    
    print("\nPhase 4: Unit test passed. Format matches spec and is under 120 tokens.")

if __name__ == '__main__':
    test_phase4()
