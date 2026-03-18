import sys, os
import time

_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

import src.core.runtime_paths as rp
rp.initialize()

from src.llm.AgentricTLM import LLMService
from src.core.PerformanceMonitor import PerformanceMonitor

def verify_fix3():
    perf = PerformanceMonitor.get()
    llm = LLMService.get()
    
    perf.start_turn()
    # Mock parameters for generate_response_stream
    # We only care about the metrics side-effect during prompt_build
    gen = llm.generate_response_stream("test prompt")
    # Prompt build happens inside the generator's initialization or first yield usually,
    # but in our LLMService, it's called right at the start of generate_response_stream.
    # Let's consume the start of the generator.
    try:
        next(gen)
    except StopIteration:
        pass
    except Exception:
        pass # Ollama might fail to connect, but prompt_build finished
        
    metrics = perf.current_turn
    print("\n[Metrics Keys]")
    print(metrics.keys())
    
    assert "segment_hashes" not in metrics, "Bug 3 still present: segment_hashes found in metrics!"
    assert "cache_report" in metrics, "cache_report SHOULD be in metrics"
    
    print("Phase 3 Fix Verification: segment_hashes removed from metrics.")

if __name__ == '__main__':
    verify_fix3()
