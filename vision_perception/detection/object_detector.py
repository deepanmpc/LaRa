"""
LaRa Vision Perception — Object Detector (YOLOv8n, throttled)
Runs YOLO inference only every YOLO_INTERVAL frames to stay under latency budget.
"""

from typing import List
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class ObjectDetector:
    """
    Wraps Ultralytics YOLOv8n with a frame-counter throttle.
    Call process() every frame; inference only happens every YOLO_INTERVAL calls.
    Returns the cached detections on skipped frames.
    """

    def __init__(self):
        self._counter: int = 0
        self._cache: List[str] = []
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from ultralytics import YOLO
            self._model = YOLO(vision_config.YOLO_MODEL_PATH)
            device = "cuda" if vision_config.USE_GPU else "cpu"
            # Warm up model
            self._model.predict(
                np.zeros((480, 640, 3), dtype=np.uint8), device=device, verbose=False
            )
            log.info({"msg": "YOLO model loaded", "path": vision_config.YOLO_MODEL_PATH, "device": device})
        except Exception as e:
            log.warning(f"YOLO load failed — object detection disabled: {e}")
            self._model = None

    def process(self, frame: np.ndarray) -> List[str]:
        """
        Returns list of detected class name strings.
        Runs inference only every YOLO_INTERVAL frames; returns cache otherwise.
        """
        self._counter += 1
        if self._model is None:
            return []
        if self._counter % vision_config.YOLO_INTERVAL != 0:
            return self._cache   # Fast path — return cached result

        device = "cuda" if vision_config.USE_GPU else "cpu"
        try:
            results = self._model.predict(frame, device=device, verbose=False)
            names: List[str] = []
            for r in results:
                for cls_id in r.boxes.cls.tolist():
                    name = self._model.names[int(cls_id)]
                    if name not in names:
                        names.append(name)
            self._cache = names
        except Exception as e:
            log.warning(f"YOLO inference error: {e}")

        return self._cache
