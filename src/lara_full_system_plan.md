# LaRa -- Full System Architecture & Implementation Plan

## Hybrid Deterministic + Guided-LLM Orchestration Model

This document defines the complete system architecture, operational
modes, state transitions, tool orchestration rules, memory design, and
implementation steps.

LaRa is a regulated therapeutic AI system. The LLM is a controlled
renderer, not the core decision engine.

  ---------------------------------------
  SECTION 1 --- HIGH LEVEL ARCHITECTURE
  ---------------------------------------

                        ┌────────────────────┐
                        │      Whisper STT   │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │    MoodDetector    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │    SessionState    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │   RegulationState  │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │   DifficultyGate   │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │  RecoveryStrategy  │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │ ReinforcementMgr   │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │    ModeController  │
                        └─────────┬──────────┘
                                  │
                ┌─────────────────┴─────────────────┐
                │                                   │
        THERAPY MODE                         EXPLORATION MODE
                │                                   │
                ▼                                   ▼
        Deterministic Tool                    LLM Tool Suggestion
        Routing Only                          (Validated)
                │                                   │
                └──────────────┬────────────────────┘
                               ▼
                        ┌────────────────────┐
                        │        LLM         │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │      Kokoro TTS    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │ LearningProgress   │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │     UserMemory     │
                        └────────────────────┘

  ---------------------------------
  SECTION 2 --- OPERATIONAL MODES
  ---------------------------------

MODE 1: THERAPY MODE (Default)

-   System decides actions.
-   LLM only renders responses.
-   No autonomous tool selection.
-   Strict pacing and regulation enforced.
-   Mood directly influences strategy.
-   Difficulty adaptation active.

MODE 2: EXPLORATION MODE

-   Triggered explicitly by user intent (e.g., "show me a dinosaur
    video").
-   LLM may suggest one tool call.
-   System validates tool call.
-   Only one tool per turn allowed.
-   No recursive agent loops.
-   No chaining.

ModeController is sovereign. LLM cannot switch modes independently.

  -----------------------------------
  SECTION 3 --- MEMORY ARCHITECTURE
  -----------------------------------

1.  Short-Term Session Memory

-   Rolling 3--5 turn buffer (token-based).
-   Session summary updated every 4--6 turns.
-   Deleted after 24 hours.

2.  Structured Session State

-   Current concept
-   Current difficulty
-   Mood streak counters
-   Regulation persistence
-   Reinforcement style
-   Turn count

3.  Long-Term User Memory (SQLite)

-   Mastery levels per concept
-   Aggregated emotional metrics
-   Reinforcement preference statistics
-   Child preferences (likes/dislikes)
-   No raw transcripts stored

  ----------------------------------------
  SECTION 4 --- TOOL ORCHESTRATION MODEL
  ----------------------------------------

ToolRegistry: - show_image - show_video - start_game -
scrape_safe_content

ToolExecutionGuard: - max_tool_calls_per_turn = 1 - no recursive calls -
whitelist validation - timeout enforcement - argument validation

LLM Tool Suggestion Format (Structured JSON):

{ "action": "show_image", "query": "blue dinosaur" }

System validates before execution.

  ------------------------------------------------
  SECTION 5 --- STATE TRANSITION FLOW (PER TURN)
  ------------------------------------------------

1.  Audio input → Whisper STT
2.  MoodDetector analyzes text + prosody
3.  SessionState.update_pre_decision()
4.  RegulationState.compute()
5.  DifficultyGate.evaluate()
6.  RecoveryStrategy.generate()
7.  ReinforcementAdaptationManager.get_style()
8.  ModeController determines operational mode
9.  Tool handling:
    -   TherapyMode → deterministic tool routing
    -   ExplorationMode → LLM suggestion validated
10. LLM generates response (strategy + reinforcement context)
11. Kokoro TTS speaks with controlled pacing
12. SessionState.update_post_response()
13. LearningProgressManager.update()
14. ReinforcementAdaptationManager.update_metrics()
15. Persist aggregated metrics to UserMemory

  --------------------------------------
  SECTION 6 --- IMPLEMENTATION ROADMAP
  --------------------------------------

PHASE 1 --- Stability Core - Finalize SessionState pre/post separation -
Ensure RegulationState operates on streak persistence - Separate
DifficultyGate and LearningProgressManager fully

PHASE 2 --- Memory Enhancement - Replace raw sliding window with
token-based buffer - Add deterministic SessionSummarizer - Inject
structured learning + regulation state into LLM context

PHASE 3 --- Hybrid Mode System - Implement ModeController - Build
ToolRegistry + ToolExecutionGuard - Add structured function-calling
protocol - Enforce single-step execution

PHASE 4 --- Reinforcement Adaptation - Track reinforcement performance
metrics - Require 5+ events before adaptation - Lock style per session
once changed

PHASE 5 --- Safety Hardening - Add stimulation level caps for media
tools - Add difficulty oscillation cooldown - Add rate limiting for tool
invocation

PHASE 6 --- Dashboard Integration (Optional) - Visualize mastery
progress - Show emotional trend metrics - Never display raw emotional
labels

  ---------------------------------
  SECTION 7 --- DESIGN PRINCIPLES
  ---------------------------------

1.  Determinism over autonomy in therapy.
2.  LLM renders language, not decisions.
3.  Emotional safety overrides exploration.
4.  No uncontrolled recursion.
5.  Conservative adaptation.
6.  Predictable pacing.
7.  Structured memory, not transcript dumping.
8.  Tools are validated, never blindly executed.

  ---------------------------------------------------------------------
  FINAL STATEMENT
  ---------------------------------------------------------------------
  END OF DOCUMENT

  ---------------------------------------------------------------------
