"""
LaRa Vision Perception — Structured Logger
No frame dumping. No raw image logging. Structured output only.
"""

import logging
import json
import sys
import time
from config import vision_config


class JsonFormatter(logging.Formatter):
    """Emits log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": round(time.time(), 4),
            "level": record.levelname,
            "module": record.module,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exc"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def get_logger(name: str = "lara-vision") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    handler = logging.StreamHandler(sys.stdout)

    if vision_config.LOG_MODE == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(module)s: %(message)s")
        )

    level = getattr(logging, vision_config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
