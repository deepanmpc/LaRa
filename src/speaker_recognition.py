import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import numpy as np
from scipy.spatial.distance import cosine

class SpeakerRecognitionModule:
    """
    Identifies if a given audio clip belongs to the target speaker.
    Uses ERes2NetV2-Large via modelscope to compute speaker embeddings.
    """
    def __init__(self, device="gpu"):
        """
        Args:
            device: 'gpu' or 'cpu'
        """
        self.device = device
        print(f"Loading ERes2NetV2-Large speaker verification model on {device}...")
        
        # Model for extracting d-vectors / embeddings
        model_id = 'damo/speech_eres2net_sv_zh-cn_16k-common'
        
        self.inference_pipeline = pipeline(
            task=Tasks.speaker_verification,
            model=model_id,
            device=device
        )
        
    def get_embedding(self, audio_path: str) -> np.ndarray:
        """
        Extract the speaker embedding from an audio file.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Numpy array of the embedding
        """
        # We can extract embeddings using speaker verification pipelines
        # Usually modelscope SV pipelines take two inputs to compare, 
        # or we can pass the same input twice to get the intermediate embedding feature.
        # Check docs, but standard is:
        result = self.inference_pipeline(audio_in=(audio_path, audio_path))
        return result
        
    def identify_target(self, target_sample_path: str, separated_tracks: list[str], threshold: float = 0.6) -> str:
        """
        Compares multiple separated tracks against a reference target sample.
        
        Args:
            target_sample_path: The reference sample of the target user's voice
            separated_tracks: List of paths to the separated speaker tracks
            threshold: Minimum similarity score to be considered a match
            
        Returns:
            Path to the matching separated track, or None if no match found
        """
        best_score = -1.0
        best_match = None
        
        print(f"Identifying target among {len(separated_tracks)} tracks...")
        for track in separated_tracks:
            # modelscope sv pipeline returns a score, higher means more similar
            print(f"  Comparing: {os.path.basename(target_sample_path)} vs {os.path.basename(track)}")
            result = self.inference_pipeline(audio_in=(target_sample_path, track))
            
            # The result format usually contains a 'score'
            if 'score' in result:
                score = result['score']
                print(f"    Similarity score: {score:.4f}")
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = track
                    
        return best_match
