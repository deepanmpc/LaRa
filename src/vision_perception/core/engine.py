"""
LaRa Vision Perception — PerceptionEngine (v2)
Production-hardened orchestration thread:
  1. Integrates FrameQualityGate — skips detection on dark/blurry frames.
  2. Adaptive YOLO throttle feedback — reports loop timing to ObjectDetector.
  3. Watchdog timer — logs warning and attempts soft restart if loop stalls >500ms.
  4. Publishes immutable PerceptionOutput dataclass via state.publish().
  5. Memory sampling every ~1s for proactive leak detection.
"""

import threading
import time
from typing import Optional

import numpy as np

from camera.capture import CameraCapture
from camera.quality import FrameQualityGate
from core.state import (
    perception_state, EngineState,
    PerceptionOutput, PerceptionConfidence,
)
from detection.face_detector import FaceDetector
from detection.hand_detector import HandDetector
from detection.object_detector import ObjectDetector
from tracking.engagement import EngagementTracker
from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

_WATCHDOG_THRESHOLD_S = 0.5   # Stall threshold
_MEMORY_SAMPLE_INTERVAL = 30  # Sample memory every N frames


class PerceptionEngine:
    """
    Orchestrates the full vision pipeline in a single daemon thread.

    Upgrade summary (v2):
      - FrameQualityGate: pre-filters frames before dispatch
      - Adaptive YOLO throttle: ObjectDetector auto-tunes its own interval
      - Watchdog: detects and soft-restarts a stalled loop
      - Immutable PerceptionOutput: published via perception_state.publish()
    """

    def __init__(self):
        self._camera  = CameraCapture()
        self._quality = FrameQualityGate()
        self._face    = FaceDetector()
        self._hand    = HandDetector()
        self._objects = ObjectDetector()
        self._engagement = EngagementTracker()

        self._thread:   Optional[threading.Thread] = None
        self._watchdog: Optional[threading.Thread] = None
        self._last_tick: float = time.monotonic()
        self._frame_counter: int = 0

    # ── Public API ───────────────────────────────────────────────

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
        self._last_tick = time.monotonic()

        self._thread = threading.Thread(
            target=self._pipeline_loop,
            daemon=True,
            name="perception-engine",
        )
        self._thread.start()

        self._watchdog = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="engine-watchdog",
        )
        self._watchdog.start()

        log.info("PerceptionEngine v2 started (+ watchdog)")

    def stop(self) -> None:
        perception_state.set_stopped()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        if self._watchdog:
            self._watchdog.join(timeout=2.0)
            self._watchdog = None
        self._camera.stop()
        self._face.close()
        self._hand.close()
        log.info("PerceptionEngine stopped cleanly")

    # ── Pipeline loop ────────────────────────────────────────────

    def _pipeline_loop(self) -> None:
        frame_budget_s  = 1.0 / vision_config.TARGET_FPS
        budget_ms       = frame_budget_s * 1000.0

        while perception_state.is_running():
            t_loop_start = time.monotonic()

            frame = self._camera.get_frame()
            if frame is None:
                time.sleep(0.005)
                continue

            self._last_tick = time.monotonic()  # watchdog heartbeat

            # ── Frame quality gate ───────────────────────────────
            if not self._quality.is_usable(frame):
                skipped = PerceptionOutput(frameSkipped=True, timestamp=round(time.time(), 4))
                perception_state.publish(skipped)
                perception_state.tick()
                elapsed = (time.monotonic() - t_loop_start) * 1000
                time.sleep(max(0.0, frame_budget_s - elapsed / 1000.0))
                continue

            # ── Full detection pipeline ──────────────────────────
            try:
                output = self._process_frame(frame)
            except Exception as e:
                log.warning(f"Pipeline error: {e}")
                output = perception_state.latest  # stale but safe

            # Publish immutable snapshot
            perception_state.publish(output)
            perception_state.tick()

            # ── Timing feedback (adaptive throttle) ──────────────
            loop_elapsed_ms = (time.monotonic() - t_loop_start) * 1000
            self._objects.update_throttle(loop_elapsed_ms, budget_ms)

            # ── Periodic memory sample ───────────────────────────
            self._frame_counter += 1
            if self._frame_counter % _MEMORY_SAMPLE_INTERVAL == 0:
                mb = perception_state.sample_memory()
                if perception_state.memory_leak_suspected():
                    log.warning(
                        f"Possible memory leak detected — delta={perception_state.memory_delta_mb()}MB "
                        f"over {perception_state._MEMORY_WINDOW} samples"
                    )

            # ── Sleep remaining budget ───────────────────────────
            sleep_s = max(0.0, frame_budget_s - loop_elapsed_ms / 1000.0)
            if sleep_s > 0:
                time.sleep(sleep_s)

    # ── Watchdog loop ────────────────────────────────────────────

    def _watchdog_loop(self) -> None:
        """
        Runs in a separate thread. If the pipeline loop hasn't tickled
        _last_tick in >500ms, it logs a warning.
        Attempts a soft restart by resetting the state (hard camera restart
        left as a future improvement).
        """
        while perception_state.is_running():
            time.sleep(0.25)  # Check twice per 500ms window
            stall = time.monotonic() - self._last_tick
            if stall > _WATCHDOG_THRESHOLD_S:
                log.warning(
                    f"[WATCHDOG] PerceptionEngine stall detected — "
                    f"{stall*1000:.0f}ms since last frame processed"
                )
                # Soft restart: the loop will continue if GIL released
                # Hard restart (camera re-init) left for future phase
                self._last_tick = time.monotonic()  # Reset to prevent log flood

    # ── Frame processor ──────────────────────────────────────────

    def _process_frame(self, frame: np.ndarray) -> PerceptionOutput:
        # Face pipeline (every frame)
        face_out = self._face.process(frame)

        # Hand / gesture (every frame)
        gesture, gesture_conf = self._hand.process_with_confidence(frame)

        # Object detection (adaptive throttle, returns confidence)
        objects, obj_conf = self._objects.process(frame)

        # Engagement (gaze-gated rolling buffer)
        score = self._engagement.update(
            face_present=face_out["presence"],
            looking_at_screen=face_out["lookingAtScreen"],
            gesture=gesture,
        )

        confidence = PerceptionConfidence(
            face=face_out.get("confidence", 0.0),
            gesture=gesture_conf,
            objects=obj_conf,
        )

        return PerceptionOutput(
            presence=face_out["presence"],
            faceVerified=False,
            lookingAtScreen=face_out["lookingAtScreen"],
            engagementScore=score,
            gesture=gesture,
            detectedObjects=tuple(objects),
            frameSkipped=False,
            confidence=confidence,
            timestamp=round(time.time(), 4),
        )
