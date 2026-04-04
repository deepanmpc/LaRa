# LaRa Dashboard — Full Database Schema & Implementation Instructions
## Agent Prompt: Complete Database + Backend + Frontend Overhaul

---

## CONTEXT & OBJECTIVE

You are working on **LaRa** — a neurodiverse therapy AI system with a Spring Boot backend, React frontend, and a Python AI pipeline. The MySQL database currently has these tables: `ai_confidence_logs`, `calibration_logs`, `children`, `clinician_profiles`, `emotional_metrics`, `knowledge_graph_edges`, `knowledge_graph_nodes`, `override_logs`, `session_summary_metrics`, `sessions`, `student_longitudinal_metrics`, `students`, `tool_interventions`, `users`, `zpd_metrics`.

**Your job is to:**
1. Replace/alter the Spring Boot JPA entity layer so ALL required tables are auto-created via `spring.jpa.hibernate.ddl-auto=update` on startup
2. Build the full REST API layer to serve real data to both Family and Clinician dashboards
3. Update the React frontend to consume real data (remove all mock services)
4. Implement child-clinician mapping with full CRUD in "Manage Children"

The Python LaRa pipeline (src/) writes data to SQLite locally. The Spring Boot dashboard must expose its own MySQL-backed analytics that receive data POSTed from the Python pipeline via HTTP after each session.

---

## PART 1: TABLES TO DROP / DEPRECATE

Remove or leave unused (do NOT delete data, just stop using):
- `students` → replaced by `children` (already exists, extend it)
- `ai_confidence_logs` → merge into `session_analytics`
- `calibration_logs` → merge into `session_analytics`
- `knowledge_graph_edges` → keep but not priority
- `knowledge_graph_nodes` → keep but not priority
- `override_logs` → keep but not priority
- `student_longitudinal_metrics` → replace with `child_learning_progress`
- `zpd_metrics` → replace with `child_learning_progress`

---

## PART 2: COMPLETE TABLE SCHEMA TO CREATE

### 2.1 RETAIN & EXTEND EXISTING TABLES

**`users`** — Already exists, keep as-is with these columns confirmed:
```
id BIGINT PK AUTO_INCREMENT
name VARCHAR(255) NOT NULL
email VARCHAR(255) UNIQUE NOT NULL
password VARCHAR(255) NOT NULL
role ENUM('ROLE_FAMILY','ROLE_CLINICIAN','ROLE_ADMIN') NOT NULL
status ENUM('ACTIVE','PENDING','APPROVED','REJECTED') NOT NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`children`** — Extend with new columns:
```
id BIGINT PK AUTO_INCREMENT
parent_id BIGINT FK → users(id) NOT NULL
assigned_clinician_id BIGINT FK → users(id) NULL   ← NEW
name VARCHAR(255) NOT NULL
age INT NOT NULL
grade_level VARCHAR(100)
date_of_birth DATE                                   ← NEW
diagnosis VARCHAR(255)                               ← NEW (e.g., ASD, ADHD, Down Syndrome)
notes TEXT                                           ← NEW (family notes)
avatar_color VARCHAR(20)                             ← NEW (hex for UI avatar)
current_focus_area VARCHAR(255)                      ← NEW (e.g., Social Scenarios)
status_badge VARCHAR(100)                            ← NEW (e.g., Doing Well, Needs Support)
weekly_session_goal INT DEFAULT 5                    ← NEW
last_session_at TIMESTAMP NULL                       ← NEW (auto-updated)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

**`clinician_profiles`** — Already exists, keep and extend:
```
id BIGINT PK AUTO_INCREMENT
user_id BIGINT FK → users(id) UNIQUE NOT NULL
phone VARCHAR(50)
organization VARCHAR(255)
license_number VARCHAR(100)
specialization VARCHAR(255)
years_of_experience INT
approval_status VARCHAR(50) DEFAULT 'PENDING'
bio TEXT                                             ← NEW
max_patients INT DEFAULT 20                          ← NEW
```

---

### 2.2 NEW CORE ANALYTICS TABLES

**`sessions`** — Extend existing:
```
id BIGINT PK AUTO_INCREMENT
session_uuid VARCHAR(36) UNIQUE NOT NULL             ← UUID from Python pipeline
child_id BIGINT FK → children(id) NOT NULL           ← CHANGE from child_id_hashed
clinician_id BIGINT FK → users(id) NULL
parent_id BIGINT FK → users(id) NULL
start_time TIMESTAMP NOT NULL
end_time TIMESTAMP NULL
duration_seconds INT
total_turns INT DEFAULT 0
peak_difficulty INT DEFAULT 1
avg_engagement_score DECIMAL(5,4) DEFAULT 0.0000
avg_mood_confidence DECIMAL(5,4) DEFAULT 0.0000
dominant_mood VARCHAR(50) DEFAULT 'neutral'
total_interventions INT DEFAULT 0
completion_status ENUM('COMPLETED','INCOMPLETE','IN_PROGRESS','CANCELLED') DEFAULT 'IN_PROGRESS'
session_notes TEXT
wake_word_triggers INT DEFAULT 0
barge_in_count INT DEFAULT 0
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`session_turn_metrics`** — Per-turn granular data from Python pipeline:
```
id BIGINT PK AUTO_INCREMENT
session_id BIGINT FK → sessions(id) NOT NULL
turn_number INT NOT NULL
timestamp TIMESTAMP NOT NULL
child_utterance TEXT
child_utterance_length INT
lara_response TEXT
detected_mood VARCHAR(50)
mood_confidence DECIMAL(5,4)
regulation_state VARCHAR(50)
frustration_persistence DECIMAL(5,4)
stability_persistence DECIMAL(5,4)
emotional_trend_score DECIMAL(5,4)
difficulty_level INT
strategy_applied VARCHAR(100)
reinforcement_style VARCHAR(100)
tts_speed DECIMAL(4,2)
prompt_build_ms INT
inference_ms INT
tts_ms INT
total_latency_ms INT
vision_presence BOOLEAN DEFAULT FALSE
vision_attention_state VARCHAR(50)
vision_engagement_score DECIMAL(5,4)
vision_gesture VARCHAR(50)
vision_distraction_frames INT DEFAULT 0
```

**`session_analytics`** — Aggregated per-session analytics (summary written at session end):
```
id BIGINT PK AUTO_INCREMENT
session_id BIGINT FK → sessions(id) UNIQUE NOT NULL
child_id BIGINT FK → children(id) NOT NULL

