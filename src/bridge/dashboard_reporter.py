"""
Dashboard Reporter — POST session data to Spring Boot API after each session.
Non-blocking: failures are logged but do NOT crash the pipeline.
"""

import requests
import logging
import json
from typing import Optional

logger = logging.getLogger("lara.bridge.dashboard_reporter")

DEFAULT_DASHBOARD_API_URL = "http://localhost:8080/api/pipeline/session-complete"


def report_session_to_dashboard(
    session_data: dict,
    child_id: int,
    api_url: str = DEFAULT_DASHBOARD_API_URL,
    timeout: float = 5.0
) -> bool:
    """
    Post completed session analytics to the Spring Boot dashboard.
    Non-blocking — failures are logged but do not crash the pipeline.
    
    Args:
        session_data: Full session payload dict
        child_id: Database child ID (from config.yaml dashboard.child_id)
        api_url: Dashboard API endpoint URL
        timeout: Request timeout in seconds
        
    Returns:
        True if successfully posted, False otherwise
    """
    try:
        payload = session_data.copy()
        payload["childId"] = child_id
        
        logger.info(f"[DashboardReporter] Posting session to dashboard (childId={child_id})...")
        
        response = requests.post(
            api_url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        
        if response.ok:
            result = response.json()
            logger.info(f"[DashboardReporter] Session reported successfully. "
                       f"Server session ID: {result.get('sessionId', 'unknown')}")
            return True
        elif response.status_code == 409:
            logger.warning(f"[DashboardReporter] Duplicate session UUID — already ingested.")
            return False
        else:
            logger.warning(f"[DashboardReporter] Failed with status {response.status_code}: "
                          f"{response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("[DashboardReporter] Could not connect to dashboard API. "
                      "Is the Spring Boot server running?")
        return False
    except requests.exceptions.Timeout:
        logger.warning("[DashboardReporter] Request timed out.")
        return False
    except Exception as e:
        logger.warning(f"[DashboardReporter] Unexpected error: {e}")
        return False


def build_session_payload(
    session,
    mood_detector=None,
    learning_manager=None,
    reinforcement_manager=None,
    vision_aggregates: Optional[dict] = None,
    performance_history: Optional[list] = None
) -> dict:
    """
    Build the full SessionCompleteRequest JSON payload from pipeline state objects.
    Uses SessionState.get_final_stats() as the primary source of truth.
    """
    import uuid
    from datetime import datetime
    
    # Generate final aggregates from session
    stats = session.get_final_stats() if hasattr(session, 'get_final_stats') else {}
    
    # Generate session UUID if not present
    session_uuid = getattr(session, 'session_uuid', None) or str(uuid.uuid4())
    
    summary = stats.get("session_summary", {})
    
    payload = {
        "sessionUuid": session_uuid,
        "childIdHashed": stats.get("session_identity", {}).get("child_id_hashed") or getattr(session, 'child_id_hashed', None),
        "startTime": _format_timestamp(getattr(session, 'created_at', None)),
        "endTime": _format_timestamp(datetime.now()),
        "durationSeconds": summary.get("duration_seconds", 0),
        "totalTurns": summary.get("total_turns", 0),
        "peakDifficulty": summary.get("peak_difficulty", 1),
        "dominantMood": summary.get("dominant_mood", "neutral"),
        "avgMoodConfidence": stats.get("emotional", {}).get("mood_confidence", 0.0),
        "avgEngagementScore": summary.get("avg_engagement_score", 0.0),
        "totalInterventions": 0, # To be added to SessionState if needed
        "wakeWordTriggers": 0,
        "bargeInCount": 0,
    }
    
    # Emotional Data (Mapping Python stats to Java DTO)
    e = stats.get("emotional", {})
    payload["emotionalData"] = {
        "overallMoodScore": int(e.get("mood_score", 50)),
        "moodTrend": "Stable", # Placeholder or derive from history
        "primaryEmotion": e.get("primary_emotion", "neutral"),
        "emotionStabilityScore": int(e.get("emotional_trend_score", 50)),
        "anxietyLevel": "Low",
        "selfRegulationScore": 50,
        "positiveInteractions": e.get("stability_index", 0),
        "challengingMoments": e.get("frustration_streak", 0),
        "pctHappy": stats.get("voice", {}).get("pct_vocal_neutral", 0.0), # Simplified for now
        "pctCalm": 0.0,
        "pctFocused": 0.0,
        "pctAnxious": 0.0,
        "pctFrustrated": stats.get("voice", {}).get("pct_vocal_arousal", 0.0),
        "pctSad": stats.get("voice", {}).get("pct_vocal_withdrawal", 0.0),
        "pctNeutral": stats.get("voice", {}).get("pct_vocal_neutral", 0.0)
    }
    
    # Engagement Data
    a = stats.get("analytics", {})
    payload["engagementData"] = {
        "focusScore": int(a.get("focus_score", 50)),
        "attentionSpanMinutes": a.get("attention_span_minutes", 0.0),
        "taskCompletionRate": int(a.get("task_completion_rate", 100)),
        "participationLevel": a.get("participation_level", "MEDIUM"),
        "distractionFrequency": a.get("distraction_frequency", "LOW"),
        "responsivenessScore": 75,
        "initiativeTakingScore": int(a.get("initiative_taking_score", 50)),
        "collaborationScore": 50,
        "weeklyGoalProgress": 0
    }
    
    # Vision Data
    v = stats.get("vision", {})
    payload["visionData"] = {
        "avgEngagementScore": v.get("avg_engagement_score", 0.0),
        "avgEngagementUiScore": v.get("avg_engagement_ui_score", 0.0),
        "avgGazeScore": v.get("avg_gaze_score", 0.0),
        "systemConfidence": v.get("system_confidence", 0.9),
        "faceConfidence": v.get("face_confidence", 0.9),
        "gestureConfidence": v.get("gesture_confidence", 0.8),
        "poseConfidence": v.get("pose_confidence", 0.8),
        "objectConfidence": v.get("object_confidence", 0.7),
        "totalDistractionFrames": v.get("distraction_frames", 0),
        "focusedDurationMinutes": v.get("focused_duration_minutes", 0.0),
        "attentionFocusedPct": v.get("attention_state_focused_pct", 0.0),
        "attentionDistractedPct": v.get("attention_state_distracted_pct", 0.0),
        "attentionAbsentPct": v.get("attention_state_absent_pct", 0.0)
    }
    
    # Voice Data
    vo = stats.get("voice", {})
    payload["voiceData"] = {
        "speakingRateWpm": int(vo.get("avg_speaking_rate_wpm", 0)),
        "avgVolume": vo.get("avg_volume", 0.0),
        "speechStabilityScore": vo.get("speech_stability_score", 0.0),
        "utteranceCount": vo.get("utterance_count", 0),
        "pctVocalNeutral": vo.get("pct_vocal_neutral", 100.0),
        "pctVocalArousal": vo.get("pct_vocal_arousal", 0.0),
        "pctVocalWithdrawal": vo.get("pct_vocal_withdrawal", 0.0)
    }
    
    # Learning Progress (Using objects if passed, else stats)
    # The stats "learning" and "reinforcement" are already built by Managers if linked
    payload["learningProgress"] = _build_learning_progress_from_stats(stats.get("learning", []))
    
    # Reinforcement data
    payload["reinforcementData"] = _build_reinforcement_data_from_stats(stats.get("reinforcement", []))
    
    # Top activities (derived from turn history concepts)
    payload["topActivities"] = _build_top_activities(session)
    
    # Difficulty trajectory
    payload["difficultyTrajectory"] = _build_difficulty_trajectory(session)
    
    # Turns
    payload["turns"] = _build_turns(session)
    
    return payload

def _build_learning_progress_from_stats(learning_stats: list) -> list:
    items = []
    for s in learning_stats:
        items.append({
            "conceptName": s.get("concept_name"),
            "curriculumArea": "General",
            "masteryLevel": int(s.get("mastery_percentage", 0) / 20), # scale 0-5
            "masteryPercentage": s.get("mastery_percentage", 0.0),
            "successRate": (s.get("success_count", 0) / s.get("attempt_count", 1)) * 100.0 if s.get("attempt_count", 0) > 0 else 0.0,
            "attemptCount": s.get("attempt_count", 0),
            "successCount": s.get("success_count", 0),
            "currentDifficulty": s.get("current_difficulty", 1)
        })
    return items

def _build_reinforcement_data_from_stats(reinforcement_stats: list) -> dict:
    if not reinforcement_stats:
        return {
            "praiseSuccessRate": 0.0, "achievementSuccessRate": 0.0,
            "validationSuccessRate": 0.0, "encouragementSuccessRate": 0.0,
            "bestReinforcementStyle": "CALM_VALIDATION"
        }
    
    best = "CALM_VALIDATION"
    best_rate = -1.0
    
    data = {
        "praiseSuccessRate": 0.0,
        "achievementSuccessRate": 0.0,
        "validationSuccessRate": 0.0,
        "encouragementSuccessRate": 0.0,
    }
    
    for s in reinforcement_stats:
        style = s.get("style_name", "")
        rate = s.get("success_rate", 0.0)
        
        if "praise" in style: data["praiseSuccessRate"] = rate
        elif "achievement" in style: data["achievementSuccessRate"] = rate
        elif "validation" in style: data["validationSuccessRate"] = rate
        elif "encouragement" in style: data["encouragementSuccessRate"] = rate
        
        if rate > best_rate:
            best_rate = rate
            best = style
            
    data["bestReinforcementStyle"] = best.upper()
    return data


def _format_timestamp(dt) -> str:
    """Format a datetime to ISO string."""
    if dt is None:
        from datetime import datetime
        dt = datetime.now()
    try:
        return dt.isoformat()
    except:
        return str(dt)


def _build_emotional_data(session, mood_detector) -> dict:
    """Build emotional data section from session and mood detector."""
    data = {
        "overallMoodScore": 50,
        "moodTrend": "Stable",
        "primaryEmotion": "Neutral",
        "emotionStabilityScore": 50,
        "anxietyLevel": "Low",
        "selfRegulationScore": 50,
        "positiveInteractions": 0,
        "challengingMoments": 0,
        "pctHappy": 0.0,
        "pctCalm": 0.0,
        "pctFocused": 0.0,
        "pctAnxious": 0.0,
        "pctFrustrated": 0.0,
        "pctSad": 0.0,
        "pctNeutral": 100.0
    }
    
    # Override with real data if available
    if mood_detector and hasattr(mood_detector, '_mood_history'):
        history = mood_detector._mood_history
        if history:
            # Calculate emotion percentages from history
            total = len(history)
            mood_counts = {}
            for entry in history:
                mood = entry.get('mood', 'neutral') if isinstance(entry, dict) else str(entry)
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            for mood, count in mood_counts.items():
                pct = (count / total) * 100
                key = f"pct{mood.capitalize()}"
                if key in data:
                    data[key] = round(pct, 2)
    
    return data


def _build_engagement_data(session, vision_aggregates) -> dict:
    """Build engagement data section."""
    return {
        "focusScore": 50,
        "attentionSpanMinutes": 0.0,
        "taskCompletionRate": 50,
        "participationLevel": "Medium",
        "distractionFrequency": "Medium",
        "responsivenessScore": 50,
        "initiativeTakingScore": 50,
        "collaborationScore": 50,
        "weeklyGoalProgress": 0
    }


def _build_voice_data(session) -> dict:
    """Build voice prosody data section."""
    return {
        "speakingRateWpm": 0,
        "avgVolume": 0.0,
        "speechStabilityScore": 0.0,
        "utteranceCount": getattr(session, 'turn_count', 0) or 0,
        "pctVocalNeutral": 100.0,
        "pctVocalArousal": 0.0,
        "pctVocalWithdrawal": 0.0
    }


def _build_learning_progress(learning_manager) -> list:
    """Build learning progress items from learning manager."""
    items = []
    try:
        if hasattr(learning_manager, 'get_all_progress'):
            progress = learning_manager.get_all_progress()
            for concept, data in progress.items():
                items.append({
                    "conceptName": concept,
                    "curriculumArea": data.get("area", "General"),
                    "masteryLevel": data.get("mastery_level", 0),
                    "masteryPercentage": data.get("mastery_percentage", 0.0),
                    "successRate": data.get("success_rate", 0.0),
                    "attemptCount": data.get("attempts", 0),
                    "successCount": data.get("successes", 0),
                    "currentDifficulty": data.get("difficulty", 1)
                })
    except Exception as e:
        logger.warning(f"[DashboardReporter] Could not build learning progress: {e}")
    return items


def _build_reinforcement_data(reinforcement_manager) -> dict:
    """Build reinforcement data from reinforcement manager."""
    data = {
        "calmValidationSuccess": 0,
        "calmValidationTotal": 0,
        "praisedBasedSuccess": 0,
        "praisedBasedTotal": 0,
        "achievementBasedSuccess": 0,
        "achievementBasedTotal": 0,
        "playfulSuccess": 0,
        "playfulTotal": 0,
        "preferredStyle": "calm_validation"
    }
    
    try:
        if hasattr(reinforcement_manager, '_session_metrics'):
            metrics = reinforcement_manager._session_metrics
            for style, counts in metrics.items():
                clean = style.replace("_", "").lower()
                if "calm" in clean:
                    data["calmValidationSuccess"] = counts.get("success", 0)
                    data["calmValidationTotal"] = counts.get("total", 0)
                elif "praise" in clean:
                    data["praisedBasedSuccess"] = counts.get("success", 0)
                    data["praisedBasedTotal"] = counts.get("total", 0)
                elif "achievement" in clean:
                    data["achievementBasedSuccess"] = counts.get("success", 0)
                    data["achievementBasedTotal"] = counts.get("total", 0)
                elif "playful" in clean:
                    data["playfulSuccess"] = counts.get("success", 0)
                    data["playfulTotal"] = counts.get("total", 0)
        
        if hasattr(reinforcement_manager, 'get_preferred_style'):
            data["preferredStyle"] = reinforcement_manager.get_preferred_style()
    except Exception as e:
        logger.warning(f"[DashboardReporter] Could not build reinforcement data: {e}")
    
    return data


def _build_top_activities(session) -> list:
    """Build top activities list from session."""
    try:
        if hasattr(session, 'activities') and session.activities:
            return [
                {"name": a.get("name", "Unknown"), "score": a.get("score", 0), "completions": a.get("completions", 1)}
                for a in session.activities[:4]
            ]
    except:
        pass
    return []


def _build_difficulty_trajectory(session) -> list:
    """Build difficulty trajectory from session."""
    try:
        if hasattr(session, 'difficulty_changes') and session.difficulty_changes:
            return [
                {
                    "turnNumber": d.get("turn", 0),
                    "before": d.get("before", 1),
                    "after": d.get("after", 1),
                    "direction": d.get("direction", "unchanged"),
                    "reason": d.get("reason", "unknown")
                }
                for d in session.difficulty_changes
            ]
    except:
        pass
    return []


def _build_turns(session) -> list:
    """Build turn-level data from session."""
    turns = []
    try:
        if hasattr(session, 'turns') and session.turns:
            for i, turn in enumerate(session.turns):
                turns.append({
                    "turnNumber": i + 1,
                    "timestamp": _format_timestamp(turn.get("timestamp")),
                    "childUtterance": turn.get("user_input", ""),
                    "laraResponse": turn.get("ai_response", ""),
                    "detectedMood": turn.get("mood", "neutral"),
                    "moodConfidence": turn.get("mood_confidence", 0.0),
                    "difficultyLevel": turn.get("difficulty", 1),
                    "strategyApplied": turn.get("strategy", "neutral"),
                    "reinforcementStyle": turn.get("reinforcement", "calm_validation"),
                    "promptBuildMs": turn.get("prompt_build_ms", 0),
                    "inferenceMs": turn.get("inference_ms", 0),
                    "ttsMs": turn.get("tts_ms", 0),
                    "totalLatencyMs": turn.get("total_latency_ms", 0),
                    "visionPresence": turn.get("vision_presence", False),
                    "visionAttentionState": turn.get("vision_attention", None),
                    "visionEngagementScore": turn.get("vision_engagement", None),
                    "visionGesture": turn.get("vision_gesture", None),
                    "visionDistractionFrames": turn.get("vision_distraction", 0)
                })
    except Exception as e:
        logger.warning(f"[DashboardReporter] Could not build turns: {e}")
    return turns
