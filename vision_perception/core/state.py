"""
LaRa Vision Perception — Shared State Container
Thread-safe enough for single-writer, multiple-reader pattern.
"""

import time
from enum import Enum
from typing import Any


class EngineState(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    ERROR   = "ERROR"


class PerceptionState:
    """
    Singleton-style shared state.
    The PerceptionEngine writes; FastAPI routes read.
    Reads are atomic dict lookups — no locking needed.
    """

    def __init__(self):
        self.engine_state: EngineState = EngineState.STOPPED
        self.error_message: str = ""
        self._fps: float = 0.0
        self._frame_count: int = 0
        self._fps_window_start: float = time.time()

        # The perception output dict — overwritten each frame
        self.latest: dict[str, Any] = {
            "presence": False,
            "faceVerified": False,
            "lookingAtScreen": False,
            "engagementScore": 0.0,
            "gesture": "NONE",
            "detectedObjects": [],
            "timestamp": 0.0,
        }

    # ── FPS helpers ─────────────────────────────────────────────

    def tick(self) -> None:
        """Call once per processed frame to update FPS counter."""
        self._frame_count += 1
        elapsed = time.time() - self._fps_window_start
        if elapsed >= 1.0:
            self._fps = round(self._frame_count / elapsed, 1)
            self._frame_count = 0
            self._fps_window_start = time.time()

    @property
    def fps(self) -> float:
        return self._fps

    # ── Convenience writers ─────────────────────────────────────

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


# Module-level singleton shared across all imports
perception_state = PerceptionState()
