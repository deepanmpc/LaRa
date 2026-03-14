"""
LaRa WebSocket Bridge Server
Runs in a background thread. Accepts browser clients.

Changes vs. original:
  - Handler now reads incoming messages instead of ignoring them.
  - Supports two commands from the UI:
        {"type": "session_start"}  → triggers _on_session_start()
        {"type": "session_stop"}   → triggers _on_session_stop()
  - Registered callbacks are invoked in a separate daemon thread so the
    async WS loop is never blocked.
  - Pipeline calls LaRaBridge.emit(event_type, payload) from any thread
    (unchanged API).
"""

import asyncio
import json
import logging
import threading
from typing import Callable, Optional

import websockets

log = logging.getLogger(__name__)

WS_HOST = "0.0.0.0"
WS_PORT = 8765


class LaRaBridge:
    """
    Singleton WebSocket server.

    Thread-safe emit()  — called from the pipeline thread → pushes to UI.
    on_session_start()  — register a callback invoked when UI sends session_start.
    on_session_stop()   — register a callback invoked when UI sends session_stop.
    """

    _instance: Optional["LaRaBridge"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._clients: set = set()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        # Registered pipeline callbacks
        self._start_callback: Optional[Callable] = None
        self._stop_callback:  Optional[Callable] = None

        # Guard: prevent double-starting the pipeline
        self._session_active = False
        self._cb_lock = threading.Lock()

    # ── Singleton ─────────────────────────────────────────────────────────────

    @classmethod
    def get(cls) -> "LaRaBridge":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = LaRaBridge()
        return cls._instance

    # ── Callback registration ─────────────────────────────────────────────────

    def on_session_start(self, callback: Callable):
        """Register the function to call when UI sends session_start."""
        self._start_callback = callback
        log.info("[Bridge] session_start callback registered")

    def on_session_stop(self, callback: Callable):
        """Register the function to call when UI sends session_stop."""
        self._stop_callback = callback
        log.info("[Bridge] session_stop callback registered")

    # ── Server lifecycle ──────────────────────────────────────────────────────

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

    # ── Connection handler ────────────────────────────────────────────────────

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
            # Send initial resting state so UI can render immediately
            await websocket.send(json.dumps({
                "type": "system_state",
                "mode": "resting",
                "turn_count": 0,
                "difficulty": 2,
            }))

            # ── Read loop — now active, not ignored ───────────────────────────
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    log.warning(f"[Bridge] Non-JSON message ignored: {raw!r}")
                    continue

                msg_type = msg.get("type")
                log.info(f"[Bridge] ← received: {msg_type}")

                if msg_type == "session_start":
                    await self._handle_session_start(websocket)

                elif msg_type == "session_stop":
                    await self._handle_session_stop(websocket)

                else:
                    log.debug(f"[Bridge] Unknown command ignored: {msg_type}")

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            log.info("[Bridge] Client disconnected")

    # ── Command handlers ──────────────────────────────────────────────────────

    async def _handle_session_start(self, websocket):
        with self._cb_lock:
            if self._session_active:
                await websocket.send(json.dumps({
                    "type": "session_ack",
                    "status": "already_running",
                }))
                return

            self._session_active = True

        await websocket.send(json.dumps({
            "type": "session_ack",
            "status": "starting",
        }))

        # Fire callback in a daemon thread so we don't block the WS loop
        if self._start_callback:
            t = threading.Thread(
                target=self._start_callback,
                daemon=True,
                name="lara-pipeline",
            )
            t.start()
            log.info("[Bridge] Pipeline start callback fired in background thread")
        else:
            log.warning("[Bridge] session_start received but no start callback registered")

    async def _handle_session_stop(self, websocket):
        with self._cb_lock:
            if not self._session_active:
                await websocket.send(json.dumps({
                    "type": "session_ack",
                    "status": "not_running",
                }))
                return

            self._session_active = False

        await websocket.send(json.dumps({
            "type": "session_ack",
            "status": "stopping",
        }))

        if self._stop_callback:
            threading.Thread(
                target=self._stop_callback,
                daemon=True,
                name="lara-pipeline-stop",
            ).start()
            log.info("[Bridge] Pipeline stop callback fired")
        else:
            log.warning("[Bridge] session_stop received but no stop callback registered")

    # ── Emit (pipeline → UI) ──────────────────────────────────────────────────

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

    # ── Session state reset (called by pipeline on natural end) ───────────────

    def mark_session_ended(self):
        """Call this when the conversation loop exits naturally."""
        with self._cb_lock:
            self._session_active = False
        self.emit("session_ended", {"reason": "natural_end"})
        log.info("[Bridge] Session marked as ended")