-- Emotional Metrics (for Family Dashboard)
overall_mood_score INT                               ← 0-100 derived score
mood_trend VARCHAR(50)                               ← Improving/Stable/Needs Support
primary_emotion VARCHAR(50)
emotion_stability_score INT                          ← 0-100
anxiety_level VARCHAR(20)                            ← Low/Medium/High
self_regulation_score INT                            ← 0-100
positive_interactions INT
challenging_moments INT

-- Emotion Breakdown Percentages (for pie/bar chart)
pct_happy DECIMAL(5,2) DEFAULT 0.00
pct_calm DECIMAL(5,2) DEFAULT 0.00
pct_focused DECIMAL(5,2) DEFAULT 0.00
pct_anxious DECIMAL(5,2) DEFAULT 0.00
pct_frustrated DECIMAL(5,2) DEFAULT 0.00
pct_sad DECIMAL(5,2) DEFAULT 0.00
pct_neutral DECIMAL(5,2) DEFAULT 0.00

-- Engagement Metrics (for Family Dashboard)
focus_score INT                                      ← 0-100
attention_span_minutes DECIMAL(5,2)
task_completion_rate INT                             ← 0-100
participation_level VARCHAR(20)                      ← Low/Medium/High
distraction_frequency VARCHAR(20)                    ← Low/Medium/High
responsiveness_score INT                             ← 0-100
initiative_taking_score INT                          ← 0-100
collaboration_score INT                              ← 0-100
weekly_goal_progress INT                             ← 0-100

-- Vision Analytics
avg_engagement_score DECIMAL(5,4)
avg_engagement_ui_score DECIMAL(5,4)
avg_gaze_score DECIMAL(5,4)
system_confidence DECIMAL(5,4)
total_distraction_frames INT DEFAULT 0
focused_duration_minutes DECIMAL(5,2)
face_confidence DECIMAL(5,4)
gesture_confidence DECIMAL(5,4)
pose_confidence DECIMAL(5,4)
object_confidence DECIMAL(5,4)

-- Voice/Prosody Analytics
speaking_rate_wpm INT
vocal_volume DECIMAL(5,4)
speech_stability_score DECIMAL(5,4)
pct_vocal_neutral DECIMAL(5,2)
pct_vocal_arousal DECIMAL(5,2)
pct_vocal_withdrawal DECIMAL(5,2)

-- Top Activities (JSON stored as text, parsed in API)
top_activities_json TEXT                             ← [{"name":"Story Sequencing","score":76,"completions":3}]

-- Session Performance
interaction_continuity_score DECIMAL(5,4)
total_engagement_average DECIMAL(5,4)
lara_response_count INT DEFAULT 0
child_utterance_count INT DEFAULT 0

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`child_learning_progress`** — Replaces zpd_metrics + student_longitudinal_metrics:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NULL

-- Curriculum / Concept Tracking
concept_name VARCHAR(255) NOT NULL                   ← e.g., counting, colors, reading
curriculum_area VARCHAR(255)                         ← e.g., Math, Language, Social Skills
topic_category VARCHAR(100)                          ← e.g., Numbers, Vocabulary, Emotions

-- Mastery
mastery_level INT DEFAULT 0                          ← 0-5
highest_mastery_reached INT DEFAULT 0
mastery_percentage DECIMAL(5,2) DEFAULT 0.00         ← 0.00-100.00
mastery_status VARCHAR(50)                           ← Not Started/In Progress/Mastered

-- Attempt Stats
attempt_count INT DEFAULT 0
success_count INT DEFAULT 0
failure_count INT DEFAULT 0
success_rate DECIMAL(5,4) DEFAULT 0.0000             ← 0.0000-1.0000

-- Time Tracking
first_attempted_at TIMESTAMP NULL
last_attempted_at TIMESTAMP NULL
last_success_at TIMESTAMP NULL
total_time_spent_seconds INT DEFAULT 0

-- Difficulty
current_difficulty INT DEFAULT 1
peak_difficulty_reached INT DEFAULT 1

