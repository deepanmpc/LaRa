import sys
import os
import queue
import re
import threading
import numpy as np
import sounddevice as sd
import webrtcvad
import time
import logging
from enum import Enum
from pywhispercpp.model import Model

# Configure logging
logging.basicConfig(
    filename='lara_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from AgentricAi.AgentricTLM import AgentricAI
except ImportError as e:
    logging.critical(f"Could not import AgentricAI: {e}")
    print(f"Error: Could not import AgentricAI. Check lara_system.log for details: {e}")
    sys.exit(1)

try:
    from kokoro_TTS import LaRaSpeech
except ImportError as e:
    logging.warning(f"Could not import LaRaSpeech (Kokoro TTS module): {e}")
    LaRaSpeech = None

try:
    from mood_detector import MoodDetector
except ImportError as e:
    logging.warning(f"Could not import MoodDetector: {e}")
    MoodDetector = None

try:
    from recovery_strategy import RecoveryStrategyManager
except ImportError as e:
    logging.warning(f"Could not import RecoveryStrategyManager: {e}")
    RecoveryStrategyManager = None

try:
    from session_state import SessionState
except ImportError as e:
    logging.warning(f"Could not import SessionState: {e}")
    SessionState = None

try:
    from user_memory import UserMemoryManager
except ImportError as e:
    logging.warning(f"Could not import UserMemoryManager: {e}")
    UserMemoryManager = None

try:
    from regulation_state import compute_regulation_state
except ImportError as e:
    logging.warning(f"Could not import compute_regulation_state: {e}")
    compute_regulation_state = None

try:
    from learning_progress import LearningProgressManager
except ImportError as e:
    logging.warning(f"Could not import LearningProgressManager: {e}")
    LearningProgressManager = None

try:
    from reinforcement_manager import ReinforcementAdaptationManager
except ImportError as e:
    logging.warning(f"Could not import ReinforcementAdaptationManager: {e}")
    ReinforcementAdaptationManager = None


# --- System Mode ---
class SystemMode(Enum):
    RESTING = "resting"
    LISTENING = "listening"
    SPEAKING = "speaking"


# --- Configuration ---
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
VAD_MODE = 3
SILENCE_DURATION_MS = 1800  # Gentle pacing: 1.8s for slow/paused speech
CHANNELS = 1

# Noise clearance threshold (Energy-based gate)
NOISE_GATE_THRESHOLD = 0.005 

# Barge-in / KWS hardening: require 300ms of continuous speech before triggering
BARGE_IN_FRAME_THRESHOLD = 10

# KWS cooldown: suppress all wake-word detection for this many seconds after an interrupt
# Prevents echo loop: interrupt → "Okay. I am listening." → KWS hears "LaRa" from speaker → infinite loop
KWS_COOLDOWN_S = 1.5

# Initialize VAD
vad = webrtcvad.Vad(VAD_MODE)
audio_queue = queue.Queue()


def callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def validate_response(text: str) -> str:
    """
    Validates and simplifies LLM output for neurodiverse cognitive safety.
    """
    if not text or not text.strip():
        return text
    
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s.strip()]
    
    if len(sentences) > 3:
        logging.info(f"[Response Validation] Trimmed from {len(sentences)} to 3 sentences.")
        sentences = sentences[:3]
    
    validated = []
    for s in sentences:
        s = re.sub(r',\s*and then\b', '.', s, flags=re.IGNORECASE)
        s = re.sub(r',\s*then\b', '.', s, flags=re.IGNORECASE)
        
        parts = s.split(',')
        if len(parts) > 3:
            logging.info(f"[Response Validation] Trimmed complex clause: '{s}'")
            s = ','.join(parts[:3]).rstrip() + '.'
        
        validated.append(s.strip())
    
    return ' '.join(validated)


def check_wake_word_in_clip(audio_frames, kws_model):
    """
    Lightweight keyword spotting: runs tiny.en on a short audio clip
    to check for the wake word 'lara'.
    Only called during SPEAKING mode when sustained speech is detected.
    Returns True if 'lara' is found in the transcription.
    """
    try:
        full_audio = np.concatenate(audio_frames).flatten().astype(np.float32)
        
        # Normalize only weak signals
        peak = np.max(np.abs(full_audio))
        if 0 < peak < 0.5:
            full_audio = full_audio / peak
        
        segments = kws_model.transcribe(full_audio)
        text = "".join([s.text for s in segments]).strip().lower()
        
        if "lara" in text:
            logging.info(f"[KWS] Wake word detected in clip: '{text}'")
            return True
        return False
    except Exception as e:
        logging.warning(f"[KWS] Error during keyword spotting: {e}")
        return False


