# LaRa Memory Architecture -- Full Technical Specification

## Deterministic, Structured, and Therapeutically Safe Memory System

This document defines the complete memory architecture for LaRa. It
replaces the previous draft and removes repetition. It is structured for
implementation by engineers and AI agents.

The goal of this system is:

-   Preserve educational progress
-   Preserve emotional trend metrics
-   Maintain session continuity
-   Avoid unsafe emotional labeling
-   Prevent memory hallucination
-   Maintain deterministic control

LaRa memory is NOT chat history storage. LaRa memory is structured
behavioral infrastructure.

  --------------------------------------
  SECTION 1 --- CORE MEMORY PHILOSOPHY
  --------------------------------------

1.  Memory must serve learning and regulation, not conversation realism.
2.  Memory must be structured, not narrative.
3.  Raw transcripts must never be permanently stored.
4.  Emotional states must be aggregated, never labeled permanently.
5.  Memory updates must require confidence thresholds.
6.  Session memory must expire automatically.
7.  Long-term memory must store only measurable metrics.
8.  Memory retrieval must be deterministic.
9.  LLM must never decide what to store.
10. All memory writes must pass validation guards.

  -----------------------------
  SECTION 2 --- MEMORY LAYERS
  -----------------------------

LaRa uses five memory layers:

1.  Immediate Turn Buffer (Ephemeral)
2.  Rolling Session Buffer (Short-Term)
3.  Session Summary Layer
4.  Structured Session State
5.  Long-Term User Memory (Persistent SQLite)

Each layer has different rules and lifespan.

  -------------------------------------
  SECTION 3 --- IMMEDIATE TURN BUFFER
  -------------------------------------

Purpose: Hold the most recent exchange during processing.

Rules: - Stores only current user utterance and AI response. - Exists
only during turn lifecycle. - Cleared after response is finalized. -
Never written to database. - Used only for local context injection.

  --------------------------------------
  SECTION 4 --- ROLLING SESSION BUFFER
  --------------------------------------

Purpose: Maintain short conversational continuity.

Implementation: - Token-based limit (not character-based). - Max
\~800--1200 tokens total. - Oldest entries dropped first. - Only last
3--5 structured turns retained.

Constraints: - Each entry truncated safely. - No emotional labeling
inside memory. - No summarization inside this buffer.

Deletion Policy: - Entire buffer deleted after 24 hours. - Auto-expiry
via timestamp.

  -------------------------------------
  SECTION 5 --- SESSION SUMMARY LAYER
  -------------------------------------

Purpose: Compress session history without storing transcripts.

Trigger: - Every 4--6 turns OR - When buffer exceeds 75% capacity.

Format (Structured):

SessionSummary: - Current concept: counting - Highest achieved
difficulty: 3 - Frustration events: 1 - Recovery events: 1 - Stability
trend: improving

Rules: - Deterministic format only. - No narrative storytelling. - No
emotional interpretation. - Replaces older raw turns.

  ----------------------------------------
  SECTION 6 --- STRUCTURED SESSION STATE
  ----------------------------------------

Stored in memory during active session only.

Fields:

-   user_id
-   current_concept
-   current_difficulty
-   mastery_baseline
-   mood_streak_frustrated
-   mood_streak_stable
-   emotional_trend_score
-   reinforcement_style
-   turn_count
-   exploration_mode_flag

SessionState updates occur in two phases:

Pre-Decision Update: - Mood - Streak counters

Post-Response Update: - Difficulty adjustment - Mastery updates -
Reinforcement metrics

SessionState never stored permanently.

  ----------------------------------------------
  SECTION 7 --- LONG-TERM USER MEMORY (SQLITE)
  ----------------------------------------------

Purpose: Store structured progress and aggregated metrics.

Tables:

1.  users
2.  learning_progress
3.  emotional_metrics
4.  reinforcement_metrics
5.  child_preferences

No table stores raw transcripts.

  ---------------------------------------
  SECTION 8 --- LEARNING PROGRESS TABLE
  ---------------------------------------

Fields:

-   user_id
-   concept_name
-   mastery_level (0--5)
-   total_attempts
-   successful_attempts
-   last_updated

Rules:

-   Mastery increases only after threshold of successful attempts.
-   Difficulty never reduced to zero.
-   Mastery decay optional (very slow).

  ---------------------------------------
  SECTION 9 --- EMOTIONAL METRICS TABLE
  ---------------------------------------

Fields:

-   user_id
-   frustration_count
-   recovery_count
-   stable_count
-   anxious_count
-   last_30_day_average
-   last_updated

