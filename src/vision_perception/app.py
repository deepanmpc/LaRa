"""
LaRa Vision Perception — FastAPI Entrypoint (v2.3)
v2.3 fixes over v2.2:

  Fix 1 – Deprecated @app.on_event("shutdown") replaced with lifespan:
    FastAPI deprecated @app.on_event() in v0.93 and removes it in v0.100+.
    The correct pattern is an asynccontextmanager lifespan function passed
    to FastAPI(lifespan=...). This silences the DeprecationWarning and
    ensures shutdown logic runs correctly on newer FastAPI/Starlette versions.

  Fix 2 – /status exposes increment_stall-compatible stall_count:
    stall_count is now fetched via the thread-safe property rather than
    direct attribute access (which was previously fine but is now routed
    through a lock in state.py v2.3).

Run: uvicorn app:app --host 0.0.0.0 --port 8001
Test: python app.py --test
"""

import argparse
import asyncio
import sys
import time
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add vision_perception root to path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

# Load CORS origins from config
_DEFAULT_CORS = ["http://localhost:5173", "http://localhost:8080"]
try:
    _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    from src.core.config_loader import CONFIG
    _cors = getattr(getattr(CONFIG, 'vision', None), 'cors_origins', None)
    _CORS_ORIGINS = _cors if _cors else _DEFAULT_CORS
except Exception:
    _CORS_ORIGINS = _DEFAULT_CORS

from core.engine import PerceptionEngine
from core.state import perception_state, EngineState
from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# Module-level engine instance (single per process)
_engine: PerceptionEngine = PerceptionEngine()


# ── FIX 1: Lifespan context manager replaces deprecated on_event ────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown lifecycle.
    Replaces @app.on_event("startup") / @app.on_event("shutdown") which are
    deprecated in FastAPI >= 0.93.
    """
    # Startup: nothing to do — engine is started explicitly via POST /start
    log.info("LaRa Vision Perception service started (lifespan context)")
    yield
    # Shutdown: stop the engine cleanly if it is still running
    if perception_state.is_running():
        log.info("FastAPI shutdown — stopping PerceptionEngine")
        _engine.stop()


# ── App & CORS ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="LaRa Vision Perception",
    description="Independent vision microservice for the LaRa learning companion system.",
    version="2.3.0",
    lifespan=lifespan,   # FIX 1: pass lifespan here
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "ok", "service": "lara-vision-perception"}


@app.get("/status")
async def status():
    """Returns engine state, FPS, memory stats, watchdog stall count, and YOLO interval."""
    mem_mb   = perception_state.sample_memory()
    over_limit = mem_mb > vision_config.MAX_MEMORY_MB

    return {
        "state":                          perception_state.engine_state.value,
        "fps":                            perception_state.fps,
        "memory_mb":                      mem_mb,
        "memory_delta_mb":                perception_state.memory_delta_mb(),
        "memory_growth_rate_mb_per_sec":  perception_state.memory_growth_rate_mb_per_sec(),
        "memory_warning":                 over_limit,
        "memory_leak_suspected":          perception_state.memory_leak_suspected(),
        "current_peak_mb":                perception_state.current_session_peak_mb,
        "peak_fragmentation_suspected":   perception_state.peak_leak_suspected(),
        # FIX 2: uses thread-safe property
        "stall_count":                    perception_state.stall_count,
        "yolo_interval":                  _engine._objects.current_interval,
        "error":                          perception_state.error_message or None,
    }


@app.post("/start")
async def start():
    """Opens camera and starts the perception pipeline."""
    if perception_state.is_running():
        return {"status": "already_running", "state": perception_state.engine_state.value}

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _engine.start)
        log.info("Engine started via /start")
        return {"status": "started", "state": perception_state.engine_state.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop")
async def stop():
    """Cleanly stops the pipeline and releases the camera."""
    if not perception_state.is_running():
        return {"status": "already_stopped"}

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _engine.stop)
    log.info("Engine stopped via /stop")
    return {"status": "stopped", "state": perception_state.engine_state.value}


@app.get("/latest")
async def latest():
    """
    Returns the last cached perception frame.
    Target response time: < 10ms (memory read only — no computation).
    """
    if not perception_state.is_running():
        raise HTTPException(
            status_code=503,
            detail="Perception engine is not running. Call POST /start first.",
        )
    return perception_state.latest.to_dict()


# ── Test Mode (CLI) ──────────────────────────────────────────────────────────

def _run_test_mode():
    """
    --test mode: starts camera, runs pipeline, prints structured output every second.
    No API server required. Press Ctrl+C to stop.
    """
    log.info("=== LaRa Vision — TEST MODE ACTIVE ===")
    import json

    try:
        _engine.start()
    except Exception as e:
        print(f"[ERROR] Failed to start engine: {e}")
        sys.exit(1)

    print("Pipeline running. Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(vision_config.TEST_MODE_LOG_INTERVAL)
            output_dict = perception_state.latest.to_dict()
            output_dict["_fps"] = perception_state.fps
            output_dict["_yolo_interval"] = _engine._objects.current_interval
            print(json.dumps(output_dict, indent=2))
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        _engine.stop()
        print("Engine stopped cleanly.")


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaRa Vision Perception Service")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode: camera + pipeline + log output (no API server)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="API host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8001, help="API port (default: 8001)")
    args = parser.parse_args()

    if args.test:
        _run_test_mode()
    else:
        uvicorn.run("app:app", host=args.host, port=args.port, reload=False, log_level="warning")