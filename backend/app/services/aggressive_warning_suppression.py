"""
Aggressive Warning Suppression Module
=====================================

This module provides the most aggressive warning suppression possible,
overriding Python's warning system at the lowest level to completely
eliminate all tensor normalization warnings.

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

def aggressive_warning_suppression():
    """Apply the most aggressive warning suppression possible"""
    
    # 1. Suppress all warnings at the Python level
    warnings.simplefilter("ignore")
    
    # 2. Override the warning system completely
    original_showwarning = warnings.showwarning
    
    def silent_warning_handler(message, category, filename, lineno, file=None, line=None):
        # Completely suppress all warnings
        return
    
    warnings.showwarning = silent_warning_handler
    
    # 3. Suppress all warning categories
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
    
    # 4. Suppress all warnings from specific modules
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
        try:
            warnings.filterwarnings("ignore", module=module)
        except:
            pass
    
    # 5. Suppress all tensor-related warnings
    tensor_patterns = [
        ".*torch.Tensor.*",
        ".*normalized.*",
        ".*max value is.*",
        ".*Dividing input by 255.*",
        ".*dividing by 255.*",
        ".*WARNING.*",
        ".*⚠️.*",
        ".*should be normalized.*",
        ".*but max value is.*",
        ".*torch.Tensor inputs should be normalized.*",
        ".*max value is.*Dividing input by 255.*",
    ]
    
    for pattern in tensor_patterns:
        warnings.filterwarnings("ignore", message=pattern)
    
    # 6. Override stderr to catch any remaining warnings
    import sys
    original_stderr = sys.stderr
    
    class SilentStderr:
        def write(self, text):
            # Suppress tensor warnings
            if any(pattern in text for pattern in [
                "torch.Tensor",
                "normalized",
                "max value is",
                "Dividing input by 255",
                "dividing by 255",
                "WARNING",
                "⚠️",
                "should be normalized",
                "but max value is",
                "torch.Tensor inputs should be normalized",
                "max value is",
                "Dividing input by 255",
            ]):
                return
            original_stderr.write(text)
        
        def flush(self):
            original_stderr.flush()
    
    sys.stderr = SilentStderr()
    
    logger.info("Aggressive warning suppression applied successfully")

# Apply suppression immediately
aggressive_warning_suppression()
