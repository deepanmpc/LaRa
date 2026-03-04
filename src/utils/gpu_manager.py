import os
import logging
import platform

def configure_gpu():
    """
    Detects if CUDA is available and sets the CUDA_VISIBLE_DEVICES environment variable
    to enforce deterministic GPU utilization on HPC nodes.
    Returns the backend device string ('cuda' or 'cpu').
    """
    try:
        import torch
        if torch.cuda.is_available():
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            return "cuda"
    except ImportError:
        pass
    
    return "cpu"

def check_vram(required_gb: float):
    """
    Checks if the currently available GPU has enough VRAM.
    Raises RuntimeError if insufficient memory is detected.
    """
    try:
        import torch
        if torch.cuda.is_available():
            # Get VRAM in GB
            total_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            if total_memory_gb < required_gb:
                raise RuntimeError(
                    f"[VRAM Checker] Insufficient GPU memory. "
                    f"Required: {required_gb}GB, Available: {total_memory_gb:.2f}GB"
                )
    except ImportError:
        pass

def get_device_and_compute_type(config_device: str, config_compute: str) -> tuple[str, str]:
    """
    Returns a unified device and compute string with CPU fallback capability.
    Used by STT and Vision models to safely degrade on non-GPU instances (like Mac).
    """
    device = configure_gpu()
    
    # If the hardware doesn't support the requested CUDA config, gracefully degrade
    if device == "cpu" and config_device == "cuda":
        logging.warning("[GPU Manager] CUDA requested but unavailable. Falling back to CPU with int8 compute.")
        return "cpu", "int8"
        
    # Apple Silicon fallback hardening
    if platform.system() == "Darwin" and device != "cpu":
        logging.warning("[GPU Manager] MacOS detected. Forcing CPU with int8 compute.")
        return "cpu", "int8"
        
    return device, config_compute
