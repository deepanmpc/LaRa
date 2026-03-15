import sys
import os
import random
import time
from collections import Counter

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from mood.mood_detector import MoodDetector, Mood

def generate_cases():
    """Generates thousands of test cases via combinatorial expansion."""
    
    prefixes = ["", "I am ", "I feel ", "It is ", "Feeling ", "You are ", "That is ", "I'm ", "I am so ", "I feel very "]
    negations = ["not ", "never ", "don't feel ", "cannot be ", "isn't ", "is not "]
    intensifiers = ["really ", "very ", "extremely ", "so ", "quite ", "fairly "]
    suffixes = ["", " today", " now", " right now", "!", ".", "...", " I guess"]

    # Mood keyword samples from the detector's own dictionary
    mood_samples = {
        Mood.HAPPY: ["happy", "excited", "wonderful", "joyful", "great", "amazing", "awesome"],
        Mood.SAD: ["sad", "unhappy", "upset", "crying", "lonely", "hurt", "bad"],
        Mood.FRUSTRATED: ["angry", "mad", "annoyed", "stuck", "broken", "impossible", "hate"],
        Mood.ANXIOUS: ["scared", "worried", "nervous", "afraid", "panic", "shaking", "help"],
        Mood.NEUTRAL: ["okay", "sure", "maybe", "book", "table", "chair", "the", "and"]
    }

    test_cases = []

    # 1. Explicit Positives (~1000 cases)
    for mood, words in mood_samples.items():
        if mood == Mood.NEUTRAL: continue
        for p in prefixes:
            for i in ["", "really ", "very "]:
                for w in words:
                    for s in suffixes:
                        text = f"{p}{i}{w}{s}".strip()
                        test_cases.append((text, mood, "explicit"))

    # 2. Negated Moods (~1500 cases)
    # Most negations should result in NEUTRAL or a non-source mood.
    # We'll expect NEUTRAL for "I am not happy".
    for mood, words in mood_samples.items():
        if mood == Mood.NEUTRAL: continue
        for p in ["I am ", "I feel ", "It's ", "Everything is "]:
            for n in negations:
                for w in words:
                    for s in suffixes:
                        text = f"{p}{n}{w}{s}".strip()
                        # Negated signal should NOT trigger that mood.
                        test_cases.append((text, Mood.NEUTRAL, "negated"))

    # 3. Neutral Fillers (~500 cases)
    filler_phrases = [
        "The weather is nice", "I have a pen", "Where is the cat?", 
        "I am sitting here", "Just a normal day", "Nothing special happened",
        "The sky is blue", "Grass is green", "One plus one is two"
    ]
    for f in filler_phrases:
        for s in suffixes:
            test_cases.append((f"{f}{s}", Mood.NEUTRAL, "neutral_filler"))

    # 4. Mixed Signals (~500 cases)
    # "I am happy but a little worried" -> Should pick dominant or stay neutral/mixed.
    # Detector picks max score.
    mixed = [
        ("I am happy but sad", Mood.HAPPY, "mixed"), # happy usually comes first
        ("I feel great but also a bit nervous", Mood.HAPPY, "mixed"),
        ("It's amazing but I'm scared", Mood.HAPPY, "mixed"),
    ]
    for text, expected, cat in mixed:
        for s in suffixes:
            test_cases.append((f"{text}{s}", expected, "mixed"))

    return test_cases

def run_mass_test():
    detector = MoodDetector()
    cases = generate_cases()
    
    print(f"Starting Massive Stress Test: {len(cases)} cases...")
    
    results = {
        "explicit": {"pass": 0, "total": 0},
        "negated": {"pass": 0, "total": 0},
        "neutral_filler": {"pass": 0, "total": 0},
        "mixed": {"pass": 0, "total": 0}
    }
    
    failures = []
    
    start_time = time.time()
    
    for text, expected, category in cases:
        # Reset history for each case to isolate results
        detector._mood_history.clear()
        detector._current_mood = Mood.NEUTRAL
        detector._consecutive_neutral_count = 0
        
        # We test the analyze() method's text-only path
        mood, conf = detector.analyze(text, [], 1.0)
        
        results[category]["total"] += 1
        
        # For negated cases, "passing" means NOT being the source mood
        if category == "negated":
            if mood != expected and mood != Mood.NEUTRAL:
                # If "not happy" becomes "sad", it's still potentially a pass 
                # depending on philosophy, but we'll stick to NEUTRAL as ideal.
                pass 
            if mood == Mood.NEUTRAL:
                results[category]["pass"] += 1
            else:
                failures.append(f"[{category}] '{text}' -> got {mood}, expected {expected}")
        else:
            if mood == expected:
                results[category]["pass"] += 1
            else:
                failures.append(f"[{category}] '{text}' -> got {mood}, expected {expected}")

    duration = time.time() - start_time
    
    print("\n" + "="*40)
    print("MASSIVE MOOD TEST RESULTS")
    print("="*40)
    
    total_pass = 0
    total_cases = 0
    
    for cat, stats in results.items():
        acc = (stats["pass"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"{cat.upper():<15}: {stats['pass']}/{stats['total']} ({acc:.1f}%)")
        total_pass += stats["pass"]
        total_cases += stats["total"]
    
    overall_acc = (total_pass / total_cases) * 100
    print("-"*40)
    print(f"OVERALL ACCURACY: {total_pass}/{total_cases} ({overall_acc:.1f}%)")
    print(f"TEST DURATION: {duration:.2f}s")
    print("="*40)
    
    if failures:
        print("\nMixed Failures:")
        for f in failures:
            if "[mixed]" in f:
                print(f"  - {f}")
        
        print(f"\nOther Sample Failures (showing first 30):")
        other_failures = [f for f in failures if "[mixed]" not in f]
        for f in other_failures[:30]:
            print(f"  - {f}")

if __name__ == "__main__":
    run_mass_test()
