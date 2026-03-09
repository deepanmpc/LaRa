"""
LaRa Vision Perception — Object Detector (v2.2, Adaptive YOLO with Hysteresis)
v2.2 fixes over v2.1:

  Fix 1 – Warmup uses configured resolution:
    Original warmup used hardcoded np.zeros((480, 640, 3)) regardless of
    vision_config.RESOLUTION. If RESOLUTION differs, YOLO's first real
    inference resizes internally and causes a one-time latency spike that
    corrupts the first throttle measurement. Now reads RESOLUTION from config.

  Fix 2 – Load failure surfaced with actionable guidance:
    The original except clause logged a generic warning that didn't distinguish
    between "model file not found" (fixable by re-running download_models.py)
    and "CUDA OOM" (fixable by reducing batch size or switching to CPU).
    Now logs the exception type and a hint.

  Fix 3 – Throttle cooldown uses monotonic clock correctly:
    _last_adjust_time was initialised to 0.0 which means on the very first
    frame, time.monotonic() - 0.0 could be a very large number, bypassing
    the cooldown entirely and triggering an immediate interval change before
    any real pipeline timing data exists. Now initialised to time.monotonic()
    at construction so the first adjustment waits the proper cooldown.

  Fix 4 – Cache cleared on model reload:
    If _load_model is called during a soft restart (e.g. after watchdog reinit),
    the stale _cache from the previous session could be returned for YOLO_INTERVAL
    frames, serving incorrect object detections. Cache is now cleared on reload.
"""

from typing import List, Tuple
import time
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class ObjectDetector:
    """
    YOLOv8n with hysteresis-protected adaptive throttle (v2.2).

    Throttle algorithm:
      - Only adjusts interval if > YOLO_ADJUST_INTERVAL_S has passed since last change.
      - Dead-band: ±YOLO_HYSTERESIS_BAND_MS around frame_budget prevents oscillation.
      - Interval adjusts by ±1 per evaluation (clamped to [1, 6]).
    """

    def __init__(self):
        self._interval: int = vision_config.YOLO_INTERVAL
        self._counter: int = 0
        self._cache: List[str] = []
        self._last_confidence: float = 0.0
        self._model = None

        # FIX 3: Initialise to current time so first cooldown wait is correct
        self._last_adjust_time: float = time.monotonic()

        self._load_model()

    # ── Adaptive throttle (with hysteresis) ─────────────────────

    def update_throttle(self, processing_ms: float, budget_ms: float) -> None:
        """
        Called by PerceptionEngine each loop.
        Adjusts YOLO interval respecting:
          - YOLO_ADJUST_INTERVAL_S minimum between changes
          - ±YOLO_HYSTERESIS_BAND_MS dead-band around the budget
        """
        now = time.monotonic()
        if now - self._last_adjust_time < vision_config.YOLO_ADJUST_INTERVAL_S:
            return  # Within cooldown window — do nothing

        band = vision_config.YOLO_HYSTERESIS_BAND_MS
        upper = budget_ms + band   # Over this → too slow, increase interval
        lower = budget_ms - band   # Under this → have headroom, decrease interval

        changed = False
        if processing_ms > upper:
            new_interval = min(self._interval + 1, vision_config.YOLO_MAX_INTERVAL)
            if new_interval != self._interval:
                self._interval = new_interval
                changed = True
        elif processing_ms < lower:
            new_interval = max(self._interval - 1, vision_config.YOLO_MIN_INTERVAL)
            if new_interval != self._interval:
                self._interval = new_interval
                changed = True

        if changed:
            self._last_adjust_time = now
            log.info({
                "msg": "YOLO interval adjusted",
                "interval": self._interval,
                "processing_ms": round(processing_ms, 1),
                "budget_ms": round(budget_ms, 1),
            })

    @property
    def current_interval(self) -> int:
        return self._interval

    # ── Detection ────────────────────────────────────────────────

    def process(self, frame: np.ndarray) -> Tuple[List[str], float]:
        """
        Returns (object_names, mean_confidence).
        Only runs inference every self._interval frames.
        """
        self._counter += 1
        if self._model is None:
            return [], 0.0
        if self._counter % self._interval != 0:
            return self._cache, self._last_confidence

        device = "cuda" if vision_config.USE_GPU else "cpu"
        try:
            results = self._model.predict(frame, device=device, verbose=False)
            names: List[str] = []
            scores: List[float] = []
            for r in results:
                for i, cls_id in enumerate(r.boxes.cls.tolist()):
                    name = self._model.names[int(cls_id)]
                    conf = float(r.boxes.conf[i])
                    if name not in names:
                        names.append(name)
                        scores.append(conf)
            self._cache = names
            self._last_confidence = round(float(np.mean(scores)) if scores else 0.0, 3)
        except RuntimeError as e:
            # Catch CUDA OOM separately for actionable logging
            if "out of memory" in str(e).lower():
                log.warning(
                    f"YOLO CUDA OOM: {e}. "
                    "Consider setting USE_GPU=False in vision_config or reducing resolution."
                )
            else:
                log.warning(f"YOLO inference RuntimeError: {e}")
        except Exception as e:
            log.warning(f"YOLO inference error ({type(e).__name__}): {e}")

        return self._cache, self._last_confidence

    # ── Model loading ────────────────────────────────────────────

    def _load_model(self) -> None:
        """
        Loads YOLOv8n and runs a warmup inference at the configured resolution.
        FIX 1: Warmup frame matches vision_config.RESOLUTION, not hardcoded 480x640.
        FIX 2: Exception type is logged for actionable error messages.
        FIX 4: Cache cleared on each (re)load.
        """
        # Clear stale cache so a fresh session doesn't serve old detections
        self._cache = []
        self._last_confidence = 0.0

        try:
            from ultralytics import YOLO
            self._model = YOLO(vision_config.YOLO_MODEL_PATH)
            device = "cuda" if vision_config.USE_GPU else "cpu"

            # FIX 1: Use configured resolution for warmup frame
            w, h = vision_config.RESOLUTION
            warmup_frame = np.zeros((h, w, 3), dtype=np.uint8)
            self._model.predict(warmup_frame, device=device, verbose=False)

            log.info({
                "msg": "YOLO v2.2 loaded (hysteresis throttle)",
                "device": device,
                "warmup_resolution": f"{w}x{h}",
            })
        except FileNotFoundError as e:
            log.warning(
                f"YOLO model file not found: {e}. "
                "Run `python scripts/download_models.py` to download. "
                "Object detection disabled."
            )
            self._model = None
        except ImportError as e:
            log.warning(
                f"ultralytics not installed: {e}. "
                "Run `pip install ultralytics`. Object detection disabled."
            )
            self._model = None
        except Exception as e:
            log.warning(
                f"YOLO load failed ({type(e).__name__}): {e}. "
                "Object detection disabled."
            )
            self._model = None