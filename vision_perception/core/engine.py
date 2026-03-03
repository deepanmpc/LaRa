"""
LaRa Vision Perception — PerceptionEngine
Main orchestration thread. Pulls frames, dispatches detectors according to
throttle counters, merges outputs, and writes to PerceptionState.latest.
"""

import threading
import time
from typing import Optional

import numpy as np

from camera.capture import CameraCapture
from core.state import perception_state, EngineState
from detection.face_detector import FaceDetector
from detection.hand_detector import HandDetector
from detection.object_detector import ObjectDetector
from tracking.engagement import EngagementTracker
from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class PerceptionEngine:
    """
    Orchestrates the perception pipeline in a single daemon thread.

    Throttle rules (all configurable via vision_config):
      - FaceDetector   → every frame
      - HandDetector   → every frame
      - ObjectDetector → every YOLO_INTERVAL frames (internal counter)
      - EngagementTracker → every frame (O(1) buffer update)
    """

    def __init__(self):
        self._camera = CameraCapture()
        self._face = FaceDetector()
        self._hand = HandDetector()
        self._objects = ObjectDetector()
        self._engagement = EngagementTracker()
        self._thread: Optional[threading.Thread] = None

    # ── Public API ──────────────────────────────────────────────

    def start(self) -> None:
        if perception_state.is_running():
            log.warning("PerceptionEngine.start() called while already RUNNING")
            return

        try:
            self._camera.start()
        except RuntimeError as e:
            perception_state.set_error(str(e))
            log.error(f"Camera failed to start: {e}")
            raise

        perception_state.set_running()
        self._thread = threading.Thread(
            target=self._pipeline_loop,
            daemon=True,
            name="perception-engine",
        )
        self._thread.start()
        log.info("PerceptionEngine started")

    def stop(self) -> None:
        perception_state.set_stopped()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        self._camera.stop()
        self._face.close()
        self._hand.close()
        log.info("PerceptionEngine stopped cleanly")

    # ── Pipeline loop ───────────────────────────────────────────

    def _pipeline_loop(self) -> None:
        frame_budget = 1.0 / vision_config.TARGET_FPS

        while perception_state.is_running():
            t_start = time.monotonic()

            frame = self._camera.get_frame()
            if frame is None:
                time.sleep(0.005)
                continue

            try:
                output = self._process_frame(frame)
            except Exception as e:
                log.warning(f"Pipeline error on frame: {e}")
                output = perception_state.latest  # keep stale output

            # Atomic dict replacement — CPython GIL makes this safe for readers
            perception_state.latest = output
            perception_state.tick()

            # Maintain target FPS budget
            elapsed = time.monotonic() - t_start
            sleep = max(0.0, frame_budget - elapsed)
            if sleep > 0:
                time.sleep(sleep)

    def _process_frame(self, frame: np.ndarray) -> dict:
        # Face pipeline (every frame)
        face_out = self._face.process(frame)

        # Hand / gesture pipeline (every frame)
        gesture = self._hand.process(frame)

        # Object detection (throttled internally)
        objects = self._objects.process(frame)

        # Engagement score (rolling buffer)
        score = self._engagement.update(
            face_present=face_out["presence"],
            looking_at_screen=face_out["lookingAtScreen"],
            gesture=gesture,
        )

        return {
            "presence": face_out["presence"],
            "faceVerified": False,   # Reserved for InsightFace embedding step
            "lookingAtScreen": face_out["lookingAtScreen"],
            "engagementScore": score,
            "gesture": gesture,
            "detectedObjects": objects,
            "timestamp": round(time.time(), 4),
        }
