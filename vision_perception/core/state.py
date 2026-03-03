"""
LaRa Vision Perception — Shared State Container (v2)
Production-hardened:
  - Immutable PerceptionOutput dataclass (not raw dict).
  - Atomic swap via threading.Lock — no CPython GIL dependency.
  - Rolling memory tracker for leak detection.
  - Confidence sub-object included in every frame output.
"""

import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List
import psutil
import os


class EngineState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    ERROR   = "ERROR"


# ── Immutable output dataclass ───────────────────────────────────────────────

@dataclass(frozen=True)
class PerceptionConfidence:
    """Confidence scores for each detection sub-system [0.0–1.0]."""
    face: float = 0.0
    gesture: float = 0.0
    objects: float = 0.0


@dataclass(frozen=True)
class PerceptionOutput:
    """
    Immutable snapshot of one perception frame.
    Frozen dataclass prevents partial mutations on the object
    even if a reference escapes to another thread.
    """
    presence:        bool                = False
    faceVerified:    bool                = False
    lookingAtScreen: bool                = False
    engagementScore: float               = 0.0
    gesture:         str                 = "NONE"
    detectedObjects: tuple               = ()   # tuple, not list — immutable
    frameSkipped:    bool                = False
    confidence:      PerceptionConfidence = field(default_factory=PerceptionConfidence)
    timestamp:       float               = 0.0

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON responses."""
        d = asdict(self)
        # Convert tuple back to list for JSON compatibility
        d["detectedObjects"] = list(d["detectedObjects"])
        return d


_NULL_OUTPUT = PerceptionOutput(timestamp=0.0)


# ── Global service state  ────────────────────────────────────────────────────

class PerceptionState:
    """
    Module-level singleton.
    Writer (PerceptionEngine) swaps `_output` reference under a minimal lock.
    Reader (FastAPI route) acquires the same lock only to copy the reference —
    actual object access is lock-free because PerceptionOutput is frozen.
    """

    _MEMORY_WINDOW = 10   # samples to track for delta

    def __init__(self):
        self.engine_state: EngineState = EngineState.STOPPED
        self.error_message: str = ""

        # Perception output — protected by _swap_lock
        self._swap_lock = threading.Lock()
        self._output: PerceptionOutput = _NULL_OUTPUT

        # FPS tracking
        self._fps: float = 0.0
        self._frame_count: int = 0
        self._fps_window_start: float = time.time()

        # Memory monitoring
        self._proc = psutil.Process(os.getpid())
        self._memory_samples: list = []

    # ── Output swap (writer) ─────────────────────────────────────

    def publish(self, output: PerceptionOutput) -> None:
        """Atomically replace the latest output snapshot."""
        with self._swap_lock:
            self._output = output

    # ── Output read (readers) ────────────────────────────────────

    @property
    def latest(self) -> PerceptionOutput:
        with self._swap_lock:
            return self._output  # reference copy — object is frozen, safe to read

    # ── FPS helpers ──────────────────────────────────────────────

    def tick(self) -> None:
        self._frame_count += 1
        elapsed = time.time() - self._fps_window_start
        if elapsed >= 1.0:
            self._fps = round(self._frame_count / elapsed, 1)
            self._frame_count = 0
            self._fps_window_start = time.time()

    @property
    def fps(self) -> float:
        return self._fps

    # ── Memory monitoring ────────────────────────────────────────

    def sample_memory(self) -> float:
        """Record current RSS (MB) and return it."""
        mb = round(self._proc.memory_info().rss / 1_048_576, 1)
        self._memory_samples.append(mb)
        if len(self._memory_samples) > self._MEMORY_WINDOW:
            self._memory_samples.pop(0)
        return mb

    def memory_delta_mb(self) -> float:
        """
        Rolling memory growth (last sample − oldest sample in window).
        Positive = growing; negative = shrinking.
        """
        if len(self._memory_samples) < 2:
            return 0.0
        return round(self._memory_samples[-1] - self._memory_samples[0], 1)

    def memory_leak_suspected(self) -> bool:
        """Flag if RSS has been monotonically increasing across the entire window."""
        if len(self._memory_samples) < self._MEMORY_WINDOW:
            return False
        return all(
            self._memory_samples[i] < self._memory_samples[i + 1]
            for i in range(len(self._memory_samples) - 1)
        )

    # ── Convenience setters ──────────────────────────────────────

    def set_running(self) -> None:
        self.engine_state = EngineState.RUNNING
        self.error_message = ""

    def set_stopped(self) -> None:
        self.engine_state = EngineState.STOPPED

    def set_error(self, msg: str) -> None:
        self.engine_state = EngineState.ERROR
        self.error_message = msg

    def is_running(self) -> bool:
        return self.engine_state == EngineState.RUNNING


# Module-level singleton
perception_state = PerceptionState()
