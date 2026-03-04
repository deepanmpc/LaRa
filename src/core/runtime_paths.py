"""
LaRa Runtime Path Manager

Centralises all runtime data paths. Every module that writes logs, databases,
vector stores, or session files MUST use this module instead of hardcoded paths.

Environment variable:
    LARA_DATA_DIR  –  override the default runtime root

Default runtime root:
    ~/lara_runtime

Directory layout (auto-created on import):
    <runtime_root>/
        logs/           lara_system.log, lara_interaction.log, lara_metrics.log
        memory/         lara_memory.db, chroma.sqlite3, lara_vector_store/
        sessions/       (reserved for future session persistence)
        models/         whisper models, YOLO weights, etc.
"""

import os
import logging

_logger = logging.getLogger(__name__)

# ── Resolve runtime root ─────────────────────────────────────

_DEFAULT_ROOT = os.path.join(os.path.expanduser("~"), "lara_runtime")

RUNTIME_ROOT: str = os.environ.get("LARA_DATA_DIR", _DEFAULT_ROOT)

# ── Required sub-directories ─────────────────────────────────

_SUBDIRS = ["logs", "memory", "sessions", "models"]


def _ensure_dirs() -> None:
    """Create the runtime directory tree if it doesn't exist."""
    for sub in _SUBDIRS:
        path = os.path.join(RUNTIME_ROOT, sub)
        os.makedirs(path, exist_ok=True)
    _logger.debug(f"Runtime directories ensured under {RUNTIME_ROOT}")


# Auto-create on import
_ensure_dirs()


# ── Public helpers ────────────────────────────────────────────

def get_runtime_root() -> str:
    """Return the resolved runtime root directory."""
    return RUNTIME_ROOT


def get_log_dir() -> str:
    """Return the logs directory path."""
    return os.path.join(RUNTIME_ROOT, "logs")


def get_log_path(filename: str) -> str:
    """Return absolute path for a log file inside the logs directory."""
    return os.path.join(RUNTIME_ROOT, "logs", filename)


def get_memory_dir() -> str:
    """Return the memory directory path."""
    return os.path.join(RUNTIME_ROOT, "memory")


def get_memory_db_path(filename: str = "lara_memory.db") -> str:
    """Return absolute path for the SQLite memory database."""
    return os.path.join(RUNTIME_ROOT, "memory", filename)


def get_vector_store_path(dirname: str = "lara_vector_store") -> str:
    """Return absolute path for the ChromaDB persistent directory."""
    path = os.path.join(RUNTIME_ROOT, "memory", dirname)
    os.makedirs(path, exist_ok=True)
    return path


def get_sessions_dir() -> str:
    """Return the sessions directory path."""
    return os.path.join(RUNTIME_ROOT, "sessions")


def get_models_dir() -> str:
    """Return the models directory path."""
    return os.path.join(RUNTIME_ROOT, "models")


def get_model_path(filename: str) -> str:
    """Return absolute path for a model file inside the models directory."""
    return os.path.join(RUNTIME_ROOT, "models", filename)


# ── Summary on import ─────────────────────────────────────────

_logger.info(f"Runtime root: {RUNTIME_ROOT}")
