import sys, os

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.llm.HistoryCompressor import HistoryCompressor

def test_history_compressor():
    history = []
    # 18 repetitive turns
    for i in range(1, 19):
        history.append({"user": str(i), "lara": "Good!"})
        
    # Last 2 turns
    history.append({"user": "What comes after 18?", "lara": "Let us count together. After 18 comes 19!"})
    history.append({"user": "19", "lara": "Excellent job!"})
    
    compressor = HistoryCompressor(max_tokens=200)
    res = compressor.compress(history)
    
    # Assertions
    assert "[Repeated encouragement: 18 turns]" in res, "Failed to summarize repetitive turns."
    assert "U: What comes after 18?" in res, "Failed to preserve T-2"
    assert "U: 19" in res, "Failed to preserve T-1"
    
    token_count = len(res) // 4
    assert token_count < 200, f"Token count {token_count} exceeds 200 limit"
    
    print("Phase 2: Unit test passed. 20-turn repetitive history compresses below 200 tokens. Last 2 raw turns always present.")

if __name__ == '__main__':
    test_history_compressor()
