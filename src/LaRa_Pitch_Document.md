# LaRa — Complete Technical Pitch Document

> **LaRa** — Low-Cost Adaptive Robotic-AI Assistant
> A regulated, deterministic, privacy-first conversational AI therapy system
> for children with Down syndrome and neurodiverse children.

---

## The Problem

Children with Down syndrome and other neurodiverse conditions often benefit enormously from consistent, predictable, one-on-one educational and therapeutic interaction. However:

- Qualified therapy time is limited and expensive
- Traditional educational software is too rigid, doesn't adapt to real-time emotional state
- Existing AI chatbots are **unpredictable** — dangerous for emotionally vulnerable children
- Cloud AI raises serious **privacy** concerns for sensitive child data

**LaRa solves this with a fully local, deterministic, adaptive AI companion that puts emotional safety first.**

---

## What LaRa Is

LaRa is not a chatbot. LaRa is a **regulated adaptive therapeutic system**.

Every component is designed around one principle: **Safety > Structure > Adaptation > Personalization**.

The LLM is a **renderer**, not a decision-maker. It reads structured guidance and generates safe, gentle language. Every behavioral decision — difficulty, pacing, reinforcement, strategy — is made by deterministic Python code, not by the AI.

---

## System Architecture

```
                         ┌──────────────────────────┐
                         │   PERCEPTION LAYER        │
   Microphone ──────────▶│ Whisper STT (local)       │
   (16kHz mono)          │ + WebRTC Voice Activity   │
                         └────────────┬─────────────┘
                                      │ Transcribed text + Audio features
                                      ▼
                         ┌──────────────────────────┐
                         │   EMOTION LAYER           │
                         │ MoodDetector              │
                         │ • Text analysis (regex)   │
                         │ • Audio prosody (RMS)     │
                         │ • 3-turn consensus filter │
                         │ → mood + confidence score │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                         ┌──────────────────────────┐
                         │   SESSION LAYER           │
                         │ SessionState.pre_update() │
                         │ • Mood streak tracking    │
                         │ • Difficulty cooldown     │
                         │ • Turn counter            │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────┼────────────────────┐
                    ▼                 ▼                     ▼
         ┌──────────────┐  ┌──────────────────┐  ┌──────────────────────┐
         │ Difficulty   │  │ RegulationState  │  │ Reinforcement        │
         │ Gating       │  │ (normalized mood │  │ Adaptation Manager   │
         │ (+1/-1/lock) │  │  persistence)    │  │ (4 styles, learns    │
         └──────────────┘  └────────┬─────────┘  │  what works)         │
                                    │             └────────┬─────────────┘
                                    ▼                      │
                         ┌──────────────────┐             │
                         │ Recovery Strategy│◀────────────┘
                         │ Manager          │
                         │ • TTS speed      │
                         │ • Response length│
                         │ • Prompt guidance│
                         └────────┬─────────┘
                                  │
                    ┌─────────────┼──────────────────┐
                    ▼             ▼                   ▼
         ┌──────────────┐ ┌──────────────┐  ┌────────────────┐
         │ Preferences  │ │ Session      │  │ Vector Memory  │
         │ (likes/      │ │ Summary      │  │ (ChromaDB RAG  │
         │  dislikes)   │ │ (structured) │  │  past stories) │
         └──────┬───────┘ └──────┬───────┘  └────────┬───────┘
                │                 │                   │
                └────────────────▼───────────────────┘
                                  │
                    ┌─────────────▼─────────────────────┐
                    │   LLM (Ollama, local)              │
                    │   Strict 7-Part Prompt:            │
                    │   1. System Rules                  │
                    │   2. Recovery Strategy Guidance    │
                    │   3. Reinforcement Style           │
                    │   4. Child Preferences + Stories   │
                    │   5. Session Summary               │
                    │   6. Last 5 Conversation Turns     │
                    │   7. Current User Message          │
                    └─────────────┬─────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │  Kokoro TTS (local)        │
                    │  af_bella voice            │
                    │  speed = strategy.tts_rate │
                    └─────────────┬─────────────┘
                                  │
                                Speaker → Child hears response
```

---
Child speaks
  → Whisper transcribes text
  → MoodDetector detects "frustrated" (conf: 0.72)
  → SessionState.pre_update()      [LAYER 4: update streak counters]
  → DifficultyGate checks streaks  [LAYER 4: 2 frustrated turns → decrease]
  → SessionSummary generated       [LAYER 3: fresh from Layer 4]
  → Preferences loaded             [LAYER 5: from child_preferences table]
  → VectorMemory checked           [LAYER 6: story trigger? → retrieve]
  → LLM prompt assembled:
        Part 1: System Rules
        Part 2: Strategy guidance (from RegulationState)
        Part 3: Reinforcement style (from reinforcement_metrics)
        Part 4: Preferences + past stories
        Part 5: Session Summary    [LAYER 3]
        Part 6: Last 5 turns       [LAYER 2]
        Part 7: Current message    [LAYER 1]
  → LLM generates response
  → Kokoro TTS speaks it
  → SessionState.post_update()     [LAYER 4: increment turn count]
  → emotional_metrics updated      [LAYER 5: frustration_count+1]
  → reinforcement_metrics updated  [LAYER 5: track style effectiveness]
  → Conversation history updated   [LAYER 2: append new turn]

