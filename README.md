# LaRa

## Low-Cost Adaptive Robotic-AI Therapy System for Down Syndrome Children

------------------------------------------------------------------------

## Overview

LaRa (Low-Cost Adaptive Robotic-AI Therapy System) is an emotion-aware
robotic assistant designed to support children with Down syndrome in
classroom and therapeutic environments.

The system integrates computer vision, emotion recognition,
deterministic decision logic, and controlled language generation to
provide adaptive and context-aware interaction. It is structured to
ensure safety, predictability, and ethical deployment in real-world
educational settings.

LaRa does not replace therapists. It extends their reach by offering
consistent engagement support, emotional awareness, and structured
interaction monitoring.

------------------------------------------------------------------------

## Project Objective

LaRa is designed to:

-   Detect user presence using real-time face detection.
-   Estimate emotional state through a vision-based emotion recognition
    model.
-   Track engagement levels and emotional trends over time.
-   Select appropriate therapeutic response categories using
    deterministic logic.
-   Generate context-aware speech and visual guidance using a
    constrained language model.
-   Log session data for caregiver and therapist review.

The system prioritizes structured control and safety over unrestricted
AI autonomy.

------------------------------------------------------------------------

## System Architecture

LaRa is organized into four major layers:

### 1. Perception Layer

-   Captures real-time video input.
-   Performs face detection to confirm user presence.
-   Estimates emotional state using valence, arousal, and confidence
    metrics.

### 2. State Aggregation Layer

-   Applies temporal smoothing to stabilize emotion outputs.
-   Estimates engagement level.
-   Detects emotional trends (improving, declining, stable).
-   Identifies frustration indicators.

This layer ensures that decisions are based on stable behavioral context
rather than frame-level fluctuations.

### 3. Decision Engine (Finite State Machine)

-   Uses deterministic rule-based logic.
-   Selects response categories such as:
    -   Encourage
    -   Simplify
    -   Progress
    -   Pause
    -   End Session
-   Enforces safety thresholds and engagement constraints.

Behavioral decisions are governed exclusively by this module.

### 4. Narrative Generation Layer

-   Receives structured contextual state.
-   Generates speech and visual suggestions aligned with the selected
    response category.
-   Operates under strict output constraints.
-   Does not influence decision-making.

This separation ensures adaptive communication while maintaining
predictable system behavior.

------------------------------------------------------------------------

## System Flow

1.  Sensor Input (Camera / Microphone)
2.  Preprocessing (Frame normalization and synchronization)
3.  Face Detection (Presence validation)
4.  Emotion Estimation (Valence, Arousal, Confidence)
5.  State Aggregation (Trend detection and engagement scoring)
6.  Decision Engine (Response category selection)
7.  Language Generation (Context-aware speech rendering)
8.  Response Execution (Text-to-Speech and visual cues)
9.  Logging and Session Summary Generation

------------------------------------------------------------------------

## What LaRa Does

When a session begins, LaRa activates visual input and verifies user
presence. If a face is detected, emotional signals are extracted and
converted into stable internal state representations.

The decision engine evaluates engagement and emotional trends to
determine the appropriate therapeutic response type. The language
generation module produces supportive and context-aware speech aligned
with that decision.

If disengagement persists, the system pauses or ends the session. All
interactions are logged to generate structured summaries for therapists
and caregivers.

LaRa functions as a structured, adaptive engagement assistant designed
for safe and explainable interaction.

------------------------------------------------------------------------

## Expected Impact

-   Improved classroom engagement for children with Down syndrome.
-   Emotion-aware adaptive interaction.
-   Objective session monitoring for therapists and caregivers.
-   Safe, explainable, and scalable system behavior.

------------------------------------------------------------------------

LaRa demonstrates a structured integration of perception models and
language models within a safety-bounded robotic therapy support system.