UNIQUE KEY (child_id, concept_name)
```

**`child_emotional_history`** — Daily/per-session emotional aggregates for trend charts:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NULL
recorded_date DATE NOT NULL
mood_score INT                                       ← 0-100
primary_emotion VARCHAR(50)
frustration_count INT DEFAULT 0
recovery_count INT DEFAULT 0
stability_count INT DEFAULT 0
anxiety_count INT DEFAULT 0
happy_count INT DEFAULT 0
calm_count INT DEFAULT 0
focused_count INT DEFAULT 0
pct_positive DECIMAL(5,2)
pct_negative DECIMAL(5,2)
regulation_index DECIMAL(5,2)
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`child_engagement_history`** — Daily engagement trends for charts:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NULL
recorded_date DATE NOT NULL
focus_score INT
attention_span_minutes DECIMAL(5,2)
engagement_score DECIMAL(5,4)
gaze_score DECIMAL(5,4)
task_completion_rate INT
distraction_frames INT DEFAULT 0
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`child_reinforcement_metrics`** — Which reinforcement styles work for this child:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NULL
style_name VARCHAR(100) NOT NULL                     ← calm_validation/praise_based/achievement_based/playful
success_count INT DEFAULT 0
total_uses INT DEFAULT 0
success_rate DECIMAL(5,4) DEFAULT 0.0000
is_preferred BOOLEAN DEFAULT FALSE
total_events INT DEFAULT 0
last_used_at TIMESTAMP NULL
UNIQUE KEY (child_id, style_name)
```

**`child_voice_metrics`** — Aggregated vocal prosody per child:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NOT NULL
avg_speaking_rate_wpm INT
avg_volume DECIMAL(5,4)
speech_stability_score DECIMAL(5,4)
utterance_count INT DEFAULT 0
avg_utterance_length_words DECIMAL(5,2)
pct_vocal_neutral DECIMAL(5,2)
pct_vocal_arousal DECIMAL(5,2)
pct_vocal_withdrawal DECIMAL(5,2)
recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`child_vision_metrics`** — Aggregated vision/attention per child per session:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NOT NULL
avg_engagement_score DECIMAL(5,4)
avg_engagement_ui_score DECIMAL(5,4)
avg_gaze_score DECIMAL(5,4)
system_confidence DECIMAL(5,4)
face_confidence DECIMAL(5,4)
gesture_confidence DECIMAL(5,4)
pose_confidence DECIMAL(5,4)
object_confidence DECIMAL(5,4)
distraction_frames INT DEFAULT 0
focused_duration_minutes DECIMAL(5,2)
absent_frames INT DEFAULT 0
dominant_gesture VARCHAR(50)
attention_state_focused_pct DECIMAL(5,2)
attention_state_distracted_pct DECIMAL(5,2)
attention_state_absent_pct DECIMAL(5,2)
recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`child_activity_performance`** — Per-activity scores per child:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
session_id BIGINT FK → sessions(id) NULL
activity_name VARCHAR(255) NOT NULL                  ← Story Sequencing, Vocabulary Builder, etc.
curriculum_area VARCHAR(100)
score INT                                            ← 0-100
completion_count INT DEFAULT 1
total_time_seconds INT DEFAULT 0
last_played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
avg_score DECIMAL(5,2)
UNIQUE KEY (child_id, activity_name)
```

**`child_clinician_mapping`** — Many-to-many: children ↔ clinicians:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
clinician_id BIGINT FK → users(id) NOT NULL
assigned_by BIGINT FK → users(id) NOT NULL           ← who assigned (parent or admin)
assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
is_primary BOOLEAN DEFAULT TRUE
notes TEXT
status ENUM('ACTIVE','INACTIVE','PENDING') DEFAULT 'ACTIVE'
UNIQUE KEY (child_id, clinician_id)
```

**`weekly_session_summaries`** — Aggregated weekly data for family dashboard cards:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
week_start_date DATE NOT NULL
sessions_this_week INT DEFAULT 0
total_duration_minutes INT DEFAULT 0
avg_mood_score INT
avg_focus_score INT
weekly_goal_progress INT                             ← 0-100
activities_completed INT DEFAULT 0
most_recent_activity VARCHAR(255)
next_scheduled_session TIMESTAMP NULL
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
UNIQUE KEY (child_id, week_start_date)
```

**`session_difficulty_trajectory`** — Tracks difficulty changes within a session:
```
id BIGINT PK AUTO_INCREMENT
session_id BIGINT FK → sessions(id) NOT NULL
child_id BIGINT FK → children(id) NOT NULL
turn_number INT
difficulty_before INT
difficulty_after INT
direction ENUM('up','down','unchanged')
reason VARCHAR(100)                                  ← frustration/stability/manual
changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

