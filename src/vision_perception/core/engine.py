"""
LaRa Vision Perception — PerceptionEngine (v2.1)
v2.1 upgrade: Watchdog escalation policy.
  - 1 stall (>500ms)    → log WARNING
  - 3 consecutive stalls → soft restart pipeline loop (new thread)
  - 5 consecutive stalls → set state = ERROR, stop engine

Also:
  - PerceptionSkipReason used for accurate skip classification.
  - systemConfidence computed as weighted mean per config weights.
  - pose_confidence routed into PerceptionConfidence.pose.
"""

import threading
import time
from typing import Optional

import numpy as np

from camera.capture import CameraCapture
from camera.quality import FrameQualityGate
from core.state import (
    perception_state, EngineState,
    PerceptionOutput, PerceptionConfidence, PerceptionSkipReason,
)
from detection.face_detector import FaceDetector
from detection.hand_detector import HandDetector
from detection.object_detector import ObjectDetector
from tracking.engagement import EngagementTracker
from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

_WATCHDOG_STALL_S = 0.5          # Stall threshold
_WATCHDOG_SOFT_RESTART_AT = 3    # Consecutive stalls before soft restart
_WATCHDOG_ERROR_AT = 5           # Consecutive stalls before ERROR state
_MEMORY_SAMPLE_INTERVAL = 30     # Frames between memory samples


class PerceptionEngine:
    """
    Orchestrates the vision pipeline in a daemon thread.
    v2.1: 3-tier watchdog escalation + accurate skip classification
          + systemConfidence weighted aggregation.
    """

    def __init__(self):
        self._camera    = CameraCapture()
        self._quality   = FrameQualityGate()
        self._face      = FaceDetector()
        self._hand      = HandDetector()
        self._objects   = ObjectDetector()
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
            raise

        perception_state.set_running()
        self._last_tick = time.monotonic()
        self._spawn_pipeline_thread()
        self._watchdog = threading.Thread(
            target=self._watchdog_loop,
            daemon=True,
            name="engine-watchdog",
        )
        self._watchdog.start()
        log.info("PerceptionEngine v2.1 started")

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
        log.info("PerceptionEngine v2.1 stopped cleanly")

    def _spawn_pipeline_thread(self) -> None:
        self._thread = threading.Thread(
            target=self._pipeline_loop,
            daemon=True,
            name="perception-engine",
        )
        self._thread.start()

    # ── Watchdog (3-tier escalation) ─────────────────────────────

    def _watchdog_loop(self) -> None:
        """
        Escalation policy:
          1 stall  → WARNING log
          3 stalls → soft restart (spawn new pipeline thread)
          5 stalls → ENGINE ERROR state
        """
        consecutive = 0
        while perception_state.is_running():
            time.sleep(0.25)
            stall_s = time.monotonic() - self._last_tick

            if stall_s <= _WATCHDOG_STALL_S:
                consecutive = 0
                continue

            consecutive += 1
            perception_state.stall_count += 1
            self._last_tick = time.monotonic()  # reset to avoid log flood

            log.warning({
                "msg": "Watchdog stall detected",
                "stall_ms": round(stall_s * 1000),
                "consecutive": consecutive,
                "stall_count_total": perception_state.stall_count,
            })

            if consecutive >= _WATCHDOG_ERROR_AT:
                log.error("Watchdog: 5 consecutive stalls — setting ENGINE ERROR")
                perception_state.set_error("Watchdog: pipeline stalled 5 consecutive times")
                break

            if consecutive == _WATCHDOG_SOFT_RESTART_AT:
                log.warning("Watchdog: 3 consecutive stalls — attempting soft restart")
                if self._thread and self._thread.is_alive():
                    # Cannot kill the thread directly — mark state and respawn
                    # Old thread will exit on its next is_running() check
                    pass
                self._spawn_pipeline_thread()
                log.info("Watchdog: new pipeline thread spawned")

    # ── Pipeline loop ────────────────────────────────────────────

    def _pipeline_loop(self) -> None:
        frame_budget_s = 1.0 / vision_config.TARGET_FPS
        budget_ms      = frame_budget_s * 1000.0

        while perception_state.is_running():
            t_loop_start = time.monotonic()

            # ── Frame acquisition ────────────────────────────────
            frame = self._camera.get_frame()
            if frame is None:
                skipped = PerceptionOutput(
                    skipped=PerceptionSkipReason(camera_drop=True),
                    timestamp=round(time.time(), 4),
                )
                perception_state.publish(skipped)
                time.sleep(0.005)
                continue

            self._last_tick = time.monotonic()

            # ── Frame quality gate ───────────────────────────────
            if not self._quality.is_usable(frame):
                skipped = PerceptionOutput(
                    skipped=PerceptionSkipReason(quality=True),
                    timestamp=round(time.time(), 4),
                )
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
                output = perception_state.latest

            perception_state.publish(output)
            perception_state.tick()

            # ── Timing feedback to adaptive throttle ─────────────
            loop_ms = (time.monotonic() - t_loop_start) * 1000
            self._objects.update_throttle(loop_ms, budget_ms)

            # ── Periodic memory sampling ──────────────────────────
            self._frame_counter += 1
            if self._frame_counter % _MEMORY_SAMPLE_INTERVAL == 0:
                perception_state.sample_memory()
                if perception_state.memory_leak_suspected():
                    log.warning({
                        "msg": "Memory leak suspected",
                        "slope_mb_s": perception_state.memory_growth_rate_mb_per_sec(),
                        "delta_mb": perception_state.memory_delta_mb(),
                    })

            # ── Sleep to maintain FPS ─────────────────────────────
            sleep_s = max(0.0, frame_budget_s - loop_ms / 1000.0)
            if sleep_s > 0:
                time.sleep(sleep_s)

    # ── Frame processing ─────────────────────────────────────────

    def _process_frame(self, frame: np.ndarray) -> PerceptionOutput:
        face_out = self._face.process(frame)
        gesture, gesture_conf = self._hand.process_with_confidence(frame)
        objects, obj_conf = self._objects.process(frame)

        score = self._engagement.update(
            face_present=face_out["presence"],
            looking_at_screen=face_out["lookingAtScreen"],
            gesture=gesture,
        )

        face_conf = face_out.get("confidence", 0.0)
        pose_conf = face_out.get("pose_confidence", 0.0)

        # ── System confidence (weighted mean of key sub-confidences)
        system_confidence = round(
            vision_config.SYSTEM_CONF_W_FACE    * face_conf
            + vision_config.SYSTEM_CONF_W_POSE  * pose_conf
            + vision_config.SYSTEM_CONF_W_OBJECTS * obj_conf,
            3,
        )

        confidence = PerceptionConfidence(
            face=face_conf,
            gesture=gesture_conf,
            objects=obj_conf,
            pose=pose_conf,
        )

        return PerceptionOutput(
            presence=face_out["presence"],
            faceVerified=False,
            lookingAtScreen=face_out["lookingAtScreen"],
            engagementScore=score,
            gesture=gesture,
            detectedObjects=tuple(objects),
            skipped=PerceptionSkipReason(),   # all False — full frame
            confidence=confidence,
            systemConfidence=system_confidence,
            timestamp=round(time.time(), 4),
        )
