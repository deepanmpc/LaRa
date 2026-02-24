import os
import wave
import subprocess
import logging
import tempfile
import platform
import time
import signal
import numpy as np
from piper import PiperVoice
from piper.config import SynthesisConfig


class LaRaSpeech:
    """
    Production-hardened TTS module for LaRa.
    Supports mid-speech interruption via wake-word detection.
    """
    
    # Cooldown: ignore repeated interrupt triggers within this window
    INTERRUPT_COOLDOWN_S = 1.0

    def __init__(self, model_path="en_US-lessac-high.onnx"):
        self.voice = None
        self.is_speaking = False
        self.os_name = platform.system()
        self._interrupt_requested = False
        self._playback_process = None
        self._last_interrupt_time = 0.0
        
        try:
            self.voice = PiperVoice.load(model_path)
            logging.info(f"Successfully loaded Piper TTS model: {model_path}")
        except Exception as e:
            logging.error(f"Failed to load Piper TTS model {model_path}: {e}")
            print(f"\033[91m[TTS Error]\033[0m Could not load voice model: {e} - System will continue silently.")

    def _get_play_command(self, filepath: str):
        """Returns the OS-appropriate audio playback command."""
        if self.os_name == "Darwin":
            return ["afplay", filepath]
        elif self.os_name == "Linux":
            return ["aplay", filepath]
        else:
            return None

    def interrupt_speech(self):
        """
        Safely interrupts ongoing TTS playback.
        Called externally when wake-word 'LaRa' is detected during SPEAKING mode.
        """
        now = time.time()
        if now - self._last_interrupt_time < self.INTERRUPT_COOLDOWN_S:
            logging.info("[TTS Interrupt] Suppressed — cooldown active.")
            return False
        
        self._interrupt_requested = True
        self._last_interrupt_time = now
        
        # Kill the playback process if running
        if self._playback_process and self._playback_process.poll() is None:
            try:
                self._playback_process.terminate()
                self._playback_process.wait(timeout=1.0)
            except Exception:
                try:
                    self._playback_process.kill()
                except Exception:
                    pass
        
        logging.info("[TTS Interrupt] Speech interrupted by wake-word.")
        return True

    def speak(self, text: str):
        """
        Synthesizes text to WAV and plays it with a pollable, interruptible subprocess.
        Returns True if speech completed fully, False if interrupted.
        """
        if not text or not text.strip():
            return True
            
        if not self.voice:
            logging.warning("TTS attempted but voice model not loaded.")
            return True

        self.is_speaking = True
        self._interrupt_requested = False
        temp_filepath = None
        was_interrupted = False
        
        try:
            # 1. Secure Temporary File
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_filepath = temp_wav.name
                
            with wave.open(temp_filepath, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.voice.config.sample_rate)

                # Speech Rate Optimization: length_scale 1.2 for neurodiverse pacing
                syn_config = SynthesisConfig(length_scale=1.2)
                for chunk in self.voice.synthesize(text, syn_config=syn_config):
                    audio_bytes = chunk.audio_int16_bytes
                    
                    # Amplitude Check
                    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                    max_amp = np.max(np.abs(audio_array)) if len(audio_array) > 0 else 0
                    if max_amp > 32000:
                        logging.warning(f"Audio amplitude spike detected ({max_amp}). Potential clipping.")
                        
                    wav_file.writeframes(audio_bytes)
            
            # 2. Non-blocking Playback with Polling for Interrupt
            play_cmd = self._get_play_command(temp_filepath)
            if not play_cmd:
                logging.error(f"Unsupported OS for audio playback: {self.os_name}")
                return True
            
            playback_start = time.time()
            self._playback_process = subprocess.Popen(
                play_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Poll every 50ms — checking for interrupt or natural completion
            while self._playback_process.poll() is None:
                if self._interrupt_requested:
                    # Kill the process
                    try:
                        self._playback_process.terminate()
                        self._playback_process.wait(timeout=1.0)
                    except Exception:
                        try:
                            self._playback_process.kill()
                        except Exception:
                            pass
                    was_interrupted = True
                    break
                time.sleep(0.05)
            
            playback_duration = time.time() - playback_start
            
            if was_interrupted:
                logging.info(f"[TTS Out] Interrupted after {playback_duration:.1f}s: {text}")
            else:
                logging.info(f"[TTS Out] Spoke: {text} | Duration: {playback_duration:.1f}s")
                if playback_duration > 12.0:
                    logging.warning(f"[TTS Duration Warning] Speech lasted {playback_duration:.1f}s")

        except Exception as e:
            logging.error(f"Error during speech synthesis/playback: {e}")
            print(f"\n\033[91m[Audio Error]\033[0m Problem playing LaRa's voice: {e}")
        
        finally:
            self.is_speaking = False
            self._interrupt_requested = False
            self._playback_process = None
            
            if temp_filepath and os.path.exists(temp_filepath):
                try:
                    os.unlink(temp_filepath)
                except Exception as e:
                    logging.warning(f"Failed to clean up audio temp file {temp_filepath}: {e}")
        
        return not was_interrupted