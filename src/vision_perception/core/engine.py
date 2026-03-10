"""
LaRa Vision Perception — PerceptionEngine (v2.3)
v2.3 fixes over v2.2:

  Fix 1 – BGR frame passed to YOLO (not RGB):
    Original code converted frame to RGB at the top of _process_frame,
    then passed `frame` (BGR) to ObjectDetector with the comment "YOLO works
    on BGR default". However, the RGB conversion was stored in `rgb_frame`
    while the original `frame` variable was still BGR — this was actually
    correct in v2.2. But this implicit contract is fragile and undocumented.
    v2.3 makes it explicit: `bgr_frame` is kept separately from `rgb_frame`
    and each detector receives exactly what it expects with clear naming.

  Fix 2 – stall_count increment now uses thread-safe increment_stall():
    `perception_state.stall_count += 1` is a read-modify-write that is NOT
    atomic on the original int attribute. Two watchdog ticks arriving close
    together could both read stale value and both write the same incremented
    value. Now uses perception_state.increment_stall() which holds the lock
    for the full operation.

  Fix 3 – Quality gate stable-state comment clarified:
    The _make_skip logic was correct in v2.2 but the inline comments were
    misleading ("Fix 2 helper" numbered out of context). Renamed and documented
    clearly for maintainability.

  Fix 4 – Soft restart resets _last_stable to None:
    After a soft restart, the stale _last_stable from the crashed session
    should not be served — the first frames after reinit should go through
    the full pipeline to establish a fresh baseline. On reinit, _last_stable
    is now cleared.

  Fix 5 – _process_frame returns typed PerceptionOutput (not bare dict):
    Previously returned PerceptionOutput correctly, but the pipeline_loop
    fallback `output = perception_state.latest` (on exception) could return
    the null output instead of last known good. Now falls back to _last_stable
    when available.
"""

import dataclasses
import threading
import time
from typing import Optional

import cv2
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
from tracking.attention import AttentionTracker
from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

_WATCHDOG_STALL_S         = 0.5
_WATCHDOG_SOFT_RESTART_AT = 3
_WATCHDOG_ERROR_AT        = 5
_MEMORY_SAMPLE_INTERVAL   = 30