Rules:

-   Store counts, not labels.
-   Apply decay over time (weekly normalization).
-   Never store phrases like "child is anxious."

  ----------------------------------------
  SECTION 10 --- CHILD PREFERENCE MEMORY
  ----------------------------------------

Fields:

-   user_id
-   likes (JSON array)
-   dislikes (JSON array)
-   last_updated

Extraction Method:

-   Regex or deterministic parsing only.
-   Max 20 stored preferences.
-   No inferred personality traits.

Preferences are injected naturally into LLM context.

  --------------------------------------------
  SECTION 11 --- REINFORCEMENT METRICS TABLE
  --------------------------------------------

Fields:

-   user_id
-   reinforcement_style
-   total_events
-   success_after_reinforcement
-   last_updated

Adaptation Rules:

-   Minimum 5 events before switching.
-   15% improvement threshold required.
-   Only one switch per session.

  ------------------------------------------
  SECTION 12 --- MEMORY RETRIEVAL PIPELINE
  ------------------------------------------

At session start:

1.  Load user profile.
2.  Load mastery levels.
3.  Load reinforcement preference.
4.  Load emotional aggregates.
5.  Initialize SessionState.

Per turn:

-   Retrieve only structured fields.
-   Inject structured context.
-   Inject short-term buffer.
-   Inject summary if present.

Never retrieve raw history.

  ------------------------------------
  SECTION 13 --- MEMORY UPDATE RULES
  ------------------------------------

Memory writes must:

1.  Pass confidence threshold.
2.  Pass cooldown check.
3.  Avoid duplicate writes.
4.  Log update timestamp.
5.  Avoid cross-user contamination.

All writes are atomic.

  -----------------------------
  SECTION 14 --- MEMORY DECAY
  -----------------------------

Emotional decay:

-   Weekly normalization reduces intensity.
-   Recent events weighted higher.

Mastery decay (optional):

-   Very slow decay if no practice in 90 days.

Preference decay:

-   Remove unused preferences after 6 months.

  -----------------------------------------
  SECTION 15 --- TOKEN INJECTION STRATEGY
  -----------------------------------------

LLM prompt includes:

1.  System Rules
2.  Recovery Strategy Context
3.  Reinforcement Style
4.  Learning State
5.  Session Summary
6.  Last 3 Turns
7.  User message

Never inject database tables directly.

  ---------------------------------------
  SECTION 16 --- OPTIONAL VECTOR MEMORY
  ---------------------------------------

Use only for:

-   Recalling past stories.
-   Thematic educational continuity.

Rules:

-   Store summaries only.
-   Max 3 retrievals per session.
-   Never inject raw conversation.

Vector memory is optional and not required for core therapy loop.

  ------------------------------
  SECTION 17 --- FAILURE MODES
  ------------------------------

Failure Mode 1: Mood misclassification.

Mitigation: Require persistence across 2 turns.

Failure Mode 2: Memory drift.

Mitigation: Session summary overwrite rule.

Failure Mode 3: Difficulty oscillation.

Mitigation: 2-turn cooldown rule.

Failure Mode 4: Reinforcement instability.

Mitigation: Minimum event threshold.

  ----------------------------------
  SECTION 18 --- STATE TRANSITIONS
  ----------------------------------

Session Start: Load persistent memory → Initialize session.

Turn Cycle: Analyze → Decide → Respond → Update metrics.

Session End: Persist aggregates → Clear session memory.

24-Hour Cleanup: Auto-delete session buffers.

  -----------------------------------
  SECTION 19 --- SAFETY CONSTRAINTS
  -----------------------------------

1.  Memory must not override RecoveryStrategy.
2.  Memory must not escalate difficulty abruptly.
3.  Memory must not increase stimulation automatically.
4.  Memory must not infer psychological diagnoses.
5.  Memory must remain conservative in adaptation.

  -----------------------------------------
  SECTION 20 --- IMPLEMENTATION CHECKLIST
  -----------------------------------------

-   Implement SQLite schema.
-   Implement atomic update wrapper.
-   Implement decay scheduler.
-   Implement session auto-expiry.
-   Implement structured summary generator.
-   Add logging for memory writes.
-   Validate cross-user isolation.
-   Add unit tests for retrieval logic.
-   Stress test token injection limits.
-   Review for privacy compliance.

  -----------------
  FINAL PRINCIPLE
  -----------------

LaRa memory is structured behavioral intelligence. It enables growth,
stability, and continuity without sacrificing safety.

Safety \> Structure \> Adaptation \> Personalization.

END OF DOCUMENT
