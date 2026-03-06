"""
LaRa Model Bootstrap Script
============================
Run this script once after cloning the repository to download all required AI models.

Usage:
    python scripts/download_models.py

Models downloaded:
  - STT:    Faster-Whisper (small.en) → runtime/models/whisper/
  - Vision: YOLOv8n                   → runtime/models/vision/
  - TTS:    Kokoro-82M                → runtime/models/tts/
  - LLM:    AgentricAI_TLM            → pulled via Ollama (auto-attempted)

All models are skipped if already present (idempotent).
"""

import os
import sys
import subprocess
import urllib.request

# ── Resolve project root ─────────────────────────────────────────────────────
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)

# Add src/ to path so we can import runtime_paths
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

from core.runtime_paths import (
    initialize,
    get_whisper_dir,
    get_vision_dir,
    get_tts_dir,
    RUNTIME_ROOT,
)

# ── ANSI colors ──────────────────────────────────────────────────────────────
_GREEN  = "\033[92m"
_YELLOW = "\033[93m"
_CYAN   = "\033[96m"
_RED    = "\033[91m"
_RESET  = "\033[0m"
_BOLD   = "\033[1m"


def _ok(msg: str):   print(f"  {_GREEN}✓{_RESET} {msg}")
def _skip(msg: str): print(f"  {_YELLOW}↷{_RESET} {msg} (already exists)")
def _info(msg: str): print(f"  {_CYAN}→{_RESET} {msg}")
def _err(msg: str):  print(f"  {_RED}✗{_RESET} {msg}")


def _progress_hook(count, block_size, total_size):
    """Simple download progress indicator."""
    if total_size > 0:
        pct = min(int(count * block_size * 100 / total_size), 100)
        bar = "█" * (pct // 5) + " " * (20 - pct // 5)
        print(f"\r    [{bar}] {pct:3d}%", end="", flush=True)
    if count * block_size >= total_size:
        print()


# ────────────────────────────────────────────────────────────────────────────
# 1. Ensure runtime directory structure
# ────────────────────────────────────────────────────────────────────────────

def setup_directories():
    print(f"\n{_BOLD}[1/4] Setting up runtime directories{_RESET}")
    initialize()
    _ok(f"Runtime root: {RUNTIME_ROOT}")
    _ok("Subdirectories: logs/, memory/, sessions/, models/whisper, models/vision, models/tts")


# ────────────────────────────────────────────────────────────────────────────
# 2. STT — Faster-Whisper (small.en)
# ────────────────────────────────────────────────────────────────────────────

def download_whisper():
    print(f"\n{_BOLD}[2/4] STT Model — Faster-Whisper (small.en){_RESET}")
    whisper_dir = get_whisper_dir()

    # Check if the model snapshot already exists (HF cache layout)
    snapshot_dir = os.path.join(whisper_dir, "models--Systran--faster-whisper-small.en")
    if os.path.isdir(snapshot_dir):
        _skip(f"Whisper model cache found at {snapshot_dir}")
        return

    _info(f"Downloading to {whisper_dir} ...")
    try:
        from faster_whisper import WhisperModel
        _ = WhisperModel("small.en", device="cpu", compute_type="int8", download_root=whisper_dir)
        del _
        _ok("Whisper small.en downloaded successfully")
    except ImportError:
        _err("faster-whisper not installed. Run: pip install faster-whisper")
    except Exception as e:
        _err(f"Whisper download failed: {e}")


# ────────────────────────────────────────────────────────────────────────────
# 3. Vision — YOLOv8n
# ────────────────────────────────────────────────────────────────────────────

_YOLO_URL  = "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt"
_YOLO_NAME = "yolov8n.pt"

def download_yolo():
    print(f"\n{_BOLD}[3/4] Vision Model — YOLOv8n{_RESET}")
    vision_dir = get_vision_dir()
    dest       = os.path.join(vision_dir, _YOLO_NAME)

    if os.path.isfile(dest):
        _skip(f"yolov8n.pt found at {dest}")
        return

    _info(f"Downloading from {_YOLO_URL} ...")
    try:
        urllib.request.urlretrieve(_YOLO_URL, dest, reporthook=_progress_hook)
        _ok(f"yolov8n.pt saved to {dest}")
    except Exception as e:
        _err(f"YOLO download failed: {e}")


# ────────────────────────────────────────────────────────────────────────────
# 3. TTS — Kokoro-82M
# ────────────────────────────────────────────────────────────────────────────

_KOKORO_REPO = "hexgrad/Kokoro-82M"

def download_kokoro():
    print(f"\n{_BOLD}[3/5] TTS Model — Kokoro-82M{_RESET}")
    tts_dir = get_tts_dir()

    # Check if model was already downloaded (presence of kokoro-v1_0.pth or similar)
    existing = [f for f in os.listdir(tts_dir) if f.endswith((".pth", ".pt", ".safetensors", ".yaml"))]
    if existing:
        _skip(f"Kokoro model files already present in {tts_dir}")
        return

    _info(f"Downloading {_KOKORO_REPO} from Hugging Face → {tts_dir} ...")
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=_KOKORO_REPO,
            local_dir=tts_dir,
            local_dir_use_symlinks=False,
        )
        _ok(f"Kokoro-82M downloaded to {tts_dir}")
    except ImportError:
        _err("huggingface_hub not installed. Run: pip install huggingface-hub")
    except Exception as e:
        _err(f"Kokoro download failed: {e}")


# ────────────────────────────────────────────────────────────────────────────
# 4. LLM — Ollama / AgentricAI_TLM
# ────────────────────────────────────────────────────────────────────────────

_OLLAMA_MODEL = "AgentricAi/AgentricAI_TLM:latest"

def setup_llm():
    print(f"\n{_BOLD}[4/5] LLM Model — AgentricAI_TLM (Ollama){_RESET}")

    # Try to auto-pull if ollama is available
    try:
        result = subprocess.run(
            ["ollama", "pull", _OLLAMA_MODEL],
            capture_output=False,
            timeout=300,
        )
        if result.returncode == 0:
            _ok(f"Ollama model '{_OLLAMA_MODEL}' pulled successfully")
        else:
            _err(f"ollama pull returned exit code {result.returncode}")
    except FileNotFoundError:
        print(f"\n  {_YELLOW}Ollama not found in PATH. Pull the model manually:{_RESET}")
        print(f"\n    {_BOLD}ollama pull {_OLLAMA_MODEL}{_RESET}\n")
    except subprocess.TimeoutExpired:
        _err("ollama pull timed out (the model may still be downloading in the background)")
    except Exception as e:
        _err(f"Ollama setup failed: {e}")


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{_CYAN}{'='*60}")
    print("  LaRa Model Bootstrap")
    print(f"{'='*60}{_RESET}")

    setup_directories()
    download_whisper()
    download_yolo()
    download_kokoro()
    setup_llm()

    print(f"\n{_GREEN}{_BOLD}{'='*60}")
    print("  Model bootstrap complete!")
    print(f"{'='*60}{_RESET}")
    print(f"\n  You can now start LaRa with:\n\n    {_BOLD}python src/main.py{_RESET}\n")


if __name__ == "__main__":
    main()
