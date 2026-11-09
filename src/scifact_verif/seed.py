import os, random

def set_seed(seed: int = 42, deterministic: bool = False) -> dict:
    """Seed Python/NumPy/PyTorch (if present). Returns what was actually set, for the run log."""
    info = {"seed": seed, "deterministic_requested": deterministic}
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)  # only affects subprocesses started after this call
    try:
        import numpy as np
        np.random.seed(seed); info["numpy"] = True
    except ImportError:
        info["numpy"] = False
    try:
        import torch
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed); info["torch"] = True
        if deterministic:
            os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            torch.use_deterministic_algorithms(True, warn_only=True)
            torch.backends.cudnn.benchmark = False
        info["torch_deterministic_algorithms"] = torch.are_deterministic_algorithms_enabled()
    except ImportError:
        info["torch"] = False
    return info