
# LaRa – Rules & Task Governance Document
## rules_task_todo.md

This document defines strict implementation rules, architectural constraints,
and execution governance for LaRa (Low-Cost Adaptive Robotic-AI Therapy System
for Down Syndrome and Neurodiverse Children).

All agents, contributors, and automation systems must follow these rules.

---------------------------------------------------------------------
SECTION 1 — CORE DESIGN PRINCIPLES
---------------------------------------------------------------------

1. Emotional Safety Over Cleverness                    ✅ ENFORCED
   - No feature may increase unpredictability.
   - Stability is more important than novelty.
   - False negatives are safer than false positives.

2. Deterministic Control Over Model Autonomy           ✅ ENFORCED
   - LLM must not control:
        - Task difficulty      → RecoveryStrategyManager controls this
        - Memory persistence   → Not yet implemented (Phase 1)
        - Emotional labeling   → MoodDetector uses internal signals only
        - State transitions    → SystemMode enum in whispercpp_STT.py
   - LLM is a renderer, not a decision-maker.

3. Conservative Adaptation                             ✅ ENFORCED
   - Adapt slowly.
   - Never escalate difficulty abruptly.
   - Never drop difficulty to zero.            → task_difficulty_modifier clamped ≥ -1
   - Maintain micro-challenge.                 → instruction_depth never 0

4. Privacy First                                       ✅ ENFORCED
   - All storage must remain local.            → Ollama, Whisper, Kokoro all local
   - No biometric or emotional data may leave device.
   - No cloud sync unless explicitly approved. → No network calls except localhost

5. Structured Memory Only                              ⚠️ PLANNED (Phase 1-2)
   - No raw emotional transcript storage long-term.
   - No narrative emotional summaries.
   - Store metrics, not judgments.

---------------------------------------------------------------------
SECTION 2 — MEMORY RULES
---------------------------------------------------------------------

Session Memory (Short-Term):                           ⏳ PHASE 1
- Exists in RAM or TTL-based local storage.
- Auto-delete after 24 hours.
- Stores:
    - current_concept         (str)
    - current_difficulty      (int, 1-5)
    - consecutive_frustration (int)
    - consecutive_stability   (int)
    - last_user_input         (str, truncated)
    - last_ai_response        (str, truncated)
    - mood                    (str, temporary)
    - mood_confidence         (float, temporary)
    - turn_count              (int)
- Must never store emotional narrative.
- File: src/session_state.py

Long-Term Memory (User Preference & Progress):         ⏳ PHASE 2
- Must be structured (SQLite).
- Tables:
    - UserProfile: user_id, baseline_instruction_depth,
      preferred_topics, preferred_tts_speed
    - LearningProgress: user_id, concept_name, mastery_level (0-5),
      highest_success_level, attempt_count, last_success_timestamp
    - EmotionalMetrics: user_id, concept_name, frustration_count,
      recovery_count, neutral_stability_count, last_updated
- Do not store: emotional narratives, raw transcripts, identity labels.
- File: src/user_memory.py

Emotional Metrics:
- Store only aggregated counts.
- Apply decay over time (multiply by 0.95 every 24h).
- Never label user permanently.

---------------------------------------------------------------------
SECTION 3 — ADAPTIVE DIFFICULTY RULES
---------------------------------------------------------------------

1. Difficulty may change only if:                      ⚠️ PHASE 3 (gating)
    - Mood confidence >= 0.6
    - Same mood persists for 2 consecutive turns

2. Difficulty changes:
    - Only one level at a time                 → modifier ∈ {-1, 0}
    - Lock for 2 turns after change            → needs cooldown counter
    - Never reduce to zero                     → clamped in strategy
    - Never increase more than +1

3. Increase difficulty only when:
    - 3 consecutive stable (neutral/happy) turns
    - Successful task completion signal
    - File: src/recovery_strategy.py → add difficulty_gating()

4. Emotional history must NOT automatically reduce difficulty.
   Use gradual scaffolding with monitoring.

---------------------------------------------------------------------
SECTION 4 — MOOD DETECTION RULES
---------------------------------------------------------------------

1. Must be temporally smoothed.                        ✅ 3-utterance window
2. Must be threshold gated.                            ✅ CONFIDENCE_THRESHOLD = 0.3
3. Must not react to single utterance.                 ✅ 2-of-3 consensus
4. Must not speak mood labels aloud.                   ✅ internal only
5. Must apply decay toward neutral.                    ✅ consecutive_neutral_count
6. Quiet is not equal to sad.                          ✅ fixed in _analyze_audio
7. Keyword matching must use word boundaries.          ✅ regex \b matching

---------------------------------------------------------------------
SECTION 5 — LLM GOVERNANCE
---------------------------------------------------------------------

The LLM must:                                          ✅ ENFORCED
- Follow system_prompt constraints.                    → 8 rules in prompt
- Provide one clear thought at a time.                 → num_predict capped
- Avoid metaphors and sarcasm.                         → Rule 3
- Never invent new tasks automatically.                → Rule 8
- Never diagnose emotional state.                      → Rule 5

The LLM must NOT:                                      ✅ ENFORCED
- Decide task difficulty.                              → strategy decides
- Persist memory.                                      → no memory API
- Change pacing logic.                                 → TTS speed by strategy
- Override RecoveryStrategyManager.                    → prompt_addition only

---------------------------------------------------------------------
SECTION 6 — IMPLEMENTATION TASK ORDER
---------------------------------------------------------------------

Phase 1: SessionState                                  ⏳ NEXT
- [ ] Implement SessionState dataclass (src/session_state.py)
- [ ] Implement TTL auto-delete (24h expiry)
- [ ] Track: concept, difficulty, frustration/stability counts
- [ ] Wire into whispercpp_STT.py main loop

Phase 2: User Memory (SQLite)                          ⏳ PLANNED
- [ ] Implement UserProfile schema
- [ ] Implement LearningProgress schema
- [ ] Implement EmotionalMetrics schema (counts + decay)
- [ ] Create UserMemoryManager class (src/user_memory.py)

Phase 3: Difficulty Gating                             ✅ PARTIAL
- [x] RecoveryStrategyManager implemented
- [x] Confidence-based strategy selection (high/low)
- [ ] Add difficulty_gating() with 2-turn lock
- [ ] Add consecutive_stability tracking for escalation
- [ ] Integrate with SessionState

Phase 4: Learning Progress                             ⏳ PLANNED
- [ ] Integrate LearningProgressManager
- [ ] Add mastery tracking per concept
- [ ] Add performance-based escalation
- [ ] Add concept progression logic

Phase 5: Logging & Dashboard                           ⏳ OPTIONAL
- [ ] Add structured logging discipline
- [ ] Add metrics export for therapist review

---------------------------------------------------------------------
SECTION 7 — SAFETY CHECKS BEFORE MERGE
---------------------------------------------------------------------

Before merging any feature:

- Does this increase unpredictability?
- Does this introduce emotional labeling?
- Does this allow LLM autonomous control?
- Does this store unnecessary user data?
- Does this increase cognitive load?

If any answer is YES → reject or redesign.

---------------------------------------------------------------------
SECTION 8 — LONG-TERM VISION CONSTRAINT
---------------------------------------------------------------------

LaRa is not a chatbot.

LaRa is a regulated adaptive therapeutic system.

Every feature must support:

- Predictability
- Emotional regulation
- Skill progression
- Privacy
- Stability

If a feature improves intelligence but reduces stability,
it must not be implemented.

---------------------------------------------------------------------
END OF DOCUMENT
---------------------------------------------------------------------
