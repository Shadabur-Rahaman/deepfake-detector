import os
import torch

def enable_cpu_fallback():
    """Enable CPU fallback for all models"""
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["FORCE_CPU"] = "1"
    os.environ["DISABLE_GPU"] = "1"
    
    print("CPU fallback enabled - all models will use CPU")
    return torch.device("cpu")

def get_fallback_device():
    """Get fallback device (CPU)"""
    return enable_cpu_fallback()

# Export for use in other modules
FALLBACK_DEVICE = get_fallback_device()