**`child_preferences`** — Topics the child likes/dislikes (from Python pipeline):
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
topic VARCHAR(255) NOT NULL
sentiment ENUM('like','dislike') NOT NULL
detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
UNIQUE KEY (child_id, topic)
```

**`curriculum_topics`** — Master list of all available learning topics:
```
id BIGINT PK AUTO_INCREMENT
name VARCHAR(255) UNIQUE NOT NULL                    ← counting, colors, shapes, reading
area VARCHAR(100) NOT NULL                           ← Math, Language, Social, Cognitive
description TEXT
difficulty_min INT DEFAULT 1
difficulty_max INT DEFAULT 5
age_range_min INT DEFAULT 2
age_range_max INT DEFAULT 18
is_active BOOLEAN DEFAULT TRUE
```

**`child_curriculum_assignments`** — Which topics are assigned to which child:
```
id BIGINT PK AUTO_INCREMENT
child_id BIGINT FK → children(id) NOT NULL
topic_id BIGINT FK → curriculum_topics(id) NOT NULL
assigned_by BIGINT FK → users(id)
status ENUM('not_started','in_progress','mastered','paused') DEFAULT 'not_started'
assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
mastered_at TIMESTAMP NULL
current_difficulty INT DEFAULT 1
notes TEXT
UNIQUE KEY (child_id, topic_id)
```

---

## PART 3: JAVA ENTITY & CONFIGURATION CHANGES

### 3.1 application.properties
Set:
```
spring.jpa.hibernate.ddl-auto=update
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQL8Dialect
```
This ensures ALL new entities auto-create their tables on startup.

### 3.2 Create JPA Entity Classes

Create the following entity files in `dashboard/backend/src/main/java/com/lara/dashboard/entity/`:

1. **`SessionTurnMetric.java`** — maps to `session_turn_metrics`
2. **`SessionAnalytics.java`** — maps to `session_analytics`
3. **`ChildLearningProgress.java`** — maps to `child_learning_progress`
4. **`ChildEmotionalHistory.java`** — maps to `child_emotional_history`
5. **`ChildEngagementHistory.java`** — maps to `child_engagement_history`
6. **`ChildReinforcementMetrics.java`** — maps to `child_reinforcement_metrics`
7. **`ChildVoiceMetrics.java`** — maps to `child_voice_metrics`
8. **`ChildVisionMetrics.java`** — maps to `child_vision_metrics`
9. **`ChildActivityPerformance.java`** — maps to `child_activity_performance`
10. **`ChildClinicianMapping.java`** — maps to `child_clinician_mapping`
11. **`WeeklySessionSummary.java`** — maps to `weekly_session_summaries`
12. **`SessionDifficultyTrajectory.java`** — maps to `session_difficulty_trajectory`
13. **`ChildPreference.java`** — maps to `child_preferences`
14. **`CurriculumTopic.java`** — maps to `curriculum_topics`
15. **`ChildCurriculumAssignment.java`** — maps to `child_curriculum_assignments`

**For each entity, use:**
```java
@Entity
@Table(name = "table_name_here")
@Data @Builder @NoArgsConstructor @AllArgsConstructor
```
With full Lombok annotations, proper `@ManyToOne`/`@OneToMany` JPA relationships, `@CreationTimestamp`, and all columns as `@Column` with correct nullable/unique constraints matching the schema above.

**Extend `Child.java`** to add:
```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "assigned_clinician_id")
private User assignedClinician;

private String diagnosis;
private String notes;
private String avatarColor;
private String currentFocusArea;
private String statusBadge;
private Integer weeklySessionGoal = 5;

@Column(name = "last_session_at")
private LocalDateTime lastSessionAt;
```

**Extend `Session.java`** to replace `childIdHashed` with:
```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "child_id", nullable = false)
private Child child;

private String sessionUuid;
private Integer totalTurns;
private Integer peakDifficulty;
private BigDecimal avgEngagementScore;
private BigDecimal avgMoodConfidence;
private String dominantMood;
private Integer totalInterventions;
private Integer wakeWordTriggers;
private Integer bargeInCount;
```

---

## PART 4: REPOSITORY LAYER

Create the following Spring Data JPA repositories in `dashboard/backend/src/main/java/com/lara/dashboard/repository/`:

```java
// SessionAnalyticsRepository
Optional<SessionAnalytics> findBySessionId(Long sessionId);
List<SessionAnalytics> findByChildIdOrderByCreatedAtDesc(Long childId);

// ChildLearningProgressRepository
List<ChildLearningProgress> findByChildId(Long childId);
Optional<ChildLearningProgress> findByChildIdAndConceptName(Long childId, String conceptName);
List<ChildLearningProgress> findByChildIdAndMasteryStatus(Long childId, String status);

// ChildEmotionalHistoryRepository
List<ChildEmotionalHistory> findByChildIdAndRecordedDateBetween(Long childId, LocalDate from, LocalDate to);
List<ChildEmotionalHistory> findTop7ByChildIdOrderByRecordedDateDesc(Long childId);

// ChildEngagementHistoryRepository
List<ChildEngagementHistory> findTop7ByChildIdOrderByRecordedDateDesc(Long childId);

// ChildReinforcementMetricsRepository
List<ChildReinforcementMetrics> findByChildId(Long childId);

// ChildClinicianMappingRepository
List<ChildClinicianMapping> findByClinicianId(Long clinicianId);
List<ChildClinicianMapping> findByChildId(Long childId);
Optional<ChildClinicianMapping> findByChildIdAndClinicianIdAndStatus(Long childId, Long clinicianId, String status);

// WeeklySessionSummaryRepository
Optional<WeeklySessionSummary> findByChildIdAndWeekStartDate(Long childId, LocalDate weekStart);
List<WeeklySessionSummary> findTop4ByChildIdOrderByWeekStartDateDesc(Long childId);

// ChildActivityPerformanceRepository
List<ChildActivityPerformance> findByChildIdOrderByAvgScoreDesc(Long childId);

// ChildCurriculumAssignmentRepository
List<ChildCurriculumAssignment> findByChildId(Long childId);
List<ChildCurriculumAssignment> findByChildIdAndStatus(Long childId, String status);

