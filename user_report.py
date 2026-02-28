import sqlite3
import os
import time
from datetime import datetime

# Path to the database
DB_PATH = "data/lara_memory.db"

def format_ts(ts):
    if not ts or ts == 0:
        return "Never"
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def print_report():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    print("\n" + "="*60)
    print("           LaRa — USER PROGRESS REPORT")
    print("="*60)

    # 1. User Profiles
    print("\n[1] ACTIVE PROFILES")
    profiles = conn.execute("SELECT * FROM user_profiles").fetchall()
    for p in profiles:
        print(f"  • User ID: {p['user_id']}")
        print(f"    - Instruction Depth: {p['baseline_instruction_depth']} (1=Simple, 3=Detailed)")
        print(f"    - Preferred Topics:  {p['preferred_topics'] if p['preferred_topics'] else 'None yet'}")
        print(f"    - Voice Speed:       {p['preferred_tts_speed']}")

    # 2. Emotional Metrics (Mood History)
    print("\n[2] EMOTIONAL STABILITY (Mood History)")
    metrics = conn.execute("SELECT * FROM emotional_metrics").fetchall()
    if not metrics:
        print("  - No emotional data recorded yet.")
    for m in metrics:
        print(f"  • Concept: {m['concept_name']}")
        print(f"    - Stable/Neutral: {m['neutral_stability_count']} times")
        print(f"    - Frustrated:     {m['frustration_count']} times")
        print(f"    - Recovered:      {m['recovery_count']} times")
        print(f"    - Last Updated:   {format_ts(m['last_updated'])}")

    # 3. Learning Progress
    print("\n[3] LEARNING & MASTERY")
    progress = conn.execute("SELECT * FROM learning_progress").fetchall()
    if not progress:
        print("  - No learning progress recorded yet.")
    for pr in progress:
        print(f"  • Concept: {pr['concept_name']}")
        print(f"    - Mastery Level:  {pr['mastery_level']}/5")
        print(f"    - Highest Reached: {pr['highest_success_level']}")
        print(f"    - Total Attempts: {pr['attempt_count']}")
        print(f"    - Last Success:   {format_ts(pr['last_success_timestamp'])}")

    # 4. Child Preferences (Likes/Dislikes)
    print("\n[4] LEARNED PREFERENCES")
    prefs = conn.execute("SELECT * FROM child_preferences").fetchall()
    if not prefs:
        print("  - No likes or dislikes learned yet.")
    for pf in prefs:
        icon = "👍" if pf['sentiment'] == 'like' else "👎"
        print(f"  {icon} {pf['topic']} ({pf['sentiment']})")

    print("\n" + "="*60)
    conn.close()

if __name__ == "__main__":
    print_report()
