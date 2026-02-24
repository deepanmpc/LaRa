import os
import wave
import subprocess
import logging
import tempfile
import platform
import time
import numpy as np
from piper import PiperVoice

class LaRaSpeech:
    def __init__(self, model_path="en_US-lessac-high.onnx"):
        self.voice = None
        self.is_speaking = False  # CRITICAL: Listening Lock
        self.os_name = platform.system()
        
        try:
            self.voice = PiperVoice.load(model_path)
            logging.info(f"Successfully loaded Piper TTS model: {model_path}")
        except Exception as e:
            logging.error(f"Failed to load Piper TTS model {model_path}: {e}")
            print(f"\033[91m[TTS Error]\033[0m Could not load voice model: {e} - System will continue silently.")

    def _play_audio(self, filepath: str):
        """Cross-platform blocking audio playback."""
        try:
            if self.os_name == "Darwin":  # macOS
                subprocess.run(["afplay", filepath], check=True)
            elif self.os_name == "Linux":
                subprocess.run(["aplay", filepath], check=True)
            elif self.os_name == "Windows":
                # Fallback for Windows if needed, though instructions specified macOS + Linux
                import winsound
                winsound.PlaySound(filepath, winsound.SND_FILENAME)
            else:
                logging.error(f"Unsupported OS to play audio: {self.os_name}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Audio playback command failed: {e}")
        except FileNotFoundError as e:
            logging.error(f"Command not found for playing audio (is afplay/aplay installed?): {e}")

    def speak(self, text: str):
        """
        Synthesizes text to a WAV file and plays it synchronously.
        Strictly enforces LaRa constraints: Blocking, clear, non-overlapping, slower paced.
        """
        if not text or not text.strip():
            return
            
        if not self.voice:
            logging.warning("TTS attempted but voice model not loaded.")
            return

        # 1. Engage Listening Lock
        self.is_speaking = True
        temp_filepath = None
        
        try:
            # 2. Secure Temporary File
            # delete=False because external process like afplay needs to read it
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_filepath = temp_wav.name
                
            with wave.open(temp_filepath, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.voice.config.sample_rate)

                # 3. Speech Rate Optimization (length_scale > 1.0 slows down voice gently)
                # length_scale 1.2 enforces slower, more comprehensible pacing for neurodiverse children.
                for chunk in self.voice.synthesize(text, length_scale=1.2):
                    audio_bytes = chunk.audio_int16_bytes
                    
                    # 4. Amplitude Check (Ensure 16-bit doesn't clip destructively)
                    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                    max_amp = np.max(np.abs(audio_array)) if len(audio_array) > 0 else 0
                    if max_amp > 32000:
                        logging.warning(f"Audio amplitude spike detected ({max_amp}). Potential clipping.")
                        
                    wav_file.writeframes(audio_bytes)
            
            # 5. Play Audio Synchronously (Blocking) with Duration Tracking
            playback_start = time.time()
            self._play_audio(temp_filepath)
            playback_duration = time.time() - playback_start
            
            # 6. Log transparency
            logging.info(f"[TTS Out] Spoke: {text} | Duration: {playback_duration:.1f}s")
            
            if playback_duration > 12.0:
                logging.warning(f"[TTS Duration Warning] Speech lasted {playback_duration:.1f}s — may exceed cognitive comfort for neurodiverse children.")

        except Exception as e:
            logging.error(f"Error during speech synthesis/playback: {e}")
            print(f"\n\033[91m[Audio Error]\033[0m Problem playing LaRa's voice: {e}")
        
        finally:
            # 7. Release Listening Lock and Cleanup Files
            self.is_speaking = False
            
            if temp_filepath and os.path.exists(temp_filepath):
                try:
                    os.unlink(temp_filepath)
                except Exception as e:
                    logging.warning(f"Failed to clean up audio temp file {temp_filepath}: {e}")