import sys, os

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.llm.HistoryCompressor import HistoryCompressor

def test_history_compressor_generic():
    history = [
        {"user": "1", "lara": "Good job!"}, # Low info
    ]
    
    compressor = HistoryCompressor(max_tokens=200)
    # Note: compress() treats last 2 turns as RAW, so to test collapse we need more turns
    history_extended = [
        {"user": "1", "lara": "Good job!"}, # Collapse candidate
        {"user": "2", "lara": "Great!"},    # Collapse candidate
        {"user": "3", "lara": "Yes!"},      # Raw (T-2)
        {"user": "4", "lara": "Next?"},     # Raw (T-1)
    ]
    
    res = compressor.compress(history_extended)
    print("\n[History Output]")
    print(res)
    
    # Check for the NEW generic label
    assert "[Short exchange: user responded, LaRa praised]" in res, "Generic label missing!"
    assert "[Counting:" not in res, "Old hardcoded label still present!"
    
    print("Phase 2 Fix Verification: Generic label correctly used.")

if __name__ == '__main__':
    test_history_compressor_generic()
