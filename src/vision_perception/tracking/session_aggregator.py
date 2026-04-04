import time
import dataclasses
from typing import Dict, List, Any
from core.state import PerceptionOutput

class VisionSessionAggregator:
    def __init__(self, target_fps: float = 15.0):
        self.target_fps = target_fps
        self.reset()
        
    def reset(self):
        self.session_started_at = time.time()
        self.frames_processed = 0
        self.focused_frames = 0
        self.distracted_frames = 0
        self.absent_frames = 0
        self.distraction_count = 0  # Number of distinct distraction events
        self.engagement_sum = 0.0
        self.peak_engagement = 0.0
        self.gesture_active_frames = 0
        self.presence_frames = 0
        self.system_confidence_sum = 0.0
        
        # Timeline tracking (per minute bins)
        self.timeline_bins: List[Dict[str, Any]] = []
        self._current_minute_index = 0
        self._current_minute_frames = 0
        self._current_minute_engagement_sum = 0.0
        
        # Track previous state to detect events
        self._previous_attention_state = None
        
    def ingest(self, frame: PerceptionOutput):
        self.frames_processed += 1
        
        attention_state = frame.attentionState
        if attention_state == "focused":
            self.focused_frames += 1
        elif attention_state == "distracted":
            self.distracted_frames += 1
            if self._previous_attention_state != "distracted":
                self.distraction_count += 1
        elif attention_state == "absent":
            self.absent_frames += 1
            
        self._previous_attention_state = attention_state
        
        if frame.presence:
            self.presence_frames += 1
            
        if frame.gesture is not None and frame.gesture != "NONE" and frame.gesture != "":
            self.gesture_active_frames += 1
            
        eng_score = frame.engagementScore
        self.engagement_sum += eng_score
        self.peak_engagement = max(self.peak_engagement, eng_score)
        
        self.system_confidence_sum += frame.systemConfidence
        
        # Handle minute binning
        elapsed_minutes = int((time.time() - self.session_started_at) / 60.0)
        
        # If we moved to a new minute, flush the previous minute bin
        if elapsed_minutes > self._current_minute_index:
            self._flush_current_minute_bin()
            self._current_minute_index = elapsed_minutes
            
        self._current_minute_frames += 1
        self._current_minute_engagement_sum += eng_score
        
    def _flush_current_minute_bin(self):
        if self._current_minute_frames > 0:
            avg_eng = self._current_minute_engagement_sum / self._current_minute_frames
            # Crude attention state approximation: just label based on average engagement
            # Alternatively could track most frequent.
            dominant_state = "focused" if avg_eng > 0.6 else ("distracted" if avg_eng > 0.3 else "absent")
            
            self.timeline_bins.append({
                "minute_index": self._current_minute_index,
                "avg_engagement": round(avg_eng, 3),
                "attention_state": dominant_state
            })
            
        self._current_minute_frames = 0
        self._current_minute_engagement_sum = 0.0
        
    def snapshot(self) -> Dict[str, Any]:
        if self.frames_processed == 0:
            return {
                "focused_percent": 0.0,
                "distracted_percent": 0.0,
                "absent_percent": 0.0,
                "distraction_count": 0,
                "avg_engagement_score": 0.0,
                "peak_engagement_score": 0.0,
                "gesture_active_percent": 0.0,
                "presence_percent": 0.0,
                "avg_system_confidence": 0.0,
                "avg_fps": 0.0,
                "total_frames_processed": 0,
                "engagement_timeline": self.timeline_bins
            }
            
        fps = self.frames_processed / max(1.0, (time.time() - self.session_started_at))
            
        return {
            "focused_percent": round((self.focused_frames / self.frames_processed) * 100, 2),
            "distracted_percent": round((self.distracted_frames / self.frames_processed) * 100, 2),
            "absent_percent": round((self.absent_frames / self.frames_processed) * 100, 2),
            "distraction_count": self.distraction_count,
            "avg_engagement_score": round(self.engagement_sum / self.frames_processed, 3),
            "peak_engagement_score": round(self.peak_engagement, 3),
            "gesture_active_percent": round((self.gesture_active_frames / self.frames_processed) * 100, 2),
            "presence_percent": round((self.presence_frames / self.frames_processed) * 100, 2),
            "avg_system_confidence": round(self.system_confidence_sum / self.frames_processed, 3),
            "avg_fps": round(fps, 1),
            "total_frames_processed": self.frames_processed,
            # include the current timeline bins
            "engagement_timeline": self.timeline_bins
        }
        
    def flush(self) -> Dict[str, Any]:
        self._flush_current_minute_bin()
        result = self.snapshot()
        return result
