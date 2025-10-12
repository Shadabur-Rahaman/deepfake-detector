import os
import torch

# Apply CUDA driver error fix
def fix_cuda_driver():
    """Fix CUDA driver initialization issues"""
    try:
        # Clear any existing CUDA context
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        
        # Set conservative CUDA settings
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32,expandable_segments:False"
        os.environ["CUDA_LAUNCH_BLOCKING"] = "0"
        os.environ["TORCH_USE_CUDA_DSA"] = "0"
        
        # Initialize CUDA with error handling
        if torch.cuda.is_available():
            device = torch.device("cuda:0")
            # Test CUDA with minimal operation
            test_tensor = torch.tensor([1.0], device=device)
            del test_tensor
            torch.cuda.empty_cache()
            return True
        return False
        
    except Exception as e:
        print(f"CUDA driver fix failed: {e}")
        return False

# Apply fix immediately
fix_cuda_driver()
