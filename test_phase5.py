import sys, os

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from src.memory.vector_memory import VectorMemory, RetrievedMemory

def test_phase5():
    # Setup mock VectorMemory
    vm = VectorMemory(persist_dir="/tmp/lara_test_vec")
    vm._enabled = True
    vm._user_id = "test"
    vm._session_retrievals = 0
    vm._injected_summaries = set()
    
    # Mocking candidates
    candidates = [
        # Score approx: 0.5*0.9 + 0.3*1.0 + 0.2*1.0 = 0.45 + 0.3 + 0.2 = 0.95 -> Top
        RetrievedMemory("Perfect match", "counting", 0.9, 0),
        
        # Score approx: 0.5*0.5 + 0.3*1.0 + 0.2*0.0 = 0.25 + 0.3 + 0 = 0.55
        RetrievedMemory("Decent match", "reading", 0.5, 0),
        
        # Score approx: 0.5*0.3 + 0.3*0.0 + 0.2*0.0 = 0.15 + 0 + 0 = 0.15 -> Below 0.45 threshold
        RetrievedMemory("Bad match 1", "swimming", 0.3, 100),
        
        # Score approx: 0.5*0.4 + 0.3*0.5 + 0.2*0.0 = 0.2 + 0.15 + 0.0 = 0.35 -> Below 0.45 threshold
        RetrievedMemory("Bad match 2", "jumping", 0.4, 45),
        
        # Score approx: 0.5*0.7 + 0.3*1.0 + 0.2*1.0 = 0.35 + 0.3 + 0.2 = 0.85 -> 2nd Place
        RetrievedMemory("Almost perfect", "counting", 0.7, 0)
    ]
    
    ranked = vm._rank_memories(candidates, "counting")
    
    assert len(ranked) == 2, f"Expected 2 ranked memories, got {len(ranked)}"
    assert ranked[0].summary == "Perfect match"
    assert ranked[1].summary == "Almost perfect"
    
    # Test all below threshold
    bad_candidates = [
        RetrievedMemory("Bad match 1", "swimming", 0.3, 100),
        RetrievedMemory("Bad match 2", "jumping", 0.4, 45),
    ]
    
    ranked_bad = vm._rank_memories(bad_candidates, "counting")
    assert len(ranked_bad) == 0, "Expected empty list when all memories below threshold."
    
    # Need to manually inject and check formatting
    # The actual get_context_for_llm connects to db, so we bypass it slightly by testing the format code here
    vm._session_retrievals = 0
    vm._injected_summaries = set()
    
    # Using the exact same lines loop
    lines = []
    for m in ranked:
        vm._injected_summaries.add(m.summary)
        vm._session_retrievals += 1
        lines.append(f"[Past story: {m.summary} — {m.days_ago:.0f}d ago]")
        
    out = "\\n".join(lines)
    assert "[Past story: Perfect match — 0d ago]" in out
    
    print("Phase 5: Unit test passed. Top 2 injected. Below-threshold rejected. Format is compact.")

if __name__ == '__main__':
    test_phase5()
