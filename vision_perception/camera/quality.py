"""
LaRa Vision Perception — Frame Quality Gate
Evaluates a frame before dispatching heavy ML pipelines.
Prevents garbage data from dark/blurry frames polluting engagement scores.
"""

import cv2
import numpy as np

from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)


class FrameQualityGate:
    """
    Two-signal quality check run before every detection cycle:
      1. Brightness — mean pixel intensity of the grayscale frame.
      2. Sharpness  — variance of the Laplacian (blur metric).

    If either signal falls below threshold, returns False (skip detection).
    Thresholds are configurable in vision_config.
    """

    def __init__(self):
        self.min_brightness: float = getattr(vision_config, "MIN_BRIGHTNESS", 30.0)
        self.min_sharpness:  float = getattr(vision_config, "MIN_SHARPNESS", 50.0)
        self._skip_count: int = 0
        log.info(
            f"FrameQualityGate: brightness≥{self.min_brightness}, "
            f"sharpness≥{self.min_sharpness}"
        )

    def is_usable(self, frame: np.ndarray) -> bool:
        """
        Returns True if the frame is bright and sharp enough for detection.
        Computation cost: ~0.5–1ms on a 640×480 BGR frame.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Brightness: mean intensity across all pixels
        brightness = float(np.mean(gray))

        # Sharpness: variance of Laplacian (higher = sharper)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        if brightness < self.min_brightness:
            self._skip_count += 1
            if self._skip_count % 30 == 1:  # Log periodically, not every frame
                log.warning(f"Frame too dark (brightness={brightness:.1f}) — skipping")
            return False

        if sharpness < self.min_sharpness:
            self._skip_count += 1
            if self._skip_count % 30 == 1:
                log.warning(f"Frame too blurry (sharpness={sharpness:.1f}) — skipping")
            return False

        self._skip_count = 0
        return True

    @property
    def total_skipped(self) -> int:
        return self._skip_count
