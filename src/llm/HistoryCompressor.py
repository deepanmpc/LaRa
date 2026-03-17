"""
LaRa History Compressor (Phase 2)
Replaces raw sliding window with token-budgeted semantic compression.
"""

import re
from typing import List, Dict

class HistoryCompressor:
    def __init__(self, max_tokens: int = 200):
        self.max_tokens = max_tokens
        
    def _normalize_text(self, text: str) -> str:
        """Removes numbers and generic names to detect repetitive patterns."""
        # Remove numbers
        t = re.sub(r'\d+', 'NUM', text)
        # Assuming typical child names or praise structures might differ slightly,
        # but just stripping numbers catches the "Good! After 2 is 3" variations trivially.
        return t.lower().strip()

    def compress(self, history: List[Dict[str, str]], budget_tokens: int = 200) -> str:
        if not history:
            return ""
            
        budget = budget_tokens if budget_tokens else self.max_tokens
        limit = max(60, budget) # Hard floor to prevent completely erasing memory

        # Process from oldest to newest into intermediate representation
        processed_blocks = [] # List of {"type": "raw"|"summary", "content": str, "priority": int}
        
        i = 0
        n = len(history)
        while i < n:
            # Check if it's the last two turns (must be RAW)
            if i >= n - 2:
                processed_blocks.append({
                    "type": "raw",
                    "content": f"U: {history[i]['user']}\nL: {history[i]['lara']}",
                    "priority": 100 # Highest priority, never drop
                })
                i += 1
                continue
                
            # Lookahead for repetition (Step 1)
            reps = 1
            current_norm = self._normalize_text(history[i]['lara'])
            for j in range(i + 1, n - 2): # Stop before last 2
                if self._normalize_text(history[j]['lara']) == current_norm:
                    reps += 1
                else:
                    break
                    
            if reps >= 3:
                processed_blocks.append({
                    "type": "summary",
                    "content": f"[Repeated encouragement: {reps} turns]",
                    "priority": 50 # High priority
                })
                i += reps
                continue
                
            # Lookahead for low-information collapse (Step 2)
            u_text = history[i]['user']
            l_text = history[i]['lara']
            # approx tokens as len/4
            u_tokens = len(u_text) // 4
            l_tokens = len(l_text) // 4
            
            if u_tokens <= 3 and l_tokens <= 8:
                processed_blocks.append({
                    "type": "summary",
                    "content": "[Counting: user answered correctly, praised]",
                    "priority": 50
                })
                i += 1
                continue
                
            # If no compression applied, keep raw (Step 4)
            processed_blocks.append({
                "type": "raw",
                "content": f"U: {u_text}\nL: {l_text}",
                "priority": 10
            })
            i += 1

        # Step 3: Token budget enforcement
        # Calculate total tokens
        while True:
            total_tokens = sum(len(b['content']) // 4 for b in processed_blocks)
            if total_tokens <= limit or len(processed_blocks) <= 2:
                break
                
            # Need to drop an item. Find the lowest priority item that isn't the last 2.
            # (Last 2 must be raw -> priority 100)
            droppable = [idx for idx, b in enumerate(processed_blocks) if b['priority'] == 10]
            if not droppable:
                break # All summaries or protected
                
            # Drop the oldest droppable raw turn
            processed_blocks.pop(droppable[0])
            
        return "\n".join(b['content'] for b in processed_blocks)
