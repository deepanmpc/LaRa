# LaRa -- Architectural Fixes & Reinforcement Adaptation Extension

## implementation_fix_and_reinforcement.md

This document defines required architectural corrections and the
controlled implementation of adaptive reinforcement style for LaRa.

This is an extension of the current pipeline:

Whisper → MoodDetector → SessionState → DifficultyGate →
RecoveryStrategy → LLM → TTS ↓ UserMemory

The following fixes and additions must be implemented deterministically.

  ------------------------------------------------
  SECTION 1 --- PIPELINE CORRECTIONS (MANDATORY)
  ------------------------------------------------

1.  SessionState Update Separation

SessionState must be updated in two phases:

Pre‑Decision Update: - Update mood - Update mood confidence - Update
consecutive frustration/stability counters

Post‑Response Update: - Update difficulty changes - Update
success/failure outcome - Update reinforcement counters - Update turn
counters

Do NOT finalize session state before DifficultyGate and RecoveryStrategy
execute.

------------------------------------------------------------------------

2.  UserMemory Read Timing

UserMemory must be loaded at session start:

At Session Initialization: - Load UserProfile - Load LearningProgress -
Load EmotionalMetrics - Inject baseline values into SessionState

During turns: - DifficultyGate reads from SessionState (not directly
from DB). - DB writes happen only after structured updates.

Never allow DifficultyGate to query SQLite every turn.

------------------------------------------------------------------------

3.  Introduce RegulationState Layer

RecoveryStrategy must not operate on raw mood directly.

Create:

class RegulationState: frustration_persistence stability_persistence
emotional_trend_score

RegulationState is computed from SessionState and passed to
RecoveryStrategy.

Raw mood classifications must not directly alter behavior.

------------------------------------------------------------------------

4.  Separate LearningProgressManager

Difficulty decisions and mastery tracking must be decoupled.

Create:

class LearningProgressManager: update_attempt(concept, difficulty,
success) update_mastery(concept) get_mastery_level(concept)

DifficultyGate: - Decides difficulty level only.

LearningProgressManager: - Updates mastery_level - Updates
success_rate - Updates attempt_count

Never mix emotional logic with mastery updates.

------------------------------------------------------------------------

5.  Emotional Metrics Storage Rule

UserMemory must store only aggregated metrics:

Allowed: - frustration_count - recovery_count -
neutral_stability_count - rolling_mood_distribution - mastery_level

Not Allowed: - Emotional transcripts - Narrative summaries - Permanent
emotional labels

Emotional metrics must decay over time.

  --------------------------------------------
  SECTION 2 --- ADAPTIVE REINFORCEMENT STYLE
  --------------------------------------------

Objective: Adapt reinforcement style based on historical response
patterns without increasing unpredictability.

Reinforcement style must be: - Structured - Deterministic - Slowly
adaptive - Based on measurable response outcomes

------------------------------------------------------------------------

1.  Reinforcement Style Types

Define controlled reinforcement categories:

-   PRAISE_BASED
-   ACHIEVEMENT_BASED
-   CALM_VALIDATION
-   PLAYFUL_ENCOURAGEMENT

Each user has a baseline reinforcement preference stored in UserProfile.

------------------------------------------------------------------------

2.  ReinforcementAdaptationManager

Create:

class ReinforcementAdaptationManager: get_style(user_id,
regulation_state) update_style_metrics(user_id, reinforcement_type,
response_outcome)

This manager must:

-   Track which reinforcement type correlates with improved stability
-   Use aggregated success metrics
-   Adapt only after statistically meaningful pattern (minimum 5 events)
-   Change reinforcement style at most once per session

------------------------------------------------------------------------

3.  Reinforcement Adaptation Rules

If user shows:

High stability after PRAISE_BASED: → Increase weight of PRAISE_BASED

Higher recovery speed after CALM_VALIDATION: → Increase weight of
CALM_VALIDATION

If playful reinforcement increases distraction: → Decrease
PLAYFUL_ENCOURAGEMENT weight

Never switch reinforcement style abruptly within the same task.

------------------------------------------------------------------------

4.  Integration into Pipeline

New Flow:

Whisper → MoodDetector → SessionState.update_mood() →
RegulationState.compute() → DifficultyGate.evaluate() →
RecoveryStrategy.generate() → ReinforcementAdaptationManager.get_style()
→ LLM.generate_response(strategy + reinforcement_style) → TTS →
LearningProgressManager.update() →
ReinforcementAdaptationManager.update_metrics() → Persist structured
metrics

------------------------------------------------------------------------

5.  LLM Governance for Reinforcement

LLM must receive structured context only:

ReinforcementStyle: PRAISE_BASED InstructionDepth: 2
ResponseLengthLimit: 2 sentences

LLM must not invent reinforcement type.

------------------------------------------------------------------------

6.  Safety Constraints

-   Reinforcement style must not escalate energy unpredictably.
-   No sudden personality shifts.
-   No sarcasm.
-   No exaggerated praise.
-   No emotional labeling.

Reinforcement must remain calm and predictable.

------------------------------------------------------------------------

## SECTION 3 --- STABILITY RULES

Reinforcement style adaptation must:

-   Require minimum 5 supporting events before change
-   Require confidence threshold \>= 0.6
-   Lock reinforcement style for remainder of session once changed
-   Persist changes only after session ends

If uncertainty exists: → Default to baseline reinforcement preference.

------------------------------------------------------------------------

## SECTION 4 --- IMPLEMENTATION ORDER

Step 1: Implement RegulationState layer.

Step 2: Separate LearningProgressManager from DifficultyGate.

Step 3: Refactor SessionState update timing.

Step 4: Implement ReinforcementAdaptationManager.

Step 5: Integrate reinforcement context into LLM call.

Step 6: Add reinforcement metrics persistence to UserMemory.

------------------------------------------------------------------------

FINAL PRINCIPLE

LaRa adapts difficulty, pacing, and reinforcement style in a controlled,
conservative, and measurable way.

LaRa does not change personality.

LaRa remains predictable, safe, and growth-oriented.

  -----------------
  END OF DOCUMENT
  -----------------