// SessionTurnMetricRepository
List<SessionTurnMetric> findBySessionIdOrderByTurnNumberAsc(Long sessionId);
```

---

## PART 5: SERVICE & CONTROLLER CHANGES

### 5.1 New Session Ingestion Endpoint

Create `POST /api/pipeline/session-complete` — called by Python pipeline at session end.

**Request body (`SessionCompleteRequest.java`):**
```json
{
  "sessionUuid": "string",
  "childId": 123,
  "startTime": "ISO timestamp",
  "endTime": "ISO timestamp",
  "durationSeconds": 1800,
  "totalTurns": 45,
  "peakDifficulty": 3,
  "dominantMood": "happy",
  "avgMoodConfidence": 0.72,
  "avgEngagementScore": 0.81,
  "totalInterventions": 12,
  "wakeWordTriggers": 2,
  "bargeInCount": 1,
  
  "emotionalData": {
    "overallMoodScore": 72,
    "moodTrend": "Improving",
    "primaryEmotion": "Happy",
    "emotionStabilityScore": 79,
    "anxietyLevel": "Low",
    "selfRegulationScore": 99,
    "positiveInteractions": 8,
    "challengingMoments": 2,
    "pctHappy": 36.0,
    "pctCalm": 43.0,
    "pctFocused": 20.0,
    "pctAnxious": 9.0,
    "pctFrustrated": 0.0,
    "pctNeutral": 2.0
  },
  
  "engagementData": {
    "focusScore": 85,
    "attentionSpanMinutes": 15.5,
    "taskCompletionRate": 84,
    "participationLevel": "High",
    "distractionFrequency": "Low",
    "responsivenessScore": 90,
    "initiativeTakingScore": 77,
    "collaborationScore": 77,
    "weeklyGoalProgress": 86
  },
  
  "visionData": {
    "avgEngagementScore": 0.81,
    "avgEngagementUiScore": 0.85,
    "avgGazeScore": 0.76,
    "systemConfidence": 0.91,
    "faceConfidence": 0.89,
    "gestureConfidence": 0.82,
    "poseConfidence": 0.85,
    "objectConfidence": 0.77,
    "totalDistractionFrames": 45,
    "focusedDurationMinutes": 12.3,
    "attentionFocusedPct": 78.0,
    "attentionDistractedPct": 18.0,
    "attentionAbsentPct": 4.0
  },
  
  "voiceData": {
    "speakingRateWpm": 112,
    "avgVolume": 0.68,
    "speechStabilityScore": 0.82,
    "utteranceCount": 45,
    "pctVocalNeutral": 62.0,
    "pctVocalArousal": 23.0,
    "pctVocalWithdrawal": 15.0
  },
  
  "learningProgress": [
    {
      "conceptName": "counting",
      "curriculumArea": "Math",
      "masteryLevel": 3,
      "masteryPercentage": 60.0,
      "successRate": 0.78,
      "attemptCount": 12,
      "successCount": 9,
      "currentDifficulty": 3
    }
  ],
  
  "reinforcementData": {
    "calmValidationSuccess": 8,
    "calmValidationTotal": 10,
    "praisedBasedSuccess": 4,
    "praisedBasedTotal": 6,
    "achievementBasedSuccess": 2,
    "achievementBasedTotal": 4,
    "playfulSuccess": 1,
    "playfulTotal": 2,
    "preferredStyle": "calm_validation"
  },
  
  "topActivities": [
    {"name": "Story Sequencing", "score": 76, "completions": 3},
    {"name": "Vocabulary Builder", "score": 78, "completions": 4},
    {"name": "Reading Comprehension", "score": 84, "completions": 2},
    {"name": "Social Scenarios", "score": 70, "completions": 1}
  ],
  
  "difficultyTrajectory": [
    {"turnNumber": 5, "before": 2, "after": 3, "direction": "up", "reason": "stability"},
    {"turnNumber": 22, "before": 3, "after": 2, "direction": "down", "reason": "frustration"}
  ],
  
  "turns": [
    {
      "turnNumber": 1,
      "timestamp": "ISO timestamp",
      "childUtterance": "...",
      "laraResponse": "...",
      "detectedMood": "neutral",
      "moodConfidence": 0.6,
      "difficultyLevel": 2,
      "strategyApplied": "neutral",
      "reinforcementStyle": "calm_validation",
      "promptBuildMs": 12,
      "inferenceMs": 340,
      "ttsMs": 180,
      "totalLatencyMs": 532,
      "visionPresence": true,
      "visionAttentionState": "FOCUSED",
      "visionEngagementScore": 0.85,
      "visionGesture": "OPEN_PALM",
      "visionDistractionFrames": 0
    }
  ]
}
```

This endpoint must:
1. Create/update the `sessions` record
2. Insert all `session_turn_metrics` records
3. Insert `session_analytics` record
4. Insert `child_emotional_history` for today's date
5. Insert `child_engagement_history` for today's date
6. Upsert `child_learning_progress` for each concept
7. Upsert `child_reinforcement_metrics` for each style
8. Insert `child_vision_metrics`
9. Insert `child_voice_metrics`
10. Upsert `child_activity_performance` for each activity
11. Insert `session_difficulty_trajectory` entries
12. Update `children.last_session_at` and `children.current_focus_area`
13. Upsert `weekly_session_summaries` for the current week

### 5.2 Family Dashboard API

**`GET /api/family/dashboard/{childId}`** — Return real data:

Response structure:
```json
{
  "childProfile": {
    "name": "string",
    "age": 2,
    "gradeLevel": "string",
    "diagnosis": "string",
    "assignedClinician": "Dr. Sarah Mitchell",
    "currentFocus": "Social Scenarios",
    "lastSessionTime": "Today, 2:30 PM",
    "statusBadge": "Doing Well",
    "therapistAssigned": "Dr. Sarah Mitchell"
  },
  "sessionSummary": {
    "totalSessionsThisWeek": 3,
    "totalSessionsAllTime": 23,
    "todaySessionDuration": "34 minutes",
    "averageSessionDuration": "28 minutes",
    "lastActivityCompleted": "Vocabulary Builder",
    "nextScheduledSession": "Tomorrow, 3:00 PM",
    "weeklyGoalProgress": 86,
    "activitiesCompletedToday": 4,
    "recentSessions": {
      "Monday": {"duration": "30 min", "mood": "Happy", "score": 82},
      "Tuesday": {"duration": "28 min", "mood": "Calm", "score": 78}
    }
  },
  "emotionalMetrics": {
    "overallMoodScore": 72,
    "moodTrend": "Improving",
    "primaryEmotion": "Happy",
    "emotionStability": 79,
    "anxietyLevel": "Low",
    "selfRegulationScore": 99,
    "positiveInteractions": 8,
    "challengingMoments": 2,
    "weeklyMoodData": [
      {"day": "Mon", "score": 68},
      {"day": "Tue", "score": 72},
      {"day": "Wed", "score": 75},
      {"day": "Thu", "score": 72},
      {"day": "Fri", "score": 80}
    ],
    "emotionBreakdown": {
      "Happy": 36,
      "Calm": 43,
      "Focused": 20,
      "Anxious": 9,
      "Frustrated": 0
    }
  },
  "engagementMetrics": {
    "focusScore": 85,
    "attentionSpanMinutes": 15,
    "taskCompletionRate": 84,
    "participationLevel": "High",
    "distractionFrequency": "Low",
    "responsiveness": 90,
    "initiativeTaking": 77,
    "collaborationScore": 77,
    "weeklyFocusData": [
      {"day": "Mon", "focus": 82, "attention": 14},
      {"day": "Tue", "focus": 85, "attention": 15}
    ],
    "topActivities": [
      {"name": "Story Sequencing", "score": 76, "completions": 3},
      {"name": "Vocabulary Builder", "score": 78, "completions": 4},
      {"name": "Reading Comprehension", "score": 84, "completions": 2},
      {"name": "Social Scenarios", "score": 70, "completions": 1}
    ]
  }
}
```

This endpoint MUST pull from real database tables, NOT mock data. Remove `MockFamilyDashboardService` entirely and replace with `RealFamilyDashboardService` that queries the new tables.

### 5.3 Clinician Dashboard API

**`GET /api/clinician/students/{childId}/analytics`** — Full clinical analytics:

```json
{
  "patient": {
    "name": "string",
    "age": 6,
    "diagnosis": "ASD",
    "gradeLevel": "1st Grade",
    "assignedClinicians": [{"id": 1, "name": "Dr. Smith", "isPrimary": true}]
  },
  "learningProgress": {
    "conceptName": "counting",
    "masteryLevel": 3,
    "masteryPercentage": 60.0,
    "attemptCount": 45,
    "successRate": 0.78,
    "currentDifficulty": 3,
    "masteryStatus": "In Progress"
  },
  "allConcepts": [
    {
      "conceptName": "counting",
      "curriculumArea": "Math",
      "masteryLevel": 3,
      "masteryPercentage": 60.0,
      "successRate": 0.78,
      "status": "in_progress"
    }
  ],
  "emotionalMetrics": {
    "frustrationCount": 8,
    "recoveryCount": 12,
    "neutralStabilityCount": 35,
    "stabilityIndex": 87
  },
  "userProfiles": {
    "preferredTopics": ["Animals", "Counting", "Colors"],
    "instructionDepth": 2
  },
  "reinforcementMetrics": {
    "calmValidation": 0.82,
    "praiseBased": 0.71,
    "achievementBased": 0.65,
    "playful": 0.58,
    "preferredStyle": "calm_validation",
    "totalEvents": 87
  },
  "visionSessionStats": {
    "avgEngagementScore": 0.81,
    "avgGazeScore": 0.76,
    "systemConfidence": 0.91
  },
  "visionBehaviorCounts": {
    "distractionFrames": 45,
    "focusedDuration": 12.3
  },
  "perceptionConfidence": {
    "faceConf": 0.89,
    "gestureConf": 0.82,
    "objectConf": 0.77
  },
  "voiceProsodyMetrics": {
    "speakingRate": 112,
    "volume": 0.68,
    "stabilityScore": 0.82
  },
  "vocalMoodDistribution": {
    "neutral": 0.62,
    "arousal": 0.23,
    "withdrawal": 0.15
  },
  "totalEngagementSummary": {
    "totalEngagementAverage": 0.81,
    "interactionContinuityScore": 0.87,
    "sessionDuration": 28.5
  },
  "curriculumAssignments": [
    {
      "topicName": "counting",
      "area": "Math",
      "status": "in_progress",
      "masteryPercentage": 60.0,
      "assignedAt": "2026-03-01"
    }
  ],
  "sessionHistory": [
    {
      "sessionUuid": "string",
      "date": "Apr 3, 2026",
      "duration": "34 min",
      "peakDifficulty": 3,
      "dominantMood": "happy",
      "avgEngagement": 0.81,
      "totalTurns": 45
    }
  ]
}
```

---

## PART 6: CHILD MANAGEMENT — ADD/DELETE/EDIT + CLINICIAN MAPPING

### 6.1 New API Endpoints for Child Management

**`GET /api/children`** — List children for logged-in parent (already exists, extend response)

**`POST /api/children`** — Create child (extend to include diagnosis, notes, assignedClinicianId)

**`PUT /api/children/{id}`** — Full edit of child details:
```json
{
  "name": "string",
  "age": 6,
  "gradeLevel": "1st Grade",
  "diagnosis": "ASD",
  "notes": "Responds well to visual cues",
  "avatarColor": "#3b82f6",
  "weeklySessionGoal": 5
}
```

**`DELETE /api/children/{id}`** — Delete child (only allowed by parent who owns it or admin)

**`POST /api/children/{childId}/assign-clinician`** — Map a clinician to a child:
```json
{
  "clinicianId": 5,
  "isPrimary": true,
  "notes": "Assigned for ABA therapy"
}
```

**`DELETE /api/children/{childId}/clinicians/{clinicianId}`** — Remove mapping

**`GET /api/children/{childId}/clinicians`** — List assigned clinicians

**`GET /api/clinicians/available`** — List all APPROVED clinicians (for assignment dropdown)

### 6.2 Frontend — ChildrenList.jsx Changes

Update the `ChildCard` component to show:
- Delete button (🗑️) with confirmation modal
- Edit button (✏️) opening an edit modal
- Assigned clinician name under child info
- Last session date (from DB, not "Never" static)

Update `AddChildModal.jsx` to include:
- diagnosis field (optional)
- notes field (optional)
- Clinician assignment dropdown (fetches from `/api/clinicians/available`)
- Edit mode (prefill form for PUT request)

Create `EditChildModal.jsx` for editing existing child details.

Create `ClinicianAssignmentModal.jsx` for:
- Viewing currently assigned clinicians
- Adding a new clinician from dropdown
- Removing a clinician assignment
- Setting primary clinician

---

## PART 7: PYTHON PIPELINE → DASHBOARD BRIDGE

### 7.1 Modify Python `src/session/session_state.py`

At session end (called from `src/main.py` in the `finally` block after `run_conversation_loop` returns), add a call to POST session data to the Spring Boot API:

Create `src/bridge/dashboard_reporter.py`:
```python
import requests
import logging

