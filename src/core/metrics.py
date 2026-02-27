"""
LaRa Metrics — Latency Tracking
Collects timing data for every stage of the pipeline.
Writes to lara_metrics.log in CSV format for easy analysis.

Usage:
    from metrics import Timer
    with Timer("STT"):
        text = model.transcribe(audio)
    # → Logs: 2026-02-27 10:00:00 | STT | 0.823s
"""

import time
import logging
import os
import csv
from contextlib import contextmanager
from collections import defaultdict
from typing import Optional

try:
    from src.core.config_loader import CONFIG
    _METRICS_LOG = "lara_metrics.log"
except Exception:
    _METRICS_LOG = "lara_metrics.log"

_METRICS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), _METRICS_LOG)


# ── In-memory summary ──────────────────────────────────────────────────────────
_timings: dict[str, list[float]] = defaultdict(list)


@contextmanager
def Timer(stage: str):
    """
    Context manager for timing a pipeline stage.
    
    Args:
        stage: Human-readable name e.g. "STT", "Mood", "LLM", "TTS"
    
    Example:
        with Timer("STT"):
            result = model.transcribe(audio)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        _timings[stage].append(elapsed)
        _log_timing(stage, elapsed)


def _log_timing(stage: str, elapsed_s: float):
    """Write a timing entry to the metrics log."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts},{stage},{elapsed_s:.4f}"
    try:
        with open(_METRICS_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    logging.debug(f"[Metrics] stage={stage} duration={elapsed_s:.3f}s")


def get_summary() -> dict[str, dict]:
    """
    Return a summary dict of all collected timings with avg, min, max, count.
    
    Returns:
        {
          "STT":  {"avg": 0.82, "min": 0.71, "max": 0.94, "count": 5},
          "LLM":  {"avg": 2.34, ...},
          ...
        }
    """
    summary = {}
    for stage, times in _timings.items():
        if times:
            summary[stage] = {
                "avg":   round(sum(times) / len(times), 3),
                "min":   round(min(times), 3),
                "max":   round(max(times), 3),
                "count": len(times),
            }
    return summary


def print_summary():
    """Print a human-readable timing summary to stdout."""
    summary = get_summary()
    if not summary:
        print("[Metrics] No timing data collected.")
        return
    print("\n── LaRa Latency Summary ──────────────────────")
    for stage, s in sorted(summary.items()):
        print(f"  {stage:<12} avg={s['avg']:.3f}s  min={s['min']:.3f}s  max={s['max']:.3f}s  ({s['count']} samples)")
    print("─────────────────────────────────────────────\n")
