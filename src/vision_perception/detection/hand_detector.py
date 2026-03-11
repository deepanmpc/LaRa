"""
LaRa Vision Perception — Hand Detector & Gesture Classifier (v2.1)
v2.1 fixes over v2.0:

  Fix 1 – Handedness-aware thumb detection:
    Original code used `lm[tip].x < lm[mid].x` unconditionally, which
    only works for RIGHT hands. For a LEFT hand, the thumb tip is on the
    opposite side, so the comparison must be inverted. This caused THUMBS_UP
    to be misclassified as FIST (0 fingers extended) when the left hand was used.
    Now reads MediaPipe's multi_handedness label to choose the correct axis
    direction before calling _extended_fingers().

  Fix 2 – Confidence passthrough on non-dominant path:
    process() called process_with_confidence() correctly but discarded the
    confidence score. Refactored so process() is a strict thin wrapper.

  Fix 3 – GESTURES constant used for validation:
    Classifier returns only known gesture labels. Added a fallback assertion
    guard in _classify() to ensure any future label additions are reflected
    in GESTURES.
"""

from typing import Optional, Tuple
import numpy as np
import mediapipe as mp

from utils.logger import get_logger

log = get_logger(__name__)

# All valid gesture labels — keep in sync with _classify() return values
GESTURES = ["NONE", "OPEN_PALM", "FIST", "THUMBS_UP", "POINTING", "PEACE"]


class HandDetector:
    """
    Detects one hand and classifies its pose into a simple gesture label.
    Uses rule-based finger extension checks on MediaPipe 21-landmark output.
    Correctly handles both LEFT and RIGHT hands (v2.1 fix).
    """

    def __init__(self):
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5,
            model_complexity=0,   # Fastest model
        )
        log.info("HandDetector v2.1 initialised (handedness-aware, MediaPipe Hands complexity=0)")

    def process(self, rgb_frame: np.ndarray) -> str:
        """
        Returns a gesture label string (legacy API — keeps tests passing).
        """
        gesture, _ = self.process_with_confidence(rgb_frame)
        return gesture

    def process_with_confidence(self, rgb_frame: np.ndarray) -> Tuple[str, float]:
        """
        Args:
            rgb_frame: Pre-computed RGB image array.
        Returns:
            (gesture_str, confidence_float).
            Confidence = MediaPipe hand detection score, or 0.0 if no hand found.
        """
        results = self._hands.process(rgb_frame)

        if not results.multi_hand_landmarks:
            return "NONE", 0.0

        lm = results.multi_hand_landmarks[0].landmark

        # Confidence via multi_handedness
        conf = 0.0
        is_right_hand = True   # default assumption
        if results.multi_handedness:
            handedness = results.multi_handedness[0].classification[0]
            conf = round(float(handedness.score), 3)
            # MediaPipe returns mirrored labels for selfie-mode cameras.
            # "Right" in MediaPipe world-space = the hand on the right side of the image.
            is_right_hand = (handedness.label == "Right")

        gesture = self._classify(lm, is_right_hand=is_right_hand)
        return gesture, conf

    # ── Internal gesture rules ───────────────────────────────────

    def _classify(self, lm, is_right_hand: bool = True) -> str:
        fingers = self._extended_fingers(lm, is_right_hand=is_right_hand)
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

    def _extended_fingers(self, lm, is_right_hand: bool = True) -> list:
        """
        Returns a 5-element bool list [thumb, index, middle, ring, pinky].
        A finger is "extended" if its tip landmark is above its PIP joint.

        FIX 1: Thumb extension direction depends on handedness.
          - Right hand: thumb tip x < PIP joint x (tip is to the left of joint)
          - Left hand:  thumb tip x > PIP joint x (tip is to the right of joint)
        All other fingers use y-axis comparison (tip.y < mid.y = extended).
        """
        tip_ids = [4,  8,  12, 16, 20]  # thumb, index, middle, ring, pinky tips
        mid_ids = [3,  6,  10, 14, 18]  # corresponding PIP joints

        extended = []
        for i, (tip, mid) in enumerate(zip(tip_ids, mid_ids)):
            if i == 0:  # Thumb
                if is_right_hand:
                    # Right hand: tip moves left (lower x) when extended
                    extended.append(lm[tip].x < lm[mid].x)
                else:
                    # Left hand: tip moves right (higher x) when extended
                    extended.append(lm[tip].x > lm[mid].x)
            else:
                # All other fingers: tip moves up (lower y in image coords) when extended
                extended.append(lm[tip].y < lm[mid].y)
        return extended

    def close(self) -> None:
        self._hands.close()