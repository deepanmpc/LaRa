import sys
import os
import queue
import re
import threading
import platform
import numpy as np
import sounddevice as sd
import webrtcvad
import time
import logging
import requests
from enum import Enum
from faster_whisper import WhisperModel
from src.utils.gpu_manager import get_device_and_compute_type, check_vram
from src.core.PerformanceMonitor import PerformanceMonitor

# Logging is already configured by main.py's setup_logging() — do NOT call basicConfig here

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load config for model paths and settings
try:
    from src.core.config_loader import CONFIG
    _STT_CFG = CONFIG.stt
except Exception:
    _STT_CFG = None

try:
    from src.llm.AgentricTLM import AgentricAI
except ImportError as e:
    logging.critical(f"Could not import AgentricAI: {e}")
    print(f"Error: Could not import AgentricAI. Check lara_system.log for details: {e}")
    sys.exit(1)

try:
    from src.tts.kokoro_TTS import LaRaSpeech
except ImportError as e:
    logging.warning(f"Could not import LaRaSpeech (Kokoro TTS module): {e}")
    LaRaSpeech = None

try:
    from src.mood.mood_detector import MoodDetector
except ImportError as e:
    logging.warning(f"Could not import MoodDetector: {e}")
    MoodDetector = None

try:
    from src.mood.recovery_strategy import RecoveryStrategyManager
except ImportError as e:
    logging.warning(f"Could not import RecoveryStrategyManager: {e}")
    RecoveryStrategyManager = None

try:
    from src.session.session_state import SessionState
except ImportError as e:
    logging.warning(f"Could not import SessionState: {e}")
    SessionState = None

try:
    from src.memory.user_memory import UserMemoryManager
except ImportError as e:
    logging.warning(f"Could not import UserMemoryManager: {e}")
    UserMemoryManager = None

try:
    from src.mood.regulation_state import compute_regulation_state
except ImportError as e:
    logging.warning(f"Could not import compute_regulation_state: {e}")
    compute_regulation_state = None

try:
    from src.memory.learning_progress import LearningProgressManager
except ImportError as e:
    logging.warning(f"Could not import LearningProgressManager: {e}")
    LearningProgressManager = None

try:
    from src.reinforcement.reinforcement_manager import ReinforcementAdaptationManager
except ImportError as e:
    logging.warning(f"Could not import ReinforcementAdaptationManager: {e}")
    ReinforcementAdaptationManager = None

try:
    from src.memory.child_preferences import ChildPreferenceManager
except ImportError as e:
    logging.warning(f"Could not import ChildPreferenceManager: {e}")
    ChildPreferenceManager = None

try:
    from src.session.session_summary import generate_session_summary, export_session_summary
except ImportError as e:
    logging.warning(f"Could not import session summaries: {e}")
    generate_session_summary = None
    export_session_summary = None

try:
    from src.memory.vector_memory import VectorMemory
except ImportError as e:
    logging.warning(f"Could not import VectorMemory: {e}")
    VectorMemory = None

# --- SINGLETON STT SERVICE ---
class STTService:
    _instance = None
    
    def __init__(self):
        if STTService._instance is not None:
            raise RuntimeError("STTService is a singleton. Use STTService.get()")
            
        logging.info("[STTService] Initializing Faster-Whisper subsystem...")
        from src.core.runtime_paths import get_whisper_dir
        try:
            from src.core.config_loader import CONFIG
            _local_cfg = CONFIG.stt
        except Exception:
            _local_cfg = None
        models_dir = get_whisper_dir()
        config_device = _local_cfg.device if _local_cfg and hasattr(_local_cfg, 'device') else 'cpu'
        config_compute = _local_cfg.compute_type if _local_cfg and hasattr(_local_cfg, 'compute_type') else 'int8'
        stt_model_name = _local_cfg.model if _local_cfg and hasattr(_local_cfg, 'model') else 'small.en'
        
        # Enforce robust device fallback matching the rest of the application
        stt_device, stt_compute = get_device_and_compute_type(config_device, config_compute)
        
        # Check VRAM limits (Wait until device is confirmed as CUDA)
        if stt_device == "cuda":
            # Require at least 2GB of VRAM for the small.en Whisper + CTranslate2 runtime
            check_vram(2.0)
            
        print(f"        [STT] Loading Faster-Whisper ({stt_model_name}) on {stt_device}...")
        
        start_time = time.time()
        self.model = WhisperModel(
            stt_model_name, 
            device=stt_device, 
            compute_type=stt_compute, 
            download_root=models_dir
        )
        
        # WARMUP INFERENCE:
        # Pytorch / CTranslate2 lazy-loads CUDA kernels on the first forward pass.
        # Run a silent zeros array through transribe() so the user interaction isn't artificially delayed.
        logging.info("[STTService] Running warmup inference to pre-compile CUDA kernels...")
        dummy_audio = np.zeros(16000, dtype=np.float32)
        try:
            self.model.transcribe(dummy_audio, beam_size=1, language="en")
        except Exception as e:
            logging.warning(f"[STTService] Warmup inference failed (benign): {e}")
            
        load_time = time.time() - start_time
        logging.info(f"[STTService] Faster-Whisper {stt_model_name} initialized in {load_time:.2f}s")
        
        STTService._instance = self

    @staticmethod
    def get():
        if STTService._instance is None:
            STTService()
        return STTService._instance


