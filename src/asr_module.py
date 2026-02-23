import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class ASRModule:
    """
    Transcribes the isolated audio into raw text using an ASR engine like SenseVoice.
    """
    def __init__(self, model_type="sensevoice", device="gpu"):
        """
        Args:
            model_type: Default currently set to SenseVoice via modelscope.
            device: 'gpu' or 'cpu'
        """
        self.device = device
        self.model_type = model_type.lower()
        
        print(f"Loading ASR model ({self.model_type}) on {device}...")
        
        if self.model_type == "sensevoice":
            # Example SenseVoice model id
            model_id = 'iic/SenseVoiceSmall' 
            self.inference_pipeline = pipeline(
                task=Tasks.auto_speech_recognition,
                model=model_id,
                device=device
            )
        else:
            raise ValueError(f"Unknown ASR model type: {model_type}")
            
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the given audio file.
        
        Args:
            audio_path: Path to the target audio file
            
        Returns:
            The raw transcribed text
        """
        print(f"Running ASR ({self.model_type}) on {audio_path}...")
        result = self.inference_pipeline(audio_in=audio_path)
        
        text = ""
        if 'text' in result:
            text = result['text']
            
        print(f"Raw transcription: {text}")
        return text
