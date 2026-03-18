"""
LaRa Performance Monitor
Establishes latency baseline and tracks cognitive pipeline performance.
"""

import time
import logging
import os
import json
from collections import deque
from statistics import median

from src.core.config_loader import CONFIG
from src.core.runtime_paths import get_metrics_log_path

class PerformanceMonitor:
    _instance = None

    def __init__(self):
        if PerformanceMonitor._instance is not None:
            raise RuntimeError("PerformanceMonitor is a singleton. Use PerformanceMonitor.get()")
        
        self.rolling_window = getattr(getattr(CONFIG, 'cognitive_pipeline', None), 'perf_rolling_window', 100)
        self.metrics_log_path = get_metrics_log_path()
        
        # In-memory per-turn data
        self.current_turn = {}
        
        # Deques for rolling calculation
        self.history_prompt_build = deque(maxlen=self.rolling_window)
        self.history_inference_time = deque(maxlen=self.rolling_window)
        self.history_tts_time = deque(maxlen=self.rolling_window)
        self.history_total_latency = deque(maxlen=self.rolling_window)
        self.turn_count = 0
        
        PerformanceMonitor._instance = self

    @staticmethod
    def get():
        if PerformanceMonitor._instance is None:
            PerformanceMonitor()
        return PerformanceMonitor._instance

    def start_turn(self):
        self.turn_count += 1
        self.current_turn = {
            "turn_start": time.perf_counter(),
            "prompt_build_time_ms": 0,
            "inference_time_ms": 0,
            "tts_time_ms": 0,
            "total_latency_ms": 0,
            "token_count_prompt": 0,
            "token_count_response": 0,
            "cache_report": {}
        }

    def start_timer(self, stage: str):
        self.current_turn[f"{stage}_start"] = time.perf_counter()

    def end_timer(self, stage: str):
        start_time = self.current_turn.get(f"{stage}_start")
        if start_time:
            self.current_turn[f"{stage}_ms"] = int((time.perf_counter() - start_time) * 1000)

    def set_metric(self, key: str, value):
        self.current_turn[key] = value

    def end_turn(self):
        # Calculate total latency
        turn_start = self.current_turn.get("turn_start")
        if turn_start:
            self.current_turn["total_latency_ms"] = int((time.perf_counter() - turn_start) * 1000)
            
        # Append to rolling history
        self.history_prompt_build.append(self.current_turn.get("prompt_build_time_ms", 0))
        self.history_inference_time.append(self.current_turn.get("inference_time_ms", 0))
        self.history_tts_time.append(self.current_turn.get("tts_time_ms", 0))
        self.history_total_latency.append(self.current_turn.get("total_latency_ms", 0))

        # Log formatted metrics
        turn_id = self.turn_count
        prompt = self.current_turn.get("prompt_build_time_ms", 0)
        inference = self.current_turn.get("inference_time_ms", 0)
        tts = self.current_turn.get("tts_time_ms", 0)
        total = self.current_turn.get("total_latency_ms", 0)
        
        tokens_p = self.current_turn.get("token_count_prompt", 0)
        tokens_r = self.current_turn.get("token_count_response", 0)
        
        cache = self.current_turn.get("cache_report", {})
        hits = [k for k, v in cache.items() if v == 'HIT']
        misses = [k for k, v in cache.items() if v == 'MISS']
        
        hit_str = ','.join(hits) if hits else 'none'
        miss_str = ','.join(misses) if misses else 'none'

        log_lines = [
            f"[Perf] turn={turn_id} prompt_build={prompt}ms inference={inference}ms tts={tts}ms total={total}ms",
            f"[Perf] tokens prompt={tokens_p} response={tokens_r}",
            f"[Perf] cache_hits={hit_str} miss={miss_str}"
        ]

        # Use root logger to ensure formatting matches the app
        for line in log_lines:
            logging.info(line)
            
        # Write to metrics log file directly
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.metrics_log_path, "a", encoding="utf-8") as f:
                for line in log_lines:
                    f.write(f"{ts} | INFO  | {line}\n")
        except Exception as e:
            logging.error(f"[PerfMonitor] Failed to write metrics: {e}")

    def _percentile(self, data: list, p: int) -> int:
        if not data:
            return 0
        sorted_data = sorted(data)
        idx = int((len(sorted_data) - 1) * p / 100.0)
        return sorted_data[idx]

    def log_session_summary(self):
        """Called upon session end to flush final percentiles."""
        if not self.history_total_latency:
            return
            
        stats = []
        for name, data in [
            ("prompt_build", list(self.history_prompt_build)),
            ("inference", list(self.history_inference_time)),
            ("tts", list(self.history_tts_time)),
            ("total", list(self.history_total_latency))
        ]:
            if not data:
                continue
            p50 = self._percentile(data, 50)
            p90 = self._percentile(data, 90)
            p99 = self._percentile(data, 99)
            stats.append(f"{name}: p50={p50}ms p90={p90}ms p99={p99}ms")
            
        summary_line = "[Perf] End of Session Summary | " + " | ".join(stats)
        logging.info(summary_line)
        
        try:
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.metrics_log_path, "a", encoding="utf-8") as f:
                f.write(f"{ts} | INFO  | {summary_line}\n")
        except Exception as e:
            logging.error(f"[PerfMonitor] Failed to write final metrics: {e}")