## The 5-Layer Memory Architecture

LaRa's memory system is the technical core of the project. It is designed to be **structured, not narrative** — storing behavioral metrics, never emotional interpretations.

### Layer 1: Immediate Turn Buffer (Ephemeral)
- Holds only the current user utterance and AI response during processing
- Cleared after every response finalization
- Never written to any database
- Purpose: local turn-level context injection

### Layer 2: Rolling Session Buffer (Short-Term RAM)
- Sliding window of last **5 conversation turns**
- Token-efficient: each turn truncated to 150 characters
- Auto-wiped after 24-hour session expiry
- Never persisted to SQLite
- Purpose: conversational continuity ("what were we doing?")

### Layer 3: Session Summary Layer
- Generated from live `SessionState` every turn
- Structured format only:
  ```
  [Session State]
  Concept: counting | Difficulty: 2/5 | Turn: 7
  Stability trend: improving | Frustration streak: 0 | Stability streak: 3
  Reinforcement: calm_validation | Mastery: 2/5
  ```
- No narrative, no emotional labels, no interpretation
- Replaces older raw turns when needed
- Injected as Part 5 of LLM prompt

### Layer 4: Structured Session State (RAM)
- All fields in memory only, expires at session end:
  - `current_concept`, `current_difficulty`, `turn_count`
  - `consecutive_frustration`, `consecutive_stability`
  - `difficulty_locked_turns` (cooldown counter)
  - `mood`, `mood_confidence`
- Two-phase update: `update_pre_decision()` before decisions, `update_post_response()` after LLM response

### Layer 5: Long-Term User Memory (SQLite — Local)

**5 Tables. No transcripts. No labels. Only measurable metrics.**

| Table | What It Stores |
|---|---|
| `users` | User ID, baseline instruction depth, TTS speed preference |
| `learning_progress` | Mastery level (0-5) per concept, attempt counts |
| `emotional_metrics` | Frustration / Recovery / Stability counts with weekly decay |
| `child_preferences` | Likes and dislikes (max 20, JSON structured, 6-month expiry) |
| `reinforcement_metrics` | Which encouragement style works best, success rate per style |

### Layer 6: Vector Memory (ChromaDB RAG — Optional)
- Stores structured **summaries** of past stories and educational themes
- Embedded locally using ChromaDB cosine similarity
- Retrieved when child says story triggers ("tell me a story", "remember when...")
- **Safety gates:**
  - Max 200 characters per summary (prevents transcript smuggling)
  - Min 60% similarity score (prevents hallucination)
  - Max 3 retrievals per session
  - 90-day soft-expiry on stored summaries
  - Never stores raw dialogue

---

## The 10 Core Components (Files)

| File | Role |
|---|---|
| `whispercpp_STT.py` | Main orchestrator — microphone, VAD, wake word, full pipeline |
| `mood_detector.py` | Text + audio prosody mood analysis with 3-turn consensus |
| `session_state.py` | RAM-based session with pre/post update phases |
| `regulation_state.py` | Normalizes mood streaks into 0.0-1.0 persistence scores |
| `recovery_strategy.py` | Translates mood → behavioral parameters (TTS speed, length, guidance) |
| `reinforcement_manager.py` | Adapts encouragement style based on historical effectiveness |
| `session_summary.py` | Generates structured, non-narrative session context for LLM |
| `child_preferences.py` | Detects and stores child's likes/dislikes, injects into LLM |
| `vector_memory.py` | ChromaDB RAG for story/theme continuity across sessions |
| `user_memory.py` | SQLite persistence layer — aggregated metrics, mastery, preferences |
| `AgentricAi/AgentricTLM.py` | LLM interface — strict 7-part prompt builder, response streaming |
| `AgentricAi/kokoro_TTS.py` | Local Kokoro text-to-speech with speed control and barge-in interruption |

---

## Key Safety Invariants (Non-Negotiable)

1. **LLM is a renderer, not a decision-maker** — Difficulty, mood, reinforcement are all decided by deterministic Python. The LLM just generates the words.
2. **No emotional labeling** — LaRa never says "you seem sad" or "you're frustrated"
3. **Gradual adaptation only** — Difficulty changes require 2+ consecutive turns + 60% confidence + 2-turn cooldown
4. **Privacy is absolute** — Everything runs locally. No cloud. No biometric data. No transcripts stored.
5. **Predictability first** — One thought at a time, one question at a time, consistent tone
6. **False negatives preferred** — If uncertain, do nothing rather than make a wrong adaptation
7. **Micro-challenge always exists** — Task difficulty never goes to zero

---

