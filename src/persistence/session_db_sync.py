import mysql.connector
from mysql.connector import pooling
import logging
import time
import json
from datetime import datetime
from threading import Lock

try:
    from src.core.config_loader import CONFIG
    _DB_CFG = CONFIG.get("mysql", {})
    DB_HOST = _DB_CFG.get("host", "localhost")
    DB_PORT = _DB_CFG.get("port", 3306)
    DB_USER = _DB_CFG.get("user", "root")
    DB_PASS = _DB_CFG.get("password", "")
    DB_NAME = _DB_CFG.get("database", "lara_dashboard")
    POOL_SIZE = _DB_CFG.get("pool_size", 5)
except Exception:
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASS = ""
    DB_NAME = "lara_dashboard"
    POOL_SIZE = 5

class SessionDBSync:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if SessionDBSync._instance is not None:
            raise RuntimeError("SessionDBSync is a singleton. Use get()")
        
        self.pool = None
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="lara_pool",
                pool_size=POOL_SIZE,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
            )
            logging.info(f"[SessionDBSync] MySQL Pool initialized: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        except Exception as e:
            logging.error(f"[SessionDBSync] Failed to initialize MySQL Pool: {e}")

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = SessionDBSync()
        return cls._instance

    def _execute(self, query, params=None, commit=True):
        if not self.pool:
            return None
        
        conn = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if commit:
                conn.commit()
                return cursor.lastrowid
            else:
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"[SessionDBSync] Query failed: {query} | Error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def session_start(self, session_uuid, child_id, parent_id=None):
        """Step 3 — Insert into Sessions Table"""
        query = """
            INSERT INTO sessions (session_uuid, child_id, parent_id, start_time, status)
            VALUES (%s, %s, %s, %s, 'IN_PROGRESS')
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        last_id = self._execute(query, (session_uuid, child_id, parent_id, now))
        logging.info(f"[SessionDBSync] Session started in DB: {session_uuid} (ID: {last_id})")
        return last_id

    def session_turn_metrics(self, session_id, turn_data):
        """Step 4 — Write Turn-Level Metrics"""
        query = """
            INSERT INTO session_turn_metrics (
                session_id, turn_number, timestamp, child_utterance, lara_response,
                detected_mood, mood_confidence, vision_attention_state, vision_presence,
                vision_gesture, vision_engagement_score, difficulty_level,
                regulation_state, reinforcement_style, strategy_applied,
                inference_ms, tts_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            session_id,
            turn_data.get("turn_number"),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            turn_data.get("child_utterance"),
            turn_data.get("lara_response"),
            turn_data.get("detected_mood"),
            turn_data.get("mood_confidence"),
            turn_data.get("vision_attention_state"),
            1 if turn_data.get("vision_presence") else 0,
            turn_data.get("vision_gesture"),
            turn_data.get("vision_engagement_score"),
            turn_data.get("difficulty_level"),
            turn_data.get("regulation_state"),
            turn_data.get("reinforcement_style"),
            turn_data.get("strategy_applied"),
            turn_data.get("inference_ms", 0),
            turn_data.get("tts_ms", 0)
        )
        self._execute(query, params)

    def session_end(self, session_id, session_uuid, child_id, final_stats):
        """Step 5 to Step 12 — Final Persistences"""
        # Step 5 — Vision Metrics
        self._persist_vision_metrics(session_id, child_id, final_stats.get("vision"))
        
        # Step 6 — Voice Metrics
        self._persist_voice_metrics(session_id, child_id, final_stats.get("voice"))
        
        # Step 7 — Emotional Metrics
        self._persist_emotional_metrics(session_uuid, child_id, final_stats.get("emotional"))
        
        # Step 8 — Learning Progress
        self._persist_learning_progress(session_id, child_id, final_stats.get("learning"))
        
        # Step 9 — Reinforcement Metrics
        self._persist_reinforcement_metrics(session_id, child_id, final_stats.get("reinforcement"))
        
        # Step 10 — Session Analytics
        self._persist_session_analytics(session_id, child_id, final_stats.get("analytics"))
        
        # Step 11 — Engagement Timeline (handled during session or bulk insert here)
        self._persist_engagement_timeline(session_id, final_stats.get("timeline"))
        
        # Step 12 — Update Session End
        self._update_session_end(session_id, final_stats.get("session_summary"))

    def _persist_vision_metrics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO child_vision_metrics (
                session_id, child_id, avg_engagement_score, avg_engagement_ui_score,
                avg_gaze_score, attention_state_focused_pct, attention_state_distracted_pct,
                attention_state_absent_pct, focused_duration_minutes, distraction_frames,
                dominant_gesture, face_confidence, gesture_confidence, object_confidence,
                pose_confidence, system_confidence, recorded_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            session_id, child_id, data.get("avg_engagement_score"), data.get("avg_engagement_ui_score"),
            data.get("avg_gaze_score"), data.get("attention_state_focused_pct"), data.get("attention_state_distracted_pct"),
            data.get("attention_state_absent_pct"), data.get("focused_duration_minutes"), data.get("distraction_frames"),
            data.get("dominant_gesture"), data.get("face_confidence"), data.get("gesture_confidence"), data.get("object_confidence"),
            data.get("pose_confidence"), data.get("system_confidence"), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self._execute(query, params)

    def _persist_voice_metrics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO child_voice_metrics (
                session_id, child_id, avg_speaking_rate_wpm, avg_utterance_length_words,
                avg_volume, utterance_count, speech_stability_score, pct_vocal_arousal,
                pct_vocal_neutral, pct_vocal_withdrawal, recorded_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            session_id, child_id, data.get("avg_speaking_rate_wpm"), data.get("avg_utterance_length_words"),
            data.get("avg_volume"), data.get("utterance_count"), data.get("speech_stability_score"), data.get("pct_vocal_arousal"),
            data.get("pct_vocal_neutral"), data.get("pct_vocal_withdrawal"), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self._execute(query, params)

    def _persist_emotional_metrics(self, session_uuid, child_id, data):
        if not data: return
        # Note: Mapping child_id_hashed to str(child_id) or actual hash if preferred
        query = """
            INSERT INTO emotional_metrics (
                session_id, child_id_hashed, mood_state, mood_confidence, frustration_score,
                frustration_streak, emotional_trend_score, stability_index, mood_score,
                primary_emotion, bayesian_confidence_score, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            session_uuid, str(child_id), data.get("mood_state"), data.get("mood_confidence"), data.get("frustration_score"),
            data.get("frustration_streak"), data.get("emotional_trend_score"), data.get("stability_index"), data.get("mood_score"),
            data.get("primary_emotion"), data.get("bayesian_confidence_score", 0.0), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self._execute(query, params)

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
            self._execute(query, params)

    def _persist_reinforcement_metrics(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO child_reinforcement_metrics (
                    session_id, child_id, style_name, total_uses, success_count,
                    success_rate, last_used_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_uses = total_uses + VALUES(total_uses),
                    success_count = success_count + VALUES(success_count),
                    success_rate = (success_count + VALUES(success_count)) / (total_uses + VALUES(total_uses)),
                    last_used_at = VALUES(last_used_at)
            """
            params = (
                session_id, child_id, item.get("style_name"), item.get("total_uses"), item.get("success_count"),
                item.get("success_rate"), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            self._execute(query, params)

    def _persist_session_analytics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO session_analytics (
                session_id, child_id, avg_engagement_score, avg_gaze_score, focus_score,
                attention_span_minutes, distraction_frequency, emotion_stability_score,
                overall_mood_score, participation_level, interaction_continuity_score,
                initiative_taking_score, task_completion_rate, positive_interactions,
                challenging_moments, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            session_id, child_id, data.get("avg_engagement_score"), data.get("avg_gaze_score"), data.get("focus_score"),
            data.get("attention_span_minutes"), data.get("distraction_frequency"), data.get("emotion_stability_score"),
            data.get("overall_mood_score"), data.get("participation_level"), data.get("interaction_continuity_score"),
            data.get("initiative_taking_score"), data.get("task_completion_rate"), data.get("positive_interactions"),
            data.get("challenging_moments"), datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        self._execute(query, params)

    def _persist_engagement_timeline(self, session_id, timeline_items):
        if not timeline_items: return
        for item in timeline_items:
            query = """
                INSERT INTO engagement_timeline (session_id, minute_index, avg_engagement, attention_state)
                VALUES (%s, %s, %s, %s)
            """
            params = (session_id, item.get("minute_index"), item.get("avg_engagement"), item.get("attention_state"))
            self._execute(query, params)

    def _update_session_end(self, session_id, summary):
        if not summary: return
        query = """
            UPDATE sessions SET
                end_time = %s,
                duration_seconds = %s,
                status = 'COMPLETED',
                total_turns = %s,
                avg_engagement_score = %s,
                dominant_mood = %s,
                peak_difficulty = %s
            WHERE id = %s
        """
        params = (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary.get("duration_seconds"),
            summary.get("total_turns"),
            summary.get("avg_engagement_score"),
            summary.get("dominant_mood"),
            summary.get("peak_difficulty"),
            session_id
        )
        self._execute(query, params)
