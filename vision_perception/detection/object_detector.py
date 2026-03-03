"""
LaRa Vision Perception — Object Detector (v2, Adaptive Throttling)
YOLOv8n with self-balancing interval:
  - If pipeline loop is over-budget → increase YOLO_INTERVAL (less frequent)
  - If pipeline has headroom        → decrease YOLO_INTERVAL (more frequent)
  - Bounds: [1, 6] — never completely disabled, never thrashing
"""

from typing import List, Tuple
import time
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

_MIN_INTERVAL = 1
_MAX_INTERVAL = 6


class ObjectDetector:
    """
    Adaptive-throttled YOLOv8n wrapper.
    Call `update_throttle(processing_ms, budget_ms)` from the engine each loop
    to let the detector self-balance its own run frequency.
    """

    def __init__(self):
        self._interval: int = vision_config.YOLO_INTERVAL
        self._counter: int = 0
        self._cache: List[str] = []
        self._last_confidence: float = 0.0
        self._model = None
        self._load_model()

    # ── Adaptive throttle ────────────────────────────────────────

    def update_throttle(self, processing_ms: float, budget_ms: float) -> None:
        """
        Called by PerceptionEngine once per loop with timing data.
        Adjusts YOLO_INTERVAL to keep total pipeline within budget.
        """
        if processing_ms > budget_ms * 0.9:  # Over 90% of budget → slow down
            self._interval = min(self._interval + 1, _MAX_INTERVAL)
        elif processing_ms < budget_ms * 0.6:  # Under 60% of budget → speed up
            self._interval = max(self._interval - 1, _MIN_INTERVAL)

    @property
    def current_interval(self) -> int:
        return self._interval

    # ── Detection ────────────────────────────────────────────────

    def process(self, frame: np.ndarray) -> Tuple[List[str], float]:
        """
        Returns (object_names_list, confidence_score).
        Runs inference only every self._interval frames; returns cache otherwise.
        """
        self._counter += 1

        if self._model is None:
            return [], 0.0

        if self._counter % self._interval != 0:
            return self._cache, self._last_confidence   # Fast path

        device = "cuda" if vision_config.USE_GPU else "cpu"
        try:
            t0 = time.monotonic()
            results = self._model.predict(frame, device=device, verbose=False)
            dt = (time.monotonic() - t0) * 1000

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
            log.info({"msg": "YOLO model loaded (adaptive throttle)", "path": vision_config.YOLO_MODEL_PATH, "device": device})
        except Exception as e:
            log.warning(f"YOLO load failed — object detection disabled: {e}")
            self._model = None
