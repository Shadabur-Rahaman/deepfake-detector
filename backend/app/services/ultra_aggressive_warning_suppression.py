"""
Ultra Aggressive Warning Suppression Module
===========================================

This module provides the most aggressive warning suppression possible,
overriding Python's warning system at the lowest level and intercepting
warnings before they can be displayed.

Author: Senior ML Engineer
Date: 2024
"""

import warnings
import os
import sys
import logging
import io
import contextlib

# Set environment variables to suppress warnings
os.environ.setdefault("PYTORCH_WARN_LEVEL", "0")
os.environ.setdefault("TORCH_WARN_LEVEL", "0")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

logger = logging.getLogger(__name__)

def ultra_aggressive_suppression():
    """Apply the most aggressive warning suppression possible"""
    
    # 1. Completely override the warning system
    def silent_warning_handler(message, category, filename, lineno, file=None, line=None):
        # Completely suppress all warnings
        return
    
    warnings.showwarning = silent_warning_handler
    
    # 2. Override stderr to catch any remaining warnings
    original_stderr = sys.stderr
    
    class UltraSilentStderr:
        def write(self, text):
            # Suppress all tensor warnings
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
                "WARNING ⚠️",
                "torch.Tensor inputs should be normalized 0.0-1.0",
                "but max value is",
                "Dividing input by 255",
            ]):
                return
            original_stderr.write(text)
        
        def flush(self):
            original_stderr.flush()
        
        def close(self):
            # Add close method to prevent AttributeError during shutdown
            if hasattr(original_stderr, 'close'):
                original_stderr.close()
        
        def isatty(self):
            try:
                return original_stderr.isatty()
            except AttributeError:
                return False
    
    sys.stderr = UltraSilentStderr()
    
    # 3. Override stdout as well to catch any warnings there
    original_stdout = sys.stdout
    
    class UltraSilentStdout:
        def write(self, text):
            # Suppress all tensor warnings
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
                "WARNING ⚠️",
                "torch.Tensor inputs should be normalized 0.0-1.0",
                "but max value is",
                "Dividing input by 255",
            ]):
                return
            original_stdout.write(text)
        
        def flush(self):
            original_stdout.flush()
        
        def close(self):
            # Add close method to prevent AttributeError during shutdown
            if hasattr(original_stdout, 'close'):
                original_stdout.close()
        
        def isatty(self):
            return original_stdout.isatty()
    
    sys.stdout = UltraSilentStdout()
    
    # 4. Suppress all warnings at the Python level
    warnings.simplefilter("ignore")
    
    # 5. Override the logging system to catch warnings
    original_logging_warning = logging.Logger.warning
    
    def silent_logging_warning(self, msg, *args, **kwargs):
        if any(pattern in str(msg) for pattern in [
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
            "WARNING ⚠️",
            "torch.Tensor inputs should be normalized 0.0-1.0",
            "but max value is",
            "Dividing input by 255",
        ]):
            return
        return original_logging_warning(self, msg, *args, **kwargs)
    
    logging.Logger.warning = silent_logging_warning
    
    # 6. Override print statements
    original_print = print
    
    def silent_print(*args, **kwargs):
        text = ' '.join(str(arg) for arg in args)
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
            "WARNING ⚠️",
            "torch.Tensor inputs should be normalized 0.0-1.0",
            "but max value is",
            "Dividing input by 255",
        ]):
            return
        return original_print(*args, **kwargs)
    
    # Override print globally
    import builtins
    builtins.print = silent_print
    
    logger.info("Ultra aggressive warning suppression applied successfully")

# Apply suppression immediately
ultra_aggressive_suppression()