DASHBOARD_API_URL = "http://localhost:8080/api/pipeline/session-complete"

def report_session_to_dashboard(session_data: dict, child_id: int):
    """
    Post completed session analytics to the Spring Boot dashboard.
    Non-blocking — failures are logged but do not crash the pipeline.
    """
    try:
        payload = session_data.copy()
        payload["childId"] = child_id
        response = requests.post(
            DASHBOARD_API_URL,
            json=payload,
            timeout=5.0
        )
        if response.ok:
            logging.info(f"[DashboardReporter] Session reported successfully")
        else:
            logging.warning(f"[DashboardReporter] Failed: {response.status_code}")
    except Exception as e:
        logging.warning(f"[DashboardReporter] Could not reach dashboard: {e}")
```

Add to `config/config.yaml`:
```yaml
dashboard:
  api_url: "http://localhost:8080"
  child_id: 1          # Default child ID for single-child mode
  enabled: true
```

### 7.2 Session Data Aggregation

In `src/perception/speech_to_text.py`, at the end of `run_conversation_loop`, collect and build the full `SessionCompleteRequest` JSON from:
- `session` (SessionState object) → turns, difficulty, mood data
- `mood_detector._mood_history` → emotion breakdown percentages
- `learning_manager` → learning progress per concept
- `reinforcement_manager._session_metrics` → reinforcement data
- Vision bridge state snapshots (aggregated over session)
- PerformanceMonitor history → latency data
- All turn-level data accumulated in session

Then call `report_session_to_dashboard(payload, child_id)`.

---

## PART 8: REMOVE ALL MOCK DATA

### 8.1 Delete / Replace Mock Services

- **DELETE** `MockFamilyDashboardService.java` entirely
- **CREATE** `RealFamilyDashboardService.java` that queries:
  - `children` + `users` (clinician join) for childProfile
  - `weekly_session_summaries` for sessionSummary
  - `session_analytics` + `child_emotional_history` for emotionalMetrics
  - `child_engagement_history` + `child_activity_performance` for engagementMetrics

- **UPDATE** `FamilyController.java` to inject and use `RealFamilyDashboardService`

- **UPDATE** `ClinicianController.java` `/students/{id}` to return real analytics from `ChildAnalyticsService`

- **UPDATE** `AdminController.java` to return real counts from actual tables

---

## PART 9: FRONTEND UPDATES

### 9.1 FamilyDashboard.jsx

- Remove all local seeded/random data
- Fetch from `GET /api/family/dashboard/{childId}` 
- Weekly mood chart: render `emotionalMetrics.weeklyMoodData` (7-day real data)
- Weekly focus chart: render `engagementMetrics.weeklyFocusData` (7-day real data)
- Emotion breakdown: render exact percentages from `emotionalMetrics.emotionBreakdown`
- All scores (mood, focus, stability, self-regulation) must show exact integer values from DB

### 9.2 ClinicianStudentDetail.jsx + ClinicalStudentSections.jsx

- Replace `getSeededMock()` with real API call to `GET /api/clinician/students/{id}/analytics`
- All 6 clinical sections must render real data:
  - Section 1 (Cognitive): mastery level, success rate, attempt count from `child_learning_progress`
  - Section 2 (Emotional): frustration/recovery/stability from `child_emotional_history`
  - Section 3 (Sensory): vision metrics from `child_vision_metrics`
  - Section 4 (Voice): prosody from `child_voice_metrics`
  - Section 5 (Engagement): totals from `session_analytics`
  - Section 6 (Reinforcement): style rankings from `child_reinforcement_metrics`

### 9.3 ChildrenList.jsx

- Add delete icon (🗑️) to each ChildCard — calls `DELETE /api/children/{id}`
- Add edit icon (✏️) to each ChildCard — opens EditChildModal
- Add "Manage Clinicians" button — opens ClinicianAssignmentModal
- Show assigned clinician name on card
- Show real `lastSessionDate` (not "Never" always)

### 9.4 New Frontend Components Needed

- `EditChildModal.jsx` — edit child name, age, grade, diagnosis, notes
- `ClinicianAssignmentModal.jsx` — view/add/remove clinician assignments
- `DeleteChildConfirmModal.jsx` — confirmation before delete

---

## PART 10: DATA SEEDING

### 10.1 CurriculumTopicSeeder.java

Create a seeder that runs on startup (implements `ApplicationRunner`) to populate `curriculum_topics` with:

```
Math: counting, addition, subtraction, shapes, patterns, numbers 1-10, numbers 1-100
Language: vocabulary, reading comprehension, story sequencing, letter recognition, phonics, sight words
Social Skills: social scenarios, emotions recognition, turn-taking, sharing, greetings
Cognitive: memory, attention, problem solving, categorization, sequencing
Communication: verbal expression, responding to questions, following instructions
```

Each with appropriate `difficulty_min`, `difficulty_max`, `age_range_min`, `age_range_max`.

---

## PART 11: SECURITY & VALIDATION

- `DELETE /api/children/{id}`: verify the authenticated user is the parent owner OR admin
- `POST /api/children/{childId}/assign-clinician`: verify authenticated user is parent of that child OR admin
- `GET /api/family/dashboard/{childId}`: verify the child belongs to the authenticated family user
- `GET /api/clinician/students/{id}/analytics`: verify a mapping exists in `child_clinician_mapping` between clinician and child, OR user is admin
- Add `@PreAuthorize` annotations on all new endpoints

---

## PART 12: EXECUTION ORDER

Implement in this exact order to avoid breaking changes:

1. Add new entity classes (no deletions yet) → JPA auto-creates new tables
2. Extend `Child.java` and `Session.java` with new fields
3. Create all new repositories
4. Create `SessionCompleteRequest.java` DTO and ingestion service
5. Create `POST /api/pipeline/session-complete` endpoint
6. Create `RealFamilyDashboardService.java`
7. Update `FamilyController` to use real service
8. Create `ChildAnalyticsService.java` for clinician analytics
9. Update `ClinicianController` to use real analytics service
10. Add child CRUD endpoints (PUT, DELETE)
11. Add clinician mapping endpoints
12. Update React frontend components
13. Create Python `dashboard_reporter.py`
14. Hook reporter into `src/main.py` session lifecycle
15. Create `CurriculumTopicSeeder.java`
16. Test end-to-end: run a Python session → verify data in MySQL → verify dashboard displays real data
17. Delete `MockFamilyDashboardService.java`

---

## PART 13: KEY CONSTRAINTS & RULES

1. **NEVER delete existing tables** — only add new ones or add columns to existing ones
2. **`spring.jpa.hibernate.ddl-auto=update`** must be set — all tables are created by JPA automatically on startup, no manual SQL files
3. **All foreign keys use BIGINT** matching the existing `users.id` and `children.id` primary keys
4. **Decimal precision**: engagement/confidence scores use `DECIMAL(5,4)` (e.g., 0.8123), percentages use `DECIMAL(5,2)` (e.g., 36.50), scores use `INT` (0-100)
5. **No mock data in production controllers** — `MockFamilyDashboardService` is only for initial dev, must be replaced
6. **Python pipeline reports via HTTP** — the Python side never writes directly to MySQL, it POSTs to Spring Boot API
7. **Child-clinician mapping is many-to-many** — one child can have multiple clinicians, one clinician can have many children
8. **Weekly summaries are upserted** — each week has one summary row per child, updated after each session in that week
9. **Emotion percentages must sum to ~100%** — validate this in the service layer before writing
10. **Session UUID must be unique** — generated by Python, used to prevent duplicate session ingestion

---

## SUMMARY: Tables to CREATE (new)

| Table | Purpose |
|-------|---------|
| `session_turn_metrics` | Per-turn granular data |
| `session_analytics` | Per-session aggregated dashboard data |
| `child_learning_progress` | Concept mastery tracking |
| `child_emotional_history` | Daily emotional trends |
| `child_engagement_history` | Daily engagement trends |
| `child_reinforcement_metrics` | Which styles work per child |
| `child_voice_metrics` | Per-session voice/prosody |
| `child_vision_metrics` | Per-session vision/attention |
| `child_activity_performance` | Per-activity scores |
| `child_clinician_mapping` | Child ↔ Clinician assignments |
| `weekly_session_summaries` | Weekly rollups for family dashboard |
| `session_difficulty_trajectory` | Difficulty change history |
| `child_preferences` | Liked/disliked topics |
| `curriculum_topics` | Master topic catalog |
| `child_curriculum_assignments` | Which topics assigned to which child |

## Summary: Tables to EXTEND (alter by adding columns)

| Table | New Columns |
|-------|------------|
| `children` | `assigned_clinician_id`, `diagnosis`, `notes`, `avatar_color`, `current_focus_area`, `status_badge`, `weekly_session_goal`, `last_session_at` |
| `sessions` | `session_uuid`, `child_id` (FK replacing hashed), `total_turns`, `peak_difficulty`, `avg_engagement_score`, `dominant_mood`, `wake_word_triggers`, `barge_in_count` |
| `clinician_profiles` | `bio`, `max_patients` |

## Summary: Tables to DEPRECATE (stop using, don't delete)

- `students` (use `children` instead)
- `ai_confidence_logs` (merge into `session_analytics`)
- `calibration_logs` (merge into `session_analytics`)
- `student_longitudinal_metrics` (replaced by `child_learning_progress`)
- `zpd_metrics` (replaced by `child_learning_progress`)
