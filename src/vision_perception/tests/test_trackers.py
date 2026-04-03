import sys
import os
import pytest

# Setup paths
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)

from tracking.engagement import EngagementTracker
from tracking.attention import AttentionTracker, FOCUS_CONFIRM_FRAMES, DISTRACT_CONFIRM_FRAMES

def test_engagement_initial():
    t = EngagementTracker()
    score, ui_score = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    assert score == 0.0
    assert ui_score == 0.0

def test_engagement_boost():
    t = EngagementTracker()
    # Continuous positive signal
    for _ in range(30):
        score, ui_score = t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    assert score > 0.95
    assert ui_score > 0.95

def test_engagement_decay():
    t = EngagementTracker()
    # First get it high
    for _ in range(30):
        t.update(face_present=True, looking_at_screen=True, gesture="OPEN_PALM")
    
    # Then drop it
    for _ in range(20):
        score, ui_score = t.update(face_present=False, looking_at_screen=False, gesture="NONE")
    
    assert score < 0.1
    # UI score should be smoother (higher during decay)
    assert ui_score >= score

def test_engagement_labels():
    t = EngagementTracker()
    assert t.label(0.9) == "Highly Engaged"
    assert t.label(0.5) == "Moderately Engaged"
    assert t.label(0.1) == "Frequently Distracted"

def test_attention_transitions():
    t = AttentionTracker()
    assert t.state == "UNKNOWN"
    
    # Focused path
    for _ in range(FOCUS_CONFIRM_FRAMES):
        state, frames = t.update(presence=True, looking_at_screen=True)
    assert state == "FOCUSED"
    assert frames == 0
    
    # Distracted path
    for _ in range(DISTRACT_CONFIRM_FRAMES):
        state, frames = t.update(presence=True, looking_at_screen=False)
    assert state == "DISTRACTED"
    assert frames == 0 # First frame of distracted
    
    # Counting distraction frames
    state, frames = t.update(presence=True, looking_at_screen=False)
    assert frames == 1

def test_attention_absent():
    t = AttentionTracker()
    state, frames = t.update(presence=False, looking_at_screen=True)
    assert state == "ABSENT"
    
    # Resetting distraction counter on absent
    t.state = "DISTRACTED"
    t._distraction_frames = 10
    state, frames = t.update(presence=False, looking_at_screen=False)
    assert state == "ABSENT"
    assert frames == 0

def test_attention_reset():
    t = AttentionTracker()
    t.update(presence=True, looking_at_screen=True)
    t.reset()
    assert t.state == "UNKNOWN"
    assert t._focus_frames == 0
    assert t._distraction_frames == 0
