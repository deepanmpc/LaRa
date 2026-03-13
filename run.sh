#!/usr/bin/env bash
# LaRa — Unified System Startup Script
# Starts Backend, Frontend, Vision, and Voice Pipeline.

set -e

# Change to root directory
cd "$(dirname "$0")"
ROOT_DIR=$(pwd)

echo -e "\033[96m"
echo "============================================================"
echo "        LaRa — Unified System Startup"
echo "============================================================"
echo -e "\033[0m"

# 1. Environment Check
if [ -d ".venv" ]; then
    echo "[Env] Activating Python 3.11 virtual environment..."
    source .venv/bin/activate
else
    echo "[Warning] .venv not found. Using system Python."
fi

# Function to kill background processes on exit
cleanup() {
    echo -e "\n\033[93m[System] Shutting down all services...\033[0m"
    # Kill the process group to ensure all background tasks are stopped
    trap - SIGINT SIGTERM # avoid infinite loop
    kill 0
}

trap cleanup SIGINT SIGTERM EXIT

# 2. Start Vision Perception Microservice (Port 8001)
echo "[Vision] Starting Perception service on port 8001..."
cd "$ROOT_DIR/src/vision_perception"
uvicorn app:app --host 0.0.0.0 --port 8001 > "$ROOT_DIR/runtime/vision.log" 2>&1 &
VISION_PID=$!

# 3. Start Dashboard Backend (Port 8080)
echo "[Backend] Starting Spring Boot service on port 8080..."
cd "$ROOT_DIR/dashboard/backend"
./run.sh > "$ROOT_DIR/runtime/backend.log" 2>&1 &
BACKEND_PID=$!

# 4. Start Dashboard Frontend (Port 5173)
echo "[Frontend] Starting React dev server on port 5173..."
cd "$ROOT_DIR/dashboard/frontend"
npm run dev -- --host > "$ROOT_DIR/runtime/frontend.log" 2>&1 &
FRONTEND_PID=$!

# Allow services a moment to warm up
echo "[System] Services starting in background. Tailing logs to 'runtime/*.log'..."
sleep 2

# 5. Start LaRa Voice Pipeline (Foreground / Interactive)
echo -e "\n\033[92m[Pipeline] Starting LaRa Voice Pipeline (Interactive)\033[0m"
cd "$ROOT_DIR"
python3 src/main.py
