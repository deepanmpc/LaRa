#!/usr/bin/env python3
"""
LaRa Database Architecture Overview
This script displays the full schema and architecture of both the Python Core Memory (SQLite)
and the Dashboard Backend (MySQL), covering vision, mood, voice, and state persistence.
"""

def print_section(title):
    print(f"\n{'='*80}")
    print(f" {title.center(78)} ")
    print(f"{'='*80}")

def print_table(name, columns, description=""):
    print(f"\n[Table: {name}]")
    if description:
        print(f"Description: {description}")
    print(f"{'-'*40}")
    for col, dtype, desc in columns:
        print(f"  {col:<25} | {dtype:<10} | {desc}")

def show_core_memory():
    print_section("PYTHON CORE MEMORY (SQLite)")
    print("Database: runtime/memory/user_memory.db (Default)")
    
    print_table("user_profiles", [
        ("user_id", "TEXT (PK)", "Unique child/user identifier"),
        ("baseline_instruction_depth", "INTEGER", "Complexity level for LLM responses"),
        ("preferred_topics", "TEXT", "Topics child is interested in"),
        ("preferred_tts_speed", "REAL", "Speed of voice output")
    ], "Stores core configuration for each child.")

    print_table("learning_progress", [
        ("user_id", "TEXT (PK)", "User identifier"),
        ("concept_name", "TEXT (PK)", "Name of the skill or topic being learned"),
        ("mastery_level", "INTEGER", "Calculated mastery (0-100)"),
        ("highest_success_level", "INTEGER", "Peak performance reached"),
        ("attempt_count", "INTEGER", "Total number of interactions for this concept"),
        ("last_success_timestamp", "REAL", "Epoch time of last successful interaction")
    ], "Tracks educational progress and mastery.")

    print_table("emotional_metrics", [
        ("user_id", "TEXT (PK)", "User identifier"),
        ("concept_name", "TEXT (PK)", "Concept being taught when emotional state was captured"),
        ("frustration_count", "INTEGER", "Instances of detected frustration"),
        ("recovery_count", "INTEGER", "Instances of recovery to positive mood"),
        ("neutral_stability_count", "INTEGER", "Time spent in neutral/stable state"),
        ("last_updated", "REAL", "Epoch time of last update")
    ], "Tracks mood patterns during learning (Mood State).")

    print_table("child_preferences", [
        ("user_id", "TEXT (PK)", "User identifier"),
        ("topic", "TEXT (PK)", "Specific interest or entity mentioned"),
        ("sentiment", "TEXT", "Positive/Negative affinity detected in voice/text"),
        ("timestamp", "REAL", "Epoch time of detection")
    ], "Captures voice-detected preferences and interests.")

    print_table("reinforcement_metrics", [
        ("user_id", "TEXT (PK)", "User identifier"),
        ("preferred_style", "TEXT", "Best performing reinforcement strategy (e.g., 'calm_validation')"),
        ("total_events", "INTEGER", "Count of reinforcement events applied"),
        ("last_updated", "REAL", "Epoch time of last update")
    ], "Optimizes the reinforcement system based on success.")

