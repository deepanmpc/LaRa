"""
LaRa Recovery Strategy Layer
Controls response parameters based on detected mood WITHOUT directly altering LLM output.

This layer sits between MoodDetector and the LLM, translating mood signals
into structured behavioral parameters that govern:
- Response length limits
- TTS speaking speed
- Instruction complexity
- Reassurance level
- Task difficulty modifiers

Design principles:
- Conservative adaptation (false negatives > false positives)
- Never reduce task difficulty to zero
- Never remove structured guidance entirely
- Maintain micro-challenge for resilience building
- Do not introduce new tasks automatically
"""

import logging
from dataclasses import dataclass


@dataclass
class RecoveryStrategy:
    """
    Behavioral parameters that control how LaRa responds.
    Applied AFTER mood detection, BEFORE LLM generation and TTS.
    """
    # Response shaping
    response_length_limit: int = 3       # Max sentences (1-3, never 0)
    instruction_depth: int = 2           # Complexity level (1=simple, 2=normal, 3=detailed)
    
    # TTS pacing
    tts_length_scale: float = 0.9        # Kokoro speed (lower = slower, 0.9 = default)
    
    # Emotional support
    reassurance_level: int = 0           # 0=none, 1=light, 2=moderate, 3=high
    
    # Task modifiers
    task_difficulty_modifier: int = 0    # -1=easier, 0=unchanged, +1=harder (never below -1)
    
    # Prompt additions (injected into LLM context, NOT spoken aloud)
    prompt_addition: str = ""            # Extra instruction for LLM tone/structure
    
    # Label for logging
    label: str = "default"


# --- Strategy Definitions ---
# Each mood maps to a carefully tuned set of parameters.
# Low-confidence detections only adjust tone, not task difficulty.

STRATEGIES = {
    "neutral": RecoveryStrategy(
        response_length_limit=3,
        instruction_depth=2,
        tts_length_scale=0.9,
        reassurance_level=0,
        task_difficulty_modifier=0,
        prompt_addition="",
        label="neutral"
    ),
    
    "happy": RecoveryStrategy(
        response_length_limit=3,
        instruction_depth=2,
        tts_length_scale=0.9,       # Normal speed — don't rush
        reassurance_level=0,
        task_difficulty_modifier=0,  # Keep task difficulty unchanged
        prompt_addition=(
            "The child seems engaged and positive. "
            "Mirror their energy gently. Encourage them. "
            "Keep the current task and pace."
        ),
        label="happy"
    ),
    
    "frustrated": RecoveryStrategy(
        response_length_limit=2,     # Shorter responses — less cognitive load
        instruction_depth=1,         # Reduce by 1 level — simpler steps
        tts_length_scale=0.8,        # Slower speech — calmer pacing
        reassurance_level=2,         # Moderate reassurance
        task_difficulty_modifier=-1, # Easier — break into smaller steps
        prompt_addition=(
            "The child seems to be finding things difficult. "
            "Break instructions into smaller, simpler steps. "
            "Add reassurance: 'You are doing well. Let us take it one step at a time.' "
            "Do NOT add new tasks. Do NOT increase complexity."
        ),
        label="frustrated"
    ),
    
    "anxious": RecoveryStrategy(
        response_length_limit=2,     # Shorter — predictable
        instruction_depth=1,         # Simple
        tts_length_scale=0.78,       # Noticeably slower — grounding
        reassurance_level=3,         # High reassurance
        task_difficulty_modifier=0,  # Pause escalation, don't reduce
        prompt_addition=(
            "The child may be feeling uncertain or overwhelmed. "
            "Use short, predictable sentences. Add a grounding phrase: "
            "'You are safe. I am right here with you.' "
            "Do NOT introduce anything new. Keep things simple and familiar."
        ),
        label="anxious"
    ),
    
    "sad": RecoveryStrategy(
        response_length_limit=2,     # Gentle, not verbose
        instruction_depth=1,         # Reduce density
        tts_length_scale=0.78,       # Slower — warm pacing
        reassurance_level=3,         # High reassurance
        task_difficulty_modifier=-1, # Lighten the load
        prompt_addition=(
            "The child seems to need comfort. "
            "Validate their feeling: 'It is okay to feel that way.' "
            "Offer an optional pause: 'We can take a break whenever you want.' "
            "Do NOT push new tasks. Focus on emotional presence."
        ),
        label="sad"
    ),
    
    "quiet": RecoveryStrategy(
        response_length_limit=2,     # Brief, not overwhelming
        instruction_depth=1,         # Simple
        tts_length_scale=0.85,       # Slightly slower
        reassurance_level=1,         # Light — not pushy
        task_difficulty_modifier=0,  # Keep current difficulty
        prompt_addition=(
            "The child is quiet. Do NOT push them to engage. "
            "Offer gentle re-engagement: 'I am here whenever you want to talk.' "
            "Keep any task simple. Do NOT escalate."
        ),
        label="quiet"
    ),
}

