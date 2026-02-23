# LaRa System Optimization & Constraint Implementation
**Date Date:** February 24, 2026

## 1. Overview
This update fundamentally restructures the LaRa backend audio pipeline to strictly conform to the interaction, behavioral, and emotional safety constraints required for neurodiverse children (specifically Down syndrome). 

Additionally, the entire architecture was optimized for **maximum inference speed** on low-cost hardware by stripping out experimental deep-learning latency bottlenecks.

---

## 2. Speed Optimizations
To achieve instant, real-time conversational responses, the following architectural bottlenecks were resolved:
- **Audio Enhancements Removed:** Denoising (`demucs`) and Voice Separation (`speechbrain.sepformer`) were completely removed from the live `whispercpp.py` loop. The micro-seconds needed to perform these operations caused unacceptable audio latency. The pipeline is now back to a fast Voice Activity Detection (VAD) buffer directly streaming to `pywhispercpp`.
- **Whisper Greedy Decoding:** Added `language='en'` to explicitly prevent Whisper from wasting CPU cycles auto-detecting the language, and enabled `beam_size=1` (greedy decoding) for absolute fastest text transcription performance.
- **LLM Context & Generation Limits:** In `AgentricTLM.py`, the Ollama request was constrained: 
   - `num_ctx: 1024` drastically limits the necessary context window memory.
   - `num_predict: 60` enforces absolute shortness by hard-capping generation length, forcing the LLM to reply instantly in 2-3 short sentences. 

---

## 3. Down Syndrome Behavioral Constraints Implemented
The LLM and VAD configurations were strictly tuned to ensure emotional safety, clarity, predictability, and low cognitive load.

### A. Gentle Pacing (`whispercpp.py`)
- **Silence Forgiveness Threshold Adjusted**: `SILENCE_DURATION_MS` increased from `1200ms` to `2500ms`. Children with Down syndrome often require more processing time or pause mid-sentence. Extending this threshold guarantees LaRa will patiently wait 2.5 seconds during a pause before cutting them off to process audio.

### B. Behavioral Constitution (`AgentricTLM.py`)
- **Strict Determinism**: Reduced LLM generation `temperature` from `0.4` down to an extremely rigid `0.15`. This prevents highly unpredictable, random, or complex novel conversational branching.
- **Massive Prompt Expansion**: Replaced the brief 8-line setup with a comprehensive, multi-section "Constitution" directly instructing the model on constraints:
   1. **Concrete Instruction:** Provide exactly *one* short, simple thought or instruction at a time.
   2. **Accessible Tone:** Never use sarcasm, metaphors, idioms, or ambiguous language. Everything must be highly literal.
   3. **No Escalation:** Explicitly forbids the AI from hallucinating tasks, escalating interaction intensity, or pushing the user past their comfort zone. 
   4. **Safe Boundaries:** Forbids rapid-fire questions, diagnosing, or making medical/psychological claims.
   5. **Graceful Fail-Safe:** If the child is confusing or frustrated, it enforces a mandated fallback phrase format: *"I am here with you. We can take our time."*

---

## 4. Traceability & Caregiver Logging
- **System Transitions:** Injected specific system state loggers (e.g., `[SYSTEM_STATE] Transitioned to AWAKE`) into the Python loop logging.
- **Interaction History:** All transcriptions and precise LLM generations are stored alongside system states natively in `lara_system.log` and `lara_interaction.log` enabling offline caregivers to accurately observe when errors occurred or when the child interacted with LaRa.

---

## 5. Dependencies Stripped
Removed heavy, slow dependencies to keep deployment ultra-lightweight and suitable for low-cost educational hardware:
- `demucs`
- `speechbrain`
- `torchaudio`
- Local `lameenc` and `vosk` legacy conflicts were resolved. The project requires only `pywhispercpp`, `webrtcvad`, and `torch/numpy` integrations.
