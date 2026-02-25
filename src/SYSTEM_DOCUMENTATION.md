# LaRa — Complete System Documentation

> **LaRa** (Low-Cost Adaptive Robotic-AI Therapy System) is a real-time conversational AI assistant designed specifically for children with Down syndrome and neurodiverse children. Every architectural decision prioritizes **emotional safety**, **predictability**, and **privacy** over intelligence or novelty.

---

## System Architecture

```
┌─────────────┐     ┌───────────────┐     ┌──────────────────┐
│  Microphone  │────▶│  Whisper STT   │────▶│   MoodDetector    │
│  (16kHz)     │     │  (small.en)    │     │  (text + audio)   │
└─────────────┘     └───────────────┘     └────────┬─────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────┐
                                          │  SessionState     │
                                          │  .update_pre()    │
                                          │  (mood + streaks) │
                                          └────────┬─────────┘
                                                    │
                                          ┌─────────▼─────────┐
                                          │  RegulationState   │
                                          │  (normalized       │
                                          │   persistence)     │
                                          └────────┬──────────┘
                                                    │
                              ┌─────────────────────┼─────────────────────┐
                              ▼                     ▼                     ▼
                    ┌──────────────┐     ┌──────────────────┐   ┌────────────────────┐
                    │ Difficulty   │     │ RecoveryStrategy  │   │ Reinforcement      │
                    │ Gate         │     │ Manager           │   │ Adaptation Manager │
                    │ (+1/-1/lock) │     │ (mood→strategy)   │   │ (style selection)  │
                    └──────┬───────┘     └────────┬─────────┘   └────────┬───────────┘
                           │                      │                      │
                           │              ┌───────▼──────────────────────▼──┐
                           │              │  LLM (Ollama)                   │
                           │              │  strategy.prompt_addition       │
                           │              │  + reinforcement_context        │
                           │              └──────────────┬─────────────────┘
                           │                             │
                           │                    ┌────────▼────────┐
                           │                    │  Kokoro TTS      │
                           │                    │  (af_bella voice) │
                           │                    │  speed = strategy │
                           │                    └────────┬────────┘
                           │                             │
                           ▼                             ▼
                    ┌──────────────┐            ┌─────────────────┐
                    │ SessionState │            │   Speaker        │
                    │ .update_post │            │   (Audio Out)    │
                    │ (finalize)   │            └─────────────────┘
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ UserMemory   │
                    │ (SQLite)     │
                    │ persist      │
                    └──────────────┘
```

---

## File-by-File Documentation

---

### 1. `whispercpp_STT.py` — Main Loop & Orchestrator

**Purpose:** The central orchestrator that ties every component together. Handles microphone input, voice activity detection, wake-word activation, transcription, and the full conversation pipeline.

**Key Features:**

| Feature | How It Works |
|---|---|
| **Voice Activity Detection** | WebRTC VAD + RMS noise gate detects when the child is speaking |
| **Wake Word** | Says "friday" to activate, "shutdown" to sleep |
| **Barge-In Detection** | If the child speaks while LaRa is talking, LaRa stops mid-sentence |
| **KWS During TTS** | Continuously monitors for wake-word even while LaRa is speaking |
| **Pipeline Orchestration** | Calls every component in the correct order (see architecture diagram) |

**Conversation Flow (per turn):**
1. Whisper transcribes speech
2. MoodDetector analyzes text + audio → `detected_mood`, `mood_conf`
3. `SessionState.update_pre_decision()` — updates mood and streaks
4. Recovery detection — if mood transitioned from frustrated→stable, record it
5. DifficultyGate — check if difficulty should change
6. `compute_regulation_state()` — normalize streaks for strategy layer
7. `RecoveryStrategyManager.get_strategy()` — select behavioral parameters
8. `ReinforcementAdaptationManager.get_style()` — select reinforcement style
9. `LLM.generate_response_stream()` — generate response with strategy + reinforcement
10. `validate_response()` — clean up LLM output
11. `SessionState.update_post_response()` — finalize turn
12. `UserMemory.record_emotional_metric()` — persist aggregated counts
13. Kokoro TTS speaks the response at strategy-controlled speed

---

### 2. `mood_detector.py` — Mood Detection Engine

**Purpose:** Analyzes both text content and audio prosody to determine the child's emotional state. Uses a conservative, multi-signal approach.

