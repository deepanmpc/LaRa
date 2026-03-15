#!/usr/bin/env bash
# =============================================================================
#  LaRa — Unified Launcher
#  Starts all four services:
#    1. Python pipeline  (src/main.py          → ws://localhost:8765)
#    2. Vision API       (src/vision_perception → http://localhost:8001)
#    3. Dashboard backend (Spring Boot          → http://localhost:8080)
#    4. Dashboard frontend (Vite               → http://localhost:5173)
#
#  Usage:  ./run.sh
#  Stop:   Ctrl+C  (all child processes are cleaned up automatically)
# =============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

log()  { echo -e "${CYAN}[LaRa]${RESET} $*"; }
ok()   { echo -e "${GREEN}[✓]${RESET} $*"; }
warn() { echo -e "${YELLOW}[!]${RESET} $*"; }
err()  { echo -e "${RED}[✗]${RESET} $*"; }

# ── PID tracking (for clean shutdown) ────────────────────────────────────────
PIDS=()

cleanup() {
    echo ""
    log "Shutting down all LaRa services…"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && ok "Stopped PID $pid"
        fi
    done
    log "All services stopped. Goodbye."
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── Prerequisite checks ───────────────────────────────────────────────────────
check_cmd() {
    command -v "$1" &>/dev/null || { err "Required command not found: $1"; exit 1; }
}

check_cmd python3
check_cmd node
check_cmd npm
check_cmd mvn
check_cmd java

echo ""
echo -e "${BOLD}${CYAN}============================================================${RESET}"
echo -e "${BOLD}${CYAN}         LaRa — Low-Cost Adaptive Robotic-AI System         ${RESET}"
echo -e "${BOLD}${CYAN}============================================================${RESET}"
echo ""

# ── 1. Python virtual environment ─────────────────────────────────────────────
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    ok "Python venv activated"
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    ok "Python venv activated"
else
    warn "No .venv found — using system Python. Consider: python3 -m venv .venv && pip install -r requirements.txt"
fi

# ── 2. LaRa Python Pipeline (src/main.py) ─────────────────────────────────────
# Pipeline boots all singletons and starts the WebSocket bridge.
# The conversation loop is GATED — it only starts when the UI sends session_start.
log "Starting Python pipeline (ws://localhost:8765)…"
python3 src/main.py >> runtime/logs/pipeline.log 2>&1 &
PIPELINE_PID=$!
PIDS+=($PIPELINE_PID)
ok "Pipeline started (PID $PIPELINE_PID)"

# Give the WS bridge a moment to bind
sleep 2

# ── 3. Vision Perception API (FastAPI) ────────────────────────────────────────
log "Starting Vision Perception API (http://localhost:8001)…"
(
    cd src/vision_perception
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    python3 -m uvicorn app:app --host 127.0.0.1 --port 8001 --log-level warning
) >> runtime/logs/vision_api.log 2>&1 &
VISION_PID=$!
PIDS+=($VISION_PID)
ok "Vision API started (PID $VISION_PID)"

# ── 4. Dashboard Backend (Spring Boot) ────────────────────────────────────────
log "Starting Dashboard Backend (http://localhost:8080)…"
(
    cd dashboard/backend
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    export JAVA_HOME=$(java -XshowSettings:properties -version 2>&1 | grep "java.home" | awk '{print $3}')
    mvn -q spring-boot:run
) >> runtime/logs/backend.log 2>&1 &
BACKEND_PID=$!
PIDS+=($BACKEND_PID)
ok "Backend started (PID $BACKEND_PID)"

# ── 5. Dashboard Frontend (Vite) ──────────────────────────────────────────────
log "Starting Dashboard Frontend (http://localhost:5173)…"
(
    cd dashboard/frontend
    npm install --silent
    npm run dev
) >> runtime/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
PIDS+=($FRONTEND_PID)
ok "Frontend started (PID $FRONTEND_PID)"

# ── Ready ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}All LaRa services are running:${RESET}"
echo -e "  ${CYAN}Frontend  ${RESET}→  http://localhost:5173"
echo -e "  ${CYAN}Backend   ${RESET}→  http://localhost:8080"
echo -e "  ${CYAN}Vision API${RESET}→  http://localhost:8001"
echo -e "  ${CYAN}WS Bridge ${RESET}→  ws://localhost:8765"
echo ""
echo -e "${YELLOW}Logs:${RESET} runtime/logs/*.log"
echo -e "${YELLOW}Stop:${RESET} Press Ctrl+C"
echo ""

# ── Wait for all children ─────────────────────────────────────────────────────
wait