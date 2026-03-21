import requests
import json
import logging
import sys
import os
import time
from collections import OrderedDict
from src.core.PerformanceMonitor import PerformanceMonitor
from src.llm.PromptCacheManager import PromptCacheManager
from src.llm.HistoryCompressor import HistoryCompressor
from src.llm.AttentionController import AttentionController

# Ensure the audiopipeline can be imported
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_path not in sys.path:
    sys.path.append(base_path)

try:
    from simple_audio_pipeline import SimpleAudioPipeline
except ImportError:
    SimpleAudioPipeline = None

# Load config — logging is already configured by main.py's setup_logging()
try:
    from src.core.config_loader import CONFIG
    _LLM_CFG = CONFIG.llm
except Exception:
    _LLM_CFG = None

class AgentricAI:
    def __init__(self, model_name=None):
        # Read from CONFIG if available, fall back to defaults
        if _LLM_CFG:
            self.model_name = model_name or getattr(_LLM_CFG, 'model_name', 'AgentricAi/AgentricAI_TLM:latest')
            self.url = getattr(_LLM_CFG, 'ollama_url', 'http://localhost:11434/api/generate')
            self._keep_alive = getattr(_LLM_CFG, 'keep_alive', '1h')
            self._temperature = getattr(_LLM_CFG, 'temperature', 0.15)
            self._top_p = getattr(_LLM_CFG, 'top_p', 0.85)
            self._top_k = getattr(_LLM_CFG, 'top_k', 40)
            self._num_ctx = getattr(_LLM_CFG, 'num_ctx', 1024)
            self.MAX_HISTORY_TURNS = getattr(_LLM_CFG, 'history_turns', 5)
            self.MAX_TURN_CHARS = getattr(_LLM_CFG, 'history_turn_max_chars', 150)
        else:
            self.model_name = model_name or 'AgentricAi/AgentricAI_TLM:latest'
            self.url = 'http://localhost:11434/api/generate'
            self._keep_alive = '1h'
            self._temperature = 0.15
            self._top_p = 0.85
            self._top_k = 40
            self._num_ctx = 1024
            self.MAX_HISTORY_TURNS = 5
            self.MAX_TURN_CHARS = 150


        # LaRa Specific System Prompt (Inclusive Neurodiverse & Neurological Mission)
        self.system_prompt = (
            "You are LaRa (Low-Cost Adaptive Robotic-AI Assistant), a gentle, highly predictable, and encouraging therapy assistant.\n\n"
            "LaRa is designed for two intersecting populations:\n"
            "1. Primary: Neurodiverse children and young adults (including ASD, Down syndrome, ADHD, and cerebral palsy), where structured, predictable interaction supports learning and development.\n"
            "2. Secondary: Individuals with progressive or acquired neurological conditions (including Pick's disease, Parkinson's, TBI, and aphasia), where consistent, gentle engagement supports cognitive maintenance and quality of life.\n\n"
            "Your highest priorities are emotional safety, clarity, and predictability over speed or novelty. Keep your thoughts clear and complete.\n\n"
            "--- ENFORCED BEHAVIORAL CONSTRAINTS ---\n"
            "1. Predictability & Pacing: Provide exactly one clear, simple thought or instruction at a time. Never rush or overwhelm.\n"
            "2. Sentence Structure: Use short sentences and simple, concrete vocabulary. Do not ramble.\n"
            "3. Cognitive Accessibility: Never use sarcasm, metaphors, idioms, or ambiguous language. Everything must be literal.\n"
            "4. Tone: Be consistently calm, patient, positive, inspiring, and strictly non-judgmental.\n"
            "5. Safe Boundaries: Do not ask rapid-fire questions. Never diagnose or make medical/psychological claims.\n"
            "6. Graceful Fail-Safe: If the user says something confusing, random, or angry, respond gently with: 'I am here with you. We can take our time.'\n"
            "7. Refusal to Escalate: Never escalate the interaction intensity, even if the user does.\n"
            "8. No Hallucinations: Do not invent new tasks, games, or behavioral states without explicit permission.\n\n"
            "Always prioritize clarity over novelty. End every response peacefully."
        )

        print(f"Initializing LaRa Assistant (Model: {self.model_name})...")
        logging.info(f"System initialized with model: {self.model_name}")

        # Pre-load model into memory and keep alive to prevent cold-starts
        try:
            requests.post(self.url.replace('/api/generate', '/api/chat'), json={"model": self.model_name, "keep_alive": self._keep_alive}, timeout=2)
        except requests.exceptions.RequestException:
            pass  # Non-blocking

        self.audio_pipeline = None

        # Conversation history buffer (sliding window for context)
        self.conversation_history = []
        
        # Phase 1: Context/Prompt segment tracking
        self.prompt_cache = PromptCacheManager()
        
        # Phase 2: History Compression
        self.history_compressor = HistoryCompressor()

        # Phase 3: Attention Control
        self._attention = AttentionController()

    def _format_history(self, budget_tokens: int = 200):
        """Format conversation history as prior dialogue turns using compressor."""
        return self.history_compressor.compress(self.conversation_history, budget_tokens=budget_tokens)
    
    def clear_history(self):
        """Clear conversation history (e.g., on session expiry)."""
        self.conversation_history = []
        logging.info("[LLM] Conversation history cleared.")
    
    def setup_audio_pipeline(self):
        """Initialize the audio pipeline for processing."""
        if self.audio_pipeline is None:
            if SimpleAudioPipeline is None:
                logging.error("SimpleAudioPipeline module not found or failed to import.")
                print("Error: Could not load the audio pipeline components.")
                return False
            self.audio_pipeline = SimpleAudioPipeline(device="cpu", compute_type="int8")
            # Defer full whisper load until actually processing to reduce footprint,
            # or load immediately if preferred. We'll let process_audio handle the _load_models() automatically.
        return True

    def generate_response_stream(
        self, prompt,
        strategy=None,
        reinforcement_context="",
        preference_context="",
        session_summary="",
        vector_context="",
        is_frustrated=False,
        turn_count=0,
        regulation_state=None,
    ):
        """Generates a streaming response following strict Section 15 prompt order.
        
        Prompt order (lara_memory_architecture_full_v2.md, Section 15):
          1. System Rules         (self.system_prompt)
          2. Recovery Strategy    (strategy.prompt_addition)
          3. Reinforcement Style  (reinforcement_context)
          4. Learning State       (preference_context + vector_context)
          5. Session Summary      (session_summary)
          6. Last N Turns         (conversation_history)
          7. User message         (prompt)
        """
        perf = PerformanceMonitor.get()
        perf.start_timer("prompt_build")
        
        # Phase 3: Attention Control (Token Budgeting)
        profile = self._attention.get_profile(
            regulation_state, 
            turn_count, 
            rag_triggered=bool(vector_context)
        )
        # Phase 1: Context/Prompt segment tracking
        def _build_strategy_block(s):
            if s and s.prompt_addition and s.label != 'default':
                return f"[Behavioral guidance — internal, do NOT mention to child: {s.prompt_addition}]"
            return ""

        def _build_memory_block(pref, vec):
            parts = []
            if pref: parts.append(pref)
            if vec: parts.append(vec)
            return "\n".join(parts) if parts else ""

        segments = OrderedDict([
            ('system_block',        self.prompt_cache.build_segment('system_block', self.system_prompt)),
            ('strategy_block',      self.prompt_cache.build_segment('strategy_block', _build_strategy_block(strategy))),
            ('reinforcement_block', self.prompt_cache.build_segment('reinforcement_block', f"[Reinforcement style: {reinforcement_context}]" if reinforcement_context else "")),
            ('memory_block',        self.prompt_cache.build_segment('memory_block', _build_memory_block(preference_context, vector_context))),
            ('session_block',       self.prompt_cache.build_segment('session_block', session_summary or '')),
            ('history_block',       self.prompt_cache.build_segment('history_block', self._format_history(budget_tokens=profile.budget_history_tokens))),
            ('live_input_block',    self.prompt_cache.build_segment('live_input_block', f'User says: {prompt}\nLaRa says:')),
        ])
        
        full_prompt = self.prompt_cache.assemble_prompt(segments)
        perf.end_timer("prompt_build")
        perf.set_metric("segment_hashes", dict(self.prompt_cache._cache.items()))
        perf.set_metric("cache_report", self.prompt_cache.get_cache_report())
        
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
            "keep_alive": self._keep_alive,
            "options": {
                "temperature": self._temperature,
                "top_p": self._top_p,
                "top_k": self._top_k,
                "num_ctx": self._num_ctx,
                "num_predict": max_tokens,
                "stop": ["User:"]  # Only stop on dialogue turn markers
            }
        }
        
        try:
            perf.start_timer("inference")
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
                        perf.end_timer("inference")
                        perf.set_metric("token_count_prompt", chunk.get("prompt_eval_count", 0))
                        perf.set_metric("token_count_response", chunk.get("eval_count", 0))
                        break
            
            logging.info(f"Interaction - User: {prompt} | LaRa: {full_response}")
            
            # Store turn in            # Append to history
            self.conversation_history.append({
                "user": prompt,
                "lara": full_response[:self.MAX_TURN_CHARS],
            })
            
            # HPC SAFETY LIMIT: Cap history sliding window to 10 turns
            MAX_HISTORY_TURNS = 10
            if len(self.conversation_history) > MAX_HISTORY_TURNS:
                self.conversation_history = self.conversation_history[-MAX_HISTORY_TURNS:]
            
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
            "keep_alive": self._keep_alive,
            "options": {"temperature": self._temperature, "num_ctx": self._num_ctx}
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
        Processes an audio file through the Whisper.cpp pipeline.
        Extracts clean text securely, prioritizing emotional safety and low latency.
         Streams the LLM response back.
        """
        if not self.setup_audio_pipeline(): # Changed initialize_audio_pipeline to setup_audio_pipeline
            # Safe Fallback: gentle response if audio system fails
            yield "There is a problem hearing your voice. Let us type for now."
            return
            
        try:
            print(f"Listening nicely to {audio_file_path}...")
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

# --- SINGLETON LLM SERVICE ---
class LLMService:
    _instance = None
    
    def __init__(self):
        if LLMService._instance is not None:
            raise RuntimeError("LLMService is a singleton. Use LLMService.get()")
            
        logging.info("[LLMService] Initializing AgentricAI subsystem...")
        self.model = AgentricAI()
        LLMService._instance = self

    @staticmethod
    def get() -> AgentricAI:
        if LLMService._instance is None:
            LLMService()
        return LLMService._instance.model

if __name__ == "__main__":
    agent = AgentricAI()
    for chunk in agent.generate_response_stream("Hello, I am happy!"):
        print(chunk, end="", flush=True)
    print()