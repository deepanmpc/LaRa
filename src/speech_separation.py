import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class SpeechSeparationModule:
    """
    Separates voices from a mixed audio file.
    Implements MossFormer2 (primary) and SepFormer (fallback/alternative).
    """
    def __init__(self, model_type="mossformer2", device="gpu"):
        """
        Args:
            model_type: 'mossformer2' or 'sepformer'
            device: 'gpu' or 'cpu'
        """
        self.device = device
        self.model_type = model_type.lower()
        
        if self.model_type == "mossformer2":
            print(f"Loading MossFormer2 separation model on {device}...")
            # Example MossFormer2 2-speaker separation model
            model_id = 'damo/speech_mossformer2_separation_temporal_8k'
        elif self.model_type == "sepformer":
            print(f"Loading SepFormer separation model on {device}...")
            model_id = 'damo/speech_sepformer_separation_temporal_8k'
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
            
        self.inference_pipeline = pipeline(
            task=Tasks.speech_separation,
            model=model_id,
            model_revision='v1.0.1', # Adjust as needed
            device=device
        )
        
    def separate(self, audio_path: str, output_dir: str = "output/separated") -> list[str]:
        """
        Separates the audio into individual speaker tracks.
        
        Args:
            audio_path: Path to the input mixed audio
            output_dir: Directory to save separated tracks
            
        Returns:
            List of paths to the separated audio files
        """
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(audio_path)
        name, _ = os.path.splitext(base_name)
        
        print(f"Running Speech Separation ({self.model_type}) on {audio_path}...")
        result = self.inference_pipeline(audio_in=audio_path)
        
        output_paths = []
        if 'output_pcm_list' in result:
            # Result contains separated audio path(s)
            separated_audio_paths = result['output_pcm_list']
            
            for i, sep_path in enumerate(separated_audio_paths):
                # We usually move or rename the output file to our desired output_dir
                target_path = os.path.join(output_dir, f"{name}_speaker_{i}.wav")
                
                # Copy or rename the temporary outputs to target
                # (modelscope sometimes outputs to its own cache temp folder)
                if os.path.exists(sep_path):
                    import shutil
                    shutil.copy2(sep_path, target_path)
                    output_paths.append(target_path)
                    
        print(f"Separated audio saved to: {output_paths}")
        return output_paths