class PerceptionEngine:
    """
    Vision pipeline orchestrator (v2.3).
    """

    def __init__(self):
        self._camera     = CameraCapture()
        self._quality    = FrameQualityGate()
        self._face       = FaceDetector()
        self._hand       = HandDetector()
        self._objects    = ObjectDetector()
        self._engagement = EngagementTracker()
        self._attention  = AttentionTracker()

        self._thread:   Optional[threading.Thread] = None
        self._watchdog: Optional[threading.Thread] = None
        self._last_tick: float = time.monotonic()
        self._frame_counter: int = 0

        # Last known-good output for quality gate fallback
        self._last_stable: Optional[PerceptionOutput] = None
        self._consecutive_quality_skips: int = 0  # NEW

    # ── Public API ───────────────────────────────────────────────────────────

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
        log.info("PerceptionEngine v2.3 started")

    def stop(self) -> None:
        perception_state.set_stopped()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        if self._watchdog:
            self._watchdog.join(timeout=2.0)
            self._watchdog = None
        self._camera.stop()
        self._close_detectors()
        log.info("PerceptionEngine v2.3 stopped cleanly")

    def _spawn_pipeline_thread(self) -> None:
        self._thread = threading.Thread(
            target=self._pipeline_loop, daemon=True, name="perception-engine"
        )
        self._thread.start()

    # ── Detector lifecycle ───────────────────────────────────────────────────

    def _reinit_detectors(self) -> None:
        """
        Fully destroy and recreate all MediaPipe and YOLO model instances.
        Called by watchdog on soft restart — assumes partial CUDA/session corruption.
        FIX 4: Clears _last_stable so stale frames are not served post-reinit.
        """
        log.warning("Reinitialising all detector instances (full session reset)")
        for detector, name in [(self._face, "FaceDetector"), (self._hand, "HandDetector")]:
            try:
                detector.close()
            except Exception as e:
                log.warning(f"Error closing {name}: {e}")

        self._face       = FaceDetector()
        self._hand       = HandDetector()
        self._objects    = ObjectDetector()
        self._engagement = EngagementTracker()
        self._attention  = AttentionTracker()

        # FIX 4: Clear stale stable output so first post-restart frame rebuilds baseline
        self._last_stable = None
        self._consecutive_quality_skips = 0  # NEW
        log.info("All detector instances and trackers reinitialised. _last_stable cleared.")

    def _close_detectors(self) -> None:
        for detector in (self._face, self._hand):
            try:
                detector.close()
            except Exception:
                pass

    # ── Watchdog ─────────────────────────────────────────────────────────────

    def _watchdog_loop(self) -> None:
        consecutive = 0
        while perception_state.is_running():
            time.sleep(0.25)
            stall_s = time.monotonic() - self._last_tick

            if stall_s <= _WATCHDOG_STALL_S:
                consecutive = 0
                continue

            consecutive += 1
            # FIX 2: thread-safe atomic increment
            total_stalls = perception_state.increment_stall()
            self._last_tick = time.monotonic()

            log.warning({
                "msg": "Watchdog stall",
                "stall_ms": round(stall_s * 1000),
                "consecutive": consecutive,
                "total_stalls": total_stalls,
            })

            if consecutive >= _WATCHDOG_ERROR_AT:
                log.error("Watchdog: 5 consecutive stalls — ENGINE ERROR")
                perception_state.set_error("Watchdog: 5 consecutive stalls")
                break

            if consecutive == _WATCHDOG_SOFT_RESTART_AT:
                log.warning("Watchdog: 3 stalls — full detector reinit + thread respawn")
                perception_state.record_session_peak()
                self._reinit_detectors()   # also clears _last_stable
                self._spawn_pipeline_thread()
                log.info("Watchdog: soft restart complete")

    # ── Pipeline loop ─────────────────────────────────────────────────────────

    def _pipeline_loop(self) -> None:
        frame_budget_s = 1.0 / vision_config.TARGET_FPS
        budget_ms      = frame_budget_s * 1000.0

        while perception_state.is_running():
            t_loop_start = time.monotonic()

            # ── Frame acquisition ──────────────────────────────────
            frame = self._camera.get_frame()
            if frame is None:
                output = self._make_skip(camera_drop=True)
                perception_state.publish(output)
                time.sleep(0.005)
                continue

            self._last_tick = time.monotonic()

            # ── Quality gate — preserve stable state on skip ───────
            if not self._quality.is_usable(frame):
                self._consecutive_quality_skips += 1

                # Decay engagement on every quality skip
                score, ui_score = self._engagement.update(
                    face_present=False,
                    looking_at_screen=False,
                    gesture="NONE",
                )

                output = self._make_skip(quality=True)

                if self._consecutive_quality_skips >= vision_config.QUALITY_SKIP_ABSENCE_THRESHOLD:
                    # Full absence — zero out everything
                    attention_state, distraction_frames = self._attention.update(
                        presence=False,
                        looking_at_screen=False,
                    )
                    output = dataclasses.replace(
                        output,
                        presence=False,
                        lookingAtScreen=False,
                        engagementScore=score,
                        engagementScoreUI=ui_score,
                        attentionState=attention_state,
                        distractionFrames=distraction_frames,
                        confidence=PerceptionConfidence(),   # ← zeros all confidence fields
                        systemConfidence=0.0,
                    )
                else:
                    # Grace period — decay scores but also decay confidence proportionally
                    attention_state, distraction_frames = self._attention.update(
                        presence=False,
                        looking_at_screen=False,
                    )
                    skip_ratio = self._consecutive_quality_skips / vision_config.QUALITY_SKIP_ABSENCE_THRESHOLD
                    prev_conf = output.confidence
                    decayed_conf = PerceptionConfidence(
                        face=round(prev_conf.face * (1.0 - skip_ratio), 3),
                        gesture=0.0,
                        objects=0.0,
                        pose=round(prev_conf.pose * (1.0 - skip_ratio), 3),
                    )
                    output = dataclasses.replace(
                        output,
                        engagementScore=score,
                        engagementScoreUI=ui_score,
                        attentionState=attention_state,
                        distractionFrames=distraction_frames,
                        confidence=decayed_conf,
                        systemConfidence=round(
                            (decayed_conf.face * vision_config.SYSTEM_CONF_W_FACE
                             + decayed_conf.pose * vision_config.SYSTEM_CONF_W_POSE)
                            / (vision_config.SYSTEM_CONF_W_FACE + vision_config.SYSTEM_CONF_W_POSE),
                            3,
                        ),
                    )

                perception_state.publish(output)
                perception_state.tick()
                elapsed = (time.monotonic() - t_loop_start) * 1000
                time.sleep(max(0.0, frame_budget_s - elapsed / 1000.0))
                continue

            # Reset skip counter on a usable frame
            self._consecutive_quality_skips = 0

            # ── Full detection pipeline ────────────────────────────
            try:
                output = self._process_frame(frame)
                self._last_stable = output
            except Exception as e:
                log.warning(f"Pipeline error: {e}")
                # FIX 5: prefer last_stable over null latest output
                output = self._last_stable if self._last_stable is not None else perception_state.latest

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

    # ── Quality skip helper ───────────────────────────────────────────────────

    def _make_skip(
        self,
        quality: bool = False,
        throttle: bool = False,
        camera_drop: bool = False,
    ) -> PerceptionOutput:
        """
        Returns last stable output with updated skip reason + timestamp.
        Ensures quality-gate skips don't zero out presence or engagement.
        If no stable output exists yet, returns a null output.
        """
        skip_reason = PerceptionSkipReason(
            quality=quality, throttle=throttle, camera_drop=camera_drop
        )
        if self._last_stable is not None:
            return dataclasses.replace(
                self._last_stable,
                skipped=skip_reason,
                timestamp=round(time.time(), 4),
            )
        return PerceptionOutput(
            skipped=skip_reason,
            timestamp=round(time.time(), 4),
        )

    # ── Frame processing ──────────────────────────────────────────────────────

    def _process_frame(self, frame: np.ndarray) -> PerceptionOutput:
        """
        Run full detection pipeline on one frame.

        FIX 1: Explicit naming — bgr_frame and rgb_frame are kept separate.
          - FaceDetector and HandDetector receive rgb_frame (MediaPipe expects RGB).
          - ObjectDetector (YOLO) receives bgr_frame (OpenCV/YOLO convention is BGR).
        """
        bgr_frame = frame  # Original OpenCV frame — BGR
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

        face_out = self._face.process(rgb_frame)
        gesture, gesture_conf = self._hand.process_with_confidence(rgb_frame)
        # YOLO operates on BGR frames — pass bgr_frame explicitly
        objects, obj_conf = self._objects.process(bgr_frame)

        # Dual-track engagement scores
        score, ui_score = self._engagement.update(
            face_present=face_out["presence"],
            looking_at_screen=face_out["lookingAtScreen"],
            gesture=gesture,
        )

        attention_state, distraction_frames = self._attention.update(
            presence=face_out["presence"],
            looking_at_screen=face_out["lookingAtScreen"],
        )

        face_conf = face_out.get("confidence", 0.0)
        pose_conf = face_out.get("pose_confidence", 0.0)

        # Weighted fusion excluding objects if 0 (no objects detected is not a failure)
        w_face = vision_config.SYSTEM_CONF_W_FACE
        w_pose = vision_config.SYSTEM_CONF_W_POSE
        w_obj = vision_config.SYSTEM_CONF_W_OBJECTS

        if obj_conf == 0.0:
            total_w = w_face + w_pose
            system_confidence = round((w_face * face_conf + w_pose * pose_conf) / total_w, 3) if total_w > 0 else 0.0
        else:
            total_w = w_face + w_pose + w_obj
            system_confidence = round((w_face * face_conf + w_pose * pose_conf + w_obj * obj_conf) / total_w, 3) if total_w > 0 else 0.0

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
            attentionState=attention_state,
            distractionFrames=distraction_frames,
            gesture=gesture,
            detectedObjects=tuple(objects),
            skipped=PerceptionSkipReason(),
            confidence=confidence,
            systemConfidence=system_confidence,
            timestamp=round(time.time(), 4),
        )