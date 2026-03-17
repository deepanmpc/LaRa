"""
LaRa Performance Monitor (Phase 0)
Tracks per-turn metrics: latency, token usage, and cache efficiency.
"""

import time
import logging
import os
import json
import numpy as np
from collections import defaultdict
from typing import Optional

from src.core.runtime_paths import get_log_path

_PERF_LOG = "lara_performance.jsonl"
_PERF_PATH = get_log_path(_PERF_LOG)

class PerformanceMonitor:
    """
    Tracks and logs performance metrics for therapy sessions.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PerformanceMonitor, cls).__new__(cls)
            cls._instance.current_turn = {}
            cls._instance.all_turns = []
            cls._instance._init_log()
        return cls._instance

    def _init_log(self):
        # Create empty log file if not exists
        if not os.path.exists(_PERF_PATH):
            with open(_PERF_PATH, "w") as f:
                pass

    def start_turn(self):
        """Called at start of a new interaction cycle."""
        self.current_turn = {
            "timestamp": time.time(),
            "prompt_build_time": 0.0,
            "inference_time": 0.0,
            "tts_time": 0.0,
            "total_latency": 0.0,
            "prompt_token_count": 0,
            "response_token_count": 0,
            "cache_hit_ratio": 0.0,
            "turn_start": time.time()
        }

    def log_metric(self, key: str, value: float):
        """Record a metric for the current turn."""
        if key in self.current_turn:
            self.current_turn[key] = value
        else:
            logging.warning(f"[PerfMonitor] Unknown metric key: {key}")

    def end_turn(self):
        """Finalize and save current turn metrics."""
        self.current_turn["total_latency"] = time.time() - self.current_turn.get("turn_start", 0)
        self.all_turns.append(self.current_turn.copy())
        
        # Write to JSONL for easy machine parsing
        try:
            with open(_PERF_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(self.all_turns[-1]) + "\n")
        except Exception as e:
            logging.error(f"[PerfMonitor] Failed to write log: {e}")
        
        logging.info(f"[PerfMonitor] Turn complete. Latency: {self.current_turn['total_latency']:.3f}s")

    def get_statistics(self):
        """Calculate p50, p90, max latency."""
        if not self.all_turns:
            return None
        
        latencies = [t["total_latency"] for t in self.all_turns]
        return {
            "p50": float(np.percentile(latencies, 50)),
            "p90": float(np.percentile(latencies, 90)),
            "max": float(np.max(latencies)),
            "count": len(latencies)
        }

    def print_baseline(self):
        """Print the Phase 0 baseline as requested."""
        stats = self.get_statistics()
        if not stats:
            print("[PerfMonitor] No baseline data recorded yet.")
            return

        print("\n" + "="*40)
        print("PHASE 0 — PERFORMANCE BASELINE")
        print("="*40)
        print(f"p50 Latency: {stats['p50']:.3f}s")
        print(f"p90 Latency: {stats['p90']:.3f}s")
        print(f"Max Latency: {stats['max']:.3f}s")
        print(f"Total Turns: {stats['count']}")
        print("="*40 + "\n")

# Convenience singleton access
monitor = PerformanceMonitor()