# --- System Mode ---
class SystemMode(Enum):
    RESTING = "resting"
    LISTENING = "listening"
    SPEAKING = "speaking"


# --- Configuration ---
# Configuration wiring for audio processing (Fixes 2 & Latency 2)
try:
    from src.core.config_loader import CONFIG
    NOISE_GATE_THRESHOLD = CONFIG.audio.noise_gate_threshold
    SILENCE_DURATION_MS = CONFIG.audio.silence_duration_ms
except Exception:
    NOISE_GATE_THRESHOLD = 0.005
    SILENCE_DURATION_MS = 1200  # Default fallback

# Barge-in / KWS hardening: require 300ms of continuous speech before triggering
BARGE_IN_FRAME_THRESHOLD = 10

# Memory leak prevention: Max 20 seconds of audio frames per utterance (Fix 7)
MAX_AUDIO_BUFFER_FRAMES = int(20000 / FRAME_DURATION_MS)

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


def get_vision_state():
    """
    Queries the Vision Perception microservice for the current engagement state.
    """
    try:
        # Use a short timeout to prevent therapy stalls if vision service is down
        r = requests.get("http://localhost:8001/latest", timeout=0.1)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


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
        
        segments, _info = kws_model.transcribe(full_audio, beam_size=1, language="en")
        text = "".join([s.text for s in segments]).strip().lower()
        
        if "lara" in text:
            logging.info(f"[KWS] Wake word detected in clip: '{text}'")
            return True
        return False
    except Exception as e:
        logging.warning(f"[KWS] Error during keyword spotting: {e}")
        return False


