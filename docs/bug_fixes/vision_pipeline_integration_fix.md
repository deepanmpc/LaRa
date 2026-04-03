# Vision Pipeline Integration Fix
## Connecting the Vision API to the Speech Therapy Pipeline

### Problem
The Vision Perception microservice runs on port **8001** but is not connected to the main therapy pipeline. Gaze tracking, engagement detection, and object awareness are currently unused during sessions.

### Goal
Use vision signals to influence therapy behavior, such as detecting distractions and adjusting reinforcement strategies.

### Implementation Plan
- The speech pipeline will periodically query the Vision API at `http://localhost:8001/engagement`.
- If engagement is low (e.g., < 0.3), the system will force an "encourage" or "grounding" strategy.

```python
import requests

def get_vision_state():
    try:
        r = requests.get("http://localhost:8001/engagement", timeout=0.1)
        return r.json()
    except:
        return None
```
