# LaRa Vision Perception — `lara-vision-perception`

An independent FastAPI microservice for real-time computer vision.
Runs completely decoupled from the main LaRa system.

---

## Quick Start

```bash
# 1. Create a dedicated virtualenv
cd vision_perception
python3 -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Start the API server (camera NOT opened yet)
uvicorn app:app --host 0.0.0.0 --port 8001

# 3b. OR run test mode (no server required)
python app.py --test
```

---

## API Reference

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/status` | Engine state, FPS, RAM usage |
| POST | `/start` | Open camera + start pipeline |
| POST | `/stop` | Clean shutdown + release camera |
| GET | `/latest` | Last cached perception frame (<10ms) |

### `/latest` Response

```json
{
  "presence": true,
  "faceVerified": false,
  "lookingAtScreen": true,
  "engagementScore": 0.87,
  "gesture": "OPEN_PALM",
  "detectedObjects": ["book", "bottle"],
  "timestamp": 1741022400.312
}
```

---

## Configuration

All tunable parameters are in `config/vision_config.py`:

```python
TARGET_FPS = 15
RESOLUTION = (640, 480)
YOLO_INTERVAL = 3          # YOLO runs every N frames
USE_GPU = False            # Toggle GPU
MAX_MEMORY_MB = 1800       # Alert threshold
GAZE_YAW_THRESHOLD = 25.0  # Degrees for "looking at screen"
```

---

## Throttle Strategy

| Pipeline | Frequency |
|----------|-----------|
| Face detection (MediaPipe) | Every frame |
| Hand / Gesture (MediaPipe) | Every frame |
| Head pose (solvePnP) | Every frame, smoothed 5-frame avg |
| Face embedding verify | Every 30 frames (~1s) |
| YOLO object detection | Every 3 frames (configurable) |
| Engagement score | Rolling 15-frame buffer average |

---

## Running Tests

```bash
cd vision_perception
pytest tests/ -v
```

Tests run **without a camera** — engine and camera are mocked.

---

## Performance Targets

- **15 FPS** stable at 640×480
- **< 80ms** full pipeline per frame
- **< 10ms** `/latest` response (memory-only read)
- **< 1.8 GB** RAM under normal operation
- **Zero coupling** to the LaRa main application
