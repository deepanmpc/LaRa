import logging
import time
import json
import hashlib
from datetime import datetime
from threading import Lock
from src.persistence.db import Database
from src.events.event_bus import EventBus, EventType
from src.persistence.data_validator import DataValidator

class SessionDBSync:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if SessionDBSync._instance is not None:
            raise RuntimeError("SessionDBSync is a singleton. Use get()")
        self.db = Database.get()
        self._register_subscribers()

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = SessionDBSync()
        return cls._instance

    def _register_subscribers(self):
        bus = EventBus.get()
        bus.subscribe(EventType.SESSION_STARTED, self._on_session_started)
        bus.subscribe(EventType.TURN_COMPLETED, self._on_turn_completed)
        bus.subscribe(EventType.ENGAGEMENT_MINUTE_SYNC, self._on_engagement_minute_sync)
        bus.subscribe(EventType.SESSION_COMPLETED, self._on_session_completed)
        # Other updates can be subscribed as needed
        bus.subscribe(EventType.VISION_UPDATE, lambda d: logging.debug(f"[SessionDBSync] Vision Update: {d}"))
        bus.subscribe(EventType.EMOTION_UPDATE, lambda d: logging.debug(f"[SessionDBSync] Emotion Update: {d}"))
        bus.subscribe(EventType.LEARNING_UPDATE, lambda d: logging.debug(f"[SessionDBSync] Learning Update: {d}"))

    def _on_session_started(self, data):
        self.session_start(data['session_uuid'], data['child_id'], data.get('parent_id'))

    def _on_turn_completed(self, data):
        self.session_turn_metrics(data['db_id'], data['turn_data'])

    def _on_engagement_minute_sync(self, data):
        self.engagement_minute_sync(data['db_id'], data['minute_index'], data['avg_engagement'], data['attention_state'])

    def _on_session_completed(self, data):
        self.session_end(data['db_id'], data['session_uuid'], data['child_id'], data['final_stats'])

    def session_start(self, session_uuid, child_id, parent_id=None):
        """Step 4 — Insert into Sessions Table"""
        child_id_val = str(child_id or 1)
        child_id_hashed = hashlib.md5(child_id_val.encode()).hexdigest()[:16]
        
        query = """
            INSERT INTO sessions (
                session_uuid, session_id, child_id, child_id_hashed, parent_id, start_time, status, completion_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, 'IN_PROGRESS', 'IN_PROGRESS', NOW())
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        last_id = self.db.execute(query, (session_uuid, session_uuid, child_id, child_id_hashed, parent_id, now))
        
        # Also create a VisionSession entry (required by engagement_timeline FK)
        try:
            v_query = """
                INSERT INTO vision_sessions (session_uuid, child_id, started_at, session_type)
                VALUES (%s, %s, %s, 'standard')
                ON DUPLICATE KEY UPDATE started_at = VALUES(started_at)
            """
            v_last_id = self.db.execute(v_query, (session_uuid, child_id, now))
            
            # If it's a duplicate, we need to fetch the ID
            if v_last_id == 0 or v_last_id is None:
                row = self.db.fetch_one("SELECT id FROM vision_sessions WHERE session_uuid = %s", (session_uuid,))
                v_last_id = row['id'] if row else None
            
            self._vision_session_id = v_last_id
        except Exception as e:
            logging.warning(f"[SessionDBSync] VisionSession start failed: {e}")
            self._vision_session_id = None

        logging.info(f"[SessionDBSync] Session started: {session_uuid} (ID: {last_id}, VisionID: {self._vision_session_id})")
        
        return last_id, child_id_hashed

    def session_turn_metrics(self, session_id, turn_data):
        """Step 5 — Write Turn-Level Metrics with Validation"""
        if not DataValidator.validate_turn_metrics(turn_data):
            logging.error(f"[SessionDBSync] Turn metrics rejected for session {session_id}")
            return

        query = """
            INSERT INTO session_turn_metrics (
                session_id, turn_number, timestamp, child_utterance, child_utterance_length,
                lara_response, detected_mood, mood_confidence, difficulty_level,
                vision_attention_state, vision_presence, vision_engagement_score,
                vision_gesture, vision_distraction_frames, regulation_state,
                frustration_persistence, stability_persistence, emotional_trend_score,
                reinforcement_style, strategy_applied, inference_ms, tts_ms, total_latency_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        child_utt = turn_data.get("child_utterance", "")
        inf_ms = turn_data.get("inference_ms", 0)
        tts_ms = turn_data.get("tts_ms", 0)
        
        trend = turn_data.get("emotional_trend_score", 0.0)
        reg_str = "stable"
        if trend > 0.3: reg_str = "improving"
        elif trend < -0.3: reg_str = "declining"

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
            reg_str,
            turn_data.get("frustration_persistence", 0.0),
            turn_data.get("stability_persistence", 0.0),
            trend,
            turn_data.get("reinforcement_style"),
            turn_data.get("strategy_applied"),
            inf_ms,
            tts_ms,
            inf_ms + tts_ms
        )
        self.db.execute(query, params)

    def engagement_minute_sync(self, session_id, minute_index, avg_engagement, attention_state):
        """Step 6 — Persist Engagement Timeline (Every 60s)"""
        v_id = getattr(self, '_vision_session_id', None)
        if not v_id:
            row = self.db.fetch_one("SELECT id FROM vision_sessions WHERE session_uuid = (SELECT session_uuid FROM sessions WHERE id = %s)", (session_id,))
            v_id = row['id'] if row else None
            self._vision_session_id = v_id
            
        if not v_id: return

        query = """
            INSERT INTO engagement_timeline (session_id, minute_index, avg_engagement, attention_state)
            VALUES (%s, %s, %s, %s)
        """
        self.db.execute(query, (v_id, minute_index, avg_engagement, attention_state))

    def session_end(self, session_id, session_uuid, child_id, final_stats):
        """Step 7 to Step 13 — Final Persistences"""
        self._persist_vision_metrics(session_id, child_id, final_stats.get("vision"))
        self._persist_voice_metrics(session_id, child_id, final_stats.get("voice"))
        self._persist_emotional_metrics(session_id, child_id, final_stats.get("emotional"))
        self._persist_learning_progress(session_id, child_id, final_stats.get("learning"))
        self._persist_reinforcement_metrics(session_id, child_id, final_stats.get("reinforcement"))
        self._persist_session_analytics(session_id, child_id, final_stats.get("analytics"))
        
        self._upsert_activity_performance(session_id, child_id, final_stats.get("activities", []))
        self._insert_difficulty_trajectory(session_id, child_id, final_stats.get("difficulty_trajectory", []))
        self._update_session_end(session_id, session_uuid, final_stats.get("session_summary"))
        self.compute_longitudinal_metrics(child_id)
        self._upsert_weekly_summary(child_id, final_stats.get("session_summary"))
        self.compute_session_risks(session_id, child_id)
        self.sync_knowledge_graph(child_id)

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
                avg_volume, utterance_count, speech_stability_score, pct_vocal_neutral,
                pct_vocal_arousal, pct_vocal_withdrawal, recorded_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        stability = data.get("speech_stability_score", 0.0)
        if stability > 1.0: stability /= 100.0
        
        params = (
            session_id, child_id, data.get("avg_speaking_rate_wpm"), data.get("avg_utterance_length_words"),
            data.get("avg_volume"), data.get("utterance_count"), stability, data.get("pct_vocal_arousal"),
            data.get("pct_vocal_neutral"), data.get("pct_vocal_withdrawal")
        )
        self.db.execute(query, params)

    def _persist_emotional_metrics(self, session_id, child_id, data):
        if not data: return
        child_id_hashed = hashlib.md5(str(child_id).encode()).hexdigest()[:16]
        
        query = """
            INSERT INTO emotional_metrics (
                session_id, child_id_hashed, mood_state, mood_confidence, frustration_score,
                frustration_streak, emotional_trend_score, stability_index, mood_score,
                primary_emotion, bayesian_confidence_score, timestamp
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (
            session_id, child_id_hashed, data.get("mood_state"), data.get("mood_confidence"), data.get("frustration_score"),
            data.get("frustration_streak"), data.get("emotional_trend_score"), data.get("stability_index"), data.get("mood_score"),
            data.get("primary_emotion"), data.get("bayesian_confidence_score", 0.0)
        )
        self.db.execute(query, params)
        
        history_query = """
            INSERT INTO child_emotional_history (
                child_id, session_id, recorded_date, mood_score, primary_emotion,
                frustration_count, recovery_count, stability_count, happy_count, pct_positive, pct_negative
            ) VALUES (%s, %s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s)
        """
        h_params = (
            child_id, session_id, data.get("mood_score"), data.get("primary_emotion"),
            data.get("frustration_streak"), 0, data.get("stability_index"), 
            1 if data.get("mood_state") == "happy" else 0,
            70.0, 30.0
        )
        self.db.execute(history_query, h_params)

    def _persist_learning_progress(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO child_learning_progress (
                    session_id, child_id, concept_name, attempt_count, success_count,
                    failure_count, mastery_percentage, success_rate, current_difficulty,
                    peak_difficulty_reached, last_attempted_at, total_time_spent_seconds
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                ON DUPLICATE KEY UPDATE
                    session_id = VALUES(session_id),
                    attempt_count = attempt_count + VALUES(attempt_count),
                    success_count = success_count + VALUES(success_count),
                    failure_count = failure_count + VALUES(failure_count),
                    mastery_percentage = VALUES(mastery_percentage),
                    success_rate = (success_count + VALUES(success_count)) / (attempt_count + VALUES(attempt_count)),
                    current_difficulty = VALUES(current_difficulty),
                    peak_difficulty_reached = GREATEST(peak_difficulty_reached, VALUES(peak_difficulty_reached)),
                    last_attempted_at = NOW(),
                    total_time_spent_seconds = total_time_spent_seconds + VALUES(total_time_spent_seconds)
            """
            params = (
                session_id, child_id, item.get("concept_name"), item.get("attempt_count"), item.get("success_count"),
                item.get("failure_count"), item.get("mastery_percentage"), 
                (item.get("success_count", 0) / item.get("attempt_count", 1)),
                item.get("current_difficulty"), item.get("peak_difficulty_reached"), item.get("total_time_spent_seconds")
            )
            self.db.execute(query, params)

    def _persist_reinforcement_metrics(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO child_reinforcement_metrics (
                    session_id, child_id, style_name, total_uses, success_count,
                    success_rate, total_events, last_used_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    session_id = VALUES(session_id),
                    total_uses = total_uses + VALUES(total_uses),
                    success_count = success_count + VALUES(success_count),
                    total_events = total_events + VALUES(total_events),
                    success_rate = (success_count + VALUES(success_count)) / (total_uses + VALUES(total_uses)),
                    last_used_at = NOW()
            """
            params = (
                session_id, child_id, item.get("style_name"), item.get("total_uses"), item.get("success_count"),
                item.get("success_rate"), item.get("total_uses")
            )
            self.db.execute(query, params)

    def _persist_session_analytics(self, session_id, child_id, data):
        if not data: return
        query = """
            INSERT INTO session_analytics (
                session_id, child_id, avg_engagement_score, avg_gaze_score, focus_score,
                attention_span_minutes, distraction_frequency, emotion_stability_score,
                overall_mood_score, primary_emotion, participation_level, interaction_continuity_score,
                initiative_taking_score, task_completion_rate, positive_interactions,
                challenging_moments, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        params = (
            session_id, child_id, data.get("avg_engagement_score"), data.get("avg_gaze_score"), data.get("focus_score"),
            data.get("attention_span_minutes"), data.get("distraction_frequency"), data.get("emotion_stability_score"),
            data.get("overall_mood_score"), data.get("primary_emotion", "neutral"), data.get("participation_level"), 
            data.get("interaction_continuity_score"), data.get("initiative_taking_score"), data.get("task_completion_rate"), 
            data.get("positive_interactions"), data.get("challenging_moments")
        )
        self.db.execute(query, params)

    def _upsert_activity_performance(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO child_activity_performance (
                    child_id, session_id, activity_name, score, completion_count, avg_score, last_played_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    session_id = VALUES(session_id),
                    completion_count = completion_count + VALUES(completion_count),
                    avg_score = (avg_score * completion_count + VALUES(score)) / (completion_count + 1),
                    last_played_at = NOW()
            """
            params = (
                child_id, session_id, item.get("name"), item.get("score"), 
                item.get("completions", 1), item.get("score")
            )
            self.db.execute(query, params)

    def _insert_difficulty_trajectory(self, session_id, child_id, items):
        if not items: return
        for item in items:
            query = """
                INSERT INTO session_difficulty_trajectory (
                    session_id, child_id, turn_number, difficulty_before, difficulty_after, direction, reason
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                session_id, child_id, item.get("turn_number"), item.get("before"),
                item.get("after"), item.get("direction"), item.get("reason")
            )
            self.db.execute(query, params)

    def _update_session_end(self, session_id, session_uuid, summary):
        if not summary: return
        query = """
            UPDATE sessions SET
                end_time = NOW(),
                duration_seconds = %s,
                status = 'COMPLETED',
                completion_status = 'COMPLETED',
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
        
        # Also update VisionSession
        v_query = """
            UPDATE vision_sessions SET
                ended_at = NOW(),
                duration_seconds = %s
            WHERE session_uuid = %s
        """
        self.db.execute(v_query, (summary.get("duration_seconds"), session_uuid))

    def _upsert_weekly_summary(self, child_id, summary):
        if not summary: return
        query = """
            INSERT INTO weekly_session_summaries (
                child_id, week_start_date, sessions_this_week, total_duration_minutes,
                avg_mood_score, avg_focus_score, weekly_goal_progress
            ) VALUES (%s, CURDATE() - INTERVAL (WEEKDAY(CURDATE())) DAY, 1, %s, %s, %s, 20)
            ON DUPLICATE KEY UPDATE
                sessions_this_week = sessions_this_week + 1,
                total_duration_minutes = total_duration_minutes + VALUES(total_duration_minutes),
                avg_mood_score = (avg_mood_score * (sessions_this_week - 1) + VALUES(avg_mood_score)) / sessions_this_week,
                weekly_goal_progress = LEAST(100, (sessions_this_week * 100) / 5)
        """
        params = (
            child_id, 
            summary.get("duration_seconds", 0) // 60,
            50, # Placeholder
            70  # Placeholder
        )
        self.db.execute(query, params)

    def compute_longitudinal_metrics(self, child_id):
        """Step 14 — Update student_longitudinal_metrics"""
        sessions = self.db.fetch_all(
            "SELECT id, avg_engagement_score, total_turns FROM sessions WHERE child_id = %s ORDER BY start_time DESC LIMIT 14",
            (child_id,)
        )
        if not sessions: return

        progress = self.db.fetch_all(
            "SELECT mastery_percentage FROM child_learning_progress WHERE child_id = %s ORDER BY id DESC LIMIT 20",
            (child_id,)
        )
        mastery_vel = 0.0
        if len(progress) >= 2:
            mastery_vel = float(progress[0]['mastery_percentage'] or 0) - float(progress[-1]['mastery_percentage'] or 0)

        engagements = [float(s['avg_engagement_score'] or 0) for s in sessions]
        volatility7 = 0.0
        if len(engagements) >= 7:
            avg = sum(engagements[:7]) / 7
            volatility7 = (sum((x - avg)**2 for x in engagements[:7]) / 7)**0.5

        query = """
            INSERT INTO student_longitudinal_metrics (
                student_id, rolling_volatility7, rolling_volatility14, recovery_trend,
                mastery_velocity, intervention_decay_index, frustration_risk_score,
                independence_score, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                rolling_volatility7 = VALUES(rolling_volatility7),
                rolling_volatility14 = VALUES(rolling_volatility14),
                recovery_trend = VALUES(recovery_trend),
                mastery_velocity = VALUES(mastery_velocity),
                last_updated = NOW()
        """
        params = (str(child_id), volatility7, volatility7 * 1.2, 0.5, mastery_vel, 0.2, 0.1, 0.8)
        self.db.execute(query, params)

    def compute_session_risks(self, session_id, child_id):
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

        meltdown_risk = 0.0
        if max_frustration_streak >= 3: meltdown_risk = 0.8
        
        engagement_decay = 0.0
        if len(turns) >= 5:
            first_avg = sum(float(t['vision_engagement_score'] or 0) for t in turns[:2]) / 2
            last_avg = sum(float(t['vision_engagement_score'] or 0) for t in turns[-2:]) / 2
            if last_avg < first_avg: engagement_decay = (first_avg - last_avg)

        logging.info(f"[Risk] Session {session_id} Risks -> Meltdown: {meltdown_risk}, Decay: {engagement_decay}")

    def sync_knowledge_graph(self, child_id):
        """Step 3 — Sync Mastery from Learning Progress to Knowledge Graph"""
        child_id_hashed = hashlib.md5(str(child_id).encode()).hexdigest()[:16]
        
        # Fetch current mastery for all concepts
        progress = self.db.fetch_all(
            "SELECT concept_name, mastery_percentage FROM child_learning_progress WHERE child_id = %s",
            (child_id,)
        )
        
        if not progress: return

        for p in progress:
            concept = p['concept_name'].lower()
            mastery = (p['mastery_percentage'] or 0.0) / 100.0
            
            # Update matching nodes in knowledge_graph_nodes
            query = """
                UPDATE knowledge_graph_nodes
                SET computed_weight = %s
                WHERE child_id_hashed = %s AND LOWER(node_id) = %s
            """
            self.db.execute(query, (mastery, child_id_hashed, concept))
            
        logging.info(f"[KnowledgeGraph] Synced {len(progress)} concepts for child {child_id}")
