from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class PunctuationModule:
    """
    Adds punctuation (periods, commas, capitalization) to raw ASR text output.
    Uses CT-Transformer via modelscope.
    """
    def __init__(self, device="gpu"):
        """
        Args:
            device: 'gpu' or 'cpu'
        """
        self.device = device
        print(f"Loading CT-Transformer punctuation model on {device}...")
        
        model_id = 'damo/punc_ct-transformer_cn-en-common-vocab471067-large'
        
        self.inference_pipeline = pipeline(
            task=Tasks.punctuation,
            model=model_id,
            device=device
        )
        
    def add_punctuation(self, text: str) -> str:
        """
        Adds punctuation to the given string.
        
        Args:
            text: Raw unpunctuated text string
            
        Returns:
            Punctuated text string
        """
        if not text or len(text.strip()) == 0:
            return text
            
        print("Running punctuation model...")
        result = self.inference_pipeline(text_in=text)
        
        punctuated_text = text
        if 'text' in result:
            punctuated_text = result['text']
            
        print(f"Punctuated text: {punctuated_text}")
        return punctuated_text
