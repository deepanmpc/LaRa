import sys
import os
import queue
import re
import numpy as np
import sounddevice as sd
import webrtcvad
import time
import logging
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
    from piper_TTS import LaRaSpeech
except ImportError as e:
    logging.warning(f"Could not import LaRaSpeech (TTS module): {e}")
    LaRaSpeech = None

# --- Configuration ---
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
VAD_MODE = 3
SILENCE_DURATION_MS = 2500 # Rule 1 & 10: Gentle pacing, wait 2.5s for slow/paused speech
CHANNELS = 1

# Noise clearance threshold (Energy-based gate)
# Values below this are treated as silence even if VAD triggers
NOISE_GATE_THRESHOLD = 0.005 

# Barge-in hardening: require this many consecutive speech frames before interrupting
# 10 frames * 30ms = 300ms of continuous intentional speech
BARGE_IN_FRAME_THRESHOLD = 10

# Initialize VAD
vad = webrtcvad.Vad(VAD_MODE)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_response(text: str) -> str:
    """
    Validates and simplifies LLM output for neurodiverse cognitive safety.
    Rules:
      - Maximum 3 sentences
      - Remove compound connectors (', and then', ', then')
      - No more than 2 commas per sentence
      - Log if trimming occurs
    """
    if not text or not text.strip():
        return text
    
    # Split into sentences on . ! ?
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s.strip()]
    
    # Trim to max 3 sentences
    if len(sentences) > 3:
        logging.info(f"[Response Validation] Trimmed from {len(sentences)} to 3 sentences.")
        sentences = sentences[:3]
    
    validated = []
    for s in sentences:
        # Remove compound connectors that create multi-step instructions
        s = re.sub(r',\s*and then\b', '.', s, flags=re.IGNORECASE)
        s = re.sub(r',\s*then\b', '.', s, flags=re.IGNORECASE)
        
        # If sentence has more than 2 commas, truncate at 2nd comma
        parts = s.split(',')
        if len(parts) > 3:
            logging.info(f"[Response Validation] Trimmed complex clause: '{s}'")
            s = ','.join(parts[:3]).rstrip() + '.'
        
        validated.append(s.strip())
    
    result = ' '.join(validated)
    return result

