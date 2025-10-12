"""
CUDA Warning Suppressor
Comprehensive suppression of CUDA-related warnings and errors
"""

import os
import sys
import logging

def suppress_all_cuda_warnings():
    """Comprehensive CUDA warning suppression"""
    
    # Import warnings inside the function to avoid import conflicts
    import warnings
    
    # Set environment variables to suppress CUDA warnings
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("ABSL_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")
    os.environ.setdefault("TORCH_CUDNN_V8_API_ENABLED", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:128")
    os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
    os.environ.setdefault("TF_GPU_THREAD_MODE", "gpu_private")
    
    # Suppress specific CUDA warning messages
    cuda_warning_patterns = [
        ".*Skipping registering GPU devices.*",
        ".*could not load the CUDA driver.*",
        ".*Unable to register cuDNN factory.*",
        ".*Unable to register cuBLAS factory.*",
        ".*Duplicate PluggableDeviceFactory.*",
        ".*computation placer already registered.*",
        ".*factory already been registered.*",
        ".*duplicate registration.*",
        ".*Unable to register.*factory.*",
        ".*cuDNN.*",
        ".*cuBLAS.*",
        ".*CUDA.*",
        ".*GPU.*",
        ".*device.*",
        ".*factory.*",
        ".*registration.*",
        ".*placer.*",
    ]
    
    # Apply warning filters
    for pattern in cuda_warning_patterns:
        warnings.filterwarnings("ignore", message=pattern)
    
    # Suppress warning categories
    warning_categories = [UserWarning, FutureWarning, DeprecationWarning, RuntimeWarning]
    for category in warning_categories:
        warnings.filterwarnings("ignore", category=category)
    
    # Configure logging to reduce CUDA noise
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    
    # Suppress specific library warnings
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except ImportError:
        pass
    
    try:
        import torch
        # Suppress PyTorch warnings
        warnings.filterwarnings("ignore", module="torch")
    except ImportError:
        pass

def create_cuda_suppression_context():
    """Create a context manager for CUDA warning suppression"""
    import contextlib
    import io
    
    @contextlib.contextmanager
    def suppress_cuda_output():
        """Context manager to suppress CUDA warnings during execution"""
        old_stderr = sys.stderr
        old_stdout = sys.stdout
        try:
            # Redirect stderr and stdout to capture CUDA warnings
            sys.stderr = io.StringIO()
            sys.stdout = io.StringIO()
            yield
        finally:
            sys.stderr = old_stderr
            sys.stdout = old_stdout
    
    return suppress_cuda_output

# Auto-apply suppression when module is imported
suppress_all_cuda_warnings()

# Export the context manager
suppress_cuda_output = create_cuda_suppression_context()

if __name__ == "__main__":
    print("CUDA warning suppressor loaded successfully")
    suppress_all_cuda_warnings()
    print("All CUDA warnings suppressed")
