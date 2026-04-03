"""
LaRa Main Entrypoint — Pipeline is GATED (starts on UI session_start click)
"""

import sys
import os
import signal
import logging
import threading
import time

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

try:
    from src.core.config_loader import CONFIG
except FileNotFoundError as e:
    print(f"[LaRa] FATAL: Config not found — {e}"); os._exit(1)
except Exception as e:
    print(f"[LaRa] FATAL: Config error — {e}"); os._exit(1)

try:
    from src.core.logger import setup_logging
    setup_logging()
except Exception as e:
    print(f"[LaRa] FATAL: Logging failed — {e}"); os._exit(1)

_shutdown_requested = False

def _handle_signal(sig, frame):
    global _shutdown_requested
    if _shutdown_requested:
        return
    _shutdown_requested = True
    print("\n[LaRa] Shutting down…")
    os._exit(0)   # bypass Python atexit/threading cleanup — no spurious traceback

signal.signal(signal.SIGINT,  _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)

_session_lock = threading.Lock()
_session_active = False
_current_session = None

def _start_pipeline(child_id=None, session_uuid=None):
    """Fired by WS bridge on session_start. Runs in daemon thread named 'lara-pipeline'."""
    global _session_active, _current_session
    
    with _session_lock:
        if _session_active:
            logging.warning("[Main] session_start ignored — session already active")
            return
        _session_active = True
        
    logging.info(f"[Main] session_start received for child {child_id} — launching conversation loop")
    print(f"\n[LaRa] Session started for child {child_id} ▶")

    session_obj = None
    try:
        from src.session.session_state import SessionState
        from src.perception.speech_to_text import run_conversation_loop
        from src.bridge.ws_server import LaRaBridge
        from src.vision.vision_bridge import VisionBridgeService

        session_obj = SessionState()
        if child_id: session_obj.child_id = child_id
        if session_uuid: session_obj.session_uuid = session_uuid
        _current_session = session_obj

        bridge = LaRaBridge.get()
        vision = VisionBridgeService.get()
        vision.start_vision_service()
        vision.start_polling(bridge=bridge, session=session_obj, interval_s=0.5)

        run_conversation_loop(
            bridge=bridge,
            skip_wake_word=True,
            session=session_obj,
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"[Main] Pipeline error: {e}", exc_info=True)
        print(f"[LaRa] Pipeline error: {e}")
    finally:
        try:
            from src.vision.vision_bridge import VisionBridgeService
            vision = VisionBridgeService.get()
            
            if session_obj:
                vision.flush_vision_analytics(
                    child_id=session_obj.child_id,
                    session_uuid=session_obj.session_uuid
                )
                
            vision.stop_polling()
            vision.stop_vision_service()
        except Exception:
            pass

        # Flush final session state to disk before clearing
        if session_obj is not None and hasattr(session_obj, 'flush_to_disk'):
            try:
                session_obj.flush_to_disk()
            except Exception as e:
                logging.warning(f"[Main] Session flush failed: {e}")

        with _session_lock:
            _session_active = False
            _current_session = None

        try:
            from src.bridge.ws_server import LaRaBridge
            LaRaBridge.get().mark_session_ended()
        except Exception:
            pass
        print("\n[LaRa] Session ended. Ready for next session.")


def _stop_pipeline():
    """Fired by WS bridge on session_stop. Raises KeyboardInterrupt in pipeline thread."""
    global _session_active, _current_session
    
    with _session_lock:
        if not _session_active:
            logging.warning("[Main] session_stop ignored — no active session")
            return
        _session_active = False
        
    logging.info("[Main] session_stop received")
    print("\n[LaRa] Session stopped by UI ■")

    # Find the thread by its registered name
    target = next((t for t in threading.enumerate() if t.name == "lara-pipeline"), None)

    if target and target.is_alive():
        import ctypes
        result = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_ulong(target.ident),
            ctypes.py_object(KeyboardInterrupt),
        )
        if result == 0:
            logging.warning("[Main] stop: thread not found via ctypes")
        elif result > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(target.ident), None)
        else:
            logging.info("[Main] KeyboardInterrupt injected into pipeline thread")
    else:
        logging.warning("[Main] stop: no active lara-pipeline thread found")
        try:
            from src.bridge.ws_server import LaRaBridge
            LaRaBridge.get().mark_session_ended()
        except Exception:
            pass

    try:
        from src.vision.vision_bridge import VisionBridgeService
        vision = VisionBridgeService.get()
        
        # Flush analytics if session is active
        if _current_session:
            vision.flush_vision_analytics(
                child_id=_current_session.child_id,
                session_uuid=_current_session.session_uuid
            )
            
        vision.stop_polling()
        vision.stop_vision_service()
    except Exception as e:
        logging.warning(f"[Main] Failed to stop vision service cleanly: {e}")

    _current_session = None


if __name__ == "__main__":
    print("\n\033[96m============================================================\033[0m")
    print("\033[96m        LaRa — Low-Cost Adaptive Robotic-AI Assistant\033[0m")
    print("\033[96m        Pipeline: GATED — starts on UI session_start click\033[0m")
    print("\033[96m============================================================\033[0m\n")

    try:
        import src.core.runtime_paths as rp; rp.initialize()
    except Exception as e:
        print(f"[LaRa] WARNING: runtime dirs — {e}")

    t0 = time.time()
    try:
        from src.system.bootstrap import initialize as initialize_system
    except ImportError as e:
        print(f"[LaRa] FATAL: bootstrap import failed — {e}"); os._exit(1)

    print("\033[93m[System Boot]\033[0m Initializing neural services (STT, TTS, LLM)…")
    try:
        initialize_system()
        print(f"\033[93m[System Boot]\033[0m Complete in {time.time() - t0:.2f}s\n")
    except Exception as e:
        print(f"[LaRa] FATAL: Initialization failed — {e}")
        logging.critical(f"[System Boot] Fatal: {e}", exc_info=True)
        os._exit(1)

    try:
        from src.bridge.ws_server import LaRaBridge
        bridge = LaRaBridge.get()
        bridge.on_session_start(_start_pipeline)
        bridge.on_session_stop(_stop_pipeline)
        bridge.start()
        print("\033[93m[System Boot]\033[0m WebSocket bridge started on ws://localhost:8765")
    except Exception as e:
        logging.warning(f"[Main] WS bridge failed: {e}")

    print("\n\033[92m[LaRa] Ready. Open the dashboard and click 'Start Session'.\033[0m\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[LaRa] Goodbye.")
        os._exit(0)
