import logging
from datetime import datetime

class DataValidator:
    @staticmethod
    def validate_turn_metrics(data):
        """Validate turn-level metrics before DB write."""
        errors = []
        
        # 1. Range Checks
        eng = data.get("vision_engagement_score", 0.0)
        if not (0.0 <= float(eng) <= 1.0):
            errors.append(f"engagement_score out of range: {eng}")
            
        mood_conf = data.get("mood_confidence", 0.0)
        if not (0.0 <= float(mood_conf) <= 1.0):
            errors.append(f"mood_confidence out of range: {mood_conf}")
            
        # 2. Latency Sanity Checks
        inf_ms = data.get("inference_ms", 0)
        if int(inf_ms) > 30000: # 30s max
            errors.append(f"inference_ms suspiciously high: {inf_ms}")
            
        tts_ms = data.get("tts_ms", 0)
        if int(tts_ms) > 30000:
            errors.append(f"tts_ms suspiciously high: {tts_ms}")
            
        # 3. Type Checks
        if not isinstance(data.get("turn_number"), int):
            errors.append(f"turn_number must be int: {type(data.get('turn_number'))}")

        if errors:
            for err in errors:
                logging.warning(f"[DataValidator] Validation failed: {err}")
            return False
        return True

    @staticmethod
    def validate_session_stats(data):
        """Validate aggregate session statistics."""
        # Add checks for final aggregation data
        return True
