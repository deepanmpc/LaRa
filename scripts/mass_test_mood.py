import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from mood.mood_detector import MoodDetector, Mood, PRECOMPILED_PATTERNS, MOOD_KEYWORDS, _keyword_match_count

def generate_cases():
    """Generates thousands of test cases via combinatorial expansion."""
    
    prefixes = ["", "I am ", "I feel ", "It is ", "Feeling ", "You are ", "That is ", "I'm ", "I am so ", "I feel very "]
    negations = ["not ", "never ", "don't feel ", "cannot be ", "isn't ", "is not "]
    suffixes = ["", " today", " now", " right now", "!", ".", "...", " I guess"]

    # Mood keyword samples
    mood_samples = {
        Mood.HAPPY: ["happy", "excited", "wonderful", "joyful", "great", "amazing", "awesome"],
        Mood.SAD: ["sad", "unhappy", "upset", "crying", "lonely", "hurt", "bad"],
        Mood.FRUSTRATED: ["angry", "mad", "annoyed", "stuck", "broken", "impossible", "hate"],
        Mood.ANXIOUS: ["scared", "worried", "nervous", "afraid", "panic", "shaking", "help"],
        Mood.NEUTRAL: ["okay", "sure", "maybe", "book", "table", "chair", "the", "and"]
    }

    test_cases = []

    # 1. Explicit Positives
    for mood, words in mood_samples.items():
        if mood == Mood.NEUTRAL: continue
        for p in prefixes:
            for i in ["", "really ", "very "]:
                for w in words:
                    for s in suffixes:
                        text = f"{p}{i}{w}{s}".strip()
                        test_cases.append((text, mood, "explicit"))

    # 2. Negated Moods
    for mood, words in mood_samples.items():
        if mood == Mood.NEUTRAL: continue
        for p in ["I am ", "I feel ", "It's ", "Everything is "]:
            for n in negations:
                for w in words:
                    for s in suffixes:
                        text = f"{p}{n}{w}{s}".strip()
                        test_cases.append((text, Mood.NEUTRAL, "negated"))

    # 3. Neutral Fillers
    filler_phrases = [
        "The weather is nice", "I have a pen", "Where is the cat?", 
        "I am sitting here", "Just a normal day", "Nothing special happened",
        "The sky is blue", "Grass is green", "One plus one is two"
    ]
    for f in filler_phrases:
        for s in suffixes:
            test_cases.append((f"{f}{s}", Mood.NEUTRAL, "neutral_filler"))

    # 4. Mixed Signals
    mixed = [
        ("I am happy but sad", Mood.HAPPY, "mixed"), 
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
    mixed_debug_done = 0
    
    for text, expected, category in cases:
        detector._mood_history.clear()
        detector._current_mood = Mood.NEUTRAL
        
        # Test the analyze path
        mood, conf = detector.analyze(text, [], 1.0)
        
        results[category]["total"] += 1
        
        # PASS criteria
        if mood == expected:
            results[category]["pass"] += 1
        elif category == "negated" and mood == Mood.NEUTRAL:
            results[category]["pass"] += 1
        else:
            msg = f"[{category}] '{text}' -> got {mood}, expected {expected} (conf: {conf:.3f})"
            if category == "mixed" and mixed_debug_done < 5:
                text_lower = text.lower()
                scores = {m: _keyword_match_count(PRECOMPILED_PATTERNS[m], text_lower) / len(MOOD_KEYWORDS[m]) for m in MOOD_KEYWORDS}
                msg += f" | Scores: { {m: round(s, 4) for m, s in scores.items() if s > 0} }"
                mixed_debug_done += 1
            failures.append(msg)

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
