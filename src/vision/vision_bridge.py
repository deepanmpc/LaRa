import logging
import threading
import time
from typing import Optional

import requests


VISION_BASE_URL = "http://localhost:8001"
ALERT_COOLDOWN_S = 10.0


class VisionBridge:
    def __init__(self):
        self._active = False
        self._fail_count = 0
        self._last_state = None
        self._last_alert_time = {}
        self._poll_thread = None
        self._stop_event = threading.Event()
        self._state_lock = threading.Lock()
        self._thread_lock = threading.Lock()
        # EMA smoothing for engagement — prevents spiky point samples from misleading the LLM
        self._ema_engagement = None  # None = not yet initialised
        self._ema_alpha = 0.4       # Responsive but smoothed (α=0.4)

    def start_vision_service(self):
        for attempt in range(1, 4):
            try:
                response = requests.post(f"{VISION_BASE_URL}/start", timeout=1.0)
                response.raise_for_status()
                payload = response.json() if response.content else {}
                status = payload.get("status", "ok")
                self._active = True
                self._fail_count = 0
                logging.info(f"[VisionBridge] Vision service start succeeded ({status})")
                return True
            except Exception as e:
                logging.warning(
                    f"[VisionBridge] Vision service start failed "
                    f"(attempt {attempt}/3): {e}"
                )
                if attempt < 3:
                    time.sleep(1)

        logging.warning("[VisionBridge] Vision service unavailable; continuing without vision")
        return False

    def stop_vision_service(self):
        try:
            response = requests.post(f"{VISION_BASE_URL}/stop", timeout=1.0)
            response.raise_for_status()
            logging.info("[VisionBridge] Vision service stop requested")
        except Exception as e:
            logging.warning(f"[VisionBridge] Vision service stop failed: {e}")
        finally:
            self._active = False

    def flush_vision_analytics(self, child_id: int, session_uuid: str):
        """
        Calls /session-flush on vision service and sends result to Dashboard Backend.
        """
        if not self._active:
            logging.debug("[VisionBridge] Service inactive, skipping flush")
            return

        try:
            # 1. Get aggregated metrics from vision service
            res = requests.post(f"{VISION_BASE_URL}/session-flush", timeout=2.0)
            res.raise_for_status()
            metrics = res.json()

            # 2. Enrich with identifiers
            metrics["child_id"] = child_id
            metrics["session_uuid"] = session_uuid
            
            # 3. Post to Dashboard Backend
            # Note: Using standard local backend URL
            BACKEND_URL = "http://localhost:8080/api/clinician/vision/flush"
            
            backend_res = requests.post(BACKEND_URL, json=metrics, timeout=2.0)
            backend_res.raise_for_status()
            logging.info(f"[VisionBridge] Flushed vision analytics for child {child_id}")
            
        except Exception as e:
            logging.warning(f"[VisionBridge] Failed to flush vision analytics: {e}")

    def start_polling(self, bridge, session, interval_s=0.5):
        with self._thread_lock:
            if self._poll_thread and self._poll_thread.is_alive():
                logging.info("[VisionBridge] Polling already active")
                return

            if not self._active:
                logging.info("[VisionBridge] Polling skipped; vision service is inactive")
                return

            self._stop_event = threading.Event()
            self._fail_count = 0
            self._last_alert_time = {}
            self._poll_thread = threading.Thread(
                target=self._poll_loop,
                args=(bridge, session, interval_s),
                daemon=True,
                name="lara-vision-poll",
            )
            self._poll_thread.start()
            logging.info(f"[VisionBridge] Polling started at {interval_s:.2f}s intervals")

    def _poll_loop(self, bridge, session, interval_s):
        while not self._stop_event.wait(interval_s):
            try:
                response = requests.get(f"{VISION_BASE_URL}/latest", timeout=0.1)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                self._fail_count += 1
                if self._fail_count > 10:
                    logging.warning(
                        "[VisionBridge] /latest failed more than 10 times consecutively; "
                        "stopping polling"
                    )
                    self._active = False
                    self._stop_event.set()
                    break

                logging.debug(
                    f"[VisionBridge] /latest poll failed "
                    f"({self._fail_count}/10 consecutive): {e}"
                )
                continue

            self._active = True
            self._fail_count = 0
            with self._state_lock:
                self._last_state = data

            try:
                self._process_frame(data, bridge, session)
            except Exception as e:
                logging.warning(f"[VisionBridge] Frame processing failed: {e}")

        logging.info("[VisionBridge] Polling stopped")

    def stop_polling(self):
        with self._thread_lock:
            self._stop_event.set()
            thread = self._poll_thread
            self._poll_thread = None

        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=1.0)

    def _process_frame(self, data, bridge, session):
        presence = bool(data.get("presence", False))
        attention = data.get("attentionState", "UNKNOWN")
        raw_engagement = float(data.get("engagementScoreUI", 0.0) or 0.0)
        gesture = data.get("gesture", "NONE") or "NONE"
        distraction_frames = int(data.get("distractionFrames", 0) or 0)
        timestamp = data.get("timestamp", time.time())

        # EMA smoothing for engagement — produces a stable signal for the LLM
        if self._ema_engagement is None:
            self._ema_engagement = raw_engagement  # Bootstrap from first sample
        self._ema_engagement = round(
            self._ema_alpha * raw_engagement + (1 - self._ema_alpha) * self._ema_engagement, 4
        )
        smooth_engagement = self._ema_engagement

        self._emit(
            bridge,
            "vision_update",
            {
                "presence": presence,
                "attentionState": attention,
                "engagementScore": smooth_engagement,
                "gesture": gesture,
                "distractionFrames": distraction_frames,
                "timestamp": timestamp,
            },
        )

        if attention == "DISTRACTED" and distraction_frames >= 45 and self._should_alert("distraction"):
            self._emit(
                bridge,
                "vision_alert",
                {
                    "alertType": "distraction",
                    "distractionFrames": distraction_frames,
                    "message": "Child has been looking away for 3+ seconds",
                },
            )

        if attention == "ABSENT" and self._should_alert("absence"):
            self._emit(
                bridge,
                "vision_alert",
                {
                    "alertType": "absence",
                    "message": "Child not detected in frame",
                },
            )

        if presence and smooth_engagement < 0.3 and self._should_alert("low_engagement"):
            self._emit(
                bridge,
                "vision_alert",
                {
                    "alertType": "low_engagement",
                    "score": smooth_engagement,
                    "message": "Engagement critically low",
                },
            )

        if gesture not in ("NONE", ""):
            self._emit(
                bridge,
                "vision_gesture",
                {
                    "gesture": gesture,
                    "timestamp": timestamp,
                },
            )

        if session is not None and hasattr(session, "vision_lock"):
            with session.vision_lock:
                session.vision_presence = presence
                session.vision_attention = attention
                session.vision_engagement = smooth_engagement
                session.vision_gesture = gesture
                session.vision_timestamp = timestamp
                
                # Step 11 — Engagement Timeline Persistence (Data Collection)
                if hasattr(session, "vision_history"):
                    session.vision_history.append({
                        "presence": presence,
                        "attention": attention,
                        "engagement": smooth_engagement,
                        "gesture": gesture,
                        "timestamp": timestamp
                    })

    def _should_alert(self, alert_type):
        now = time.time()
        last_fired = self._last_alert_time.get(alert_type, 0.0)
        if now - last_fired < ALERT_COOLDOWN_S:
            return False
        self._last_alert_time[alert_type] = now
        return True

    def _emit(self, bridge, event_type, payload):
        if bridge is None:
            return

        try:
            bridge.emit(event_type, payload)
        except Exception as e:
            logging.debug(f"[VisionBridge] Failed to emit {event_type}: {e}")

    def get_current_state(self) -> Optional[dict]:
        with self._state_lock:
            if self._last_state is None:
                return None
            return dict(self._last_state)


class VisionBridgeService:
    _instance = None

    def __init__(self):
        if VisionBridgeService._instance is not None:
            raise RuntimeError("VisionBridgeService is a singleton. Use VisionBridgeService.get()")

        logging.info("[VisionBridge] Initializing vision bridge subsystem...")
        self.bridge = VisionBridge()
        VisionBridgeService._instance = self

    @staticmethod
    def get() -> VisionBridge:
        if VisionBridgeService._instance is None:
            VisionBridgeService()
        return VisionBridgeService._instance.bridge
