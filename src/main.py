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
setup_logging(log_dir=os.path.join(_ROOT_DIR, 'data'))

# ── Step 3: Import everything else after logging is ready ──────────────────────
try:
    from src.perception.whispercpp_STT import run_conversation_loop
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
    run()
