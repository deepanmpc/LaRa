
# LaRa Vision Analytics Persistence Layer
## Clean Implementation Guide

Version: 1.0
Purpose: Persist session-level vision analytics for parents and clinicians
Scope: Adds an aggregation + database layer without modifying the real-time vision pipeline

---

# 1. Current Architecture (Already Correct)

Your current system uses the correct robotics-style perception architecture.

Camera
↓
vision_perception
↓
PerceptionOutput (RAM)
↓
Session State
↓
LLM Context Injection

Key properties:

- Vision data is not written to a database
- Latest perception frame lives in RAM
- LLM receives live context snapshot
- Vision service remains stateless and fast

This prevents performance collapse from writing every frame to SQL.

Example load:

15 FPS  
900 frames / minute  
54000 frames / hour

Persisting frames would overload storage and computation.

---

# 2. What Is Missing

Parents and clinicians need **analytics**, not raw frames.

Example session insights:

- Session duration
- Focus percentage
- Distraction count
- Engagement trend
- Gesture activity
- Presence percentage

These must come from aggregated statistics.

---

# 3. Correct Solution

Introduce a Session Aggregator Layer.

Architecture:

vision_perception  
↓  
PerceptionOutput (frame data)  
↓  
Session Aggregator  
↓  
Session Summary  
↓  
Backend API  
↓  
Database  

The aggregator converts thousands of frames into a single session summary.

---

# 4. Aggregator Responsibilities

The aggregator collects metrics during the session.

Example internal counters:

frames_processed  
focused_frames  
distracted_frames  
absent_frames  
engagement_sum  
peak_engagement  
gesture_counts  
presence_frames  

Derived metrics:

focused_percent  
distracted_percent  
avg_engagement  
distraction_count  
presence_percent  
gesture_activity  

---

# 5. Session Lifecycle

Session Start:

Create row in table:

vision_sessions

Session End:

Flush aggregated metrics to database.

---

# 6. Database Tables

## vision_sessions

Stores session metadata.

id  
child_id  
session_uuid  
session_type  
started_at  
ended_at  
duration_seconds  

---

## vision_metrics

Stores aggregated vision metrics.

session_id  
focused_percent  
distracted_percent  
absent_percent  
distraction_count  
avg_engagement_score  
peak_engagement_score  
gesture_active_percent  
presence_percent  
avg_system_confidence  
avg_fps  
total_frames_processed  

---

## engagement_timeline

Used for dashboard graphs.

session_id  
minute_index  
avg_engagement  
attention_state  

Example timeline row:

minute: 3  
avg_engagement: 0.72  
attention_state: focused  

---

# 7. Aggregator Module

Create:

src/vision_perception/tracking/session_aggregator.py

Responsibilities:

- Receive PerceptionOutput frames
- Maintain counters
- Produce session summary

Example interface:

class VisionSessionAggregator:

    def ingest(frame):
        pass

    def snapshot():
        pass

    def flush():
        pass

    def reset():
        pass

---

# 8. Vision Service API

Add endpoints to vision microservice.

GET /session-metrics

Returns current aggregated snapshot.

Example:

{
  "focused_percent": 68.2,
  "distracted_percent": 21.5,
  "avg_engagement_score": 0.64,
  "distraction_count": 9
}

POST /session-flush

Returns final session metrics for database storage.

---

# 9. Backend Persistence

Spring Boot backend handles SQL writes.

Flow:

Vision Service  
↓  
Session Flush API  
↓  
Spring Backend  
↓  
Save metrics  
↓  
MySQL  

The vision microservice must remain database-free.

---

# 10. Dashboard Usage

Parents and clinicians will see:

- Engagement timeline
- Focus percentage
- Distraction events
- Gesture counts
- Session duration

These metrics power the Clinical Dashboard.

---

# 11. Critical Design Rule

Never store raw frames in SQL.

Correct:

frame data → aggregated metrics → database

Incorrect:

frame data → database

---

# 12. Final Architecture

Camera  
↓  
vision_perception  
↓  
PerceptionOutput (RAM)  
↓  
SessionAggregator  
↓  
SessionSummary  
↓  
Backend API  
↓  
MySQL Database  
↓  
Parent / Clinician Dashboard  

---

# 13. Outcome

This architecture provides:

- Real-time perception for AI tutoring
- Session analytics for parents
- Clinical insights for therapists
- Stable high-performance vision processing
