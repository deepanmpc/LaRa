"""
LaRa Structured Logger
Provides consistent key=value structured log formatting across all modules.
Configures root logger based on config.yaml settings.
"""

import logging
import os
import sys
import time

from src.core.runtime_paths import get_log_path

try:
    from src.core.config_loader import CONFIG
    _cfg = CONFIG.logging
    LOG_LEVEL   = getattr(logging, _cfg.level.upper(), logging.INFO)
    SYSTEM_LOG  = _cfg.system_log
    INTERACTION_LOG = _cfg.interaction_log
    STRUCTURED  = _cfg.structured
except Exception:
    LOG_LEVEL   = logging.INFO
    SYSTEM_LOG  = "lara_system.log"
    INTERACTION_LOG = "lara_interaction.log"
    STRUCTURED  = True

# ── Rate Limiting ─────────────────────────────────────────────────────────────
_last_log_time = {}

def rate_limited_log(key: str, message: str, level: int = logging.INFO, interval: int = 5) -> bool:
    """
    Prevents high-frequency logs from spamming the console or file system
    if they occur inside tight perception / sensory loops.
    
    Args:
        key: Unique identifier for the log event
        message: The actual string to log
        level: logging.INFO, logging.WARNING, etc.
        interval: Minimum seconds required between logs with this key
        
    Returns:
        True if the log was emitted, False if throttled.
    """
    now = time.time()
    if key not in _last_log_time or (now - _last_log_time[key]) > interval:
        _last_log_time[key] = now
        logging.log(level, message)
        return True
    return False


# ── Formatter ─────────────────────────────────────────────────────────────────

class StructuredFormatter(logging.Formatter):
    """
    Formats log records as:
    2026-02-27 10:00:00 | INFO  | [Component] key=value key=value
    """

    LEVEL_LABELS = {
        logging.DEBUG:    "DEBUG",
        logging.INFO:     "INFO ",
        logging.WARNING:  "WARN ",
        logging.ERROR:    "ERROR",
        logging.CRITICAL: "CRIT ",
    }

    def format(self, record: logging.LogRecord) -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        level = self.LEVEL_LABELS.get(record.levelno, "INFO ")
        msg = record.getMessage()
        return f"{ts} | {level} | {msg}"


def _build_handler(filename: str, level: int) -> logging.FileHandler:
    """Build a file handler with structured formatter."""
    handler = logging.FileHandler(filename, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(StructuredFormatter())
    return handler


def _build_console_handler(level: int) -> logging.StreamHandler:
    """Build a console handler for WARNING+ so startup errors are visible."""
    h = logging.StreamHandler(sys.stderr)
    h.setLevel(logging.WARNING)
    h.setFormatter(StructuredFormatter())
    return h


# ── Setup ─────────────────────────────────────────────────────────────────────

def setup_logging(log_dir: str = None):
    """
    Configure the root logger with file + console handlers.
    Call this once at startup (from main.py).

    Args:
        log_dir: DEPRECATED — log directory is now controlled by LARA_DATA_DIR.
                 Kept for backward compatibility (ignored if runtime_paths works).
    """
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    # Remove any pre-existing handlers (from basicConfig calls)
    root.handlers.clear()

    # Use runtime_paths for log file locations
    system_path = get_log_path(SYSTEM_LOG)
    interaction_path = get_log_path(INTERACTION_LOG)

    root.addHandler(_build_handler(system_path, LOG_LEVEL))
    root.addHandler(_build_handler(interaction_path, logging.INFO))
    root.addHandler(_build_console_handler(logging.WARNING))

    logging.info(
        f"[Logger] setup complete | level={logging.getLevelName(LOG_LEVEL)} "
        f"system_log={system_path}"
    )


# ── Component Logger Helper ───────────────────────────────────────────────────

def get_logger(component: str) -> logging.Logger:
    """
    Get a named logger for a component.
    Produces structured logs like: [SessionState] mood=frustrated conf=0.72

    Usage:
        log = get_logger("SessionState")
        log.info(f"mood={mood} conf={conf}")
        # → 2026-02-27 10:00:00 | INFO  | [SessionState] mood=frustrated conf=0.72
    """
    logger = logging.getLogger(component)

    class _PrefixFilter(logging.Filter):
        def filter(self, record):
            record.msg = f"[{component}] {record.msg}"
            return True

    if not logger.filters:
        logger.addFilter(_PrefixFilter())

    return logger
