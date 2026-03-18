"""
LaRa Prompt Cache Manager (Phase 1)
Segments prompts into stable vs dynamic blocks and tracking hashes.
Designed specifically to take advantage of Ollama prefix caching.
"""

import hashlib
import logging
from collections import OrderedDict
from typing import Dict

class PromptCacheManager:
    """
    Manages prompt segmentation. Facilitates token caching by
    producing stable byte-identical prefixes for Ollama.
    """
    def __init__(self):
        # Maps segment_name -> (hash, content)
        self._cache = {}
        self._last_report = {}
        logging.info("[PromptCache] Initialized segment manager.")

    def build_segment(self, name: str, content: str) -> str:
        """
        Computes the SHA-1 hash of the content.
        Marks it as HIT or MISS based on previous cached state.
        Returns the content unchanged.
        """
        if not content:
            content_to_hash = ""
        else:
            content_to_hash = content
            
        current_hash = hashlib.sha1(content_to_hash.encode('utf-8')).hexdigest()
        
        cached_entry = self._cache.get(name)
        if cached_entry and cached_entry[0] == current_hash:
            self._last_report[name] = "HIT"
        else:
            self._last_report[name] = "MISS"
            self._cache[name] = (current_hash, content_to_hash)
            
        return content_to_hash

    def assemble_prompt(self, segments: OrderedDict) -> str:
        """
        Takes OrderedDict of segment contents and joins them sequentially.
        """
        parts = []
        # Strict order enforced by the OrderedDict input, but we just iterate
        for name, content in segments.items():
            if content:  # Ignore empty blocks
                parts.append(content)
                
        return "\n".join(parts)

    def get_cache_report(self) -> Dict[str, str]:
        """Returns HIT/MISS dictionary for the recent assembly."""
        report = self._last_report.copy()
        self._last_report.clear() # Reset for next turn
        return report

    def invalidate_dynamic_segments(self):
        """
        Phase 6: Barge-In KV Safety
        Clears cached history and live_input preventing contaminated memory.
        """
        for name in ('history_block', 'live_input_block'):
            if name in self._cache:
                del self._cache[name]
        logging.info("[PromptCache] Dynamic segments invalidated (barge-in)")
