"""
Comprehensive Warning Suppression Module
========================================

This module provides comprehensive suppression of all PyTorch tensor normalization warnings
and other common warnings that clutter the logs.

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

# Enhanced CUDA and ultralytics environment variables
os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")
os.environ.setdefault("TORCH_USE_CUDA_DSA", "1")
os.environ.setdefault("ULTRALYTICS_VERBOSE", "False")
os.environ.setdefault("YOLO_VERBOSE", "False")

logger = logging.getLogger(__name__)

def suppress_all_tensor_warnings():
    """Comprehensive suppression of all tensor-related warnings"""
    
    # Suppress all PyTorch tensor normalization warnings
    tensor_warning_patterns = [
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
    
    for pattern in tensor_warning_patterns:
        warnings.filterwarnings("ignore", message=pattern)
    
    # Suppress all warning categories
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
    
    # Suppress warnings from specific modules
    module_patterns = [
        "torch",
        "torchvision",
        "torch.nn",
        "torch.functional",
        "torch.optim",
        "torch.utils",
        "ultralytics",
        "yolo",
        "timm",
        "transformers",
        "cv2",
        "numpy",
        "PIL",
        "matplotlib",
    ]
    
    for module in module_patterns:
        warnings.filterwarnings("ignore", category=UserWarning, module=module)
        warnings.filterwarnings("ignore", category=FutureWarning, module=module)
        warnings.filterwarnings("ignore", category=DeprecationWarning, module=module)
        warnings.filterwarnings("ignore", category=RuntimeWarning, module=module)

def override_warning_system():
    """Override Python's warning system to catch and suppress all tensor warnings"""
    
    original_showwarning = warnings.showwarning
    
    def custom_showwarning(message, category, filename, lineno, file=None, line=None):
        if isinstance(message, str):
            # Check for tensor-related warning patterns
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
                "torch.Tensor",
                "normalized",
                "dividing by 255",
                "max value is",
                "Dividing input by 255",
                "NMS backend",
                "ultralytics",
                "YOLO",
                "timm",
                "transformers",
                "CUDA",
                "cuda",
                "backend",
            ]
            
            # If any pattern matches, suppress the warning
            for pattern in tensor_patterns:
                if pattern in message:
                    return
            
            # Also suppress warnings from specific files
            if filename and any(module in filename for module in ["torch", "torchvision", "ultralytics", "yolo", "timm", "transformers"]):
                return
        
        # For non-tensor warnings, show them normally
        return original_showwarning(message, category, filename, lineno, file, line)
    
    warnings.showwarning = custom_showwarning

def suppress_pytorch_warnings():
    """Suppress PyTorch-specific warnings using monkey patching"""
    try:
        # Try to access PyTorch's internal logging API
        import torch
        if hasattr(torch, '_C') and hasattr(torch._C, '_log_api_usage'):
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
                        "NMS backend",
                        "ultralytics",
                        "YOLO",
                        "timm",
                        "CUDA",
                    ]
                    
                    for pattern in tensor_patterns:
                        if pattern in args[0]:
                            return
                
                return original_warn(*args, **kwargs)
            
            torch._C._log_api_usage._warn = suppress_tensor_warnings
            logger.info("PyTorch warning suppression applied successfully")
        else:
            logger.info("PyTorch internal logging API not available, using alternative suppression")
            # Use alternative suppression methods
            suppress_pytorch_warnings_alternative()
        
    except (ImportError, AttributeError, Exception) as e:
        logger.info(f"PyTorch warning suppression not available: {e}")
        # Use alternative suppression methods
        suppress_pytorch_warnings_alternative()

def suppress_pytorch_warnings_alternative():
    """Alternative PyTorch warning suppression when internal API is not available"""
    try:
        import torch
        # Set torch to not show warnings
        if hasattr(torch, 'set_warn_always'):
            torch.set_warn_always(False)
        
        # Suppress warnings at the logging level
        import logging
        torch_logger = logging.getLogger("torch")
        torch_logger.setLevel(logging.ERROR)
        
        logger.info("Alternative PyTorch warning suppression applied")
        
    except Exception as e:
        logger.info(f"Alternative PyTorch warning suppression failed: {e}")

def apply_comprehensive_suppression():
    """Apply all warning suppression methods"""
    try:
        suppress_all_tensor_warnings()
        override_warning_system()
        suppress_pytorch_warnings()
        
        # Additional aggressive suppression
        import warnings
        warnings.simplefilter("ignore")
        
        # Suppress all warnings from specific modules
        for module_name in ["torch", "torchvision", "ultralytics", "yolo", "timm", "transformers", "cv2", "numpy", "PIL", "matplotlib"]:
            try:
                warnings.filterwarnings("ignore", module=module_name)
            except:
                pass
        
        logger.info("Comprehensive warning suppression applied successfully")
    except Exception as e:
        logger.error(f"Failed to apply warning suppression: {e}")

def setup_comprehensive_warning_suppression():
    """Setup function for comprehensive warning suppression"""
    apply_comprehensive_suppression()
    return True

class WarningSuppressionContext:
    """Context manager for selective warning suppression"""
    
    def __init__(self, suppress_level="all"):
        self.suppress_level = suppress_level
        self.original_filters = []
        
    def __enter__(self):
        # Store original warning filters
        self.original_filters = warnings.filters[:]
        
        if self.suppress_level == "all":
            warnings.simplefilter("ignore")
        elif self.suppress_level == "tensor":
            suppress_all_tensor_warnings()
        elif self.suppress_level == "pytorch":
            suppress_pytorch_warnings()
            
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original warning filters
        warnings.filters[:] = self.original_filters

class EnhancedLoggingFilter(logging.Filter):
    """Enhanced logging filter to catch runtime warnings"""
    
    def filter(self, record):
        # Suppress warnings from specific modules
        if record.name in ["torch", "torchvision", "ultralytics", "yolo", "timm", "transformers"]:
            return False
        
        # Suppress specific warning messages
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            warning_patterns = [
                "torch.Tensor inputs should be normalized",
                "NMS backend",
                "CUDA",
                "timm",
                "ultralytics",
                "YOLO"
            ]
            
            for pattern in warning_patterns:
                if pattern in message:
                    return False
        
        return True

# Apply suppression immediately when module is imported
apply_comprehensive_suppression()