## Adaptive Systems in Detail

### Mood Detection
- **6 mood categories:** neutral, happy, frustrated, anxious, sad, quiet
- **Dual input:** text keywords (regex with word-boundary protection) + audio RMS energy
- **3-turn consensus filter:** requires 2-of-3 recent turns to agree before acting
- **Confidence decay:** consecutive neutrals decay confidence → falls back to neutral safely

### Difficulty Gating
- **Decrease trigger:** 2 consecutive frustrated turns + confidence ≥ 0.60
- **Increase trigger:** 3 consecutive stable turns + confidence ≥ 0.60
- **Lock:** 2-turn cooldown after any change (prevents oscillation)
- **Boundaries:** difficulty range always 1–5, never 0

### Reinforcement Adaptation
- **4 styles:** Calm Validation, Praise-Based, Achievement-Based, Playful Encouragement
- **Adaptation rules:** minimum 5 events, requires 15% improvement, locks once per session
- **Safe default:** always starts at Calm Validation
- Persists preferred style to SQLite only at session end

### Child Preference Memory
- **Regex-based detection:** detects "I like X", "I hate Y", "My favorite is Z", "I'm scared of X"
- **Max 20 preferences** per child
- **Deduplication:** updates sentiment if topic already stored (e.g., dislike → like)
- **LLM injection:** preferences are woven naturally into responses, not listed

---

## What LaRa Tells the LLM on Every Turn

Here is the exact text LaRa constructs and sends to the LLM for a typical turn:

```
You are LaRa (Low-Cost Adaptive Robotic-AI Assistant), a gentle, highly
predictable, and encouraging therapy assistant for children with Down
syndrome...
[8 behavioral constraints...]

[Behavioral guidance — internal: The child seems to be finding things
difficult. Break instructions into tiny, single steps...]

[Reinforcement style: Use calm, grounding validation phrases...]

[Child's preferences — weave naturally:
Likes: dinosaurs, blue, blocks; Dislikes: loud sounds]

[Session State]
Concept: counting | Difficulty: 2/5 | Turn: 4
Stability trend: declining | Frustration streak: 2 | Stability streak: 0
Reinforcement: calm_validation | Mastery: 1/5

--- Recent conversation ---
User: Can we learn counting?
LaRa: Of course! Let us count together. Can you say one?
User: One!
LaRa: Wonderful! That was perfect. Now can you say two?
User: This is too hard
LaRa: That is okay. We can go slower. Let us just do one at a time.
--- End of history ---

User says: I still can't do it
LaRa says:
```

The LLM reads all of this before writing a single word. This is why LaRa gives contextually appropriate, safe responses.

---

## Running LaRa

### Requirements
- macOS (Apple Silicon or Intel)
- Python 3.11+
- Ollama (local LLM server)
- Microphone

### Setup
```bash
git clone <repo>
cd LaRa
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Pull the model
ollama pull AgentricAi/AgentricAI_TLM:latest

# Start
python3 src/whispercpp_STT.py
```

### Voice Commands
| Say | Effect |
|---|---|
| **"friday"** | Wake LaRa up |
| **"shutdown"** | Put LaRa to sleep |
| **"lara"** | Interrupt LaRa mid-sentence |

---

## Privacy Design

| Concern | LaRa's Approach |
|---|---|
| Raw speech | Never stored after transcription |
| Emotional labels | Never stored ("frustrated" → count only) |
| Conversation transcripts | Not stored anywhere, ever |
| Cloud processing | Zero — 100% local inference |
| Biometric data | Not collected |
| Session data | Auto-expires after 24 hours |
| Emotional metrics | Decay over time (weekly 0.95× normalization) |
| Story summaries | Soft-expire after 90 days |

---

## Technology Stack

| Component | Technology | Why |
|---|---|---|
| Speech-to-text | OpenAI Whisper (small.en, local) | Accurate, fast, no cloud |
| Language Model | Ollama (AgentricAI_TLM 2B) | 128K context, fully local |
| Text-to-speech | Kokoro-82M (af_bella) | Natural, lightweight, controllable speed |
| Long-term memory | SQLite | Simple, local, no server needed |
| Vector memory | ChromaDB | Local embeddings for semantic story recall |
| Voice activity | WebRTC VAD | Battery-efficient, precise |
| Language | Python 3.11 | Compatibility with numpy, chromadb |

---

## What's Next

- **Therapist Dashboard:** Export `get_session_summary()` to a caregiver-facing HTML/JSON report showing mastery trends, emotional stability, and concept progress — no transcripts, no labels
- **Curriculum Integration:** Connect `LearningProgressManager` to a structured concept curriculum (colours → numbers → shapes → words)
- **Multi-user Support:** The full system is user-isolated by `user_id` — a single LaRa device could serve multiple children with separate SQLite rows and separate vector collections

---

*LaRa is structured behavioral intelligence. It enables growth, stability, and continuity without sacrificing safety.*

**Safety > Structure > Adaptation > Personalization.**

