"""
LaRa Vision Perception — Configuration
All tuneable parameters for the vision pipeline.
Edit here to change behaviour without touching code.
"""

# ─── Camera ───────────────────────────────────────────────
CAMERA_INDEX: int = 0             # 0 = default webcam
TARGET_FPS: int = 15
RESOLUTION: tuple = (640, 480)    # (width, height)

# ─── Detection throttling ─────────────────────────────────
YOLO_INTERVAL: int = 3            # Run YOLO every N frames
FACE_VERIFY_INTERVAL: int = 30    # Frames between embedding verification (~1s @ 30fps)

# ─── Smoothing buffers ────────────────────────────────────
HEAD_POSE_BUFFER: int = 5         # Moving average window for head pose
ENGAGEMENT_BUFFER: int = 15       # Rolling window for engagement score

# ─── Model paths ─────────────────────────────────────────
YOLO_MODEL_PATH: str = "models/yolov8n.pt"
INSIGHTFACE_MODEL: str = "buffalo_sc"     # Smallest InsightFace model

# ─── Hardware ─────────────────────────────────────────────
USE_GPU: bool = False              # True = use CUDA if available
MAX_MEMORY_MB: int = 1800          # Alert if RSS exceeds this

# ─── Engagement thresholds ────────────────────────────────
ENGAGEMENT_THRESHOLDS: dict = {
    "high":   0.7,   # >= 0.7 → "Highly Engaged"
    "medium": 0.4,   # >= 0.4 → "Moderately Engaged"
                     # <  0.4 → "Frequently Distracted"
}

# ─── Head pose "looking at screen" window ─────────────────
# Yaw and pitch tolerance in degrees
GAZE_YAW_THRESHOLD: float = 25.0
GAZE_PITCH_THRESHOLD: float = 20.0

# ─── Logging ──────────────────────────────────────────────
LOG_LEVEL: str = "INFO"            # DEBUG / INFO / WARNING
LOG_MODE: str = "json"             # "json" | "text"

# ─── Test mode ────────────────────────────────────────────
TEST_MODE_LOG_INTERVAL: float = 1.0   # Seconds between log prints in --test mode
