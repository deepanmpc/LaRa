import sys
import os
import queue
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

# Initialize VAD
vad = webrtcvad.Vad(VAD_MODE)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_console()
    print("\033[94m[System]\033[0m Initializing LaRa AI...")
    
    # Point to the local models_dir for offline reference
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, 'model')
    
    # Speed Optimization: language='en' disables auto-detect. 
    whisper_model = Model('small.en', models_dir=models_dir, n_threads=6, print_progress=False, language='en')
    agent = AgentricAI()
    
    clear_console()
    print("="*60)
    print("        \033[95mLaRa: Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("="*60)
    print("\033[90mCommands: 'model wake up' | 'model shutdown'\033[0m")
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
                            if np.max(np.abs(full_audio)) > 0:
                                full_audio = full_audio / np.max(np.abs(full_audio))
                                
                            # Speed Optimization: num_threads=6 matching hardware, beam_size=1 (greedy decoding) for absolute fastest inference.
                            segments = whisper_model.transcribe(full_audio, num_threads=6, beam_size=1)
                            text = "".join([s.text for s in segments]).strip()
                            
                            if not text: continue

                            # Handle Shutdown
                            if "model shutdown" in text.lower():
                                print(f"\n\033[91m[Shutdown]\033[0m LaRa: Goodbye! Have a lovely day.")
                                return

                            # Handle Awake State
                            if not is_awake:
                                if "model wake up" in text.lower():
                                    is_awake = True
                                    msg = "\n\033[92m[System Transition]\033[0m LaRa is now AWAKE."
                                    print(msg)
                                    logging.info("[SYSTEM_STATE] Transitioned to AWAKE")
                                    print(f"\033[95mLaRa:\033[0m Hello! I am here to play and learn with you.")
                                else:
                                    # Subtle notification in-place
                                    sys.stdout.write(f"\r\033[90m(Heard: \"{text}\" - say 'model wake up' to activate)\033[0m")
                                    sys.stdout.flush()
                                continue

                            # --- Integrated Chat UI ---
                            # We print user and AI in the same block
                            print(f"\n\033[94mYou:\033[0m {text}")
                            print(f"\033[95mLaRa:\033[0m ", end="", flush=True)
                            
                            interrupted = False
                            for chunk in agent.generate_response_stream(text):
                                print(chunk, end="", flush=True)
                                
                                # Barge-in check
                                try:
                                    while not audio_queue.empty():
                                        peek_data = audio_queue.get_nowait()
                                        if len(peek_data) == FRAME_SIZE:
                                            peek_rms = np.sqrt(np.mean(peek_data**2))
                                            peek_pcm = (peek_data * 32767).astype(np.int16)
                                            if vad.is_speech(peek_pcm.tobytes(), SAMPLE_RATE) and peek_rms > NOISE_GATE_THRESHOLD:
                                                print("\033[90m... [Listening]\033[0m")
                                                interrupted = True
                                                is_speaking = True
                                                utterance_frames = [peek_data]
                                                silence_frames = 0
                                                break
                                    if interrupted: break
                                except queue.Empty: pass
                            
                            if not interrupted:
                                print("\n" + "-"*30)
                            
    except KeyboardInterrupt:
        print("\n\n\033[91m[System Transition]\033[0m Stopping gently...")
        logging.info("[SYSTEM_STATE] Transitioned to SHUTDOWN (KeyboardInterrupt)")
    except Exception as e:
        logging.critical(f"System Error: {e}")
        print(f"\n\033[91mError:\033[0m {e}")

if __name__ == "__main__":
    main()
