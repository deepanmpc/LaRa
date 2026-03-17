"""
LaRa History Compressor (Phase 2)
Replaces sliding window with deterministic semantic compression.
Preserves task-relevant transitions and emotional continuity.
"""
from typing import List, Dict

class HistoryCompressor:
    def __init__(self, max_tokens: int = 200):
        self.max_tokens = max_tokens
        # Rough token approximation: ~4 chars per token
        self.max_chars = max_tokens * 4

    def compress(self, history: List[Dict[str, str]], budget_tokens: int = 200) -> str:
        """
        Compresses conversation history to fit within budget.
        Always preserves the last 2 turns verbatim.
        Compresses older turns deterministically.
        """
        if not history:
            return ""

        max_chars = budget_tokens * 4
        
        # Test if raw fits
        raw_length = sum(len(t.get('user', '')) + len(t.get('lara', '')) for t in history)
        if raw_length < max_chars and len(history) <= 3:
            return self._format_raw(history)

        compressed_lines = []
        
        # Preserve most recent 2 turns
        recent_turns = history[-2:]
        older_turns = history[:-2]

        if older_turns:
            # Semantic compression of older turns (no LLM)
            user_words = sum(len(t.get('user', '').split()) for t in older_turns)
            lara_words = sum(len(t.get('lara', '').split()) for t in older_turns)
            
            # Emotional markers extraction
            frustration_markers = ["frustrated", "sad", "angry", "no", "stop", "i don't want to", "hard"]
            found_frustration = any(
                any(marker in t.get('user', '').lower() for marker in frustration_markers)
                for t in older_turns
            )
            
            summary = f"  • [{len(older_turns)} older turns summarized]: User spoke ~{user_words} words, LaRa responded ~{lara_words} words."
            if found_frustration:
                summary += " User showed past signs of frustration/difficulty."
            else:
                summary += " User was generally stable."
                
            compressed_lines.append("[Compressed History]")
            compressed_lines.append(summary)
            compressed_lines.append("[Recent History]")

        # Append recent verbatim
        for i, turn in enumerate(recent_turns):
            compressed_lines.append(f"User: {turn['user']}")
            compressed_lines.append(f"LaRa: {turn['lara']}")

        return "\n".join(compressed_lines)

    def _format_raw(self, history: List[Dict[str, str]]) -> str:
        lines = ["[Recent History]"]
        for turn in history:
            lines.append(f"User: {turn['user']}")
            lines.append(f"LaRa: {turn['lara']}")
        return "\n".join(lines)