def main():
    clear_console()
    print("\033[94m[System]\033[0m Initializing LaRa AI...")
    
    # Point to the local models_dir for offline reference
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'model')
    
    # Speed Optimization: language='en' disables auto-detect.
    whisper_model = Model('small.en', models_dir=models_dir, n_threads=6, print_progress=False, language='en')
    agent = AgentricAI()
    
    # Initialize Piper TTS safely
    lara_voice = None
    if LaRaSpeech:
        voice_model_path = os.path.join(models_dir, 'en_US-lessac-high.onnx')
        # If the model isn't in models_dir, fallback to root or wherever piper defaults it
        if not os.path.exists(voice_model_path):
            voice_model_path = 'en_US-lessac-high.onnx' 
        lara_voice = LaRaSpeech(model_path=voice_model_path)
    
    clear_console()
    print("="*60)
    print("        \033[95mLaRa: Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("="*60)
    print("\033[90mCommands: 'friday' (wake) | 'shutdown' (sleep)\033[0m")
    print("-" * 60)
    print("\033[92mStatus:\033[0m Resting (Listening for wake word...)")

    utterance_frames = []
    silence_frames = 0
    silence_threshold = int(SILENCE_DURATION_MS / FRAME_DURATION_MS)
    is_speaking = False
    is_awake = False
    
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, 
                            callback=callback, blocksize=FRAME_SIZE):
            while True:
                indata = audio_queue.get()
                if len(indata) != FRAME_SIZE: continue
                
                # CRITICAL: Listening Lock
                # If LaRa is currently speaking via TTS, we completely discard microphone frames 
                # so that she never hears or transcribes her own voice loop.
                if lara_voice and lara_voice.is_speaking:
                    if is_speaking:
                        # Reset internal state if we were tracking user speech
                        is_speaking = False
                        utterance_frames = []
                        silence_frames = 0
                    continue
                
                # --- Noise Clearance / Audio Pre-processing ---
                # 1. Simple Energy Check (Noise Gate)
                rms = np.sqrt(np.mean(indata**2))
                
                # 2. Conversion for VAD
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
                            
                            # Normalize audio for clearer transcription
                            # Safety: Only normalize weak signals to prevent amplifying background noise
                            peak = np.max(np.abs(full_audio))
                            if 0 < peak < 0.5:
                                full_audio = full_audio / peak
                                
                            # Speed Optimization: n_threads=6 set at model init, greedy decoding used by default.
                            segments = whisper_model.transcribe(full_audio)
                            text = "".join([s.text for s in segments]).strip()
                            
                            if not text: continue

                            # Handle Shutdown
                            if "shutdown" in text.lower():
                                print(f"\n\033[91m[Shutdown]\033[0m LaRa: Goodbye! Have a lovely day.")
                                return

                            # Handle Awake State
                            if not is_awake:
                                if "friday" in text.lower():
                                    is_awake = True
                                    msg = "\n\033[92m[System Transition]\033[0m LaRa is now AWAKE."
                                    print(msg)
                                    logging.info("[SYSTEM_STATE] Transitioned to AWAKE")
                                    welcome_text = "Hello! I am here to play and learn with you."
                                    print(f"\033[95mLaRa:\033[0m {welcome_text}")
                                    if lara_voice:
                                        lara_voice.speak(welcome_text)
                                        # Flush queue to avoid hearing our own welcome voice
                                        while not audio_queue.empty():
                                            try: audio_queue.get_nowait()
                                            except queue.Empty: break
                                else:
                                    # Subtle notification in-place
                                    sys.stdout.write(f"\r\033[90m(Heard: \"{text}\" - say 'friday' to activate)\033[0m")
                                    sys.stdout.flush()
                                continue

                            # --- Integrated Chat UI (Buffered via Stream) ---
                            # Use the proven streaming endpoint but accumulate internally.
                            # Display and speak atomically after full generation completes.
                            print(f"\n\033[94mYou:\033[0m {text}")
                            
                            # Accumulate full response from the streaming endpoint
                            full_ai_response = ""
                            for chunk in agent.generate_response_stream(text):
                                full_ai_response += chunk
                            
                            # Validate response for cognitive safety before display or speech
                            full_ai_response = validate_response(full_ai_response)
                            
                            # Check if user tried to interrupt during generation
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
                                                logging.info("[Barge-In] User interrupted during LLM generation (300ms+ continuous speech).")
                                                break
                                        else:
                                            barge_in_count = 0  # Reset: must be consecutive
                                except queue.Empty:
                                    break
                            
                            if not interrupted:
                                # Display and speak the validated response atomically
                                print(f"\033[95mLaRa:\033[0m {full_ai_response}")
                                print("-"*30)
                                
                                # Audio Synthesis & Safe Playback
                                if lara_voice and full_ai_response.strip():
                                    lara_voice.speak(full_ai_response.strip())
                                    
                                    # Secondary Safety Constraint: Clear queue
                                    while not audio_queue.empty():
                                        try:
                                            audio_queue.get_nowait()
                                        except queue.Empty:
                                            break
                            else:
                                # Barge-in detected: Do not speak the response to avoid confusion
                                print(f"\033[90m... [User interrupted — listening]\033[0m")
                            
    except KeyboardInterrupt:
        print("\n\n\033[91m[System Transition]\033[0m Stopping gently...")
        logging.info("[SYSTEM_STATE] Transitioned to SHUTDOWN (KeyboardInterrupt)")
    except Exception as e:
        logging.critical(f"System Error: {e}")
        print(f"\n\033[91mError:\033[0m {e}")

if __name__ == "__main__":
    main()
