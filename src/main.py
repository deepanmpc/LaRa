"""
LaRa Main Entrypoint

On boot:
  1. Initializes runtime directories and logging.
  2. Loads config.
  3. Initializes all ML singletons (STT, TTS, LLM) — heavy, one-time cost.
  4. Starts the WebSocket bridge (ws://localhost:8765).
  5. Registers session_start / session_stop callbacks on the bridge.
  6. WAITS — the pipeline does NOT start until the UI sends {"type":"session_start"}.

Usage:
    python3 src/main.py

Or after setup.py install:
    lara
"""

import sys
import os
import signal
import logging
import threading

# Ensure project root is on path
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

# ── Step 1: Load config FIRST ──────────────────────────────────────────────────
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

# ── Graceful shutdown handler ──────────────────────────────────────────────────
def _handle_signal(sig, frame):
    logging.info(f"[Main] Signal {sig} received — shutting down gracefully...")
    print("\n[LaRa] Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT,  _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ── Pipeline session control ───────────────────────────────────────────────────

# A threading Event that the bridge flips when session_start arrives from the UI.
_session_start_event = threading.Event()
_pipeline_thread: threading.Thread = None


def _start_pipeline():
    """
    Called by the WS bridge when the UI sends {"type": "session_start"}.
    Runs in a daemon thread — does NOT block the WS server.
    """
    global _pipeline_thread

    logging.info("[Main] session_start received — launching conversation loop")
    print("\n[LaRa] Session started by UI ▶")

    try:
        from src.perception.speech_to_text import run_conversation_loop
        from src.bridge.ws_server import LaRaBridge
        bridge = LaRaBridge.get()
        run_conversation_loop(bridge=bridge)
    except Exception as e:
        logging.error(f"[Main] Pipeline error: {e}", exc_info=True)
        print(f"[LaRa] Pipeline error: {e}")
    finally:
        from src.bridge.ws_server import LaRaBridge
        LaRaBridge.get().mark_session_ended()
        logging.info("[Main] Conversation loop ended — ready for next session")
        print("\n[LaRa] Session ended. Ready for next session.")


def _stop_pipeline():
    """
    Called by the WS bridge when the UI sends {"type": "session_stop"}.
    Signals the conversation loop to exit cleanly.
    """
    logging.info("[Main] session_stop received — stopping pipeline")
    print("\n[LaRa] Session stopped by UI ■")
    # The run_conversation_loop checks a global flag; raise KeyboardInterrupt
    # via thread interrupt to unblock blocking I/O in the loop.
    if _pipeline_thread and _pipeline_thread.is_alive():
        import ctypes
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(_pipeline_thread.ident),
            ctypes.py_object(KeyboardInterrupt),
        )


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n\033[96m============================================================\033[0m")
    print("\033[96m        LaRa — Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("\033[96m        Model: AgentricAi/AgentricAI_TLM:latest\033[0m")
    print("\033[96m        Pipeline: GATED — starts on UI session_start\033[0m")
    print("\033[96m============================================================\033[0m\n")

    # 1. Pre-init runtime directories
    import src.core.runtime_paths as rp
    rp.initialize()

    # 2. Configure loggers (already called above, safe to call again)
    setup_logging()

    # 3. Load heavy ML components
    import time
    t0 = time.time()
    try:
        from src.system.bootstrap import initialize as initialize_system
    except ImportError as e:
        logging.error(f"[Main] Could not load system bootstrap: {e}")
        sys.exit(1)

    print("\033[93m[System Boot]\033[0m Initializing neural services (STT, TTS, LLM)…")
    try:
        initialize_system()
        print(f"\033[93m[System Boot]\033[0m Complete in {time.time() - t0:.2f}s\n")
    except Exception as e:
        logging.critical(f"[System Boot] Fatal initialization error: {e}")
        sys.exit(1)

    # 4. Start WebSocket bridge
    try:
        from src.bridge.ws_server import LaRaBridge
        bridge = LaRaBridge.get()

        # Register callbacks — pipeline starts ONLY when UI sends session_start
        bridge.on_session_start(_start_pipeline)
        bridge.on_session_stop(_stop_pipeline)

        bridge.start()
        print("\033[93m[System Boot]\033[0m WebSocket bridge started on ws://localhost:8765")
    except Exception as e:
        logging.warning(f"[Main] WebSocket bridge failed to start: {e} — continuing without UI bridge")

    print("\n\033[92m[LaRa] Ready. Open the dashboard and click 'Start Session'.\033[0m\n")

    # 5. Keep main thread alive — everything else is in daemon threads
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[LaRa] Shutdown requested. Goodbye.")
        sys.exit(0)