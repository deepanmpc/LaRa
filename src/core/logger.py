"""
LaRa Structured Logger
Provides consistent key=value structured log formatting across all modules.
Configures root logger based on config.yaml settings.
"""

import logging
import os
import sys
import time

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
        log_dir: Directory for log files. Defaults to CWD (src/).
    """
    if log_dir is None:
        log_dir = os.path.dirname(os.path.abspath(__file__))

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)

    # Remove any pre-existing handlers (from basicConfig calls)
    root.handlers.clear()

    system_path = os.path.join(log_dir, SYSTEM_LOG)
    interaction_path = os.path.join(log_dir, INTERACTION_LOG)

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
