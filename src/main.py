"""
LaRa Main Entrypoint
Clean application runner that initializes all components and starts the
conversation loop. Replaces running whispercpp_STT.py directly.

Usage:
    python3 src/main.py
    
Or with the CLI entry point (after setup.py install):
    lara
"""

import sys
import os
import signal
import logging

# Ensure project root is on path so `import src.something` works
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

# ── Step 1: Load config FIRST (before anything else) ──────────────────────────
try:
    from src.core.config_loader import CONFIG
except FileNotFoundError as e:
    print(f"[LaRa] FATAL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[LaRa] FATAL: Config error — {e}")
    sys.exit(1)

# ── Step 2: Setup structured logging ──────────────────────────────────────────
from src.core.logger import setup_logging
setup_logging()

# ── Step 3: Import everything else after logging is ready ──────────────────────
try:
    from src.system.bootstrap import initialize as initialize_system
    from src.perception.speech_to_text import run_conversation_loop
except ImportError as e:
    logging.error(f"[Main] Could not import conversation loop: {e}")
    sys.exit(1)


# ── Graceful shutdown handler ──────────────────────────────────────────────────
_running = True

def _handle_signal(sig, frame):
    global _running
    logging.info(f"[Main] Signal {sig} received — shutting down gracefully...")
    print("\n[LaRa] Shutting down...")
    _running = False
    sys.exit(0)

signal.signal(signal.SIGINT,  _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ── Entrypoint ─────────────────────────────────────────────────────────────────
def setup_logging():
    """Configure system and interaction loggers."""
    from src.core.runtime_paths import get_log_path
    from src.core.constants import SYSTEM_LOG, INTERACTION_LOG, LOG_LEVEL
    
    # 1. Root logger (System errors)
    sys_log = get_log_path(SYSTEM_LOG)
    logging.basicConfig(
        filename=sys_log,
        level=LOG_LEVEL,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 2. Add an explicit StreamHandler so users see warnings on console natively
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)
    
    # 3. Dedicated logger for conversational interactions
    int_log = get_log_path(INTERACTION_LOG)
    interact_logger = logging.getLogger("InteractionLog")
    interact_logger.setLevel(logging.INFO)
    fh = logging.FileHandler(int_log, encoding="utf-8")
    fh.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    interact_logger.addHandler(fh)
    
    logging.info("=" * 60)
    logging.info("LaRa System Boot Sequence Started")
    logging.info("=" * 60)

def run():
    """Main entrypoint — called by CLI script or directly."""
    logging.info(
        f"[Main] LaRa starting | "
        f"model={CONFIG.llm.model_name} | "
        f"user={CONFIG.app.user_id} | "
        f"wake_word={CONFIG.app.wake_word}"
    )

    print("=" * 60)
    print("        \033[95mLaRa — Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print(f"        Model: {CONFIG.llm.model_name}")
    print(f"        Wake word: '{CONFIG.app.wake_word}'")
    print("=" * 60)

    try:
        # The system initialization and heavy imports are now handled in __main__
        # This function primarily runs the conversation loop.
        from src.perception.speech_to_text import run_conversation_loop
        run_conversation_loop()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"[Main] Unexpected error: {e}", exc_info=True)
        print(f"\n[LaRa] Unexpected error: {e}")
        sys.exit(1)
    finally:
        logging.info("[Main] LaRa session ended.")
        print("\n[LaRa] Session ended. Goodbye.")


if __name__ == "__main__":
    print("\n\033[96m============================================================\033[0m")
    print("\033[96m        LaRa — Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("\033[96m        Model: AgentricAi/AgentricAI_TLM:latest\033[0m")
    print("\033[96m        Wake word: 'friday'\033[0m")
    print("\033[96m============================================================\033[0m\n")

    # 1. Pre-init runtime directories required for all file I/O operations
    import src.core.runtime_paths as rp
    rp.initialize()

    # 2. Configure loggers
    setup_logging()
    
    # 3. Import heavy components (Lazy-loads CTranslate2, WhisperModel, Torch, etc.)
    import time
    t0 = time.time()
    try:
        from src.system.bootstrap import initialize as initialize_system
        # run_conversation_loop is now imported inside the run() function
    except ImportError as e:
        logging.error(f"[Main] Could not load conversational logic: {e}")
        sys.exit(1)
    
    # 4. Spin up singletons
    print("\033[93m[System Boot]\033[0m Initializing neural services (STT, TTS, LLM)...")
    try:
        initialize_system()
        print(f"\033[93m[System Boot]\033[0m Complete. Services loaded in {time.time()-t0:.2f}s\n")
    except Exception as e:
        logging.critical(f"[System Boot] Fatal initialization error: {e}")
        sys.exit(1)
    
    # 5. Run the main application loop
    run()
