#!/usr/bin/env python3
"""
LaRa Memory & Session Test Script
Simulates a multi-turn conversation and shows what SessionState and UserMemory are doing.

Run: python3 src/test_memory_session.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from session_state import SessionState
from regulation_state import compute_regulation_state
from recovery_strategy import RecoveryStrategyManager
from reinforcement_manager import ReinforcementAdaptationManager
from user_memory import UserMemoryManager
from learning_progress import LearningProgressManager

# Colors for terminal
G = "\033[92m"   # Green
Y = "\033[93m"   # Yellow
R = "\033[91m"   # Red
C = "\033[96m"   # Cyan
M = "\033[95m"   # Magenta
D = "\033[90m"   # Dim
RESET = "\033[0m"
BOLD = "\033[1m"

def header(text):
    print(f"\n{BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}")

def show_session(s):
    print(f"  {D}├─ Turn:        {RESET}{s.turn_count}")
    print(f"  {D}├─ Mood:        {RESET}{s.mood} (conf: {s.mood_confidence:.2f})")
    print(f"  {D}├─ Difficulty:  {RESET}{s.current_difficulty}")
    print(f"  {D}├─ Frustration: {RESET}{s.consecutive_frustration} consecutive turns")
    print(f"  {D}├─ Stability:   {RESET}{s.consecutive_stability} consecutive turns")
    print(f"  {D}├─ Locked:      {RESET}{'Yes (' + str(s.difficulty_locked_turns) + ' turns)' if s.difficulty_locked_turns > 0 else 'No'}")
    print(f"  {D}└─ Last input:  {RESET}{s.last_user_input[:50] or '(none)'}")

def show_regulation(reg):
    print(f"  {D}├─ Frustration persistence: {RESET}{reg.frustration_persistence:.2f}")
    print(f"  {D}├─ Stability persistence:   {RESET}{reg.stability_persistence:.2f}")
    print(f"  {D}└─ Emotional trend:         {RESET}{reg.emotional_trend_score:+.2f} {'↑' if reg.emotional_trend_score > 0 else '↓' if reg.emotional_trend_score < 0 else '→'}")

def show_db(mem, user_id):
    print(f"\n  {C}[SQLite Database Contents]{RESET}")
    
    # User profile
    profile = mem.get_or_create_user(user_id)
    print(f"  {D}├─ User: {RESET}{profile.user_id} (depth={profile.baseline_instruction_depth}, tts_speed={profile.preferred_tts_speed})")
    
    # Emotional metrics
    rows = mem._conn.execute("SELECT * FROM emotional_metrics WHERE user_id = ?", (user_id,)).fetchall()
    if rows:
        for r in rows:
            print(f"  {D}├─ Emotional [{r['concept_name']}]: {RESET}frustration={r['frustration_count']}, recovery={r['recovery_count']}, stability={r['neutral_stability_count']}")
    else:
        print(f"  {D}├─ Emotional: {RESET}(no data yet)")
    
    # Reinforcement
    rows = mem._conn.execute("SELECT * FROM reinforcement_metrics WHERE user_id = ?", (user_id,)).fetchall()
    if rows:
        for r in rows:
            print(f"  {D}├─ Reinforcement: {RESET}style={r['preferred_style']}, events={r['total_events']}")
    else:
        print(f"  {D}├─ Reinforcement: {RESET}(no data yet)")
    
    # Learning
    rows = mem._conn.execute("SELECT * FROM learning_progress WHERE user_id = ?", (user_id,)).fetchall()
    if rows:
        for r in rows:
            print(f"  {D}└─ Learning [{r['concept_name']}]: {RESET}mastery={r['mastery_level']}/5, attempts={r['attempt_count']}")
    else:
        print(f"  {D}└─ Learning: {RESET}(no data yet)")


# =====================================================
# SETUP
# =====================================================
header("INITIALIZING COMPONENTS")

# Use a test DB so we don't mess with real data
TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lara_test_memory.db")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

session = SessionState()
memory = UserMemoryManager(db_path=TEST_DB)
strategy_mgr = RecoveryStrategyManager()
reinforcement_mgr = ReinforcementAdaptationManager(memory)
learning_mgr = LearningProgressManager(memory)

USER_ID = "test_child"
memory.get_or_create_user(USER_ID)
reinforcement_mgr.set_user(USER_ID)
learning_mgr.set_user(USER_ID)

print(f"  {G}✓{RESET} SessionState created (id: {session.session_id})")
print(f"  {G}✓{RESET} UserMemory created (db: {os.path.basename(TEST_DB)})")
print(f"  {G}✓{RESET} StrategyManager, ReinforcementManager, LearningProgress ready")

# =====================================================
# SIMULATED CONVERSATION
# =====================================================
# Each turn: (user_text, detected_mood, mood_confidence, ai_response)
turns = [
    ("Hello! I want to play!", "happy", 0.7, "Hello! I am happy to play with you. What would you like to do?"),
    ("Can we count things?", "neutral", 0.5, "Of course! Let us count together. How many fingers am I holding up?"),
    ("Three!", "happy", 0.8, "That is right! Great job! You counted three."),
    ("This is too hard, I don't get it", "frustrated", 0.7, "That is okay. Let us take it one step at a time. We can go slower."),
    ("I still don't understand", "frustrated", 0.8, "You are doing well. Let us try something simpler together."),
    ("Okay... I'll try", "neutral", 0.6, "That is great. I am here with you. Let us try this one."),
    ("I got it!", "happy", 0.9, "Wonderful! You did it! I knew you could."),
    ("What else can we do?", "neutral", 0.5, "We can try colors next. Would you like that?"),
    ("Yes please!", "happy", 0.7, "Let us start with colors. What color is the sky?"),
]

session.current_concept = "counting"

for i, (user_text, mood, conf, ai_response) in enumerate(turns):
    header(f"TURN {i+1}: \"{user_text}\"")
    
    prev_mood = session.mood
    
    # --- PRE-DECISION ---
    print(f"\n  {Y}[1] Pre-Decision Update{RESET}")
    session.update_pre_decision(mood, conf)
    
    # Check recovery
    if prev_mood in ("frustrated", "sad") and mood in ("neutral", "happy"):
        memory.record_recovery(USER_ID, session.current_concept or "general")
        reinforcement_mgr.update_metrics(reinforcement_mgr._current_style, True)
        print(f"  {G}★ Recovery detected! ({prev_mood} → {mood}){RESET}")
    
    # --- DIFFICULTY GATING ---
    print(f"\n  {Y}[2] Difficulty Gating{RESET}")
    if session.should_decrease_difficulty():
        old_diff = session.current_difficulty
        session.change_difficulty(-1)
        print(f"  {R}↓ Difficulty DECREASED: {old_diff} → {session.current_difficulty} (locked for 2 turns){RESET}")
    elif session.should_increase_difficulty():
        old_diff = session.current_difficulty
        session.change_difficulty(+1)
        print(f"  {G}↑ Difficulty INCREASED: {old_diff} → {session.current_difficulty} (locked for 2 turns){RESET}")
    else:
        reason = ""
        if session.difficulty_locked_turns > 0:
            reason = f"(locked: {session.difficulty_locked_turns} turns left)"
        elif conf < 0.6:
            reason = f"(confidence {conf:.2f} < 0.6)"
        else:
            reason = f"(frustration={session.consecutive_frustration}, stability={session.consecutive_stability})"
        print(f"  {D}→ No change {reason}{RESET}")
    
    # --- REGULATION STATE ---
    print(f"\n  {Y}[3] RegulationState{RESET}")
    regulation = compute_regulation_state(session)
    show_regulation(regulation)
    
    # --- STRATEGY ---
    print(f"\n  {Y}[4] RecoveryStrategy{RESET}")
    strategy = strategy_mgr.get_strategy(mood, conf)
    print(f"  {D}├─ Strategy: {RESET}{strategy.label}")
    print(f"  {D}├─ TTS speed: {RESET}{strategy.tts_length_scale}")
    print(f"  {D}├─ Max sentences: {RESET}{strategy.response_length_limit}")
    print(f"  {D}└─ Prompt: {RESET}{strategy.prompt_addition[:60]}..." if strategy.prompt_addition else f"  {D}└─ Prompt: {RESET}(none)")
    
    # --- REINFORCEMENT ---
    print(f"\n  {Y}[5] Reinforcement{RESET}")
    r_style = reinforcement_mgr.get_style(regulation)
    print(f"  {D}└─ Style: {RESET}{r_style}")
    
    # --- POST-RESPONSE ---
    print(f"\n  {Y}[6] Post-Response Update{RESET}")
    session.update_post_response(user_text, ai_response)
    print(f"  {M}LaRa:{RESET} {ai_response}")
    
    # --- RECORD METRICS ---
    memory.record_emotional_metric(USER_ID, session.current_concept or "general", mood)
    
    # Add a learning attempt on turn 3 and 7 (simulating task completion)
    if i == 2:
        learning_mgr.update_attempt("counting", session.current_difficulty, True)
        print(f"  {G}★ Learning: counting attempt recorded (success){RESET}")
    if i == 6:
        learning_mgr.update_attempt("counting", session.current_difficulty, True)
        print(f"  {G}★ Learning: counting attempt recorded (success){RESET}")
    
    # Show session state
    print(f"\n  {C}[Session State]{RESET}")
    show_session(session)

# =====================================================
# FINAL STATE
# =====================================================
header("FINAL DATABASE STATE")
reinforcement_mgr.persist_session_metrics()
show_db(memory, USER_ID)

header("SESSION SUMMARY")
show_session(session)
summary = memory.get_session_summary(USER_ID)
print(f"\n  {C}Dashboard Export:{RESET}")
print(f"  {summary}")

# Cleanup
memory.close()
os.remove(TEST_DB)
print(f"\n  {D}(Test database cleaned up){RESET}")
header("TEST COMPLETE")
