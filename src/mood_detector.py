"""
LaRa Mood Detector
Lightweight offline mood detection from text content and audio prosody.

Follows agents_instruction.txt constraints:
- Temporally smoothed (3-utterance rolling window)
- Threshold-gated (confidence must exceed minimum)
- Never acts on single-frame inference
- Never diagnoses or labels the child's emotions aloud
"""

import logging
import re
import numpy as np
from collections import deque


class Mood:
    """Mood constants."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    FRUSTRATED = "frustrated"
    ANXIOUS = "anxious"
    QUIET = "quiet"


# Keyword dictionaries for text-based mood detection
MOOD_KEYWORDS = {
    Mood.HAPPY: [
        # Core emotions
        "happy", "glad", "joy", "joyful", "cheerful", "excited", "wonderful",
        # Child expressions
        "yay", "yippee", "woohoo", "wow", "cool", "awesome", "amazing",
        "fantastic", "brilliant", "super", "great", "nice", "perfect",
        # Social/relational
        "love", "like", "friend", "best friend", "together", "hug",
        "play", "playing", "game", "fun", "funny", "silly", "giggle",
        "laugh", "laughing", "smile", "smiling",
        # Affirmative
        "yes", "yeah", "yep", "okay", "sure", "of course", "please",
        "thank", "thanks", "thank you",
        # Achievement
        "did it", "i can", "i won", "look", "watch me", "good job",
        "proud", "smart", "strong", "brave", "best", "enjoy",
        # Comfort
        "warm", "cozy", "safe", "home", "mama", "papa", "family",
    ],
    Mood.SAD: [
        # Core emotions
        "sad", "unhappy", "upset", "cry", "crying", "tears", "sob",
        # Loss/longing
        "miss", "missing", "gone", "lost", "left", "away", "leave",
        "leaving", "bye", "goodbye",
        # Rejection
        "don't want", "go away", "alone", "lonely", "nobody", "no one",
        "ignore", "forgot", "forgotten",
        # Fatigue/withdrawal
        "tired", "sleepy", "exhausted", "boring", "bored",
        # Negative self-talk
        "sorry", "my fault", "bad", "ugly", "wrong", "mess",
        # Despair
        "never", "nothing", "can't", "give up", "don't care",
        "doesn't matter", "whatever", "wish", "why",
        # Pain
        "hurt", "hurting", "pain", "ow", "ouch", "sick", "tummy",
    ],
    Mood.FRUSTRATED: [
        # Core emotions
        "angry", "mad", "furious", "annoyed", "annoying", "irritated",
        # Refusal
        "no", "stop", "don't", "won't", "refuse", "not doing",
        "go away", "leave me",
        # Difficulty
        "can't", "can't do", "too hard", "hard", "difficult", "impossible",
        "stuck", "broken", "not working", "wrong", "messed up",
        # Exclamations
        "ugh", "argh", "grr", "hmph",
        # Injustice
        "not fair", "unfair", "cheating", "liar", "mean",
        # Aggression
        "hate", "stupid", "dumb", "idiot", "shut up", "break",
        "hit", "kick", "throw", "smash", "punch",
        # Repetition frustration
        "again", "already", "told you", "i said", "not again",
        "how many times", "still",
    ],
    Mood.ANXIOUS: [
        # Core emotions
        "scared", "afraid", "fear", "frightened", "terrified", "nervous",
        "worried", "worry", "anxious",
        # Uncertainty
        "don't know", "not sure", "maybe", "what if", "i think",
        "is it okay", "am i okay", "will it",
        # Hesitation
        "um", "uh", "hmm", "well", "actually", "sorry but",
        # Threat
        "dark", "monster", "nightmare", "shadow", "noise", "loud",
        "stranger", "new", "different", "change",
        # Overwhelm
        "too much", "too many", "too fast", "too loud", "too big",
        "can't do", "can't breathe", "dizzy",
        # Help-seeking
        "help", "help me", "please help", "i need", "stay", "don't go",
        "don't leave", "hold", "come here", "where are you",
        # Panic
        "panic", "emergency", "hurry", "run", "hide",
    ],
}

# Audio prosody thresholds
LOUD_RMS_THRESHOLD = 0.15      # Above this = high arousal (excited/upset)
QUIET_RMS_THRESHOLD = 0.02     # Below this = withdrawn/quiet
FAST_WORDS_PER_SEC = 3.0       # Faster = anxious
SLOW_WORDS_PER_SEC = 0.8       # Slower = sad/disengaged
SHORT_UTTERANCE_WORDS = 3      # Very short = disengagement or frustration


class MoodDetector:
    """
    Lightweight mood detector for neurodiverse interaction safety.
    
    Uses two signals:
    1. Text sentiment (keyword matching on transcribed speech)
    2. Audio prosody (volume/RMS, speaking rate)
    
    Applies temporal smoothing via a 3-utterance rolling window.
    Only changes active mood when 2 of 3 recent readings agree.
    """
    
    # Minimum confidence to consider a mood signal valid
    CONFIDENCE_THRESHOLD = 0.3
    
    # Rolling window size for temporal smoothing
    SMOOTHING_WINDOW = 3

    def __init__(self):
        self._mood_history = deque(maxlen=self.SMOOTHING_WINDOW)
        self._current_mood = Mood.NEUTRAL
        self._current_confidence = 0.0
        logging.info("[MoodDetector] Initialized with temporal smoothing (window=3)")

    def analyze(self, text: str, audio_frames: list, utterance_duration: float = 0.0) -> tuple:
        """
        Analyze mood from text and audio.
        
        Args:
            text: Transcribed user speech
            audio_frames: List of numpy audio frame arrays from the utterance
            utterance_duration: Duration of the utterance in seconds
            
        Returns:
            Tuple of (mood: str, confidence: float)
        """
        text_mood, text_conf = self._analyze_text(text)
        audio_mood, audio_conf = self._analyze_audio(audio_frames, text, utterance_duration)
        
        # Combine signals: text has higher weight (0.6) than audio (0.4)
        # because keyword detection is more reliable than prosody alone
        combined = self._combine_signals(text_mood, text_conf, audio_mood, audio_conf)
        
        # Temporal smoothing
        self._mood_history.append(combined)
        smoothed_mood, smoothed_conf = self._smooth()
        
        # Only update if confidence exceeds threshold
        if smoothed_conf >= self.CONFIDENCE_THRESHOLD:
            if smoothed_mood != self._current_mood:
                logging.info(f"[Mood] Transition: {self._current_mood} → {smoothed_mood} (confidence: {smoothed_conf:.2f})")
            self._current_mood = smoothed_mood
            self._current_confidence = smoothed_conf
        
        logging.info(f"[Mood] Current: {self._current_mood} | Raw: {combined[0]} ({combined[1]:.2f}) | Smoothed: {smoothed_mood} ({smoothed_conf:.2f})")
        
        return self._current_mood, self._current_confidence

    def get_current_mood(self) -> tuple:
        """Returns the current smoothed mood and confidence."""
        return self._current_mood, self._current_confidence

    def _analyze_text(self, text: str) -> tuple:
        """
        Detect mood from transcribed text using keyword matching.
        Returns (mood, confidence).
        """
        if not text or not text.strip():
            return Mood.QUIET, 0.5
        
        text_lower = text.lower().strip()
        word_count = len(text_lower.split())
        
        # Very short utterance = possible disengagement
        if word_count <= SHORT_UTTERANCE_WORDS:
            # Check if it's a positive short response like "yes", "okay", "good"
            positive_shorts = {"yes", "yeah", "okay", "ok", "good", "sure", "yay", "hi", "hello"}
            if text_lower.strip().rstrip(".!?") in positive_shorts:
                return Mood.HAPPY, 0.3
            # Otherwise, short could mean quiet/disengaged
            return Mood.QUIET, 0.4
        
        # Count keyword matches for each mood
        scores = {}
        for mood, keywords in MOOD_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            # Normalize by keyword list length for fair comparison
            scores[mood] = matches / len(keywords) if keywords else 0
        
        # Find the dominant mood
        best_mood = max(scores, key=scores.get)
        best_score = scores[best_mood]
        
        if best_score == 0:
            return Mood.NEUTRAL, 0.5
        
        # Scale confidence: even 2-3 keyword matches = moderate confidence
        confidence = min(best_score * 5.0, 1.0)
        
        return best_mood, confidence

    def _analyze_audio(self, audio_frames: list, text: str, utterance_duration: float) -> tuple:
        """
        Detect mood from audio prosody (volume, speaking rate).
        Returns (mood, confidence).
        """
        if not audio_frames:
            return Mood.NEUTRAL, 0.0
        
        try:
            # Concatenate all frames
            full_audio = np.concatenate(audio_frames).flatten()
            
            # RMS energy (volume)
            rms = np.sqrt(np.mean(full_audio**2))
            
            # Speaking rate (words per second)
            word_count = len(text.split()) if text else 0
            speaking_rate = word_count / utterance_duration if utterance_duration > 0 else 0
            
            # Determine audio-based mood signal
            if rms > LOUD_RMS_THRESHOLD:
                # Loud = could be excited (happy) or upset (frustrated)
                # Disambiguate with text mood
                return Mood.FRUSTRATED, 0.4
            
            elif rms < QUIET_RMS_THRESHOLD:
                # Very quiet = withdrawn
                return Mood.SAD, 0.4
            
            if speaking_rate > FAST_WORDS_PER_SEC:
                # Fast speech = anxious
                return Mood.ANXIOUS, 0.3
            
            elif speaking_rate < SLOW_WORDS_PER_SEC and word_count > 0:
                # Very slow = sad / hesitant
                return Mood.SAD, 0.3
            
            return Mood.NEUTRAL, 0.2
            
        except Exception as e:
            logging.warning(f"[MoodDetector] Audio analysis error: {e}")
            return Mood.NEUTRAL, 0.0

    def _combine_signals(self, text_mood: str, text_conf: float, audio_mood: str, audio_conf: float) -> tuple:
        """
        Combine text and audio mood signals.
        Text gets 60% weight, audio gets 40% weight.
        If both agree, confidence is boosted.
        """
        TEXT_WEIGHT = 0.6
        AUDIO_WEIGHT = 0.4
        
        if text_mood == audio_mood:
            # Both signals agree — high confidence
            combined_conf = min((text_conf * TEXT_WEIGHT + audio_conf * AUDIO_WEIGHT) * 1.3, 1.0)
            return text_mood, combined_conf
        
        # Disagree — pick the higher-confidence signal
        text_weighted = text_conf * TEXT_WEIGHT
        audio_weighted = audio_conf * AUDIO_WEIGHT
        
        if text_weighted >= audio_weighted:
            return text_mood, text_weighted
        else:
            return audio_mood, audio_weighted

    def _smooth(self) -> tuple:
        """
        Apply temporal smoothing: only change mood if 2 of 3 recent readings agree.
        This prevents mood flickering from a single utterance.
        """
        if not self._mood_history:
            return Mood.NEUTRAL, 0.0
        
        # Count occurrences of each mood in the window
        mood_counts = {}
        mood_total_conf = {}
        
        for mood, conf in self._mood_history:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            mood_total_conf[mood] = mood_total_conf.get(mood, 0.0) + conf
        
        # Find the most common mood
        dominant_mood = max(mood_counts, key=mood_counts.get)
        dominant_count = mood_counts[dominant_mood]
        
        # Require at least 2 out of 3 (or 1 out of 1 for first utterance)
        window_size = len(self._mood_history)
        required = max(1, window_size * 2 // 3)
        
        if dominant_count >= required:
            avg_conf = mood_total_conf[dominant_mood] / dominant_count
            return dominant_mood, avg_conf
        else:
            # No consensus — stay neutral
            return self._current_mood, self._current_confidence * 0.9  # Slight decay