**Mood Categories:**
| Mood | Meaning |
|---|---|
| `neutral` | Default state, no strong emotional signal |
| `happy` | Positive engagement, enthusiasm |
| `frustrated` | Difficulty, struggle, annoyance |
| `anxious` | Uncertainty, worry, nervousness |
| `sad` | Low mood, withdrawal |
| `quiet` | Disengagement, silence (NOT the same as sad) |

**Detection Methods:**

- **Text Analysis** — Regex word-boundary keyword matching (`\b` boundaries to prevent false positives like "the**rap**y" → "rap"). Keywords for each mood category with confidence scores.
- **Audio Analysis** — RMS energy (volume) and speaking rate (words/second). Loud audio is disambiguated with text mood (loud + happy text = happy, loud + frustrated text = frustrated, loud + unclear = anxious).
- **Signal Combination** — Text weight 60%, audio weight 40% (dynamic: reduces text weight to 35% when text confidence is very low to avoid transcription error influence).
- **Temporal Smoothing** — 3-utterance sliding window, requires 2-of-3 consensus to change mood. Prevents single-utterance reactions.
- **Mood Decay** — 2 consecutive neutral readings decay confidence by 0.8×. Falls back to neutral if confidence drops below threshold.

**Safety Rules:**
- Never speaks mood labels aloud
- False negatives preferred over false positives
- Speaking rate capped at 6.0 words/sec, ignored for utterances < 0.5s
- Quiet ≠ Sad (explicitly separated)

---

### 3. `recovery_strategy.py` — Recovery Strategy Layer

**Purpose:** Translates detected mood + confidence into structured behavioral parameters. This is the control layer between mood detection and the LLM/TTS — mood never directly alters LLM output.

**RecoveryStrategy Dataclass Fields:**

| Field | Type | Purpose |
|---|---|---|
| `response_length_limit` | int (1-3) | Max sentences in LLM response |
| `instruction_depth` | int (1-3) | Complexity of instructions |
| `tts_length_scale` | float | Kokoro TTS speed (lower = slower) |
| `reassurance_level` | int (0-3) | How much reassurance to add |
| `task_difficulty_modifier` | int (-1, 0) | Difficulty adjustment (never below -1) |
| `prompt_addition` | str | Behavioral instruction injected into LLM prompt |
| `label` | str | For logging |

**Dual Strategy Tables:**
- **High confidence (≥0.5):** Full adaptation — adjusts response length, TTS speed, instruction depth, AND task difficulty
- **Low confidence (<0.5):** Conservative — only adjusts tone (TTS speed, light reassurance). No task difficulty changes.

**Per-Mood Strategies:**

| Mood | Response Length | TTS Speed | Difficulty | Key Behavior |
|---|---|---|---|---|
| Neutral | 3 sentences | 0.9 | unchanged | Normal operation |
| Happy | 3 sentences | 0.9 | unchanged | Mirror energy gently |
| Frustrated | 2 sentences | 0.8 (slower) | -1 (easier) | Simplify, break into steps |
| Anxious | 2 sentences | 0.78 (slow) | unchanged | Grounding phrases, predictable |
| Sad | 2 sentences | 0.78 (slow) | -1 (easier) | Validate feelings, offer pause |
| Quiet | 2 sentences | 0.85 | unchanged | Don't push, offer gentle re-engagement |

---

### 4. `session_state.py` — In-Memory Session Tracking

**Purpose:** Tracks the current interaction session in RAM. Provides context for difficulty gating and strategy selection. Never stores emotional narratives.

**Key Fields:**
- `turn_count` — how many conversational turns have occurred
- `current_concept` — what concept is being practiced
- `current_difficulty` — difficulty level (1-5, never 0)
- `consecutive_frustration` — how many turns the child has been frustrated
- `consecutive_stability` — how many turns the child has been stable
- `difficulty_locked_turns` — cooldown counter after difficulty changes

**Two-Phase Update (from implementation_fix_and_reinforcement.md):**

| Phase | When | What It Does |
|---|---|---|
| `update_pre_decision()` | BEFORE DifficultyGate and Strategy | Updates mood, confidence, and streak counters |
| `update_post_response()` | AFTER LLM response generated | Increments turn count, stores truncated text |

This split ensures decisions are made on fresh mood data, but the session doesn't finalize before the response is generated.

**Difficulty Gating Rules:**
- **Decrease:** 2 consecutive frustrated turns + confidence ≥ 0.6
- **Increase:** 3 consecutive stable turns + confidence ≥ 0.6
- **Lock:** 2-turn cooldown after any change (prevents oscillation)
- **Boundaries:** Never below 1, never above 5