def run_conversation_loop(bridge=None, skip_wake_word=False):
    """Main conversation loop — called by main.py or directly."""
    
    def _emit(event_type: str, **payload):
        """Emit to bridge if connected. Never raises — bridge failure must not break conversation."""
        if bridge is not None:
            try:
                bridge.emit(event_type, payload)
            except Exception as e:
                logging.debug(f"[Bridge] Emit failed silently: {e}")
    
    # Retrieve singletons
    stt_service = STTService.get()
    whisper_model = stt_service.model
    kws_model = whisper_model  # Reuse for wake-word detection on short clips
    
    from src.llm.AgentricTLM import LLMService
    agent = LLMService.get()
    
    from src.tts.kokoro_TTS import TTSService
    lara_voice = TTSService.get()
    
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
    
    # Initialize Child Preference Manager
    preference_manager = None
    if ChildPreferenceManager and memory:
        preference_manager = ChildPreferenceManager(memory)
        preference_manager.set_user(USER_ID)
    
    # Initialize Vector Memory (ChromaDB RAG)
    vector_memory = None
    if VectorMemory:
        vector_memory = VectorMemory()
        vector_memory.set_user(USER_ID)
    
    # State & Context Initialization (prevents UnboundLocalError)
    regulation = None
    strategy = None
    detected_mood = "neutral"
    mood_conf = 0.0
    text = ""
    full_ai_response = ""
    reinforcement_prompt = ""
    preference_context = ""
    summary_context = ""
    vector_context = ""

    clear_console()
    print("="*60)
    print("        \033[95mLaRa: Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("="*60)
    print("\033[90mCommands: 'shutdown' (end session) | 'lara' (interrupt LaRa mid-speech)\033[0m")
    print("-" * 60)
    print("\033[92mStatus:\033[0m Starting session...")

    utterance_frames = []
    silence_frames = 0
    silence_threshold = int(SILENCE_DURATION_MS / FRAME_DURATION_MS)
    is_speaking = False

    # When launched via UI button, skip RESTING entirely and go straight to LISTENING
    if skip_wake_word:
        system_mode = SystemMode.LISTENING
        flush_audio_queue()  # discard any stale frames before we start listening
        _emit("system_state", mode="listening", turn_count=0,
              difficulty=session.current_difficulty if session else 2)
        welcome_text = "Hello! I am here to play and learn with you."
        print(f"\033[95mLaRa:\033[0m {welcome_text}")
        logging.info("[SYSTEM_STATE] UI-triggered start — skipping wake word, entering LISTENING")
        if lara_voice:
            _emit("system_state", mode="speaking", turn_count=0,
                  difficulty=session.current_difficulty if session else 2)
            _emit("lara_response", speaker="lara", text=welcome_text,
                  mood="neutral", mood_confidence=0.0, strategy="neutral")
            speak_and_monitor(welcome_text)
            _emit("system_state", mode="listening", turn_count=0,
                  difficulty=session.current_difficulty if session else 2)
        print("\033[92mStatus:\033[0m Listening...")
    else:
        system_mode = SystemMode.RESTING
        _emit("system_state", mode="resting", turn_count=0,
              difficulty=session.current_difficulty if session else 2)
        print("\033[92mStatus:\033[0m Resting (say 'friday' to wake)")
    
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
            
            # VAD + Energy check on the frame (flattened for 1D calculation)
            flat_data = indata.flatten()
            rms = np.sqrt(np.mean(flat_data**2))
            pcm_data = (flat_data * 32767).astype(np.int16)
            
            try:
                is_speech = vad.is_speech(pcm_data.tobytes(), SAMPLE_RATE) and rms > NOISE_GATE_THRESHOLD
            except Exception:
                continue
            
            if is_speech:
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
        speech_thread.join(timeout=10.0)
        
        # Flush queue to prevent echo
        flush_audio_queue()
        
        return speech_result[0]

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, 
                            callback=callback, blocksize=FRAME_SIZE):
            while True:
                indata = audio_queue.get()
                if len(indata) != FRAME_SIZE: continue
                
                # Prevent memory leaks for extremely long background noise
                if len(utterance_frames) > MAX_AUDIO_BUFFER_FRAMES:
                    utterance_frames.pop(0)
                
                # --- Noise Clearance / Audio Pre-processing ---
                # sounddevice returns 2D chunks (frames, channels), we need 1D for VAD and Whisper
                flat_data = indata.flatten()
                rms = np.sqrt(np.mean(flat_data**2))
                pcm_data = (flat_data * 32767).astype(np.int16)
                
                try:
                    is_speech = vad.is_speech(pcm_data.tobytes(), SAMPLE_RATE) and rms > NOISE_GATE_THRESHOLD
                except Exception as e:
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug(f"[VAD] Frame error: {e}")
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
                            
                            # Transcribe (beam_size=1 for latency improvement)
                            perf = PerformanceMonitor.get()
                            perf.start_turn()
                            
                            full_audio = np.concatenate(utterance_frames).flatten().astype(np.float32)
                            
                            # Normalize only weak signals
                            peak = np.max(np.abs(full_audio))
                            if 0 < peak < 0.5:
                                full_audio = full_audio / peak
                                
                            segments, _info = whisper_model.transcribe(full_audio, beam_size=1, language="en")
                            text = "".join([s.text for s in segments]).strip()
                            
                            if not text: continue

                            # Handle Shutdown
                            if "shutdown" in text.lower() or "shut down" in text.lower():
                                _emit("session_ended", reason="shutdown_command", turn_count=session.turn_count if session else 0)
                                goodbye = "Goodbye! Have a lovely day."
                                print(f"\n\033[91m[Shutdown]\033[0m LaRa: {goodbye}")
                                if lara_voice:
                                    system_mode = SystemMode.SPEAKING
                                    lara_voice.speak(goodbye)
                                return

                            # Handle RESTING mode (only reached when launched without skip_wake_word)
                            if system_mode == SystemMode.RESTING:
                                if "friday" in text.lower():
                                    system_mode = SystemMode.LISTENING
                                    _emit("system_state", mode="listening", turn_count=0,
                                          difficulty=session.current_difficulty if session else 2)
                                    logging.info("[SYSTEM_STATE] Wake word detected — entering LISTENING")
                                    welcome_text = "Hello! I am here to play and learn with you."
                                    print(f"\033[95mLaRa:\033[0m {welcome_text}")
                                    if lara_voice:
                                        system_mode = SystemMode.SPEAKING
                                        _emit("system_state", mode="speaking", turn_count=0,
                                              difficulty=session.current_difficulty if session else 2)
                                        _emit("lara_response", speaker="lara", text=welcome_text,
                                              mood="neutral", mood_confidence=0.0, strategy="neutral")
                                        speak_and_monitor(welcome_text)
                                        system_mode = SystemMode.LISTENING
                                        _emit("system_state", mode="listening", turn_count=0,
                                              difficulty=session.current_difficulty if session else 2)
                                else:
                                    sys.stdout.write(
                                        f"\r\033[90m(Heard: \"{text}\" — say 'friday' to activate)\033[0m"
                                    )
                                    sys.stdout.flush()
                                continue

                            # --- Active Conversation (LISTENING mode) ---
                            _emit("system_state", mode="thinking", turn_count=session.turn_count if session else 0, difficulty=session.current_difficulty if session else 2)
                            _emit("transcript", speaker="child", text=text, timestamp=time.time())
                            print(f"\n\033[94mYou:\033[0m {text}")
                            
                            # Check session TTL
                            if session and session.is_expired():
                                logging.info("[Session] Expired — creating new session.")
                                if reinforcement_manager:
                                    reinforcement_manager.persist_session_metrics()
                                session = SessionState()
                            
                            # 1. Mood detection (text + audio signals)
                            detected_mood = "neutral"
                            mood_conf = 0.0
                            if mood_detector and text:
                                utterance_duration = len(utterance_frames) * FRAME_DURATION_MS / 1000.0
                                detected_mood, mood_conf = mood_detector.analyze(
                                    text, utterance_frames, utterance_duration
                                )
                                mood_icon = {"happy": "\U0001f60a", "sad": "\U0001f622", "frustrated": "\U0001f624", "anxious": "\U0001f630", "quiet": "\U0001f92b"}.get(detected_mood, "")
                                if mood_icon:
                                    print(f"\033[90m[Mood: {detected_mood} {mood_icon}]\033[0m")
                            
                            # 2. Update session state (PRE-DECISION)
                            if session:
                                prev_mood = session.mood
                                session.update_pre_decision(detected_mood, mood_conf)
                                
                                # Detect recovery (frustration → stability transition)
                                if prev_mood in ("frustrated", "sad") and detected_mood in ("neutral", "happy"):
                                    if memory:
                                        concept = session.current_concept or "general"
                                        memory.record_recovery(USER_ID, concept)
                                    if reinforcement_manager:
                                        # Fix 5: Use public current_style
                                        reinforcement_manager.update_metrics(
                                            reinforcement_manager.current_style, True
                                        )
                            
                            # 3. Compute RegulationState
                            # order corrected (Fix 4): must happen AFTER session update
                            regulation = None
                            if compute_regulation_state and session:
                                regulation = compute_regulation_state(session)
                                if regulation:
                                    _emit("mood_update", mood=detected_mood, confidence=mood_conf,
                                          regulation={
                                              "frustration_persistence": regulation.frustration_persistence,
                                              "stability_persistence": regulation.stability_persistence,
                                              "trend": regulation.emotional_trend_score,
                                          })
                                else:
                                    logging.warning("[Pipeline] Regulation state computation returned None.")
                                    _emit("mood_update", mood=detected_mood, confidence=mood_conf, regulation={})
                            else:
                                _emit("mood_update", mood=detected_mood, confidence=mood_conf, regulation={})
                            
                            # --- Difficulty Gating ---
                            if session:
                                old_d = session.current_difficulty
                                if session.should_decrease_difficulty():
                                    session.change_difficulty(-1)
                                    _emit("difficulty_change", old_difficulty=old_d, new_difficulty=session.current_difficulty, direction="down")
                                    print(f"\033[90m[Difficulty: decreased to {session.current_difficulty}]\033[0m")
                                elif session.should_increase_difficulty():
                                    session.change_difficulty(+1)
                                    _emit("difficulty_change", old_difficulty=old_d, new_difficulty=session.current_difficulty, direction="up")
                                    print(f"\033[90m[Difficulty: increased to {session.current_difficulty}]\033[0m")
                            
                            # --- Compute RegulationState moved up ---
                            # --- Get RecoveryStrategy ---
                            strategy = None
                            if strategy_manager:
                                # Prioritize Vision signals for engagement-based overrides
                                vision_state = get_vision_state()
                                if vision_state and vision_state.get("engagementScore", 1.0) < 0.3:
                                    engagement = vision_state.get("engagementScore")
                                    print(f"\033[91m[Vision] Low engagement detected ({engagement:.2f}) \u2192 forcing recovery.\033[0m")
                                    logging.info(f"[Vision] Low engagement ({engagement:.2f}) override triggered.")
                                    # Force 'frustrated' strategy as it simplifies instructions and adds grounding
                                    strategy = strategy_manager.force_strategy("frustrated")
                                else:
                                    strategy = strategy_manager.get_strategy(detected_mood, mood_conf)
                                
                                if strategy.label != "neutral":
                                    print(f"\033[90m[Strategy: {strategy.label}]\033[0m")
                            
                            # --- Get Reinforcement Style (Step 4) ---
                            reinforcement_prompt = ""
                            if reinforcement_manager and regulation:
                                r_style = reinforcement_manager.get_style(regulation)
                                reinforcement_prompt = reinforcement_manager.get_style_prompt()
                            
                            # --- Extract & Inject Child Preferences ---
                            preference_context = ""
                            if preference_manager:
                                new_prefs = preference_manager.process_utterance(text)
                                if new_prefs:
                                    for p in new_prefs:
                                        print(f"\033[90m[Preference: {p.sentiment} \u2192 {p.topic}]\033[0m")
                                preference_context = preference_manager.get_context_for_llm()
                            
                            # --- Session Summary (Section 5, injected as Part 5 of prompt) ---
                            summary_context = ""
                            if generate_session_summary and session:
                                summary_context = generate_session_summary(
                                    session,
                                    learning_manager=learning_manager,
                                    reinforcement_manager=reinforcement_manager,
                                )
                                if export_session_summary:
                                    export_session_summary(summary_context, session.session_id)
                            
                            # --- Vector Memory Retrieval (Section 16, RAG) ---
                            vector_context = ""
                            if vector_memory and VectorMemory and VectorMemory.is_story_trigger(text):
                                vector_context = vector_memory.get_context_for_llm(text)
                                if vector_context:
                                    print(f"\033[90m[VectorMemory: recalled past story]\033[0m")
                            
                            # --- Generate LLM Response (strict 7-part prompt, Section 15) ---
                            full_ai_response = ""
                            for chunk in agent.generate_response_stream(
                                text, strategy=strategy,
                                reinforcement_context=reinforcement_prompt,
                                preference_context=preference_context,
                                session_summary=summary_context,
                                vector_context=vector_context,
                                is_frustrated=(detected_mood in ("frustrated", "sad", "angry")),
                                turn_count=(session.turn_count if session else 0),
                                regulation_state=regulation
                            ):
                                full_ai_response += chunk
                                _emit("lara_chunk", chunk=chunk, index=len(full_ai_response))
                            
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
                                    _emit("system_state", mode="speaking",
                                        turn_count=session.turn_count if session else 0,
                                        difficulty=session.current_difficulty if session else 2)
                                    _emit("lara_response",
                                        speaker="lara",
                                        text=full_ai_response,
                                        mood=detected_mood,
                                        mood_confidence=mood_conf,
                                        strategy=strategy.label if strategy else "neutral")
                                    
                                    perf.start_timer("tts")
                                    completed = speak_and_monitor(full_ai_response.strip())
                                    perf.end_timer("tts")
                                    perf.end_turn()
                                    
                                    system_mode = SystemMode.LISTENING
                                    _emit("system_state", mode="listening",
                                        turn_count=session.turn_count if session else 0,
                                        difficulty=session.current_difficulty if session else 2)
                                    
                                    if not completed:
                                        # Wake-word interrupt occurred — acknowledge calmly
                                        ack_text = "Okay. I am listening."
                                        print(f"\033[95mLaRa:\033[0m {ack_text}")
                                        lara_voice.speak(ack_text)
                                        flush_audio_queue()
                            else:
                                print(f"\033[90m... [User interrupted — listening]\033[0m")
                            
    except KeyboardInterrupt:
        _emit("session_ended", reason="keyboard_interrupt", turn_count=session.turn_count if session else 0)
        print("\n\n\033[91m[System Transition]\033[0m Stopping gently...")
        logging.info("[SYSTEM_STATE] Transitioned to SHUTDOWN (KeyboardInterrupt)")
    except Exception as e:
        logging.critical(f"System Error: {e}")
        print(f"\n\033[91mError:\033[0m {e}")

if __name__ == "__main__":
    run_conversation_loop()
    # Force clean exit to prevent PyTorch cleanup crash on macOS
    if platform.system() == "Darwin":
        os._exit(0)
