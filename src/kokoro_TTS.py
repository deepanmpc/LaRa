"""
Kokoro TTS Module for LaRa
Voice: af_bella (American Female - Clear)
Features: Interruptible playback, listening lock, duration logging, echo cooldown.
"""

import os
import time
import logging
import threading
import numpy as np
import sounddevice as sd


class LaRaSpeech:
    """
    Production-hardened Kokoro TTS module for LaRa.
    Drop-in replacement for the Piper-based LaRaSpeech.
    Supports mid-speech interruption via wake-word detection.
    """

    # Cooldown: ignore repeated interrupt triggers within this window
    INTERRUPT_COOLDOWN_S = 1.0

    def __init__(self, voice='af_bella', repo_id='hexgrad/Kokoro-82M'):
        self.voice_id = voice
        self.is_speaking = False
        self._interrupt_requested = False
        self._last_interrupt_time = 0.0
        self._playback_lock = threading.Lock()
        self._current_stream = None
        self.speed = 0.9  # Default speed, adjustable by recovery strategy

        # Lazy-load Kokoro to avoid import-time delays
        self.pipeline = None
        self._repo_id = repo_id

        try:
            from kokoro import KPipeline
            self.pipeline = KPipeline(lang_code='a', repo_id=repo_id)
            logging.info(f"Successfully loaded Kokoro TTS (voice: {voice})")
        except Exception as e:
            logging.error(f"Failed to load Kokoro TTS: {e}")
            print(f"\033[91m[TTS Error]\033[0m Could not load Kokoro: {e} - System will continue silently.")

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

        # Stop sounddevice playback immediately
        try:
            sd.stop()
        except Exception:
            pass

        logging.info("[TTS Interrupt] Speech interrupted by wake-word.")
        return True

    def speak(self, text: str):
        """
        Synthesizes and plays text using Kokoro TTS with chunk-by-chunk streaming.
        Checks for interrupt between each chunk for responsive wake-word detection.
        Returns True if speech completed fully, False if interrupted.
        """
        if not text or not text.strip():
            return True

        if not self.pipeline:
            logging.warning("TTS attempted but Kokoro pipeline not loaded.")
            return True

        self.is_speaking = True
        self._interrupt_requested = False
        was_interrupted = False
        playback_start = time.time()

        try:
            # Speed controlled by recovery strategy (default 0.9 for neurodiverse pacing)
            generator = self.pipeline(text, voice=self.voice_id, speed=self.speed)

            for i, (gs, ps, audio) in enumerate(generator):
                # Check for interrupt BEFORE playing each chunk
                if self._interrupt_requested:
                    was_interrupted = True
                    break

                # Convert to numpy (prevents bus error on Apple Silicon)
                audio_np = audio.numpy() if hasattr(audio, 'numpy') else np.array(audio, dtype=np.float32)

                # Amplitude check
                max_amp = np.max(np.abs(audio_np)) if len(audio_np) > 0 else 0
                if max_amp > 0.99:
                    logging.warning(f"Audio amplitude spike detected ({max_amp:.3f}). Potential clipping.")

                # Play chunk and wait for completion
                sd.play(audio_np, 24000)

                # Poll while playing — check for interrupt every 50ms
                while sd.get_stream().active:
                    if self._interrupt_requested:
                        sd.stop()
                        was_interrupted = True
                        break
                    time.sleep(0.05)

                if was_interrupted:
                    break

            playback_duration = time.time() - playback_start

            if was_interrupted:
                logging.info(f"[TTS Out] Interrupted after {playback_duration:.1f}s: {text}")
            else:
                logging.info(f"[TTS Out] Spoke: {text} | Duration: {playback_duration:.1f}s")
                if playback_duration > 12.0:
                    logging.warning(f"[TTS Duration Warning] Speech lasted {playback_duration:.1f}s")

        except Exception as e:
            logging.error(f"Error during Kokoro speech synthesis/playback: {e}")
            print(f"\n\033[91m[Audio Error]\033[0m Problem playing LaRa's voice: {e}")

        finally:
            self.is_speaking = False
            self._interrupt_requested = False

        return not was_interrupted
