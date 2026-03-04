"""
LaRa Startup Bootstrap
Centralized initialization for model singletons.
"""

import os
import logging
from src.utils.gpu_manager import configure_gpu

def initialize():
    """
    Boots up the system, ensuring models are loaded identically across roles.
    Checks the LARA_ROLE environment variable to disable unused models in
    distributed / multi-service topologies.
    """
    logging.info("[Bootstrap] Starting LaRa initialization sequence...")
    
    # Secure GPU environment variables
    configure_gpu()
    
    # Identify deployment role (default to "all")
    role = os.getenv("LARA_ROLE", "all").lower()
    logging.info(f"[Bootstrap] Detected LARA_ROLE: {role}")

    # Load resources conditionally based on Role
    if role in ("all", "speech"):
        logging.info("[Bootstrap] Initializing Speech singletons...")
        from src.perception.speech_to_text import STTService
        STTService.get()
        
        from src.tts.kokoro_TTS import TTSService
        TTSService.get()
        
    if role in ("all", "dialogue"):
        logging.info("[Bootstrap] Initializing LLM singletons...")
        from src.llm.AgentricTLM import LLMService
        LLMService.get()
        
    logging.info("[Bootstrap] Initialization sequence complete.")
