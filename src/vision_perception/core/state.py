"""
LaRa Vision Perception — Shared State Container (v2.1)
Upgrades over v2.0:
  - PerceptionSkipReason replaces simple bool frameSkipped.
  - PerceptionConfidence gains pose field.
  - PerceptionOutput gains systemConfidence field.
  - Memory tracker upgraded to slope-based leak detection (20-sample window).
  - Watchdog stall_count exposed for /status.
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


# ── Skip reason sub-object ───────────────────────────────────────────────────

@dataclass(frozen=True)
class PerceptionSkipReason:
    """
    Granular skip classification.
    Exactly one of these should be True on a skipped frame,
    or all False on a full detection frame.
    """
    quality:     bool = False   # Failed brightness/sharpness gate
    throttle:    bool = False   # Skipped by YOLO throttle logic
    camera_drop: bool = False   # get_frame() returned None


# ── Confidence sub-object ────────────────────────────────────────────────────

@dataclass(frozen=True)
class PerceptionConfidence:
    """Detection confidence scores [0.0–1.0] per sub-system."""
    face:    float = 0.0
    gesture: float = 0.0
    objects: float = 0.0
    pose:    float = 0.0   # ← NEW: solvePnP reprojection quality score


# ── Immutable output dataclass ───────────────────────────────────────────────

@dataclass(frozen=True)
class PerceptionOutput:
    """
    Immutable snapshot of one perception frame (v2.1 schema).
    Frozen → no partial mutations from any thread holding a reference.
    """
    presence:          bool                  = False
    faceVerified:      bool                  = False
    lookingAtScreen:   bool                  = False
    engagementScore:   float                 = 0.0
    gesture:           str                   = "NONE"
    detectedObjects:   tuple                 = ()
    skipped:           PerceptionSkipReason  = field(default_factory=PerceptionSkipReason)
    confidence:        PerceptionConfidence  = field(default_factory=PerceptionConfidence)
    systemConfidence:  float                 = 0.0  # ← NEW: composite meta-score
    timestamp:         float                 = 0.0

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON responses."""
        d = asdict(self)
        d["detectedObjects"] = list(d["detectedObjects"])
        return d


_NULL_OUTPUT = PerceptionOutput(timestamp=0.0)


# ── Global service state  ────────────────────────────────────────────────────

class PerceptionState:
    """
    Module-level singleton. Thread-safe via a single _swap_lock for output.
    Watchdog state and memory stats are written only by their dedicated threads.
    """

    _MEMORY_WINDOW       = 20   # v2.1: wider slope window
    _SLOPE_WINDOW_S      = 5.0  # seconds per slope calculation interval
    _CONSECUTIVE_NEEDED  = 3    # consecutive high-slope windows to flag leak

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

        # Memory monitoring (v2.1: slope-based)
        self._proc = psutil.Process(os.getpid())
        self._memory_samples: list = []          # (timestamp, rss_mb) tuples
        self._memory_slope_mb_s: float = 0.0
        self._high_slope_streak: int = 0
        self._memory_leak_suspected: bool = False

        # Watchdog stall tracker
        self.stall_count: int = 0

    # ── Output swap (writer) ─────────────────────────────────────

    def publish(self, output: PerceptionOutput) -> None:
        """Atomically replace the latest output snapshot."""
        with self._swap_lock:
            self._output = output

    # ── Output read (readers) ────────────────────────────────────

    @property
    def latest(self) -> PerceptionOutput:
        with self._swap_lock:
            return self._output

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

    # ── Memory monitoring (v2.1 slope-based) ─────────────────────

    def sample_memory(self) -> float:
        """Record timestamped RSS sample; update slope & leak flag. Returns RSS MB."""
        mb = round(self._proc.memory_info().rss / 1_048_576, 1)
        now = time.time()
        self._memory_samples.append((now, mb))
        if len(self._memory_samples) > self._MEMORY_WINDOW:
            self._memory_samples.pop(0)
        self._update_slope()
        return mb

    def _update_slope(self) -> None:
        """Compute MB/sec slope from oldest→newest sample pair."""
        from config import vision_config
        if len(self._memory_samples) < 2:
            return
        t0, m0 = self._memory_samples[0]
        t1, m1 = self._memory_samples[-1]
        dt = t1 - t0
        if dt < 0.1:
            return
        slope = (m1 - m0) / dt
        self._memory_slope_mb_s = round(slope, 4)

        if slope > vision_config.MEMORY_SLOPE_THRESHOLD_MB_S:
            self._high_slope_streak += 1
        else:
            self._high_slope_streak = 0

        self._memory_leak_suspected = (
            self._high_slope_streak >= vision_config.MEMORY_CONSECUTIVE_WINDOWS
        )

    @property
    def memory_mb(self) -> float:
        if not self._memory_samples:
            return 0.0
        return self._memory_samples[-1][1]

    def memory_delta_mb(self) -> float:
        if len(self._memory_samples) < 2:
            return 0.0
        return round(self._memory_samples[-1][1] - self._memory_samples[0][1], 1)

    def memory_growth_rate_mb_per_sec(self) -> float:
        return self._memory_slope_mb_s

    def memory_leak_suspected(self) -> bool:
        return self._memory_leak_suspected

    # ── Convenience setters ──────────────────────────────────────

    def set_running(self) -> None:
        self.engine_state = EngineState.RUNNING
        self.error_message = ""
        self.stall_count = 0

    def set_stopped(self) -> None:
        self.engine_state = EngineState.STOPPED

    def set_error(self, msg: str) -> None:
        self.engine_state = EngineState.ERROR
        self.error_message = msg

    def is_running(self) -> bool:
        return self.engine_state == EngineState.RUNNING


# Module-level singleton
perception_state = PerceptionState()
