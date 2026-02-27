"""
LaRa Config Loader
Loads config/config.yaml and provides a validated singleton CONFIG object.
All modules import CONFIG from here instead of hard-coding values.
"""

import os
import sys
import logging

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

# ── Locate config file ─────────────────────────────────────────────────────────
_SRC_DIR    = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR   = os.path.dirname(_SRC_DIR)
_CONFIG_PATH = os.path.join(_ROOT_DIR, "config", "config.yaml")


def _load_config(path: str) -> dict:
    """Load and return the raw YAML config dict."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            f"Expected at: {path}\n"
            "Create config/config.yaml in the project root."
        )
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config file is empty or malformed: {path}")
    return data


def _validate(cfg: dict):
    """Validate required keys exist. Raises on missing critical sections."""
    required_sections = [
        "audio", "stt", "llm", "tts", "session",
        "mood", "regulation", "reinforcement",
        "preferences", "vector_memory", "memory",
        "logging", "app",
    ]
    missing = [s for s in required_sections if s not in cfg]
    if missing:
        raise KeyError(
            f"Config is missing required sections: {missing}\n"
            f"Check config/config.yaml"
        )


class _Config:
    """
    Dot-access wrapper around the yaml config dict.
    Access nested keys with: CONFIG.llm.model_name
    """
    def __init__(self, data: dict):
        self._data = data
        # Create sub-section accessors
        for key, val in data.items():
            if isinstance(val, dict):
                setattr(self, key, _Config(val))
            else:
                setattr(self, key, val)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __repr__(self):
        return f"<Config sections={list(self._data.keys())}>"


# ── Singleton ──────────────────────────────────────────────────────────────────
_raw = _load_config(_CONFIG_PATH)
_validate(_raw)
CONFIG = _Config(_raw)

logging.debug(f"[Config] Loaded from {_CONFIG_PATH}")
