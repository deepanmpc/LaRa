"""
LaRa Vision Perception — PerceptionEngine (v2.2)
v2.2 risk surface fixes:

  Fix 1 – Soft Restart Safety:
    On 3-stall restart, fully reinitialise detector instances
    (MediaPipe face, MediaPipe hands, YOLO session). Assumes partial
    CUDA/session corruption and treats model objects as disposable.

  Fix 2 – Quality Gate Stable State:
    If frame fails quality gate, publish last STABLE output
    (dataclasses.replace to update skip reason + timestamp) instead
    of a blank PerceptionOutput. Prevents dim-lighting from being
    misinterpreted as child absence.

  Fix 3 – Pessimistic systemConfidence:
    systemConfidence = min(face, pose, objects) — exposes the weakest
    link instead of averaging it out. Appropriate for safety-critical
    robotics. Hides nothing.

  Fix 4 – Dual Engagement Score:
    Passes (score, ui_score) from EngagementTracker into PerceptionOutput
    for both engagementScore and engagementScoreUI.

  Fix 5 – Peak Memory Session Tracking:
    Calls perception_state.record_session_peak() on every soft restart
    so the peak-climb detector accumulates data at restart boundaries.
"""

import concurrent.futures
import dataclasses
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

_WATCHDOG_STALL_S        = 0.5
_WATCHDOG_SOFT_RESTART_AT = 3
_WATCHDOG_ERROR_AT       = 5
_MEMORY_SAMPLE_INTERVAL  = 30


