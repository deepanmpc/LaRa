import requests
import json
import logging
import sys
import os

# Ensure the audiopipeline can be imported
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_path not in sys.path:
    sys.path.append(base_path)

try:
    from simple_audio_pipeline import SimpleAudioPipeline
except ImportError:
    SimpleAudioPipeline = None

# Configure logging for caregiver review
logging.basicConfig(
    filename='lara_interaction.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AgentricAI:
    def __init__(self, model_name="AgentricAi/AgentricAI_TLM:latest"):
        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"
        
        # LaRa Specific System Prompt
        self.system_prompt = (
            "You are LaRa, a gentle and encouraging therapy assistant for children with Down syndrome. "
            "Follow these rules strictly:\n"
            "1. Use very short sentences.\n"
            "2. Use simple, clear vocabulary.\n"
            "3. Be calm, patient, and non-judgmental.\n"
            "4. Provide only one instruction or thought at a time.\n"
            "5. Avoid sarcasm, metaphors, or ambiguous language.\n"
            "6. Always be encouraging and positive.\n"
            "7. Do not make medical or psychological claims.\n"
        )
        
        print(f"Initializing LaRa Assistant (Model: {self.model_name})...")
        logging.info(f"System initialized with model: {self.model_name}")
        
        self.audio_pipeline = None

    def initialize_audio_pipeline(self):
        """Lazy load the simple audio pipeline model when first needed to save memory."""
        if self.audio_pipeline is None:
            if SimpleAudioPipeline is None:
                logging.error("SimpleAudioPipeline module not found or failed to import.")
                print("Error: Could not load the audio pipeline components.")
                return False
            self.audio_pipeline = SimpleAudioPipeline(device="cpu", compute_type="int8")
            # Defer full whisper load until actually processing to reduce footprint,
            # or load immediately if preferred. We'll let process_audio handle the _load_models() automatically.
        return True

    def generate_response_stream(self, prompt):
        """Generates a streaming response following LaRa's behavioral constraints."""
        # Combine system prompt with user input
        full_prompt = f"{self.system_prompt}\nUser says: {prompt}\nLaRa says:"
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": True,
            "options": {
                "temperature": 0.4, # Lower temperature for more predictability
                "top_p": 0.9,
                "stop": ["User:", "\n"] # Prevent the model from hallucinating dialogue
            }
        }
        
        try:
            response = requests.post(self.url, json=payload, stream=True)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    text_chunk = chunk.get('response', '')
                    full_response += text_chunk
                    yield text_chunk
                    if chunk.get('done', False):
                        break
            
            logging.info(f"Interaction - User: {prompt} | LaRa: {full_response}")
            
        except Exception as e:
            error_msg = "I am sorry, I am having trouble thinking right now. Let us try again."
            logging.error(f"Ollama Error: {e}")
            yield error_msg

    def generate_response(self, prompt):
        """Legacy non-streaming method with LaRa constraints."""
        full_prompt = f"{self.system_prompt}\nUser says: {prompt}\nLaRa says:"
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            res_text = response.json().get("response", "")
            return res_text
        except Exception as e:
            logging.error(f"Ollama Error: {e}")
            return "I am here with you. Let us take a deep breath."

    def handle_audio_input(self, audio_file_path: str):
        """
        Processes an audio file through the fast WhisperX pipeline.
        Extracts clean text securely, prioritizing emotional safety and low latency.
         Streams the LLM response back.
        """
        if not self.initialize_audio_pipeline():
            # Safe Fallback: gentle response if audio system fails
            yield "There is a problem hearing your voice. Let us type for now."
            return
            
        try:
            print(f"Listening to nicely to {audio_file_path}...")
            transcribed_text = self.audio_pipeline.process_audio(audio_file_path)
            
            # Constraints: If detection is low or empty -> default to neutral supportive behavior
            if not transcribed_text or len(transcribed_text.strip()) < 2:
                yield "I am here with you. Can you say that one more time?"
                return
                
            print(f"Transcribed Text for LLM: '{transcribed_text}'")
            logging.info(f"Audio Processing Output -> LLM Input: {transcribed_text}")
            
            # Ask the LLM to generate the safe, structured response
            for chunk in self.generate_response_stream(transcribed_text):
                yield chunk
                
        except Exception as e:
            # Constraints: Never escalate intensity automatically on failure
            logging.error(f"Pipeline Error: {e}")
            yield "I am listening, but it is a bit noisy. Let us take our time."

if __name__ == "__main__":
    agent = AgentricAI()
    for chunk in agent.generate_response_stream("Hello, I am happy!"):
        print(chunk, end="", flush=True)
    print()