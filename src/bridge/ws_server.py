"""
LaRa WebSocket Bridge Server

Key points:
  - origins=None on websockets.serve() disables the library's built-in
    origin rejection (which caused "connection handler failed" spam).
  - Manual origin check in _handler still rejects non-localhost IPs.
  - Supports session_start / session_stop commands from the UI.
  - emit() pushes events from the pipeline to all connected browsers.
"""

import asyncio
import json
import logging
import threading
from typing import Callable, Optional
from urllib.parse import urlparse

import websockets

log = logging.getLogger(__name__)

WS_HOST = "0.0.0.0"
WS_PORT = 8765


class LaRaBridge:
    _instance: Optional["LaRaBridge"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._clients: set = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._start_callback: Optional[Callable] = None
        self._stop_callback:  Optional[Callable] = None
        self._session_active = False
        self._cb_lock = threading.Lock()

    @classmethod
    def get(cls) -> "LaRaBridge":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = LaRaBridge()
        return cls._instance

    def on_session_start(self, callback: Callable):
        self._start_callback = callback
        log.info("[Bridge] session_start callback registered")

    def on_session_stop(self, callback: Callable):
        self._stop_callback = callback
        log.info("[Bridge] session_stop callback registered")

    def start(self):
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True, name="lara-ws-bridge"
        )
        self._thread.start()
        log.info(f"[Bridge] Starting on ws://{WS_HOST}:{WS_PORT}")

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self):
        # origins=None disables websockets' built-in origin check entirely.
        # We do our own check inside _handler.
        async with websockets.serve(self._handler, WS_HOST, WS_PORT, origins=None):
            log.info(f"[Bridge] Listening on ws://{WS_HOST}:{WS_PORT}")
            await asyncio.Future()

    async def _handler(self, websocket):
        # Manual origin check — allow localhost only, block external IPs
        try:
            origin = websocket.request.headers.get("Origin", "")
        except AttributeError:
            # Older websockets API
            origin = getattr(websocket, "request_headers", {}).get("Origin", "")

        if origin:
            host = urlparse(origin).hostname or ""
            # Strict allowed hosts for local development
            if host not in ("localhost", "127.0.0.1"):
                log.warning(f"[Bridge] Security Alert: Rejected external origin '{origin}' from {websocket.remote_address}")
                await websocket.close(1008, "Origin not allowed")
                return
        else:
            # Reject clients with no Origin header (prevent non-browser bypass)
            log.warning(f"[Bridge] Rejected client with no Origin header from {websocket.remote_address}")
            await websocket.close(1008, "Origin required")
            return

        self._clients.add(websocket)
        log.info(f"[Bridge] Client connected: {websocket.remote_address}")

        try:
            # Send initial resting state
            await websocket.send(json.dumps({
                "type": "system_state",
                "mode": "resting",
                "turn_count": 0,
                "difficulty": 2,
            }))

            # Set a moderate message size limit (10KB is plenty for commands)
            max_size = 10 * 1024 
            
            async for raw in websocket:
                if len(raw) > max_size:
                    log.warning(f"[Bridge] Rejected oversized message ({len(raw)} bytes)")
                    continue

                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    log.debug("[Bridge] Malformed JSON received")
                    continue

                if not isinstance(msg, dict):
                    continue

                msg_type = msg.get("type")
                
                # Strict command validation
                if msg_type == "session_start":
                    log.info(f"[Bridge] <- session_start")
                    await self._handle_session_start(websocket)
                elif msg_type == "session_stop":
                    log.info(f"[Bridge] <- session_stop")
                    await self._handle_session_stop(websocket)
                else:
                    log.debug(f"[Bridge] Ignored unknown/invalid command type: {msg_type}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            log.info("[Bridge] Client disconnected")

    async def _handle_session_start(self, websocket):
        with self._cb_lock:
            if self._session_active:
                await websocket.send(json.dumps({"type": "session_ack", "status": "already_running"}))
                return
            self._session_active = True

        await websocket.send(json.dumps({"type": "session_ack", "status": "starting"}))

        if self._start_callback:
            threading.Thread(
                target=self._start_callback,
                daemon=True,
                name="lara-pipeline",   # name must match what _stop_pipeline searches for
            ).start()
            log.info("[Bridge] Pipeline start callback fired")
        else:
            log.warning("[Bridge] session_start: no callback registered")

    async def _handle_session_stop(self, websocket):
        with self._cb_lock:
            if not self._session_active:
                await websocket.send(json.dumps({"type": "session_ack", "status": "not_running"}))
                return
            self._session_active = False

        await websocket.send(json.dumps({"type": "session_ack", "status": "stopping"}))

        if self._stop_callback:
            threading.Thread(
                target=self._stop_callback,
                daemon=True,
                name="lara-pipeline-stop",
            ).start()
            log.info("[Bridge] Pipeline stop callback fired")
        else:
            log.warning("[Bridge] session_stop: no callback registered")

    def emit(self, event_type: str, payload: dict):
        if not self._loop or not self._clients:
            return
        
        # Explicit serialization to prevent payload from overwriting 'type'
        # and ensure no unexpected keys are leaked
        safe_msg = {"type": event_type}
        if isinstance(payload, dict):
            for k, v in payload.items():
                if k != "type": # Prevent 'type' injection
                    safe_msg[k] = v

        message = json.dumps(safe_msg)
        asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)

    async def _broadcast(self, message: str):
        dead = set()
        for ws in self._clients:
            try:
                await ws.send(message)
            except Exception:
                dead.add(ws)
        self._clients -= dead

    def mark_session_ended(self):
        with self._cb_lock:
            self._session_active = False
        self.emit("session_ended", {"reason": "natural_end"})
        log.info("[Bridge] Session marked as ended")