# Conservative version — used when confidence is low (<0.5)
# Only adjusts tone, does NOT modify task difficulty
STRATEGIES_LOW_CONF = {
    "neutral": STRATEGIES["neutral"],
    
    "happy": RecoveryStrategy(
        response_length_limit=3,
        instruction_depth=2,
        tts_length_scale=0.9,
        reassurance_level=0,
        task_difficulty_modifier=0,  # No change at low confidence
        prompt_addition="Maintain a warm, encouraging tone.",
        label="happy_low_conf"
    ),
    
    "frustrated": RecoveryStrategy(
        response_length_limit=3,
        instruction_depth=2,         # No reduction at low confidence
        tts_length_scale=0.85,       # Slightly slower only
        reassurance_level=1,         # Light reassurance only
        task_difficulty_modifier=0,  # NO task change at low confidence
        prompt_addition="Use a patient, calm tone. Add light encouragement.",
        label="frustrated_low_conf"
    ),
    
    "anxious": RecoveryStrategy(
        response_length_limit=3,
        instruction_depth=2,
        tts_length_scale=0.85,
        reassurance_level=1,
        task_difficulty_modifier=0,
        prompt_addition="Use a calm, steady tone. Keep sentences short.",
        label="anxious_low_conf"
    ),
    
    "sad": RecoveryStrategy(
        response_length_limit=3,
        instruction_depth=2,
        tts_length_scale=0.85,
        reassurance_level=1,
        task_difficulty_modifier=0,
        prompt_addition="Be gentle and warm. No pressure.",
        label="sad_low_conf"
    ),
    
    "quiet": RecoveryStrategy(
        response_length_limit=2,
        instruction_depth=2,
        tts_length_scale=0.9,
        reassurance_level=0,
        task_difficulty_modifier=0,
        prompt_addition="",
        label="quiet_low_conf"
    ),
}


class RecoveryStrategyManager:
    """
    Translates mood + confidence into a RecoveryStrategy.
    
    Rules:
    - confidence < 0.5 → conservative (tone only, no task changes)
    - confidence >= 0.5 → full strategy
    - Never reduce task difficulty below -1
    - Never remove structured guidance entirely
    - Maintain micro-challenge for resilience building
    """
    
    CONFIDENCE_THRESHOLD_FULL = 0.5  # Below this, use conservative strategies
    
    def __init__(self):
        self._previous_strategy = STRATEGIES["neutral"]
        logging.info("[RecoveryStrategy] Manager initialized.")
    
    def get_strategy(self, mood: str, confidence: float) -> RecoveryStrategy:
        """
        Returns the appropriate RecoveryStrategy for the given mood and confidence.
        Conservative at low confidence, full adaptation at high confidence.
        """
        # Select strategy table based on confidence
        if confidence < self.CONFIDENCE_THRESHOLD_FULL:
            strategy_table = STRATEGIES_LOW_CONF
        else:
            strategy_table = STRATEGIES
        
        # Look up strategy (fall back to neutral if unknown mood)
        strategy = strategy_table.get(mood, STRATEGIES["neutral"])
        
        # Safety: ensure task difficulty never drops below -1
        if strategy.task_difficulty_modifier < -1:
            strategy = RecoveryStrategy(
                response_length_limit=strategy.response_length_limit,
                instruction_depth=max(strategy.instruction_depth, 1),
                tts_length_scale=strategy.tts_length_scale,
                reassurance_level=strategy.reassurance_level,
                task_difficulty_modifier=-1,
                prompt_addition=strategy.prompt_addition,
                label=strategy.label + "_clamped"
            )
        
        # Log strategy change
        if strategy.label != self._previous_strategy.label:
            logging.info(
                f"[RecoveryStrategy] {self._previous_strategy.label} → {strategy.label} "
                f"(mood={mood}, confidence={confidence:.2f})"
            )
        
        self._previous_strategy = strategy
        return strategy
    
    def get_previous_strategy(self) -> RecoveryStrategy:
        """Returns the last applied strategy."""
        return self._previous_strategy
