import logging
import time
import json
import hashlib
from datetime import datetime
from threading import Lock
from src.persistence.db import Database

class SessionDBSync:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if SessionDBSync._instance is not None:
            raise RuntimeError("SessionDBSync is a singleton. Use get()")
        self.db = Database.get()

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = SessionDBSync()
        return cls._instance

    def session_start(self, session_uuid, child_id, parent_id=None):
        """Step 4 — Insert into Sessions Table"""
        child_id_val = str(child_id or 1)
        child_id_hashed = hashlib.md5(child_id_val.encode()).hexdigest()[:16]
        
        query = """
            INSERT INTO sessions (
                session_uuid, session_id, child_id, child_id_hashed, parent_id, start_time, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, 'IN_PROGRESS', NOW())
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        last_id = self.db.execute(query, (session_uuid, session_uuid, child_id, child_id_hashed, parent_id, now))
        logging.info(f"[SessionDBSync] Session started in DB: {session_uuid} (ID: {last_id})")
        return last_id, child_id_hashed

    def session_turn_metrics(self, session_id, turn_data):
        """Step 5 — Write Turn-Level Metrics"""
        query = """
            INSERT INTO session_turn_metrics (
                session_id, turn_number, timestamp, child_utterance, child_utterance_length,
                lara_response, detected_mood, mood_confidence, difficulty_level,
                vision_attention_state, vision_presence, vision_engagement_score,
                vision_gesture, vision_distraction_frames, regulation_state,
                reinforcement_style, strategy_applied, inference_ms, tts_ms, total_latency_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        child_utt = turn_data.get("child_utterance", "")
        inf_ms = turn_data.get("inference_ms", 0)
        tts_ms = turn_data.get("tts_ms", 0)
        
        params = (
            session_id,
            turn_data.get("turn_number"),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            child_utt,
            len(child_utt),
            turn_data.get("lara_response"),
            turn_data.get("detected_mood"),
            turn_data.get("mood_confidence"),
            turn_data.get("difficulty_level"),
            turn_data.get("vision_attention_state"),
            1 if turn_data.get("vision_presence") else 0,
            turn_data.get("vision_engagement_score"),
            turn_data.get("vision_gesture"),
            turn_data.get("vision_distraction_frames", 0),
            turn_data.get("regulation_state"),
            turn_data.get("reinforcement_style"),
            turn_data.get("strategy_applied"),
            inf_ms,
            tts_ms,
            inf_ms + tts_ms
        )
        self.db.execute(query, params)

    def engagement_minute_sync(self, session_id, minute_index, avg_engagement, attention_state):
        """Step 6 — Persist Engagement Timeline (Every 60s)"""
        query = """
            INSERT INTO engagement_timeline (session_id, minute_index, avg_engagement, attention_state)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute(query, (session_id, minute_index, avg_engagement, attention_state))

    def session_end(self, session_id, session_uuid, child_id, final_stats):
        """Step 7 to Step 13 — Final Persistences"""
        self._persist_vision_metrics(session_id, child_id, final_stats.get("vision"))
        self._persist_voice_metrics(session_id, child_id, final_stats.get("voice"))
        self._persist_emotional_metrics(session_uuid, child_id, final_stats.get("emotional"))
        self._persist_learning_progress(session_id, child_id, final_stats.get("learning"))
        self._persist_reinforcement_metrics(session_id, child_id, final_stats.get("reinforcement"))
        self._persist_session_analytics(session_id, child_id, final_stats.get("analytics"))
        
        # Step 13 — Update Session Summary
        self._update_session_end(session_id, final_stats.get("session_summary"))
        
        # Step 14 — Longitudinal Metrics
        self.compute_longitudinal_metrics(child_id)
        
        # Risk Prediction
        self.compute_session_risks(session_id, child_id)

    def _persist_vision_metrics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO child_vision_metrics (
                session_id, child_id, avg_engagement_score, avg_engagement_ui_score,
                avg_gaze_score, attention_state_focused_pct, attention_state_distracted_pct,
                attention_state_absent_pct, focused_duration_minutes, distraction_frames,
                dominant_gesture, face_confidence, gesture_confidence, object_confidence,
                pose_confidence, system_confidence, recorded_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (
            session_id, child_id, data.get("avg_engagement_score"), data.get("avg_engagement_ui_score"),
            data.get("avg_gaze_score"), data.get("attention_state_focused_pct"), data.get("attention_state_distracted_pct"),
            data.get("attention_state_absent_pct"), data.get("focused_duration_minutes"), data.get("distraction_frames"),
            data.get("dominant_gesture"), data.get("face_confidence"), data.get("gesture_confidence"), data.get("object_confidence"),
            data.get("pose_confidence"), data.get("system_confidence")
        )
        self.db.execute(query, params)

    def _persist_voice_metrics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO child_voice_metrics (
                session_id, child_id, avg_speaking_rate_wpm, avg_utterance_length_words,
                avg_volume, utterance_count, speech_stability_score, pct_vocal_arousal,
                pct_vocal_neutral, pct_vocal_withdrawal, recorded_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (
            session_id, child_id, data.get("avg_speaking_rate_wpm"), data.get("avg_utterance_length_words"),
            data.get("avg_volume"), data.get("utterance_count"), data.get("speech_stability_score"), data.get("pct_vocal_arousal"),
            data.get("pct_vocal_neutral"), data.get("pct_vocal_withdrawal")
        )
        self.db.execute(query, params)

    def _persist_emotional_metrics(self, session_uuid, child_id, data):
        if not data: return
        query = """
            INSERT INTO emotional_metrics (
                session_id, child_id_hashed, mood_state, mood_confidence, frustration_score,
                frustration_streak, emotional_trend_score, stability_index, mood_score,
                primary_emotion, bayesian_confidence_score, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (
            session_uuid, str(child_id), data.get("mood_state"), data.get("mood_confidence"), data.get("frustration_score"),
            data.get("frustration_streak"), data.get("emotional_trend_score"), data.get("stability_index"), data.get("mood_score"),
            data.get("primary_emotion"), data.get("bayesian_confidence_score", 0.0)
        )
        self.db.execute(query, params)

    def _persist_learning_progress(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO child_learning_progress (
                    session_id, child_id, concept_name, attempt_count, success_count,
                    failure_count, mastery_percentage, current_difficulty,
                    peak_difficulty_reached, total_time_spent_seconds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    attempt_count = attempt_count + VALUES(attempt_count),
                    success_count = success_count + VALUES(success_count),
                    failure_count = failure_count + VALUES(failure_count),
                    mastery_percentage = VALUES(mastery_percentage),
                    current_difficulty = VALUES(current_difficulty),
                    peak_difficulty_reached = GREATEST(peak_difficulty_reached, VALUES(peak_difficulty_reached)),
                    total_time_spent_seconds = total_time_spent_seconds + VALUES(total_time_spent_seconds)
            """
            params = (
                session_id, child_id, item.get("concept_name"), item.get("attempt_count"), item.get("success_count"),
                item.get("failure_count"), item.get("mastery_percentage"), item.get("current_difficulty"),
                item.get("peak_difficulty_reached"), item.get("total_time_spent_seconds")
            )
            self.db.execute(query, params)

    def _persist_reinforcement_metrics(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO child_reinforcement_metrics (
                    session_id, child_id, style_name, total_uses, success_count,
                    success_rate, last_used_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    total_uses = total_uses + VALUES(total_uses),
                    success_count = success_count + VALUES(success_count),
                    success_rate = (success_count + VALUES(success_count)) / (total_uses + VALUES(total_uses)),
                    last_used_at = NOW()
            """
            params = (
                session_id, child_id, item.get("style_name"), item.get("total_uses"), item.get("success_count"),
                item.get("success_rate")
            )
            self.db.execute(query, params)

    def _persist_session_analytics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO session_analytics (
                session_id, child_id, avg_engagement_score, avg_gaze_score, focus_score,
                attention_span_minutes, distraction_frequency, emotion_stability_score,
                overall_mood_score, participation_level, interaction_continuity_score,
                initiative_taking_score, task_completion_rate, positive_interactions,
                challenging_moments, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (
            session_id, child_id, data.get("avg_engagement_score"), data.get("avg_gaze_score"), data.get("focus_score"),
            data.get("attention_span_minutes"), data.get("distraction_frequency"), data.get("emotion_stability_score"),
            data.get("overall_mood_score"), data.get("participation_level"), data.get("interaction_continuity_score"),
            data.get("initiative_taking_score"), data.get("task_completion_rate"), data.get("positive_interactions"),
            data.get("challenging_moments")
        )
        self.db.execute(query, params)

    def _update_session_end(self, session_id, summary):
        if not summary: return
        query = """
            UPDATE sessions SET
                end_time = NOW(),
                duration_seconds = %s,
                status = 'COMPLETED',
                total_turns = %s,
                avg_engagement_score = %s,
                dominant_mood = %s,
                peak_difficulty = %s
            WHERE id = %s
        """
        params = (
            summary.get("duration_seconds"),
            summary.get("total_turns"),
            summary.get("avg_engagement_score"),
            summary.get("dominant_mood"),
            summary.get("peak_difficulty"),
            session_id
        )
        self.db.execute(query, params)

    def compute_longitudinal_metrics(self, child_id):
        """Step 14 — Update student_longitudinal_metrics"""
        # Fetch last 14 sessions
        sessions = self.db.fetch_all(
            "SELECT id, avg_engagement_score, total_turns FROM sessions WHERE child_id = %s ORDER BY start_time DESC LIMIT 14",
            (child_id,)
        )
        if not sessions: return

        # Example logic for mastery_velocity
        progress = self.db.fetch_all(
            "SELECT mastery_percentage FROM child_learning_progress WHERE child_id = %s ORDER BY id DESC LIMIT 20",
            (child_id,)
        )
        mastery_vel = 0.0
        if len(progress) >= 2:
            mastery_vel = progress[0]['mastery_percentage'] - progress[-1]['mastery_percentage']

        # Simplified volatility (std dev of engagement as proxy)
        engagements = [s['avg_engagement_score'] for s in sessions if s['avg_engagement_score'] is not None]
        volatility7 = 0.0
        if len(engagements) >= 7:
            avg = sum(engagements[:7]) / 7
            volatility7 = (sum((x - avg)**2 for x in engagements[:7]) / 7)**0.5

        query = """
            INSERT INTO student_longitudinal_metrics (
                child_id, rolling_volatility7, rolling_volatility14, recovery_trend,
                mastery_velocity, intervention_decay_index, frustration_risk_score,
                independence_score, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                rolling_volatility7 = VALUES(rolling_volatility7),
                rolling_volatility14 = VALUES(rolling_volatility14),
                recovery_trend = VALUES(recovery_trend),
                mastery_velocity = VALUES(mastery_velocity),
                updated_at = NOW()
        """
        params = (child_id, volatility7, volatility7 * 1.2, 0.5, mastery_vel, 0.2, 0.1, 0.8)
        self.db.execute(query, params)

    def compute_session_risks(self, session_id, child_id):
        """Risk Prediction derived from session metrics"""
        # Fetch turn metrics to analyze trends
        turns = self.db.fetch_all(
            "SELECT detected_mood, vision_engagement_score, vision_distraction_frames FROM session_turn_metrics WHERE session_id = %s ORDER BY turn_number ASC",
            (session_id,)
        )
        if not turns: return

        frustration_streak = 0
        max_frustration_streak = 0
        for t in turns:
            if t['detected_mood'] in ('frustrated', 'sad'):
                frustration_streak += 1
                max_frustration_streak = max(max_frustration_streak, frustration_streak)
            else:
                frustration_streak = 0

        # Risk indicators
        meltdown_risk = 0.0
        if max_frustration_streak >= 3: meltdown_risk = 0.8
        
        engagement_decay = 0.0
        if len(turns) >= 5:
            first_avg = sum(t['vision_engagement_score'] for t in turns[:2]) / 2
            last_avg = sum(t['vision_engagement_score'] for t in turns[-2:]) / 2
            if last_avg < first_avg: engagement_decay = (first_avg - last_avg)

        # Update session_analytics with risks if columns exist, or store elsewhere
        # Since I can't change schema, I'll log them for now or assume they are in analytics
        logging.info(f"[Risk] Session {session_id} Risks -> Meltdown: {meltdown_risk}, Decay: {engagement_decay}")
