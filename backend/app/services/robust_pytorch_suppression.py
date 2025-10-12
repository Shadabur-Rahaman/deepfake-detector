"""
Robust PyTorch Warning Suppression Module
=========================================

This module provides robust PyTorch warning suppression that handles
all edge cases and PyTorch version differences gracefully.

Author: Senior ML Engineer
Date: 2024
"""

import warnings
import os
import sys
import logging

# Set environment variables to suppress warnings
os.environ.setdefault("PYTORCH_WARN_LEVEL", "0")
os.environ.setdefault("TORCH_WARN_LEVEL", "0")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

logger = logging.getLogger(__name__)

def apply_robust_pytorch_suppression():
    """Apply robust PyTorch warning suppression that handles all edge cases"""
    
    # 1. Set environment variables
    os.environ["PYTORCH_WARN_LEVEL"] = "0"
    os.environ["TORCH_WARN_LEVEL"] = "0"
    os.environ["PYTHONWARNINGS"] = "ignore"
    
    # 2. Suppress all warnings at Python level
    warnings.simplefilter("ignore")
    
    # 3. Suppress specific PyTorch warning patterns
    pytorch_patterns = [
        ".*torch.Tensor inputs should be normalized.*",
        ".*max value is.*",
        ".*Dividing input by 255.*",
        ".*dividing by 255.*",
        ".*WARNING.*torch.Tensor.*",
        ".*should be normalized 0.0-1.0.*",
        ".*but max value is.*",
        ".*⚠️.*torch.Tensor.*",
        ".*WARNING ⚠️.*",
        ".*torch.Tensor.*normalized.*",
        ".*normalized 0.0-1.0.*",
        ".*max value is.*Dividing input by 255.*",
        ".*torch.Tensor.*should be normalized.*",
        ".*torch.Tensor.*max value is.*",
        ".*torch.Tensor.*Dividing input by 255.*",
        ".*torch.Tensor.*dividing by 255.*",
        ".*torch.Tensor.*WARNING.*",
        ".*torch.Tensor.*should be normalized 0.0-1.0.*",
        ".*torch.Tensor.*but max value is.*",
        ".*torch.Tensor.*⚠️.*",
        ".*torch.Tensor.*WARNING ⚠️.*",
        ".*torch.Tensor.*normalized.*",
        ".*torch.Tensor.*normalized 0.0-1.0.*",
        ".*torch.Tensor.*max value is.*Dividing input by 255.*",
    ]
    
    for pattern in pytorch_patterns:
        warnings.filterwarnings("ignore", message=pattern)
    
    # 4. Suppress all warning categories
    warning_categories = [
        UserWarning,
        FutureWarning,
        DeprecationWarning,
        RuntimeWarning,
        PendingDeprecationWarning,
        ImportWarning,
        UnicodeWarning,
        BytesWarning,
        ResourceWarning,
    ]
    
    for category in warning_categories:
        warnings.filterwarnings("ignore", category=category)
    
    # 5. Suppress warnings from specific modules
    modules_to_suppress = [
        "torch",
        "torchvision", 
        "torch.nn",
        "torch.functional",
        "torch.optim",
        "torch.utils",
        "ultralytics",
        "cv2",
        "numpy",
        "PIL",
        "matplotlib",
    ]
    
    for module in modules_to_suppress:
        warnings.filterwarnings("ignore", module=module)
    
    # 6. Try PyTorch-specific suppression methods
    try_pytorch_specific_suppression()
    
    # 7. Override warning system
    override_warning_system()
    
    logger.info("Robust PyTorch warning suppression applied successfully")

def try_pytorch_specific_suppression():
    """Try PyTorch-specific suppression methods with comprehensive error handling"""
    
    try:
        import torch
        
        # Method 1: Try to set torch warning level
        if hasattr(torch, 'set_warn_always'):
            torch.set_warn_always(False)
        
        # Method 2: Try to access internal logging API
        if hasattr(torch, '_C') and hasattr(torch._C, '_log_api_usage'):
            try:
                original_warn = torch._C._log_api_usage._warn
                
                def suppress_tensor_warnings(*args, **kwargs):
                    if len(args) > 0 and isinstance(args[0], str):
                        tensor_patterns = [
                            "torch.Tensor inputs should be normalized",
                            "max value is",
                            "Dividing input by 255",
                            "dividing by 255",
                            "WARNING",
                            "torch.Tensor",
                            "normalized 0.0-1.0",
                            "should be normalized 0.0-1.0",
                            "but max value is",
                            "⚠️",
                            "WARNING ⚠️",
                        ]
                        
                        for pattern in tensor_patterns:
                            if pattern in args[0]:
                                return
                    
                    return original_warn(*args, **kwargs)
                
                torch._C._log_api_usage._warn = suppress_tensor_warnings
                logger.info("PyTorch internal API warning suppression applied")
                
            except (AttributeError, Exception) as e:
                logger.info(f"PyTorch internal API not available: {e}")
        
        # Method 3: Set logging level for torch
        import logging
        torch_logger = logging.getLogger("torch")
        torch_logger.setLevel(logging.ERROR)
        
        # Method 4: Try to suppress warnings at the module level
        try:
            import torchvision
            if hasattr(torchvision, 'set_warn_always'):
                torchvision.set_warn_always(False)
        except (ImportError, AttributeError):
            pass
        
        logger.info("PyTorch-specific suppression methods applied")
        
    except ImportError:
        logger.info("PyTorch not available, skipping PyTorch-specific suppression")
    except Exception as e:
        logger.info(f"PyTorch-specific suppression failed: {e}")

def override_warning_system():
    """Override Python's warning system to catch and suppress all warnings"""
    
    original_showwarning = warnings.showwarning
    
    def silent_warning_handler(message, category, filename, lineno, file=None, line=None):
        # Suppress all warnings silently
        return
    
    warnings.showwarning = silent_warning_handler
    
    logger.info("Warning system override applied")

def apply_comprehensive_suppression():
    """Apply comprehensive warning suppression"""
    try:
        apply_robust_pytorch_suppression()
        logger.info("Comprehensive warning suppression applied successfully")
    except Exception as e:
        logger.info(f"Warning suppression failed: {e}")
        # Fallback to basic suppression
        warnings.simplefilter("ignore")
        os.environ["PYTHONWARNINGS"] = "ignore"

if __name__ == "__main__":
    apply_comprehensive_suppression()