**TTL:** Auto-expires after 24 hours. Privacy-safe text truncation (200 chars max).

---

### 5. `regulation_state.py` — Regulation State Layer

**Purpose:** Sits between SessionState and RecoveryStrategy. Normalizes raw session data into structured regulation signals. RecoveryStrategy reads this — never raw mood directly.

**RegulationState Fields:**

| Field | Range | Meaning |
|---|---|---|
| `frustration_persistence` | 0.0-1.0 | How sustained the frustration is (0 = no streak, 1 = max) |
| `stability_persistence` | 0.0-1.0 | How sustained the stability is |
| `emotional_trend_score` | -1.0 to +1.0 | Net direction: negative = worsening, positive = improving |
| `current_difficulty` | 1-5 | Pass-through from session |
| `difficulty_locked` | bool | Whether difficulty is in cooldown |

**Key Function:** `compute_regulation_state(session)` — normalizes streaks against MAX_STREAK values and computes the emotional trend score.

---

### 6. `learning_progress.py` — Learning Progress Manager

**Purpose:** Tracks concept mastery independently from difficulty gating and emotional logic. Clean separation of concerns.

**Key Methods:**
| Method | Purpose |
|---|---|
| `update_attempt(concept, difficulty, success)` | Record a learning attempt outcome |
| `get_mastery_level(concept)` | Get current mastery (0-5) |
| `get_baseline_difficulty(concept)` | Suggest difficulty from mastery level |

**Mastery → Difficulty Mapping:**
| Mastery Level | Suggested Difficulty |
|---|---|
| 0-1 | 1 (simple) |
| 2-3 | 2 (normal) |
| 4 | 3 (intermediate) |
| 5 | 4 (advanced) |

**Design Rule:** Never mixes emotional logic with mastery updates. Reads/writes via UserMemoryManager.

---

### 7. `reinforcement_manager.py` — Reinforcement Adaptation Manager

**Purpose:** Adapts how LaRa encourages the child based on what works best for them. Tracks which reinforcement style correlates with improved stability.

**4 Reinforcement Styles:**

| Style | Example Phrase | When |
|---|---|---|
| `PRAISE_BASED` | "Great job! You did it!" | Child responds well to warm praise |
| `ACHIEVEMENT_BASED` | "You got that right! You are getting better!" | Child responds to progress acknowledgment |
| `CALM_VALIDATION` | "You are doing well. Let us keep going." | Child prefers steady, calm encouragement |
| `PLAYFUL_ENCOURAGEMENT` | "That was fun! Want to try one more?" | Child responds to gentle playfulness |

**Adaptation Rules:**
- Tracks success rate per style (was the next turn stable after using this style?)
- Requires minimum **5 events** before considering a change
- Requires at least **15% improvement** over current style
- Changes style **at most once per session**
- **Locks style** for remainder of session after change
- Persists preferred style to SQLite **only at session end**
- Defaults to `CALM_VALIDATION` if uncertain

**Safety:** No sudden personality shifts, no sarcasm, no exaggerated praise, no emotional labeling.

---

### 8. `user_memory.py` — Persistent User Memory (SQLite)

**Purpose:** Local SQLite database for structured persistence. Stores counts and levels — never narratives or transcripts.

**Database Tables:**

| Table | Fields | Purpose |
|---|---|---|
| `user_profiles` | user_id, baseline_instruction_depth, preferred_topics, preferred_tts_speed | User preferences |
| `learning_progress` | user_id, concept_name, mastery_level (0-5), highest_success_level, attempt_count | Per-concept mastery |
| `emotional_metrics` | user_id, concept_name, frustration_count, recovery_count, neutral_stability_count | Aggregated emotional counts |
| `reinforcement_metrics` | user_id, preferred_style, total_events | Reinforcement effectiveness |
| `decay_log` | last_decay_timestamp | Tracks when decay was last applied |

**Emotional Metric Decay:**
- Every 24 hours, all emotional counts are multiplied by **0.95**
- Compound decay: if LaRa hasn't been used for 3 days, factor = 0.95³ ≈ 0.857
- Prevents stale emotional data from permanently influencing behavior

**What Is NEVER Stored:**
- Raw transcripts
- Emotional narratives ("child was sad on Tuesday")
- Identity-level labels ("child is anxious")
- Psychological interpretations

---

### 9. `AgentricTLM.py` — LLM Interface (Ollama)

**Purpose:** Interfaces with the local Ollama LLM. Receives structured context from the strategy and reinforcement layers.

