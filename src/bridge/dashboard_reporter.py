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
    
    Args:
        session: SessionState object
        mood_detector: MoodDetector instance (for emotion breakdown)
        learning_manager: LearningManager instance (for concept mastery)
        reinforcement_manager: ReinforcementManager instance (for style metrics)
        vision_aggregates: Pre-aggregated vision metrics dict
        performance_history: List of performance snapshots
        
    Returns:
        Dict matching the SessionCompleteRequest schema
    """
    import uuid
    from datetime import datetime
    
    # Generate session UUID if not present
    session_uuid = getattr(session, 'session_uuid', None) or str(uuid.uuid4())
    
    payload = {
        "sessionUuid": session_uuid,
        "startTime": _format_timestamp(getattr(session, 'start_time', None)),
        "endTime": _format_timestamp(datetime.now()),
        "durationSeconds": getattr(session, 'duration_seconds', 0) or 0,
        "totalTurns": getattr(session, 'turn_count', 0) or 0,
        "peakDifficulty": getattr(session, 'peak_difficulty', 1) or 1,
        "dominantMood": getattr(session, 'dominant_mood', 'neutral') or 'neutral',
        "avgMoodConfidence": getattr(session, 'avg_mood_confidence', 0.0) or 0.0,
        "avgEngagementScore": getattr(session, 'avg_engagement', 0.0) or 0.0,
        "totalInterventions": getattr(session, 'intervention_count', 0) or 0,
        "wakeWordTriggers": getattr(session, 'wake_word_count', 0) or 0,
        "bargeInCount": getattr(session, 'barge_in_count', 0) or 0,
    }
    
    # Emotional data
    payload["emotionalData"] = _build_emotional_data(session, mood_detector)
    
    # Engagement data
    payload["engagementData"] = _build_engagement_data(session, vision_aggregates)
    
    # Vision data
    if vision_aggregates:
        payload["visionData"] = vision_aggregates
    
    # Voice data
    payload["voiceData"] = _build_voice_data(session)
    
    # Learning progress
    if learning_manager:
        payload["learningProgress"] = _build_learning_progress(learning_manager)
    
    # Reinforcement data
    if reinforcement_manager:
        payload["reinforcementData"] = _build_reinforcement_data(reinforcement_manager)
    
    # Top activities
    payload["topActivities"] = _build_top_activities(session)
    
    # Difficulty trajectory
    payload["difficultyTrajectory"] = _build_difficulty_trajectory(session)
    
    # Turns
    payload["turns"] = _build_turns(session)
    
    return payload


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