def show_dashboard_db():
    print_section("DASHBOARD BACKEND (MySQL)")
    print("Database: lara_dashboard (Production)")

    print_table("users", [
        ("id", "BIGINT (PK)", "User ID"),
        ("name", "VARCHAR", "Full name"),
        ("email", "VARCHAR (U)", "Login email"),
        ("role", "ENUM", "ADMIN, PARENT, CLINICIAN"),
        ("status", "ENUM", "ACTIVE, SUSPENDED"),
        ("createdAt", "DATETIME", "Account creation time")
    ], "Dashboard user management and authentication.")

    print_table("children", [
        ("id", "BIGINT (PK)", "Child ID"),
        ("parent_id", "BIGINT (FK)", "Reference to users.id"),
        ("name", "VARCHAR", "Child's name"),
        ("age", "INTEGER", "Child's age"),
        ("grade_level", "VARCHAR", "Educational level"),
        ("created_at", "DATETIME", "Profile creation time")
    ], "Profiles for children being monitored.")

    print_table("sessions", [
        ("id", "BIGINT (PK)", "Session ID"),
        ("sessionId", "VARCHAR", "UUID of the session"),
        ("child_id", "BIGINT (FK)", "Reference to children.id"),
        ("durationSeconds", "INTEGER", "Total session length"),
        ("avgMoodConfidence", "DOUBLE", "Average confidence of mood detection"),
        ("totalInterventions", "INTEGER", "Count of system interventions"),
        ("startTime", "DATETIME", "Session start"),
        ("endTime", "DATETIME", "Session end"),
        ("status", "ENUM", "COMPLETED, ABANDONED, FAILED"),
        ("interventionUsed", "VARCHAR", "Primary tool used during session")
    ], "Main session log linking voice, mood, and system state.")

    print_table("vision_sessions", [
        ("id", "BIGINT (PK)", "Vision session ID"),
        ("child_id", "BIGINT", "Child identifier"),
        ("session_uuid", "VARCHAR (U)", "Links to main sessions table"),
        ("session_type", "VARCHAR", "Standard/Testing/Calibration"),
        ("started_at", "DATETIME", "Processing start"),
        ("ended_at", "DATETIME", "Processing end"),
        ("duration_seconds", "INTEGER", "Vision-active duration")
    ], "Vision-specific session metadata.")

    print_table("vision_metrics", [
        ("id", "BIGINT (PK)", "Metric ID"),
        ("session_id", "BIGINT (FK)", "Reference to vision_sessions.id"),
        ("focused_percent", "DOUBLE", "Time spent looking at screen/task"),
        ("distracted_percent", "DOUBLE", "Time spent looking away"),
        ("absent_percent", "DOUBLE", "Time user was not in frame"),
        ("distraction_count", "INTEGER", "Number of focus breaks"),
        ("avg_engagement_score", "DOUBLE", "Combined score of attention and engagement"),
        ("gesture_active_percent", "DOUBLE", "Hand activity detection rate"),
        ("avg_fps", "DOUBLE", "Vision pipeline performance")
    ], "Detailed Vision Perception analytics.")

    print_table("emotional_metrics", [
        ("id", "BIGINT (PK)", "Metric ID"),
        ("childIdHashed", "VARCHAR", "Hashed child ID for privacy"),
        ("moodScore", "INTEGER", "Numerical mood value (1-10)"),
        ("primaryEmotion", "VARCHAR", "Dominant emotion (Joy, Neutral, Sad, etc.)"),
        ("timestamp", "DATETIME", "Time of detection")
    ], "Time-series mood data for dashboard visualization.")

    print_table("zpd_metrics", [
        ("id", "BIGINT (PK)", "Metric ID"),
        ("childIdHashed", "VARCHAR", "Hashed child ID"),
        ("score", "INTEGER", "Zone of Proximal Development score"),
        ("timestamp", "DATETIME", "Time of detection")
    ], "State analytics for educational progression.")

    print_table("engagement_timeline", [
        ("id", "BIGINT (PK)", "Metric ID"),
        ("session_id", "BIGINT (FK)", "Reference to vision_sessions.id"),
        ("minute_index", "INTEGER", "Minute within the session"),
        ("avg_engagement", "DOUBLE", "Average engagement for this minute"),
        ("attention_state", "VARCHAR", "FOCUSED, SEMI_FOCUSED, DISTRACTED")
    ], "Granular time-series engagement for line charts.")

    print_table("tool_interventions", [
        ("id", "BIGINT (PK)", "Intervention ID"),
        ("session_id", "VARCHAR", "Reference to main session"),
        ("tool_id", "VARCHAR", "Identifier of the tool used (Voice/TTS/Visual)"),
        ("intervention_type", "VARCHAR", "Prompting, Scaffolding, Validation"),
        ("outcome", "VARCHAR", "SUCCESS, NEUTRAL, FAILURE")
    ], "Detailed breakdown of system interventions.")

def main():
    print("\n" + "*"*80)
    print(" LARA FULL DATABASE ARCHITECTURE ".center(80, '*'))
    print("*"*80)
    
    show_core_memory()
    show_dashboard_db()
    
    print_section("DATA FLOW & SYNC")
    print("1. Python Core (SQLite) handles real-time learning state and reinforcement.")
    print("2. Vision Perception (App) sends real-time metrics to Bridge/Dashboard.")
    print("3. Voice interactions update child_preferences and emotional_metrics.")
    print("4. Dashboard Backend (MySQL) aggregates data for Clinician/Parent oversight.")
    print("5. State synchronization occurs at the end of every session via Bridge.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