**System Prompt:** 8 behavioral constraints:
1. One clear thought at a time
2. Short sentences, simple vocabulary
3. No sarcasm, metaphors, idioms
4. Calm, patient, positive tone
5. No rapid-fire questions, no diagnoses
6. Graceful fail-safe for confusion
7. Never escalate intensity
8. No hallucinated tasks

**Dynamic LLM Control:**
| Parameter | Controlled By | Values |
|---|---|---|
| `num_predict` (max tokens) | `strategy.response_length_limit` | 50 / 80 / 120 tokens |
| `num_ctx` (context window) | Fixed | 1024 tokens |
| `temperature` | Fixed | 0.15 (very deterministic) |
| Strategy prompt | `strategy.prompt_addition` | Internal behavioral guidance |
| Reinforcement prompt | `reinforcement_context` | Reinforcement style instruction |

**Critical Design:** The LLM is a **renderer, not a decision-maker**. It does not:
- Decide task difficulty
- Persist memory
- Change pacing logic
- Override the strategy layer
- Know the child's detected mood by label

---

### 10. `kokoro_TTS.py` — Text-to-Speech (Kokoro)

**Purpose:** Converts LaRa's text responses into natural speech using the Kokoro-82M model with the `af_bella` voice.

**Key Features:**
- **Chunk-by-chunk streaming** — splits text into sentences, generates audio per chunk
- **Interruptible** — can be stopped mid-sentence via barge-in or wake-word
- **Configurable speed** — `self.speed` attribute controlled by RecoveryStrategy's `tts_length_scale`
- **Thread-safe playback** — uses `sounddevice` for direct audio output

**Speed by Mood:**
| Mood | TTS Speed | Effect |
|---|---|---|
| Neutral/Happy | 0.9 | Normal pace |
| Quiet | 0.85 | Slightly slower |
| Frustrated | 0.8 | Noticeably calmer |
| Anxious/Sad | 0.78 | Deliberate, grounding |

---

## Safety & Governance

### System Invariants (Never Violated)
1. **LLM is not a decision engine** — it generates language only
2. **Emotional safety over intelligence** — if a feature increases unpredictability, it is rejected
3. **No emotional labeling** — LaRa never says "You are anxious/sad"
4. **Gradual adaptation only** — no multi-level jumps, no oscillation, no instant resets
5. **Privacy is absolute** — all processing local, no cloud, no biometric retention
6. **Predictability required** — one instruction at a time, no surprises
7. **Micro-challenge always exists** — tasks never become trivially easy

### Conservative Adaptation Philosophy
- False negatives > false positives
- Adapt slowly (2+ turns before action)
- Lock after changes (2-turn cooldown)
- Low confidence → tone adjustments only, no structural changes
- Reinforcement changes require 5+ events and 15% improvement

---

## Governance Documents

| Document | Purpose |
|---|---|
| [rules_task_todo.md](file:///Users/deepandee/Desktop/LaRa/src/rules_task_todo.md) | Master rules and implementation phases with compliance status |
| [memory_architecture.md](file:///Users/deepandee/Desktop/LaRa/src/memory_architecture.md) | Dual-layer memory design (session + long-term) |
| [adaptive_learning_design.md](file:///Users/deepandee/Desktop/LaRa/src/adaptive_learning_design.md) | Difficulty adjustment rules and educational philosophy |
| [system_invariants.md](file:///Users/deepandee/Desktop/LaRa/src/system_invariants.md) | Non-negotiable architectural truths |
| [therapist_dashboard_spec.md](file:///Users/deepandee/Desktop/LaRa/src/therapist_dashboard_spec.md) | Dashboard modules for therapist review |
| [implementation_fix_and_reinforcement.md](file:///Users/deepandee/Desktop/LaRa/src/implementation_fix_and_reinforcement.md) | Architectural corrections and reinforcement extension |

---

## Running LaRa

```bash
# Activate environment
cd /Users/deepandee/Desktop/LaRa
source .venv/bin/activate

# Ensure Ollama is running with the model
ollama run AgentricAi/AgentricAI_TLM:latest

# Start LaRa
python3 src/whispercpp_STT.py
```

**Runtime commands:**
- Say **"friday"** — wake LaRa up
- Say **"shutdown"** — put LaRa to sleep
- Say **"lara"** — interrupt LaRa while she's speaking

---

*LaRa is not a chatbot. LaRa is a regulated adaptive therapeutic system designed for neurodiverse children. Every feature must support predictability, emotional regulation, skill progression, privacy, and stability.*
