import os
import sys

# Define base path to ensure imports work
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.append(base_path)

from denoising import DenoisingModule
from vad_module import VADModule
from endpoint_detection import EndpointDetectionModule
from speech_separation import SpeechSeparationModule
from speaker_recognition import SpeakerRecognitionModule
from asr_module import ASRModule
from punctuation import PunctuationModule

class AudioPipeline:
    """
    Orchestrates the 7-stage advanced audio processing pipeline.
    """
    def __init__(self, device=None):
        print("Initializing Advanced Audio Processing Pipeline...")
        self.device = device
        
        # Lazy loading or initialization could go here. For now we initialize sequentially
        # to ensure they are ready, but in a real low-memory environment, we'd load/unload.
        # We will load them when needed in process() to save VRAM if required, 
        # but for performance (if enough VRAM) we initialize them once.
        self.models_loaded = False
        
    def _load_models(self):
        if self.models_loaded:
            return
            
        print("Loading pipeline models (this may take significant RAM/VRAM)...")
        # 1. Denoising (Demucs)
        self.denoiser = DenoisingModule(device=self.device)
        # 2. VAD (Silero)
        self.vad = VADModule(device=self.device)
        # 3. Endpointing (CAM++)
        self.endpointing = EndpointDetectionModule(device=self.device)
        # 4. Separation (MossFormer2)
        self.separator = SpeechSeparationModule(device=self.device)
        # 5. Speaker Recognition (ERes2NetV2-Large)
        self.speaker_rec = SpeakerRecognitionModule(device=self.device)
        # 6. ASR (SenseVoice)
        self.asr = ASRModule(device=self.device)
        # 7. Punctuation (CT-Transformer)
        self.punctuator = PunctuationModule(device=self.device)
        
        self.models_loaded = True

    def process(self, input_audio_path: str, target_speaker_sample: str) -> str:
        """
        Executes the full pipeline on an audio file to extract clean text from the target speaker.
        
        Args:
            input_audio_path: The mixed/noisy audio file.
            target_speaker_sample: A clean sample of the target speaker to identify them.
            
        Returns:
            The final punctuated transcription string.
        """
        self._load_models()
        
        print("\n--- Starting Audio Pipeline Processing ---")
        
        # 1. Denoising
        print("\n[Step 1/7] Denoising...")
        clean_audio = self.denoiser.process(input_audio_path)
        
        # 2. VAD
        print("\n[Step 2/7] Voice Activity Detection...")
        vad_audio = self.vad.extract_speech_chunks(clean_audio)
        if not vad_audio:
            print("No speech detected by VAD. Aborting.")
            return ""
            
        # 3. Endpoint Detection (Optional pass or logging, VAD handles extraction but CAM++ gets precise boundaries if needed)
        print("\n[Step 3/7] Endpoint Detection...")
        endpoints = self.endpointing.get_endpoints(vad_audio)
        print(f"Detected {len(endpoints)} fine-grained speech segments.")
        
        # 4. Speech Separation
        print("\n[Step 4/7] Speech Separation...")
        separated_tracks = self.separator.separate(vad_audio)
        if not separated_tracks:
            print("Failed to separate tracks. Aborting.")
            return ""
            
        # 5. Speaker Recognition (Identify target)
        print("\n[Step 5/7] Speaker Recognition...")
        target_track = self.speaker_rec.identify_target(target_speaker_sample, separated_tracks)
        
        if not target_track:
            print("Target speaker not found among separated tracks. Using track 0 as fallback.")
            target_track = separated_tracks[0]
        else:
            print(f"Matched target track: {target_track}")
            
        # 6. ASR
        print("\n[Step 6/7] ASR / Transcription...")
        raw_text = self.asr.transcribe(target_track)
        
        # 7. Punctuation
        print("\n[Step 7/7] Punctuation...")
        final_text = self.punctuator.add_punctuation(raw_text)
        
        print("\n--- Pipeline Complete ---")
        return final_text

if __name__ == "__main__":
    # Test script for the pipeline
    pipeline = AudioPipeline()
    # Dummy paths for testing syntax
    # text = pipeline.process("noisy_input.wav", "target_voice.wav")
    # print(f"Output text: {text}")
