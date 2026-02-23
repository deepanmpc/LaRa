import os
import torch
import torchaudio

class VADModule:
    """
    Uses Silero VAD to detect speech segments in an audio file.
    """
    def __init__(self, device=None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        print(f"Loading Silero VAD on {self.device}...")
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        self.model.to(self.device)
        self.get_speech_timestamps = utils[0]
        self.save_audio = utils[1]
        self.read_audio = utils[2]
        self.VAD_ITERATOR = utils[3]
        self.COLLECT_CHUNKS = utils[4]
        
    def detect_speech(self, audio_path: str, threshold: float = 0.5, sampling_rate: int = 16000):
        """
        Detects speech segments in the provided audio file.
        
        Args:
            audio_path: Path to the audio file
            threshold: Confidence threshold for speech detection
            sampling_rate: Target sampling rate (Silero usually expects 16k)
            
        Returns:
            List of dictionaries containing 'start' and 'end' samples of speech segments
        """
        # Silero VAD utility for reading audio ensures it's 1D, 16kHz
        wav = self.read_audio(audio_path, sampling_rate=sampling_rate)
        wav = wav.to(self.device)
        
        # Get speech timestamps (in samples)
        speech_timestamps = self.get_speech_timestamps(
            wav, 
            self.model, 
            sampling_rate=sampling_rate,
            threshold=threshold
        )
        
        return speech_timestamps, wav

    def extract_speech_chunks(self, audio_path: str, output_dir: str = "output/vad", sampling_rate: int = 16000) -> str:
        """
        Extracts speech segments and stitches them together, saving the result.
        
        Args:
            audio_path: Path to the source audio
            output_dir: Directory to save the output
            
        Returns:
            Path to the concatenated speech audio file.
        """
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(audio_path)
        name, ext = os.path.splitext(base_name)
        out_path = os.path.join(output_dir, f"{name}_speech_only.wav")
        
        speech_timestamps, wav = self.detect_speech(audio_path, sampling_rate=sampling_rate)
        
        if not speech_timestamps:
            print(f"No speech detected in {audio_path}")
            return None
            
        print(f"Found {len(speech_timestamps)} speech segments in {base_name}.")
        
        # Collect all chunks into one tensor
        speech_tensor = self.COLLECT_CHUNKS(speech_timestamps, wav)
        
        # Save concatenated audio
        self.save_audio(out_path, speech_tensor, sampling_rate=sampling_rate)
        print(f"Speech-only audio saved to {out_path}")
        
        return out_path
