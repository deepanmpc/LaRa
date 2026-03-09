"""
LaRa Vision Perception — Shared State Container (v2.3)
v2.3 fixes over v2.2:

  Fix 1 – peak_leak_suspected off-by-one:
    Original: range(len - 3, len - 1) compares indices [n-3, n-2] only,
    silently ignoring the most recent peak at index [n-1]. This means a
    3-peak climbing sequence like [100, 200, 300] would only compare
    (100, 200) and report False because index 2 (300) was excluded.
    Fix: compare the last 3 entries as a slice [-3:] directly.

  Fix 2 – engagementScoreUI in PerceptionOutput:
    Retained from v2.2 — no change needed.

  Fix 3 – stall_count not thread-safe:
    stall_count was written from the watchdog thread and read from the
    FastAPI handler without a lock. Replaced with threading.atomic-style
    increment via a dedicated lock. The value is still an int for JSON
    serialisation simplicity.

  Fix 4 – memory_delta_mb uses absolute delta (not signed):
    The original returned a signed delta which could be negative (meaning
    memory was freed). The dashboard interprets negative as "no growth"
    which is fine, but the /status endpoint should expose both a signed
    delta (for raw truth) and an absolute peak-relative figure. Kept signed
    for now; documented explicitly so callers are not surprised.
"""

import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
import psutil
import os


class EngineState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    ERROR   = "ERROR"


# ── Skip reason sub-object ───────────────────────────────────────────────────

@dataclass(frozen=True)
class PerceptionSkipReason:
    """Granular skip classification — exactly one flag is True on a skip frame."""
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
    pose:    float = 0.0


# ── Immutable output dataclass ───────────────────────────────────────────────

@dataclass(frozen=True)
class PerceptionOutput:
    """
    Immutable snapshot of one perception frame (v2.3 schema).

    engagementScore   — fast-decay internal signal (raw truth)
    engagementScoreUI — slow-decay, smoothed for human-facing dashboard
    """
    presence:           bool                  = False
    faceVerified:       bool                  = False
    lookingAtScreen:    bool                  = False
    engagementScore:    float                 = 0.0
    engagementScoreUI:  float                 = 0.0
    gesture:            str                   = "NONE"
    detectedObjects:    tuple                 = ()
    skipped:            PerceptionSkipReason  = field(default_factory=PerceptionSkipReason)
    confidence:         PerceptionConfidence  = field(default_factory=PerceptionConfidence)
    systemConfidence:   float                 = 0.0
    timestamp:          float                 = 0.0

    def to_dict(self) -> dict:
        """Serialise to a plain dict for JSON responses."""
        d = asdict(self)
        d["detectedObjects"] = list(d["detectedObjects"])
        return d


_NULL_OUTPUT = PerceptionOutput(timestamp=0.0)


# ── Global service state  ────────────────────────────────────────────────────

class PerceptionState:
    """
    Module-level singleton.
    Writer (PerceptionEngine) swaps _output reference under a minimal lock.
    Reader (FastAPI) acquires the same lock only to copy the reference.
    """

    _MEMORY_WINDOW       = 20
    _CONSECUTIVE_NEEDED  = 3

    def __init__(self):
        self.engine_state: EngineState = EngineState.STOPPED
        self.error_message: str = ""

        self._swap_lock     = threading.Lock()
        self._stall_lock    = threading.Lock()   # FIX 3: dedicated stall counter lock
        self._output: PerceptionOutput = _NULL_OUTPUT

        # FPS
        self._fps: float = 0.0
        self._frame_count: int = 0
        self._fps_window_start: float = time.time()

        # Memory monitoring
        self._proc = psutil.Process(os.getpid())
        self._memory_samples: list = []          # (timestamp, rss_mb)
        self._memory_slope_mb_s: float = 0.0
        self._high_slope_streak: int = 0
        self._memory_leak_suspected: bool = False

        # Peak memory tracking — catches fragmentation across restarts
        self._current_session_peak_mb: float = 0.0
        self._session_peaks: list = []

        # FIX 3: stall counter with lock
        self._stall_count: int = 0

    # ── Stall counter (FIX 3: thread-safe) ──────────────────────

    @property
    def stall_count(self) -> int:
        with self._stall_lock:
            return self._stall_count

    @stall_count.setter
    def stall_count(self, value: int) -> None:
        with self._stall_lock:
            self._stall_count = value

    def increment_stall(self) -> int:
        """Atomically increment stall count and return new value."""
        with self._stall_lock:
            self._stall_count += 1
            return self._stall_count

    # ── Output swap (writer) ─────────────────────────────────────

    def publish(self, output: PerceptionOutput) -> None:
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

    # ── Memory monitoring ─────────────────────────────────────────

    def sample_memory(self) -> float:
        """Record timestamped RSS sample. Returns current RSS MB."""
        mb = round(self._proc.memory_info().rss / 1_048_576, 1)
        now = time.time()
        self._memory_samples.append((now, mb))
        if len(self._memory_samples) > self._MEMORY_WINDOW:
            self._memory_samples.pop(0)

        # Peak tracking
        if mb > self._current_session_peak_mb:
            self._current_session_peak_mb = mb

        self._update_slope()
        return mb

    def record_session_peak(self) -> None:
        """
        Record the current session peak and reset for next window.
        Called by watchdog on each soft restart.
        """
        self._session_peaks.append(self._current_session_peak_mb)
        self._current_session_peak_mb = 0.0

    def peak_leak_suspected(self) -> bool:
        """
        Returns True if the last 3 session peaks are strictly increasing.

        FIX 1: Use [-3:] slice directly instead of range(len-3, len-1)
        which previously excluded the most recent peak.
        """
        if len(self._session_peaks) < 3:
            return False
        # Correct: compare the last 3 entries as a contiguous window
        last_three = self._session_peaks[-3:]
        return all(
            last_three[i] < last_three[i + 1]
            for i in range(len(last_three) - 1)
        )

    @property
    def current_session_peak_mb(self) -> float:
        return self._current_session_peak_mb

    def _update_slope(self) -> None:
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
        return self._memory_samples[-1][1] if self._memory_samples else 0.0

    def memory_delta_mb(self) -> float:
        """
        Signed delta (current - oldest sample in window).
        Positive = memory growing, negative = memory was freed.
        """
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
        self.stall_count = 0      # Uses the thread-safe setter

    def set_stopped(self) -> None:
        self.engine_state = EngineState.STOPPED

    def set_error(self, msg: str) -> None:
        self.engine_state = EngineState.ERROR
        self.error_message = msg

    def is_running(self) -> bool:
        return self.engine_state == EngineState.RUNNING


# Module-level singleton
perception_state = PerceptionState()