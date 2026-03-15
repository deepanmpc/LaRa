import sys
import os
import logging
import numpy as np

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mood.mood_detector import MoodDetector, Mood

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
# Disable debug logging from the detector to keep output clean
logging.getLogger().setLevel(logging.WARNING)

def run_test_suite():
    md = MoodDetector()
    
    # Category 1: Explicit Moods
    explicit_cases = [
        ("I am so happy!", Mood.HAPPY),
        ("I feel very sad today", Mood.SAD),
        ("I am so frustrated with this", Mood.FRUSTRATED),
        ("I am really scared about the loud noise", Mood.ANXIOUS),
        ("It is so nice to play with you", Mood.HAPPY),
        ("I want to cry", Mood.SAD),
        ("This is too hard for me", Mood.FRUSTRATED),
        ("Help me please, I am worried", Mood.ANXIOUS),
    ]
    
    # Category 2: Negations (The trickiest cases)
    negation_cases = [
        ("I am not sad", Mood.NEUTRAL),
        ("I don't think I'm happy", Mood.NEUTRAL),
        ("I am not angry anymore", Mood.NEUTRAL),
        ("I am not scared of the dark", Mood.NEUTRAL),
        ("It's not that hard", Mood.NEUTRAL),
        ("I don't hate this", Mood.NEUTRAL),
        ("I am not missing my mom", Mood.NEUTRAL),
    ]
    
    # Category 3: Mixed Emotions
    mixed_cases = [
        ("I am happy but also a little scared", Mood.HAPPY), # Usually picks the first or strongest
        ("I am sad because it is hard", Mood.SAD),
        ("I like you but I am tired", Mood.HAPPY), # 'tired' is in sad
        ("Yay, but it's cold", Mood.HAPPY),
    ]
    
    # Category 4: Sarcasm / Intensity
    sarcasm_cases = [
        ("Oh great, another broken toy", Mood.FRUSTRATED),
        ("I am just so thrilled to be stuck here", Mood.FRUSTRATED),
        ("This is just fantastic, now I lost it", Mood.FRUSTRATED), # 'fantastic' vs 'lost'
    ]
    
    # Category 5: Conversational Baseline (Should be Neutral)
    baseline_cases = [
        ("The dog is brown", Mood.NEUTRAL),
        ("I am counting the blocks", Mood.NEUTRAL),
        ("One two three four five", Mood.NEUTRAL),
        ("Can we play another game", Mood.NEUTRAL),
        ("Where is the ball", Mood.NEUTRAL),
        ("I am sitting on the floor", Mood.NEUTRAL),
    ]
    
    # Category 6: Child-specific Language
    child_cases = [
        ("Mama where are you", Mood.ANXIOUS),
        ("Yay yippee", Mood.HAPPY),
        ("Ugh stop it", Mood.FRUSTRATED),
        ("Tummy hurt", Mood.SAD),
        ("Shadow scary", Mood.ANXIOUS),
    ]

    all_cases = {
        "Explicit": explicit_cases,
        "Negations": negation_cases,
        "Mixed": mixed_cases,
        "Sarcasm": sarcasm_cases,
        "Baseline": baseline_cases,
        "Child-specific": child_cases
    }

    print("="*60)
    print(f"{'LaRa Mood Detector Stress Test':^60}")
    print("="*60)
    
    total_passed = 0
    total_tests = 0
    
    for category, cases in all_cases.items():
        print(f"\n[Category: {category}]")
        passed = 0
        for text, expected in cases:
            # Re-init for each test to avoid temporal smoothing interference in isolated tests
            # unless we WANT to test smoothing
            test_md = MoodDetector()
            mood, conf = test_md.analyze(text, [], 1.0)
            
            status = "PASS" if mood == expected else "FAIL"
            if status == "PASS":
                passed += 1
            
            print(f"  {status:4} | {text:40} | Got: {mood:10} (Conf: {conf:.2f}) | Exp: {expected}")
        
        print(f"  Result: {passed}/{len(cases)} passed")
        total_passed += passed
        total_tests += len(cases)

    # 1000+ Variations Generation (Simulation)
    # We won't print 1000 lines, but we will run them and show summary
    print("\n" + "="*60)
    print(f"{'Generative Stress Test (1000+ Variations)':^60}")
    print("="*60)
    
    gen_passed = 0
    gen_count = 0
    
    subjects = ["I am", "I feel", "It is", "The toy is", "Playing is"]
    modifiers = ["very", "really", "so", "a little", "bit", "extremely", ""]
    
    test_data = [
        (Mood.HAPPY, ["happy", "glad", "wonderful", "great", "nice", "fun"]),
        (Mood.SAD, ["sad", "unhappy", "upset", "crying", "broken", "gone"]),
        (Mood.FRUSTRATED, ["mad", "angry", "annoying", "too hard", "not working", "stuck"]),
        (Mood.ANXIOUS, ["scared", "afraid", "worried", "nervous", "loud"]),
    ]
    
    for expected_mood, keywords in test_data:
        for subj in subjects:
            for mod in modifiers:
                for kw in keywords:
                    text = f"{subj} {mod} {kw}".replace("  ", " ")
                    test_md = MoodDetector()
                    mood, conf = test_md.analyze(text, [], 1.0)
                    if mood == expected_mood:
                        gen_passed += 1
                    gen_count += 1
                    
                    # Also test negations for all these
                    neg_text = f"I am not {mod} {kw}".replace("  ", " ")
                    test_md = MoodDetector()
                    mood, conf = test_md.analyze(neg_text, [], 1.0)
                    if mood == Mood.NEUTRAL:
                        gen_passed += 1
                    gen_count += 1

    print(f"  Generated Tests: {gen_count}")
    print(f"  Generated Passed: {gen_passed}")
    print(f"  Success Rate: {(gen_passed/gen_count)*100:.1f}%")
    
    print("\n" + "="*60)
    print(f"OVERALL SUMMARY: {total_passed + gen_passed}/{total_tests + gen_count} passed")
    print("="*60)

if __name__ == "__main__":
    run_test_suite()
