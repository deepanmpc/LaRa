"""
LaRa Vision Perception — FastAPI Entrypoint
Run: uvicorn app:app --host 0.0.0.0 --port 8001
Test: python app.py --test
"""

import argparse
import asyncio
import sys
import time
import os

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add vision_perception root to path so relative imports work
sys.path.insert(0, os.path.dirname(__file__))

from core.engine import PerceptionEngine
from core.state import perception_state, EngineState
from config import vision_config
from utils.logger import get_logger

log = get_logger(__name__)

# ── App & CORS ───────────────────────────────────────────────
app = FastAPI(
    title="LaRa Vision Perception",
    description="Independent vision microservice for the LaRa learning companion system.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module-level engine instance (single per process)
_engine: PerceptionEngine = PerceptionEngine()


# ── Lifecycle ────────────────────────────────────────────────
@app.on_event("shutdown")
async def _on_shutdown():
    if perception_state.is_running():
        log.info("FastAPI shutdown — stopping PerceptionEngine")
        _engine.stop()


# ── Routes ───────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Liveness probe."""
    return {"status": "ok", "service": "lara-vision-perception"}


@app.get("/status")
async def status():
    """Returns engine state, FPS, and memory usage."""
    proc = psutil.Process()
    mem_mb = round(proc.memory_info().rss / 1_048_576, 1)
    over_limit = mem_mb > vision_config.MAX_MEMORY_MB

    return {
        "state":    perception_state.engine_state.value,
        "fps":      perception_state.fps,
        "memory_mb": mem_mb,
        "memory_warning": over_limit,
        "error":    perception_state.error_message or None,
    }


@app.post("/start")
async def start():
    """Opens camera and starts the perception pipeline."""
    if perception_state.is_running():
        return {"status": "already_running", "state": perception_state.engine_state.value}

    try:
        # Run in thread pool so FastAPI event loop is not blocked
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
    return perception_state.latest


# ── Test Mode (CLI) ──────────────────────────────────────────

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
            output = perception_state.latest
            output["_fps"] = perception_state.fps
            print(json.dumps(output, indent=2))
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        _engine.stop()
        print("Engine stopped cleanly.")


# ── Entrypoint ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaRa Vision Perception Service")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode: camera + pipeline + log output (no API server)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="API host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001, help="API port (default: 8001)")
    args = parser.parse_args()

    if args.test:
        _run_test_mode()
    else:
        uvicorn.run("app:app", host=args.host, port=args.port, reload=False, log_level="warning")
