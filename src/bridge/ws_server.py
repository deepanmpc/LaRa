"""
LaRa WebSocket Bridge Server
Runs in a background thread. Accepts browser clients.
Pipeline calls LaRaBridge.emit(event_type, payload) from any thread.
"""

import asyncio
import json
import logging
import threading
from typing import Optional

import websockets

log = logging.getLogger(__name__)

WS_HOST = "0.0.0.0"
WS_PORT = 8765


class LaRaBridge:
    """
    Singleton WebSocket server.
    Thread-safe emit() called from the conversation loop.
    """
    _instance: Optional["LaRaBridge"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._clients: set = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._server = None

    @classmethod
    def get(cls) -> "LaRaBridge":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = LaRaBridge()
        return cls._instance

    def start(self):
        """Start the WebSocket server in a daemon thread."""
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="lara-ws-bridge"
        )
        self._thread.start()
        log.info(f"[Bridge] WebSocket server starting on ws://{WS_HOST}:{WS_PORT}")

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        async with websockets.serve(self._handler, WS_HOST, WS_PORT):
            log.info(f"[Bridge] WebSocket server listening on ws://{WS_HOST}:{WS_PORT}")
            await asyncio.Future()  # run forever

    async def _handler(self, websocket):
        # Origin check — only allow known dev origins
        allowed_origins = {"http://localhost:5173", "http://localhost:3000"}
        origin = websocket.request_headers.get("Origin", "")
        if origin and origin not in allowed_origins:
            await websocket.close(1008, "Origin not allowed")
            return

        self._clients.add(websocket)
        log.info(f"[Bridge] Client connected: {websocket.remote_address}")
        try:
            # Send initial state so UI can render immediately
            await websocket.send(json.dumps({
                "type": "system_state",
                "mode": "resting",
                "turn_count": 0,
                "difficulty": 2,
            }))
            # Keep connection open — we only push, never pull
            async for _ in websocket:
                pass  # Ignore any incoming messages (UI is read-only)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            log.info("[Bridge] Client disconnected")

    def emit(self, event_type: str, payload: dict):
        """
        Thread-safe event emission from the pipeline.
        Called from the conversation loop thread.
        """
        if not self._loop or not self._clients:
            return
        message = json.dumps({"type": event_type, **payload})
        asyncio.run_coroutine_threadsafe(
            self._broadcast(message), self._loop
        )

    async def _broadcast(self, message: str):
        dead = set()
        for ws in self._clients:
            try:
                await ws.send(message)
            except Exception:
                dead.add(ws)
        self._clients -= dead