def main():
    clear_console()
    print("\033[94m[System]\033[0m Initializing LaRa AI...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'model')
    
    # Whisper model for transcription and KWS (reuse same model for both)
    whisper_model = Model('small.en', models_dir=models_dir, n_threads=6, print_progress=False, language='en')
    kws_model = whisper_model  # Reuse for wake-word detection on short clips
    
    agent = AgentricAI()
    
    # Initialize Kokoro TTS
    lara_voice = None
    if LaRaSpeech:
        lara_voice = LaRaSpeech(voice='af_bella')
    
    # Initialize Mood Detector and Recovery Strategy
    mood_detector = MoodDetector() if MoodDetector else None
    strategy_manager = RecoveryStrategyManager() if RecoveryStrategyManager else None
    
    # Initialize Session State (Phase 1) and User Memory (Phase 2)
    session = SessionState() if SessionState else None
    memory = UserMemoryManager() if UserMemoryManager else None
    
    # Default user (single-user mode for now)
    USER_ID = "default_child"
    if memory:
        memory.get_or_create_user(USER_ID)
    
    # Initialize LearningProgressManager (Step 2)
    learning_manager = None
    if LearningProgressManager and memory:
        learning_manager = LearningProgressManager(memory)
        learning_manager.set_user(USER_ID)
    
    # Initialize ReinforcementAdaptationManager (Step 4)
    reinforcement_manager = None
    if ReinforcementAdaptationManager:
        reinforcement_manager = ReinforcementAdaptationManager(memory)
        reinforcement_manager.set_user(USER_ID)
    
    clear_console()
    print("="*60)
    print("        \033[95mLaRa: Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("="*60)
    print("\033[90mCommands: 'friday' (wake) | 'shutdown' (sleep) | 'lara' (interrupt)\033[0m")
    print("-" * 60)
    print("\033[92mStatus:\033[0m Resting (Listening for wake word...)")

    utterance_frames = []
    silence_frames = 0
    silence_threshold = int(SILENCE_DURATION_MS / FRAME_DURATION_MS)
    is_speaking = False
    system_mode = SystemMode.RESTING
    
    # KWS state tracking during SPEAKING mode
    kws_speech_frames = []
    kws_consecutive_count = 0
    kws_last_trigger_time = 0.0  # Timestamp of last KWS interrupt (for cooldown)
    
    def flush_audio_queue():
        """Drain the microphone queue to prevent stale frames."""
        while not audio_queue.empty():
            try:
                audio_queue.get_nowait()
            except queue.Empty:
                break

    def speak_and_monitor(text):
        """
        Speaks text via TTS while monitoring for wake-word interrupt.
        Runs TTS in a background thread, monitors audio in main thread.
        Returns True if speech completed, False if interrupted.
        
        ECHO PROTECTION:
        - KWS is disabled for KWS_COOLDOWN_S seconds after the last interrupt
        - This prevents the acknowledgment phrase from triggering a new detection
        - The cooldown is checked BEFORE any Whisper transcription runs
        """
        nonlocal kws_speech_frames, kws_consecutive_count, kws_last_trigger_time
        
        if not lara_voice or not text.strip():
            return True
        
        # ECHO GUARD: If we recently interrupted, skip KWS entirely for this utterance
        # This covers the case where we speak the acknowledgment immediately after interrupt
        if time.time() - kws_last_trigger_time < KWS_COOLDOWN_S:
            logging.info("[KWS] Cooldown active — skipping wake-word monitoring for this utterance.")
            lara_voice.speak(text)
            flush_audio_queue()
            return lara_voice.is_speaking == False  # True if completed normally
        
        kws_speech_frames = []
        kws_consecutive_count = 0
        
        # Start TTS in a background thread so we can monitor audio in main thread
        speech_result = [True]  # Use list to allow mutation from thread
        
        def _speak():
            speech_result[0] = lara_voice.speak(text)
        
        speech_thread = threading.Thread(target=_speak, daemon=True)
        speech_thread.start()
        
        # Monitor audio queue for wake-word while TTS is playing
        while speech_thread.is_alive():
            try:
                indata = audio_queue.get(timeout=0.05)
            except queue.Empty:
                continue
            
            if len(indata) != FRAME_SIZE:
                continue
            
            # COOLDOWN CHECK: If triggered recently, skip all detection
            if time.time() - kws_last_trigger_time < KWS_COOLDOWN_S:
                continue
            
            # VAD + Energy check on the frame
            rms = np.sqrt(np.mean(indata**2))
            pcm_data = (indata * 32767).astype(np.int16)
            
            try:
                frame_is_speech = vad.is_speech(pcm_data.tobytes(), SAMPLE_RATE) and rms > NOISE_GATE_THRESHOLD
            except Exception:
                continue
            
            if frame_is_speech:
                kws_consecutive_count += 1
                kws_speech_frames.append(indata)
                
                # Only run KWS after 300ms of sustained speech
                if kws_consecutive_count >= BARGE_IN_FRAME_THRESHOLD:
                    # Run lightweight transcription on the buffered clip
                    if check_wake_word_in_clip(kws_speech_frames, kws_model):
                        # Interrupt!
                        kws_last_trigger_time = time.time()  # Set cooldown BEFORE interrupt
                        if lara_voice.interrupt_speech():
                            print(f"\n\033[93m[Interrupted]\033[0m Wake word detected.")
                            logging.info(f"[KWS] Interrupt triggered. Cooldown active for {KWS_COOLDOWN_S}s.")
                            speech_result[0] = False
                        break
            else:
                kws_consecutive_count = 0
                kws_speech_frames = []
        
        # Wait for the speech thread to fully finish
        speech_thread.join(timeout=2.0)
        
        # Flush queue to prevent echo
        flush_audio_queue()
        
        return speech_result[0]

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, 
                            callback=callback, blocksize=FRAME_SIZE):
            while True:
                indata = audio_queue.get()
                if len(indata) != FRAME_SIZE: continue
                
                # --- Noise Clearance / Audio Pre-processing ---
                rms = np.sqrt(np.mean(indata**2))
                pcm_data = (indata * 32767).astype(np.int16)
                
                try:
                    is_speech = vad.is_speech(pcm_data.tobytes(), SAMPLE_RATE) and rms > NOISE_GATE_THRESHOLD
                except:
                    continue

                if is_speech:
                    if not is_speaking:
                        is_speaking = True
                        utterance_frames = []
                        silence_frames = 0
                    utterance_frames.append(indata)
                    silence_frames = 0
                else:
                    if is_speaking:
                        utterance_frames.append(indata)
                        silence_frames += 1
                        
                        if silence_frames >= silence_threshold:
                            is_speaking = False
                            
                            # Transcribe
                            full_audio = np.concatenate(utterance_frames).flatten().astype(np.float32)
                            
                            # Normalize only weak signals
                            peak = np.max(np.abs(full_audio))
                            if 0 < peak < 0.5:
                                full_audio = full_audio / peak
                                
                            segments = whisper_model.transcribe(full_audio)
                            text = "".join([s.text for s in segments]).strip()
                            
                            if not text: continue

                            # Handle Shutdown
                            if "shutdown" in text.lower() or "shut down" in text.lower():
                                goodbye = "Goodbye! Have a lovely day."
                                print(f"\n\033[91m[Shutdown]\033[0m LaRa: {goodbye}")
                                if lara_voice:
                                    system_mode = SystemMode.SPEAKING
                                    lara_voice.speak(goodbye)
                                return

                            # Handle Wake State (RESTING → LISTENING)
                            if system_mode == SystemMode.RESTING:
                                if "friday" in text.lower():
                                    system_mode = SystemMode.LISTENING
                                    msg = "\n\033[92m[System Transition]\033[0m LaRa is now AWAKE."
                                    print(msg)
                                    logging.info("[SYSTEM_STATE] Transitioned to LISTENING")
                                    welcome_text = "Hello! I am here to play and learn with you."
                                    print(f"\033[95mLaRa:\033[0m {welcome_text}")
                                    if lara_voice:
                                        system_mode = SystemMode.SPEAKING
                                        speak_and_monitor(welcome_text)
                                        system_mode = SystemMode.LISTENING
                                else:
                                    sys.stdout.write(f"\r\033[90m(Heard: \"{text}\" - say 'friday' to activate)\033[0m")
                                    sys.stdout.flush()
                                continue

                            # --- Active Conversation (LISTENING mode) ---
                            print(f"\n\033[94mYou:\033[0m {text}")
                            
                            # Check session TTL
                            if session and session.is_expired():
                                logging.info("[Session] Expired — creating new session.")
                                if reinforcement_manager:
                                    reinforcement_manager.persist_session_metrics()
                                session = SessionState()
                            
                            # Mood detection (text + audio signals)
                            detected_mood = "neutral"
                            mood_conf = 0.0
                            if mood_detector:
                                utterance_duration = len(utterance_frames) * FRAME_DURATION_MS / 1000.0
                                detected_mood, mood_conf = mood_detector.analyze(
                                    text, utterance_frames, utterance_duration
                                )
                                mood_icon = {"happy": "\U0001f60a", "sad": "\U0001f622", "frustrated": "\U0001f624", "anxious": "\U0001f630", "quiet": "\U0001f92b"}.get(detected_mood, "")
                                if mood_icon:
                                    print(f"\033[90m[Mood: {detected_mood} {mood_icon}]\033[0m")
                            
                            # === PRE-DECISION UPDATE (Step 3) ===
                            # Update mood + streaks BEFORE gating/strategy decisions
                            if session:
                                prev_mood = session.mood
                                session.update_pre_decision(detected_mood, mood_conf)
                                
                                # Detect recovery (frustration → stability transition)
                                if prev_mood in ("frustrated", "sad") and detected_mood in ("neutral", "happy"):
                                    if memory:
                                        concept = session.current_concept or "general"
                                        memory.record_recovery(USER_ID, concept)
                                    if reinforcement_manager:
                                        reinforcement_manager.update_metrics(
                                            reinforcement_manager._current_style, True
                                        )
                            
                            # --- Difficulty Gating ---
                            if session:
                                if session.should_decrease_difficulty():
                                    session.change_difficulty(-1)
                                    print(f"\033[90m[Difficulty: decreased to {session.current_difficulty}]\033[0m")
                                elif session.should_increase_difficulty():
                                    session.change_difficulty(+1)
                                    print(f"\033[90m[Difficulty: increased to {session.current_difficulty}]\033[0m")
                            
                            # --- Compute RegulationState (Step 1) ---
                            regulation = None
                            if compute_regulation_state and session:
                                regulation = compute_regulation_state(session)
                            
                            # --- Get RecoveryStrategy ---
                            strategy = None
                            if strategy_manager:
                                strategy = strategy_manager.get_strategy(detected_mood, mood_conf)
                                if strategy.label != "neutral":
                                    print(f"\033[90m[Strategy: {strategy.label}]\033[0m")
                            
                            # --- Get Reinforcement Style (Step 4) ---
                            reinforcement_prompt = ""
                            if reinforcement_manager and regulation:
                                r_style = reinforcement_manager.get_style(regulation)
                                reinforcement_prompt = reinforcement_manager.get_style_prompt()
                            
                            # --- Generate LLM Response (Step 5: strategy + reinforcement) ---
                            full_ai_response = ""
                            for chunk in agent.generate_response_stream(
                                text, strategy=strategy,
                                reinforcement_context=reinforcement_prompt
                            ):
                                full_ai_response += chunk
                            
                            # Validate response
                            full_ai_response = validate_response(full_ai_response)
                            
                            # === POST-RESPONSE UPDATE (Step 3) ===
                            if session:
                                session.update_post_response(text, full_ai_response)
                            
                            # Record emotional metric (Phase 2)
                            if memory:
                                concept = session.current_concept if session else "general"
                                memory.record_emotional_metric(USER_ID, concept or "general", detected_mood)
                            
                            # Check for barge-in during LLM generation
                            interrupted = False
                            barge_in_count = 0
                            while not audio_queue.empty():
                                try:
                                    peek_data = audio_queue.get_nowait()
                                    if len(peek_data) == FRAME_SIZE:
                                        peek_rms = np.sqrt(np.mean(peek_data**2))
                                        peek_pcm = (peek_data * 32767).astype(np.int16)
                                        if vad.is_speech(peek_pcm.tobytes(), SAMPLE_RATE) and peek_rms > NOISE_GATE_THRESHOLD:
                                            barge_in_count += 1
                                            if barge_in_count >= BARGE_IN_FRAME_THRESHOLD:
                                                interrupted = True
                                                is_speaking = True
                                                utterance_frames = [peek_data]
                                                silence_frames = 0
                                                logging.info("[Barge-In] User interrupted during LLM generation.")
                                                break
                                        else:
                                            barge_in_count = 0
                                except queue.Empty:
                                    break
                            
                            if not interrupted:
                                # Display and speak atomically
                                print(f"\033[95mLaRa:\033[0m {full_ai_response}")
                                print("-"*30)
                                
                                if lara_voice and full_ai_response.strip():
                                    # Apply TTS speed from recovery strategy
                                    if strategy:
                                        lara_voice.speed = strategy.tts_length_scale
                                    
                                    system_mode = SystemMode.SPEAKING
                                    completed = speak_and_monitor(full_ai_response.strip())
                                    system_mode = SystemMode.LISTENING
                                    
                                    if not completed:
                                        # Wake-word interrupt occurred — acknowledge calmly
                                        ack_text = "Okay. I am listening."
                                        print(f"\033[95mLaRa:\033[0m {ack_text}")
                                        lara_voice.speak(ack_text)
                                        flush_audio_queue()
                            else:
                                print(f"\033[90m... [User interrupted — listening]\033[0m")
                            
    except KeyboardInterrupt:
        print("\n\n\033[91m[System Transition]\033[0m Stopping gently...")
        logging.info("[SYSTEM_STATE] Transitioned to SHUTDOWN (KeyboardInterrupt)")
    except Exception as e:
        logging.critical(f"System Error: {e}")
        print(f"\n\033[91mError:\033[0m {e}")

if __name__ == "__main__":
    main()
    # Force clean exit to prevent PyTorch cleanup crash on macOS
    os._exit(0)
