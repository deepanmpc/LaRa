"""
LaRa Vision Perception — Camera Capture
Runs OpenCV cap in a dedicate daemon thread.
Provides get_frame() for PerceptionEngine with zero-copy.
"""

import threading
import time
from typing import Optional

import cv2
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class CameraCapture:
    """
    Thread-safe single-frame buffer fed by a background reader thread.
    The reader always tries to maintain TARGET_FPS; it drops frames rather
    than queuing them, keeping pipeline latency predictable.
    """

    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self._frame: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    # ── Public API ──────────────────────────────────────────────

    def start(self) -> None:
        if self._running:
            log.warning("CameraCapture already running — ignoring start()")
            return

        self._cap = cv2.VideoCapture(vision_config.CAMERA_INDEX)
        if not self._cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera at index {vision_config.CAMERA_INDEX}"
            )

        # Configure resolution
        w, h = vision_config.RESOLUTION
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self._cap.set(cv2.CAP_PROP_FPS, vision_config.TARGET_FPS)

        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True, name="cam-reader")
        self._thread.start()
        log.info({"msg": "Camera started", "resolution": vision_config.RESOLUTION, "fps": vision_config.TARGET_FPS})

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._cap:
            self._cap.release()
            self._cap = None
        with self._lock:
            self._frame = None
        log.info("Camera stopped and released")

    def get_frame(self) -> Optional[np.ndarray]:
        """Returns the latest captured frame or None if camera not ready."""
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def is_open(self) -> bool:
        return self._running and self._cap is not None and self._cap.isOpened()

    # ── Internal ────────────────────────────────────────────────

    def _reader_loop(self) -> None:
        frame_interval = 1.0 / vision_config.TARGET_FPS
        while self._running:
            t_start = time.monotonic()
            if self._cap is None or not self._cap.isOpened():
                break

            ret, frame = self._cap.read()
            if not ret:
                log.warning("Frame read failed — camera may have disconnected")
                time.sleep(0.05)
                continue

            with self._lock:
                self._frame = frame  # Replace, not queue

            # Sleep only remaining budget to hit target FPS
            elapsed = time.monotonic() - t_start
            sleep = max(0.0, frame_interval - elapsed)
            if sleep > 0:
                time.sleep(sleep)
