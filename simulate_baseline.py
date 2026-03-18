import sys
import os
import time

# Ensure imports work
_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

import src.core.runtime_paths as rp
rp.initialize()

from src.core.PerformanceMonitor import PerformanceMonitor

# Mock out agentric loop
perf = PerformanceMonitor.get()

for i in range(20):
    perf.start_turn()
    
    # Simulate Prompt Build
    perf.start_timer("prompt_build")
    time.sleep(0.01) # 10ms build time
    perf.end_timer("prompt_build")
    
    # Set hashes simulating Phase 1 preview
    perf.set_metric("segment_hashes", {"system_block": "abc", "history_block": f"def{i}"})
    perf.set_metric("cache_report", {"system_block": "HIT", "history_block": "MISS"})
    
    # Simulate Inference
    perf.start_timer("inference")
    time.sleep(0.3) # 300ms inference
    perf.end_timer("inference")
    
    perf.set_metric("token_count_prompt", 350 + i)
    perf.set_metric("token_count_response", 45 + i%5)
    
    # Simulate TTS
    perf.start_timer("tts")
    time.sleep(0.05)
    perf.end_timer("tts")
    
    perf.end_turn()

perf.log_session_summary()
print("Baseline generated.")
