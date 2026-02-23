import os
import torch
import torchaudio
from demucs.pretrained import get_model
from demucs.apply import apply_model

class DenoisingModule:
    """
    Handles audio clean up using Demucs Hybrid v4.
    Removes background noise and reverberation.
    """
    def __init__(self, model_name="htdemucs", device=None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading Demucs model '{model_name}' on {self.device}...")
        self.model = get_model(model_name)
        self.model.to(self.device)
        self.model.eval()
        
    def process(self, audio_path: str, output_dir: str = "output/denoised") -> str:
        """
        Denoises the audio file and saves the isolated vocals/speech track.
        
        Args:
            audio_path: Path to the input audio file
            output_dir: Directory to save the denoised audio
            
        Returns:
            Path to the denoised audio file
        """
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(audio_path)
        name, ext = os.path.splitext(base_name)
        out_path = os.path.join(output_dir, f"{name}_clean.wav")
        
        # Load audio (Demucs expects certain sample rates, usually 44100)
        wav, sr = torchaudio.load(audio_path)
        # Convert to stereo if needed, Demucs typically expects stereo
        if wav.shape[0] == 1:
            wav = wav.repeat(2, 1)
            
        wav = wav.to(self.device)
        # Add batch dimension: (batch, channels, length)
        wav = wav.unsqueeze(0)
        
        print(f"Applying Demucs to {base_name}...")
        with torch.no_grad():
            # sources are usually order: vocals, drums, bass, other
            sources = apply_model(self.model, wav, shifts=1, split=True, overlap=0.25)
            
        # Extract vocals (usually index 3 for htdemucs, but check model definition)
        # For standard htdemucs: ['drums', 'bass', 'other', 'vocals']
        vocals_idx = self.model.sources.index('vocals')
        vocals = sources[0, vocals_idx]
        
        # Move back to CPU and save
        vocals = vocals.cpu()
        torchaudio.save(out_path, vocals, self.model.samplerate)
        
        print(f"Denoised audio saved to {out_path}")
        return out_path