class PerceptionEngine:
    """
    Vision pipeline orchestrator (v2.2).
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
        self._executor  = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self._last_tick: float = time.monotonic()
        self._frame_counter: int = 0

        # Fix 2: last stable output for quality gate fallback
        self._last_stable: Optional[PerceptionOutput] = None

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
            target=self._watchdog_loop, daemon=True, name="engine-watchdog"
        )
        self._watchdog.start()
        log.info("PerceptionEngine v2.2 started")

    def stop(self) -> None:
        perception_state.set_stopped()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        if self._watchdog:
            self._watchdog.join(timeout=2.0)
            self._watchdog = None
        if hasattr(self, '_executor') and self._executor:
            self._executor.shutdown(wait=False)
        self._camera.stop()
        self._close_detectors()
        log.info("PerceptionEngine v2.2 stopped cleanly")

    def _spawn_pipeline_thread(self) -> None:
        self._thread = threading.Thread(
            target=self._pipeline_loop, daemon=True, name="perception-engine"
        )
        self._thread.start()

    # ── Fix 1: Full detector reinit (called by watchdog on soft restart) ──────

    def _reinit_detectors(self) -> None:
        """
        Fully destroy and recreate all MediaPipe and YOLO model instances.
        Required on soft restart — assumes session/CUDA context may be corrupted.
        """
        log.warning("Reinitialising all detector instances (full session reset)")
        try:
            self._face.close()
        except Exception as e:
            log.warning(f"Error closing FaceDetector: {e}")
        try:
            self._hand.close()
        except Exception as e:
            log.warning(f"Error closing HandDetector: {e}")

        self._face    = FaceDetector()
        self._hand    = HandDetector()
        self._objects = ObjectDetector()
        log.info("All detector instances reinitialised successfully")

    def _close_detectors(self) -> None:
        try:
            self._face.close()
        except Exception:
            pass
        try:
            self._hand.close()
        except Exception:
            pass

    # ── Watchdog (3-tier escalation + peak session recording) ────

    def _watchdog_loop(self) -> None:
        consecutive = 0
        while perception_state.is_running():
            time.sleep(0.25)
            stall_s = time.monotonic() - self._last_tick

            if stall_s <= _WATCHDOG_STALL_S:
                consecutive = 0
                continue

            consecutive += 1
            perception_state.stall_count += 1
            self._last_tick = time.monotonic()

            log.warning({
                "msg": "Watchdog stall",
                "stall_ms": round(stall_s * 1000),
                "consecutive": consecutive,
                "total_stalls": perception_state.stall_count,
            })

            if consecutive >= _WATCHDOG_ERROR_AT:
                log.error("Watchdog: 5 consecutive stalls — ENGINE ERROR")
                perception_state.set_error("Watchdog: 5 consecutive stalls")
                break

            if consecutive == _WATCHDOG_SOFT_RESTART_AT:
                log.warning("Watchdog: 3 stalls — full detector reinit + thread respawn")
                # Record session peak before restart — feeds peak-leak detector
                perception_state.record_session_peak()
                # Fix 1: fully reinitialise model sessions
                self._reinit_detectors()
                self._spawn_pipeline_thread()
                log.info("Watchdog: soft restart complete")

    # ── Pipeline loop ─────────────────────────────────────────────

    def _pipeline_loop(self) -> None:
        frame_budget_s = 1.0 / vision_config.TARGET_FPS
        budget_ms      = frame_budget_s * 1000.0

        while perception_state.is_running():
            t_loop_start = time.monotonic()

            # ── Frame acquisition ─────────────────────────────────
            frame = self._camera.get_frame()
            if frame is None:
                output = self._make_skip(camera_drop=True)
                perception_state.publish(output)
                time.sleep(0.005)
                continue

            self._last_tick = time.monotonic()

            # ── Fix 2: Quality gate — preserve stable state ───────
            if not self._quality.is_usable(frame):
                output = self._make_skip(quality=True)
                perception_state.publish(output)
                perception_state.tick()
                elapsed = (time.monotonic() - t_loop_start) * 1000
                time.sleep(max(0.0, frame_budget_s - elapsed / 1000.0))
                continue

            # ── Full detection pipeline ───────────────────────────
            try:
                output = self._process_frame(frame)
                self._last_stable = output          # update stable snapshot
            except Exception as e:
                log.warning(f"Pipeline error: {e}")
                output = perception_state.latest

            perception_state.publish(output)
            perception_state.tick()

            loop_ms = (time.monotonic() - t_loop_start) * 1000
            self._objects.update_throttle(loop_ms, budget_ms)

            self._frame_counter += 1
            if self._frame_counter % _MEMORY_SAMPLE_INTERVAL == 0:
                perception_state.sample_memory()
                if perception_state.memory_leak_suspected():
                    log.warning({
                        "msg": "Memory leak (slope)",
                        "slope_mb_s": perception_state.memory_growth_rate_mb_per_sec(),
                    })
                if perception_state.peak_leak_suspected():
                    log.warning({
                        "msg": "Memory leak (peak fragmentation)",
                        "peak_mb": perception_state.current_session_peak_mb,
                    })

            sleep_s = max(0.0, frame_budget_s - loop_ms / 1000.0)
            if sleep_s > 0:
                time.sleep(sleep_s)

    # ── Fix 2 helper: stable-state quality skip ───────────────────

    def _make_skip(
        self,
        quality: bool = False,
        throttle: bool = False,
        camera_drop: bool = False,
    ) -> PerceptionOutput:
        """
        Returns the last stable output with updated skip reason + timestamp.
        If no stable output exists yet, returns a null output.
        This ensures quality-gate skips don't zero-out presence or engagement.
        """
        skip_reason = PerceptionSkipReason(
            quality=quality, throttle=throttle, camera_drop=camera_drop
        )
        if self._last_stable is not None:
            # Clone last known-good frame; only override skip + timestamp
            return dataclasses.replace(
                self._last_stable,
                skipped=skip_reason,
                timestamp=round(time.time(), 4),
            )
        return PerceptionOutput(
            skipped=skip_reason,
            timestamp=round(time.time(), 4),
        )

    # ── Frame processing ──────────────────────────────────────────

    def _process_frame(self, frame: np.ndarray) -> PerceptionOutput:
        import cv2
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        future_face = self._executor.submit(self._face.process, rgb_frame)
        future_hand = self._executor.submit(self._hand.process_with_confidence, rgb_frame)
        
        face_out = future_face.result()
        gesture, gesture_conf = future_hand.result()
        
        objects, obj_conf = self._objects.process(frame) # YOLO works on BGR default

        # Fix 4: unpack dual-track engagement scores
        score, ui_score = self._engagement.update(
            face_present=face_out["presence"],
            looking_at_screen=face_out["lookingAtScreen"],
            gesture=gesture,
        )

        face_conf = face_out.get("confidence", 0.0)
        pose_conf = face_out.get("pose_confidence", 0.0)

        # Fix 3: pessimistic fusion — min exposes weakest sensor
        system_confidence = round(min(face_conf, pose_conf, obj_conf), 3)

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
            engagementScoreUI=ui_score,
            gesture=gesture,
            detectedObjects=tuple(objects),
            skipped=PerceptionSkipReason(),
            confidence=confidence,
            systemConfidence=system_confidence,
            timestamp=round(time.time(), 4),
        )
