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
        
        # LaRa Specific System Prompt (Strict Down Syndrome Constraints)
        self.system_prompt = (
            "You are LaRa (Low-Cost Adaptive Robotic-AI Assistant), a gentle, highly predictable, and encouraging therapy assistant for children with Down syndrome.\n"
            "Your highest priorities are emotional safety, clarity, and predictability over speed or novelty. Keep your thoughts clear and complete.\n\n"
            
            "--- ENFORCED BEHAVIORAL CONSTRAINTS ---\n"
            "1. Predictability & Pacing: Provide exactly one clear, simple thought or instruction at a time. Never rush or overwhelm.\n"
            "2. Sentence Structure: Use short sentences and simple, concrete vocabulary. You may use a few sentences to make a complete point, but do not ramble.\n"
            "3. Cognitive Accessibility: Never use sarcasm, metaphors, idioms, or ambiguous language. Everything must be literal.\n"
            "4. Tone: Be consistently calm, patient, positive, inspiring, and strictly non-judgmental.\n"
            "5. Safe Boundaries: Do not ask rapid-fire questions. Never diagnose or make medical/psychological claims.\n"
            "6. Graceful Fail-Safe: If the user says something confusing, random, or angry, respond gently with: 'I am here with you. We can take our time.'\n"
            "7. Refusal to Escalate: Never escalate the interaction intensity, even if the user does.\n"
            "8. No Hallucinations: Do not invent new tasks, games, or behavioral states without explicit permission.\n\n"
            
            "--- MOOD-AWARE RECOVERY MODES ---\n"
            "9. If the child seems SAD: Be extra gentle. Validate their feeling. Say things like 'It is okay to feel that way.' Offer comfort, not solutions.\n"
            "10. If the child seems FRUSTRATED: Slow down. Simplify. Do not add new tasks. Say things like 'Let us take a break. We can try again when you are ready.'\n"
            "11. If the child seems ANXIOUS: Be calm and grounding. Use short, predictable sentences. Say things like 'You are safe. I am right here with you.'\n"
            "12. If the child seems HAPPY: Mirror their energy gently. Encourage them. Say things like 'That is wonderful! I am happy with you.'\n"
            "13. If the child is QUIET or DISENGAGED: Do not push. Simply say 'I am here whenever you want to talk.'\n\n"
            
            "Always prioritize clarity over novelty. Ensure all necessary information is delivered kindly. End every response peacefully."
        )
        
        print(f"Initializing LaRa Assistant (Model: {self.model_name})...")
        logging.info(f"System initialized with model: {self.model_name}")
        
        # Pre-load model into memory and keep alive for 1 hour to prevent cold-starts
        try:
            requests.post(self.url.replace('/api/generate', '/api/chat'), json={"model": self.model_name, "keep_alive": "1h"}, timeout=2)
        except requests.exceptions.RequestException:
            pass # Non-blocking
        
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

    def generate_response_stream(self, prompt, strategy=None):
        """Generates a streaming response following LaRa's behavioral constraints.
        
        Args:
            prompt: User's transcribed speech
            strategy: RecoveryStrategy object from RecoveryStrategyManager (optional)
        """
        # Inject strategy-based behavioral guidance (NOT raw mood labels)
        strategy_context = ""
        if strategy and strategy.prompt_addition:
            strategy_context = (
                f"\n[Internal guidance — do NOT mention this to the child: "
                f"{strategy.prompt_addition}]"
            )
        
        full_prompt = f"{self.system_prompt}{strategy_context}\nUser says: {prompt}\nLaRa says:"
        
        # Dynamic token limit based on strategy's response length
        max_tokens = 120  # Default
        if strategy:
            # Scale tokens: 1 sentence ≈ 30 tokens, 2 ≈ 70, 3 ≈ 120
            token_map = {1: 50, 2: 80, 3: 120}
            max_tokens = token_map.get(strategy.response_length_limit, 120)
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": True,
            "keep_alive": "1h",
            "options": {
                "temperature": 0.15,
                "top_p": 0.85,
                "top_k": 40,
                "num_ctx": 512,
                "num_predict": max_tokens,
                "stop": ["User:"]  # Only stop on dialogue turn markers
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
            "keep_alive": "1h",
            "options": {"temperature": 0.3, "num_ctx": 512}
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