"""
LaRa Prompt Cache Manager (Phase 1)
Segments prompts, computes block hashes, and prepares for future KV caching.
"""

import hashlib
import logging
from typing import Dict, Tuple

class PromptCacheManager:
    """
    Manages prompt segmentation and hashing for the AgentricTLM.
    Tracks changes in contextual blocks to optimize future inference.
    """
    def __init__(self):
        self.block_hashes: Dict[str, str] = {}
        logging.info("[PromptCache] Initialized segment hasher.")

    def _hash_block(self, content: str) -> str:
        """Compute SHA-1 hash of a text block."""
        if not content:
            return "empty"
        return hashlib.sha1(content.encode('utf-8')).hexdigest()

    def segment_and_hash(self, segments: Dict[str, str]) -> Tuple[str, Dict[str, bool]]:
        """
        Receives dictionary of prompt segments.
        Returns the full combined prompt string and a dict of which blocks changed.
        """
        changed_blocks = {}
        ordered_keys = [
            "system_block",
            "strategy_block",
            "reinforcement_block",
            "memory_block",
            "session_block",
            "history_block",
            "live_input_block"
        ]
        
        full_prompt_parts = []
        
        for key in ordered_keys:
            content = segments.get(key, "")
            if content:
                full_prompt_parts.append(content)
            
            # Compute hash
            current_hash = self._hash_block(content)
            
            # Check if changed
            previous_hash = self.block_hashes.get(key)
            if current_hash != previous_hash:
                changed_blocks[key] = True
                self.block_hashes[key] = current_hash
                if previous_hash is not None:  # Don't log on very first turn
                    logging.debug(f"[PromptCache] Block changed: {key}")
            else:
                changed_blocks[key] = False

        full_prompt = "\n".join(full_prompt_parts)
        return full_prompt, changed_blocks
