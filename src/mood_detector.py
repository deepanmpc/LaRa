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
MAX_SPEAKING_RATE = 6.0        # Cap to prevent artificial spikes
MIN_DURATION_FOR_RATE = 0.5    # Ignore speaking rate below this duration


def _keyword_match_count(keywords: list, text_lower: str) -> int:
    """
    Count keyword matches using word-boundary regex.
    Prevents false positives like 'I don't hate it' triggering on 'hate'.
    Multi-word phrases (e.g. 'too hard', 'not fair') are supported.
    """
    count = 0
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, text_lower):
            count += 1
    return count


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
        self._consecutive_neutral_count = 0  # For mood decay
        self._last_speaking_rate = 0.0       # For rate smoothing
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
        audio_mood, audio_conf = self._analyze_audio(audio_frames, text, text_mood, utterance_duration)
        
        # Combine signals: text has higher weight (0.6) than audio (0.4)
        # because keyword detection is more reliable than prosody alone
        combined = self._combine_signals(text_mood, text_conf, audio_mood, audio_conf)
        
        # Temporal smoothing
        self._mood_history.append(combined)
        smoothed_mood, smoothed_conf = self._smooth()
        
        # Mood decay: if consecutive neutral readings, decay confidence toward neutral
        if combined[0] == Mood.NEUTRAL:
            self._consecutive_neutral_count += 1
        else:
            self._consecutive_neutral_count = 0
        
        if self._consecutive_neutral_count >= 2 and self._current_mood != Mood.NEUTRAL:
            self._current_confidence *= 0.8
            if self._current_confidence < self.CONFIDENCE_THRESHOLD:
                logging.info(f"[Mood] Decay: {self._current_mood} → neutral (confidence decayed below threshold)")
                self._current_mood = Mood.NEUTRAL
                self._current_confidence = 0.0
                return self._current_mood, self._current_confidence
        
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
        Detect mood from transcribed text using word-boundary regex matching.
        Returns (mood, confidence).
        """
        if not text or not text.strip():
            return Mood.QUIET, 0.5
        
        text_lower = text.lower().strip()
        word_count = len(text_lower.split())
        
        # Short utterance handling — check specific keywords before defaulting to QUIET
        if word_count <= SHORT_UTTERANCE_WORDS:
            cleaned = text_lower.rstrip(".!?")
            
            # Positive short response
            positive_shorts = {"yes", "yeah", "okay", "ok", "good", "sure", "yay", "hi", "hello", "cool", "nice"}
            if cleaned in positive_shorts:
                return Mood.HAPPY, 0.3
            
            # Check frustration keywords in short utterance
            if _keyword_match_count(MOOD_KEYWORDS[Mood.FRUSTRATED], text_lower) > 0:
                return Mood.FRUSTRATED, 0.35
            
            # Check anxiety/help-seeking keywords in short utterance
            if _keyword_match_count(MOOD_KEYWORDS[Mood.ANXIOUS], text_lower) > 0:
                return Mood.ANXIOUS, 0.35
            
            # Check sad keywords
            if _keyword_match_count(MOOD_KEYWORDS[Mood.SAD], text_lower) > 0:
                return Mood.SAD, 0.35
            
            # No signal — default to quiet (low confidence)
            return Mood.QUIET, 0.3
        
        # Full utterance: count keyword matches using word-boundary regex
        scores = {}
        for mood, keywords in MOOD_KEYWORDS.items():
            matches = _keyword_match_count(keywords, text_lower)
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

    def _analyze_audio(self, audio_frames: list, text: str, text_mood: str, utterance_duration: float) -> tuple:
        """
        Detect mood from audio prosody (volume, speaking rate).
        Uses text_mood to disambiguate loud audio signals.
        Returns (mood, confidence).
        """
        if not audio_frames:
            return Mood.NEUTRAL, 0.0
        
        try:
            # Concatenate all frames
            full_audio = np.concatenate(audio_frames).flatten()
            
            # RMS energy (volume)
            rms = np.sqrt(np.mean(full_audio**2))
            
            # Speaking rate (words per second) with safety caps
            word_count = len(text.split()) if text else 0
            if utterance_duration >= MIN_DURATION_FOR_RATE and word_count > 0:
                speaking_rate = min(word_count / utterance_duration, MAX_SPEAKING_RATE)
                # Smooth with previous rate to reduce spikes
                speaking_rate = (speaking_rate + self._last_speaking_rate) / 2.0 if self._last_speaking_rate > 0 else speaking_rate
                self._last_speaking_rate = speaking_rate
            else:
                # Duration too short for reliable rate — ignore
                speaking_rate = 0
            
            # Volume-based mood — disambiguated with text mood (no bias)
            if rms > LOUD_RMS_THRESHOLD:
                if text_mood == Mood.HAPPY:
                    return Mood.HAPPY, 0.35
                elif text_mood == Mood.FRUSTRATED:
                    return Mood.FRUSTRATED, 0.4
                else:
                    # Loud but unclear — lean toward anxious (lower confidence)
                    return Mood.ANXIOUS, 0.25
            
            elif rms < QUIET_RMS_THRESHOLD:
                # Very quiet — only SAD if text has negative keywords
                # Otherwise QUIET (a calm child is not a sad child)
                if text_mood in (Mood.SAD, Mood.FRUSTRATED, Mood.ANXIOUS):
                    return Mood.SAD, 0.35
                else:
                    return Mood.QUIET, 0.25
            
            # Speaking rate signals (only if rate is valid)
            if speaking_rate > 0:
                if speaking_rate > FAST_WORDS_PER_SEC:
                    return Mood.ANXIOUS, 0.3
                elif speaking_rate < SLOW_WORDS_PER_SEC:
                    return Mood.SAD, 0.25
            
            return Mood.NEUTRAL, 0.2
            
        except Exception as e:
            logging.warning(f"[MoodDetector] Audio analysis error: {e}")
            return Mood.NEUTRAL, 0.0

    def _combine_signals(self, text_mood: str, text_conf: float, audio_mood: str, audio_conf: float) -> tuple:
        """
        Combine text and audio mood signals.
        Text gets 60% weight, audio gets 40% weight.
        If text confidence is very low, reduce text weight dynamically
        to prevent Whisper transcription errors from dominating.
        If both agree, confidence is boosted.
        """
        # Dynamic weight: reduce text influence when confidence is very low
        if text_conf < 0.2:
            TEXT_WEIGHT = 0.35
            AUDIO_WEIGHT = 0.65
        else:
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
