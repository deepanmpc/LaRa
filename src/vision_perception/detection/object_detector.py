"""
LaRa Vision Perception — Object Detector (v2.1, Adaptive YOLO with Hysteresis)
v2.1 upgrade:
  - Minimum 2-second cooldown between interval adjustments.
  - ±5ms hysteresis dead-band to prevent oscillation at threshold boundary.
  - Interval bounds remain 1–6.
"""

from typing import List, Tuple
import time
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class ObjectDetector:
    """
    YOLOv8n with hysteresis-protected adaptive throttle.

    Throttle algorithm (v2.1):
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

        # Hysteresis state
        self._last_adjust_time: float = 0.0   # epoch seconds of last interval change
        self._load_model()

    # ── Adaptive throttle (with hysteresis) ─────────────────────

    def update_throttle(self, processing_ms: float, budget_ms: float) -> None:
        """
        Called by PerceptionEngine each loop.
        Adjusts YOLO interval respecting:
          - 2-second minimum between changes
          - ±5ms dead-band around the budget
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
            log.info({"msg": "YOLO interval adjusted", "interval": self._interval,
                      "processing_ms": round(processing_ms, 1), "budget_ms": round(budget_ms, 1)})

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
        except Exception as e:
            log.warning(f"YOLO inference error: {e}")

        return self._cache, self._last_confidence

    # ── Model loading ────────────────────────────────────────────

    def _load_model(self) -> None:
        try:
            from ultralytics import YOLO
            self._model = YOLO(vision_config.YOLO_MODEL_PATH)
            device = "cuda" if vision_config.USE_GPU else "cpu"
            self._model.predict(
                np.zeros((480, 640, 3), dtype=np.uint8), device=device, verbose=False
            )
            log.info({"msg": "YOLO v2.1 loaded (hysteresis throttle)", "device": device})
        except Exception as e:
            log.warning(f"YOLO load failed — object detection disabled: {e}")
            self._model = None
