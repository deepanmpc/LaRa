"""
LaRa Vision Perception — Configuration v2.1
All tuneable parameters for the vision pipeline.
Edit here to change behaviour without touching code.
"""

# ─── Camera ───────────────────────────────────────────────
CAMERA_INDEX: int = 0             # 0 = default webcam
TARGET_FPS: int = 15
RESOLUTION: tuple = (640, 480)    # (width, height)

# ─── Detection throttling ─────────────────────────────────
YOLO_INTERVAL: int = 3            # Run YOLO every N frames (adaptive overrides this)
FACE_VERIFY_INTERVAL: int = 30    # Frames between embedding verification

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
}

# ─── Engagement decay (absence) ──────────────────────────
# FAST (internal): collapses score quickly — raw signal fidelity
ENGAGEMENT_DECAY_RATE_FAST: float = 0.7
# SLOW (UI): exposed to dashboard — smooth decay for human perception
# 0.95^15 ≈ 0.46  (halved after 1 sec at 15fps — perceptible but not jarring)
ENGAGEMENT_DECAY_RATE_UI: float = 0.95

# ─── Head pose "looking at screen" window ─────────────────
GAZE_YAW_THRESHOLD: float = 25.0
GAZE_PITCH_THRESHOLD: float = 20.0

# ─── Head pose confidence ─────────────────────────────────
# solvePnP reprojection error threshold (pixels)
# Below this = high confidence in the pose estimate
POSE_REPROJECTION_THRESHOLD: float = 8.0
# Minimum confidence score to trust lookingAtScreen classification
POSE_CONFIDENCE_MIN: float = 0.40
# Minimum mean landmark visibility to enter pose estimation
LANDMARK_VISIBILITY_MIN: float = 0.5

# ─── Frame quality gate ────────────────────────────────────
MIN_BRIGHTNESS: float = 30.0      # 0–255
MIN_SHARPNESS:  float = 50.0      # Laplacian variance

# ─── Adaptive YOLO throttle ───────────────────────────────
YOLO_MIN_INTERVAL: int = 1
YOLO_MAX_INTERVAL: int = 6
YOLO_HYSTERESIS_BAND_MS: float = 5.0   # ±ms dead-band to prevent oscillation
YOLO_ADJUST_INTERVAL_S: float = 2.0    # Minimum seconds between interval changes

# ─── Memory monitoring ────────────────────────────────────
MEMORY_WINDOW: int = 20                 # Rolling sample window
MEMORY_SLOPE_THRESHOLD_MB_S: float = 0.5  # MB/sec growth rate trigger
MEMORY_CONSECUTIVE_WINDOWS: int = 3      # Must exceed slope for N windows
MEMORY_TRACK_PEAK: bool = True           # Track per-session RSS peaks for fragmentation detection

# ─── System confidence weights ────────────────────────────
# Weighted mean → systemConfidence
SYSTEM_CONF_W_FACE:    float = 0.40
SYSTEM_CONF_W_POSE:    float = 0.35
SYSTEM_CONF_W_OBJECTS: float = 0.25

# ─── Logging ──────────────────────────────────────────────
LOG_LEVEL: str = "INFO"
LOG_MODE: str = "json"

# ─── Test mode ────────────────────────────────────────────
TEST_MODE_LOG_INTERVAL: float = 1.0
