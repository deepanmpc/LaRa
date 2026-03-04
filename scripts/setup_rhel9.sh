#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# LaRa — RHEL 9 + A100 Setup Script
# Run once on a fresh RHEL 9 VM with A100 GPU.
#
# Usage:
#   chmod +x scripts/setup_rhel9.sh
#   sudo ./scripts/setup_rhel9.sh
# ──────────────────────────────────────────────────────────
set -euo pipefail

echo "═══════════════════════════════════════════════════════"
echo "  LaRa — RHEL 9 + A100 Environment Setup"
echo "═══════════════════════════════════════════════════════"

# ── 1. System packages ────────────────────────────────────
echo "[1/6] Installing system packages..."
dnf install -y \
    python3.11 python3.11-pip python3.11-devel \
    gcc gcc-c++ make cmake \
    git wget curl \
    alsa-lib-devel portaudio-devel \
    mesa-libGL mesa-libGL-devel \
    sqlite sqlite-devel \
    libffi-devel openssl-devel \
    epel-release

# ── 2. CUDA Toolkit (if not already installed by cluster admin) ──
echo "[2/6] Checking CUDA..."
if ! command -v nvcc &> /dev/null; then
    echo "  CUDA toolkit not found. Installing CUDA 12.x..."
    dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo
    dnf install -y cuda-toolkit-12-4
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> /etc/profile.d/cuda.sh
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> /etc/profile.d/cuda.sh
    source /etc/profile.d/cuda.sh
else
    echo "  CUDA already installed: $(nvcc --version | grep release)"
fi

# ── 3. Verify A100 GPU ───────────────────────────────────
echo "[3/6] Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "  WARNING: nvidia-smi not found. GPU may not be available."
fi

# ── 4. Python virtual environment ─────────────────────────
echo "[4/6] Setting up Python 3.11 virtual environment..."
VENV_DIR="${LARA_VENV:-/opt/lara/venv}"
python3.11 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel

# ── 5. Install PyTorch with CUDA 12.x ────────────────────
echo "[5/6] Installing PyTorch with CUDA 12.x support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# ── 6. Install LaRa dependencies ─────────────────────────
echo "[6/6] Installing LaRa Python dependencies..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
pip install -r "$PROJECT_ROOT/requirements.txt"

# ── 7. Install Ollama ─────────────────────────────────────
echo "[Bonus] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "  Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "  Pull the LaRa model: ollama pull AgentricAi/AgentricAI_TLM:latest"
else
    echo "  Ollama already installed: $(ollama --version)"
fi

# ── Done ──────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Setup complete!"
echo ""
echo "  Next steps:"
echo "    1. source $VENV_DIR/bin/activate"
echo "    2. ollama pull AgentricAi/AgentricAI_TLM:latest"
echo "    3. python3 src/main.py"
echo "═══════════════════════════════════════════════════════"
