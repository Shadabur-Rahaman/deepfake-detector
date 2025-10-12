import os
import warnings
import torch

# Suppress CUDA warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*CUDA.*")

def safe_cuda_init():
    """Safely initialize CUDA with error handling"""
    try:
        # Set conservative settings before any CUDA operations
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32,expandable_segments:False"
        os.environ["CUDA_LAUNCH_BLOCKING"] = "0"
        
        if not torch.cuda.is_available():
            return False
            
        # Test CUDA with minimal operation
        device = torch.device("cuda:0")
        test_tensor = torch.zeros(1, device=device)
        del test_tensor
        torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        print(f"CUDA initialization failed: {e}")
        # Fallback to CPU
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        return False

def get_safe_device():
    """Get a safe device (CUDA if available, CPU otherwise)"""
    try:
        if safe_cuda_init():
            return torch.device("cuda:0")
        else:
            return torch.device("cpu")
    except:
        return torch.device("cpu")

# Initialize on import
safe_device = get_safe_device()
print(f"Safe device initialized: {safe_device}")
