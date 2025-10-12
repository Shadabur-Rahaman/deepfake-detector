# startup_safety.py - Comprehensive startup safety measures to prevent segmentation faults

import os
import sys
import logging
import warnings
from contextlib import contextmanager
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to track if heavy imports are safe
_heavy_imports_safe = False
_import_cache = {}

def is_heavy_imports_safe() -> bool:
    """Check if it's safe to import heavy ML libraries"""
    return _heavy_imports_safe

def set_heavy_imports_safe(safe: bool = True):
    """Set the flag indicating heavy imports are safe"""
    global _heavy_imports_safe
    _heavy_imports_safe = safe

@contextmanager
def safe_import_context():
    """Context manager for safe imports that won't cause segfaults"""
    try:
        # Suppress all warnings during import
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Set environment variables to prevent CUDA conflicts
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable CUDA initially
            os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
            os.environ['TF_DISABLE_MKL'] = '1'
            
            yield
            
    except Exception as e:
        logger.error(f"Import context error: {e}")
        raise
    finally:
        # Restore environment
        if 'CUDA_VISIBLE_DEVICES' in os.environ:
            del os.environ['CUDA_VISIBLE_DEVICES']

def safe_import(module_name: str, fallback=None):
    """Safely import a module with fallback"""
    if module_name in _import_cache:
        return _import_cache[module_name]
    
    try:
        with safe_import_context():
            module = __import__(module_name)
            _import_cache[module_name] = module
            return module
    except Exception as e:
        logger.warning(f"Failed to import {module_name}: {e}")
        if fallback is not None:
            return fallback
        raise ImportError(f"Could not import {module_name}")

def defer_heavy_imports():
    """Defer heavy imports until they're actually needed"""
    global _heavy_imports_safe
    
    # Only allow heavy imports after the app is fully started
    _heavy_imports_safe = False
    
    # Create lazy import wrappers
    def lazy_torch():
        if not _heavy_imports_safe:
            raise RuntimeError("Heavy imports not yet safe. Call set_heavy_imports_safe(True) first.")
        return safe_import('torch')
    
    def lazy_tensorflow():
        if not _heavy_imports_safe:
            raise RuntimeError("Heavy imports not yet safe. Call set_heavy_imports_safe(True) first.")
        return safe_import('tensorflow')
    
    def lazy_cv2():
        if not _heavy_imports_safe:
            raise RuntimeError("Heavy imports not yet safe. Call set_heavy_imports_safe(True) first.")
        return safe_import('cv2')
    
    def lazy_mtcnn():
        if not _heavy_imports_safe:
            raise RuntimeError("Heavy imports not yet safe. Call set_heavy_imports_safe(True) first.")
        return safe_import('mtcnn')
    
    # Store lazy importers
    _import_cache['torch'] = lazy_torch
    _import_cache['tensorflow'] = lazy_tensorflow
    _import_cache['cv2'] = lazy_cv2
    _import_cache['mtcnn'] = lazy_mtcnn

def enable_heavy_imports():
    """Enable heavy imports after app startup is complete"""
    global _heavy_imports_safe
    _heavy_imports_safe = True
    logger.info("[OK] Heavy imports are now safe to use")

def check_system_health():
    """Check system health before allowing heavy imports"""
    try:
        # Check available memory
        import psutil
        memory = psutil.virtual_memory()
        if memory.available < 1024 * 1024 * 1024:  # Less than 1GB
            logger.warning("Low memory available, heavy imports may fail")
            return False
        
        # Check if CUDA is available (but don't initialize it yet)
        cuda_available = False
        try:
            with safe_import_context():
                import torch
                cuda_available = torch.cuda.is_available()
        except:
            pass
        
        logger.info(f"System health check passed. CUDA available: {cuda_available}")
        return True
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return False

def initialize_safe_startup():
    """Initialize safe startup sequence"""
    logger.info("[START] Initializing safe startup sequence...")
    
    # Defer heavy imports
    defer_heavy_imports()
    
    # Check system health
    if not check_system_health():
        logger.warning("System health check failed, but continuing...")
    
    logger.info("[OK] Safe startup sequence initialized")

# Initialize on import
initialize_safe_startup()
