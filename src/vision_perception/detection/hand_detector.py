"""
LaRa Vision Perception — Hand Detector & Gesture Classifier (v2)
MediaPipe Hands → landmark-based rule classifier + confidence output.
"""

from typing import Optional
import numpy as np
import mediapipe as mp

from utils.logger import get_logger

log = get_logger(__name__)

# Gesture labels
GESTURES = ["NONE", "OPEN_PALM", "FIST", "THUMBS_UP", "POINTING", "PEACE"]


class HandDetector:
    """
    Detects one hand and classifies its pose into a simple gesture label.
    Uses rule-based finger extension checks on MediaPipe 21-landmark output.
    """

    def __init__(self):
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
            model_complexity=0,   # Fastest model
        )
        log.info("HandDetector initialised (MediaPipe Hands, complexity=0)")

    def process(self, rgb_frame: np.ndarray) -> str:
        """
        Returns a gesture label string (legacy API — keeps tests passing).
        """
        gesture, _ = self.process_with_confidence(rgb_frame)
        return gesture

    def process_with_confidence(self, rgb_frame: np.ndarray) -> tuple:
        """
        Args:
            rgb_frame: Pre-computed RGB image array.
        Returns (gesture_str, confidence_float).
        Confidence = MediaPipe hand detection score, or 0.0 if no hand found.
        """
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return "NONE", 0.0

        lm = results.multi_hand_landmarks[0].landmark
        # MediaPipe confidence via multi_handedness
        conf = 0.0
        if results.multi_handedness:
            conf = round(float(results.multi_handedness[0].classification[0].score), 3)

        return self._classify(lm), conf

    # ── Internal gesture rules ───────────────────────────────────

    def _classify(self, lm) -> str:
        fingers = self._extended_fingers(lm)
        n = sum(fingers)

        # Rule checks (heuristic, order matters)
        if n == 5:
            return "OPEN_PALM"
        if n == 0:
            return "FIST"
        if fingers == [True, False, False, False, False]:
            return "THUMBS_UP"
        if fingers == [False, True, False, False, False]:
            return "POINTING"
        if fingers == [False, True, True, False, False]:
            return "PEACE"
        return "NONE"

    def _extended_fingers(self, lm) -> list:
        """
        Returns a 5-element bool list [thumb, index, middle, ring, pinky].
        A finger is "extended" if its tip landmark y-coord is above (smaller y)
        than its middle-joint landmark — holding for pinky→index.
        Thumb uses x-axis comparison.
        """
        # MediaPipe hand landmark indices
        tip_ids  = [4,  8,  12, 16, 20]  # thumb, index, …, pinky tips
        mid_ids  = [3,  6,  10, 14, 18]  # corresponding PIP joints

        extended = []
        for i, (tip, mid) in enumerate(zip(tip_ids, mid_ids)):
            if i == 0:  # Thumb: compare x (works for right hand)
                extended.append(lm[tip].x < lm[mid].x)
            else:
                extended.append(lm[tip].y < lm[mid].y)
        return extended

    def close(self) -> None:
        self._hands.close()
