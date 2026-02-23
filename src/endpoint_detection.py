import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class EndpointDetectionModule:
    """
    Finds exact start and end boundaries of speech segments using CAM++.
    """
    def __init__(self, device="gpu"):
        """
        Args:
            device: 'gpu' or 'cpu'
        """
        self.device = device
        print(f"Loading CAM++ endpoint detection model on {device}...")
        
        # Note: modelscope usually maps 'gpu' to cuda:0 automatically if available
        # using the 'speech_timestamp_estimation' task usually handles endpointing
        # or we use voice activity detection models explicitly mapped to CAM++
        model_id = 'damo/speech_campplus_vad_zh-cn_16k-common'
        
        self.inference_pipeline = pipeline(
            task=Tasks.voice_activity_detection,
            model=model_id,
            device=device
        )
        
    def get_endpoints(self, audio_path: str):
        """
        Get precise start and end boundaries.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of dictionaries with 'start' and 'end' times (in milliseconds or seconds depending on model)
        """
        print(f"Running CAM++ endpoint detection on {audio_path}...")
        result = self.inference_pipeline(audio_in=audio_path)
        
        # Result format typically looks like:
        # {'text': [[start_time, end_time], [start_time, end_time]]}
        timestamps = []
        if 'text' in result:
            for seg in result['text']:
                if len(seg) == 2:
                    timestamps.append({
                        'start': seg[0],
                        'end': seg[1]
                    })
                    
        return timestamps
