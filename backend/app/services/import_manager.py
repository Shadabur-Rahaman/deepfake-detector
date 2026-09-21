# backend/app/services/import_manager.py
# Centralized Import Management for Deepfake Detection Backend

import os
import sys
import warnings
import logging
import threading
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# =============================================================================
# GLOBAL IMPORT CACHE
# =============================================================================
_IMPORT_CACHE = {
    'initialized': False,
    'torch': None,
    'torchvision': None,
    'cv2': None,
    'yolo': None,
    'numpy': None,
    'cuda_status': None
}
_import_lock = threading.Lock()

# =============================================================================
# GLOBAL WARNING SUPPRESSION
# =============================================================================
def setup_global_warnings():
    """Setup comprehensive global warning suppression"""
    # Suppress all warning categories
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.simplefilter("ignore")
    
    # Set environment variables for comprehensive suppression
    os.environ.setdefault("PYTORCH_WARN_LEVEL", "0")
    os.environ.setdefault("TORCH_WARN_LEVEL", "0")
    os.environ.setdefault("PYTHONWARNINGS", "ignore")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")
    
    # Apply PyTorch-specific suppression
    try:
        from .robust_pytorch_suppression import apply_comprehensive_suppression
        apply_comprehensive_suppression()
    except (ImportError, Exception):
        pass

# =============================================================================
# CUDA AVAILABILITY CHECK
# =============================================================================
def check_cuda_availability() -> Dict[str, Any]:
    """Check CUDA availability and return status"""
    cuda_status = {
        "available": False,
        "device_name": None,
        "cuda_version": None,
        "memory_gb": None
    }
    
    try:
        import torch
        # Check if CUDA is disabled by environment variables
        if os.environ.get("CUDA_VISIBLE_DEVICES") == "" or os.environ.get("FORCE_CPU_MODE") == "1":
            print("[INFO] CUDA disabled by environment variables, using CPU")
            cuda_status["available"] = False
        elif torch.cuda.is_available():
            try:
                cuda_status["available"] = True
                cuda_status["device_name"] = torch.cuda.get_device_name(0)
                cuda_status["cuda_version"] = torch.version.cuda
                cuda_status["memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
                print(f"[INFO] CUDA available: {cuda_status['cuda_version']}, GPU: {cuda_status['device_name']}")
            except (AssertionError, RuntimeError) as e:
                print(f"[WARNING] CUDA device access failed: {e}, using CPU")
                cuda_status["available"] = False
        else:
            print("[WARNING] CUDA not detected, running on CPU")
    except ImportError:
        print("[WARNING] PyTorch not available")
    
    return cuda_status

# =============================================================================
# CACHED IMPORT FUNCTIONS
# =============================================================================
def get_cached_torch() -> Optional[Any]:
    """Get cached PyTorch import"""
    with _import_lock:
        if _IMPORT_CACHE['torch'] is None and not _IMPORT_CACHE['initialized']:
            _IMPORT_CACHE['torch'] = safe_import_torch()
        return _IMPORT_CACHE['torch']

def get_cached_torchvision() -> Optional[Any]:
    """Get cached torchvision import"""
    with _import_lock:
        if _IMPORT_CACHE['torchvision'] is None and not _IMPORT_CACHE['initialized']:
            _IMPORT_CACHE['torchvision'] = safe_import_torchvision()
        return _IMPORT_CACHE['torchvision']

def get_cached_opencv() -> Optional[Any]:
    """Get cached OpenCV import"""
    with _import_lock:
        if _IMPORT_CACHE['cv2'] is None and not _IMPORT_CACHE['initialized']:
            _IMPORT_CACHE['cv2'] = safe_import_opencv()
        return _IMPORT_CACHE['cv2']

def get_cached_yolo() -> Optional[Any]:
    """Get cached YOLO import"""
    with _import_lock:
        if _IMPORT_CACHE['yolo'] is None and not _IMPORT_CACHE['initialized']:
            _IMPORT_CACHE['yolo'] = safe_import_yolo()
        return _IMPORT_CACHE['yolo']

def get_cached_numpy() -> Optional[Any]:
    """Get cached NumPy import"""
    with _import_lock:
        if _IMPORT_CACHE['numpy'] is None and not _IMPORT_CACHE['initialized']:
            try:
                import numpy as np
                _IMPORT_CACHE['numpy'] = np
            except ImportError as e:
                logger.error(f"NumPy import failed: {e}")
                _IMPORT_CACHE['numpy'] = None
        return _IMPORT_CACHE['numpy']

# =============================================================================
# SAFE IMPORT FUNCTIONS (INTERNAL)
# =============================================================================
def safe_import_torch() -> Optional[Any]:
    """Safely import PyTorch with error handling"""
    try:
        import torch
        return torch
    except ImportError as e:
        logger.error(f"PyTorch import failed: {e}")
        return None

def safe_import_yolo() -> Optional[Any]:
    """Safely import YOLOv8 with error handling"""
    try:
        from ultralytics import YOLO
        return YOLO
    except ImportError as e:
        logger.error(f"YOLOv8 import failed: {e}")
        return None

def safe_import_torchvision() -> Optional[Any]:
    """Safely import torchvision with error handling"""
    try:
        from torchvision import models, transforms
        return {"models": models, "transforms": transforms}
    except ImportError as e:
        logger.error(f"torchvision import failed: {e}")
        return None

def safe_import_opencv() -> Optional[Any]:
    """Safely import OpenCV with error handling"""
    try:
        import cv2
        return cv2
    except ImportError as e:
        logger.error(f"OpenCV import failed: {e}")
        return None

# =============================================================================
# MODEL LOADING UTILITIES
# =============================================================================
def fix_efficientnet_classifier(model, num_classes: int = 2):
    """Fix EfficientNet classifier dimensions for binary classification"""
    try:
        import torch
        if hasattr(model, 'classifier'):
            if isinstance(model.classifier, torch.nn.Sequential):
                # For torchvision EfficientNet
                num_ftrs = model.classifier[1].in_features
                model.classifier[1] = torch.nn.Linear(num_ftrs, num_classes)
            else:
                # For other EfficientNet implementations
                num_ftrs = model.classifier.in_features
                model.classifier = torch.nn.Linear(num_ftrs, num_classes)
        return model
    except Exception as e:
        logger.error(f"Failed to fix EfficientNet classifier: {e}")
        return model

def load_model_with_fallback(model_path: str, device: str = "cpu") -> Optional[Any]:
    """Load model with comprehensive fallback handling"""
    torch = safe_import_torch()
    if torch is None:
        return None
    
    try:
        # Try loading with weights_only=False for compatibility
        model = torch.load(model_path, map_location=device, weights_only=False)
        return model
    except Exception as e:
        logger.warning(f"Model loading failed: {e}")
        try:
            # Fallback: try with weights_only=True
            model = torch.load(model_path, map_location=device, weights_only=True)
            return model
        except Exception as e2:
            logger.error(f"Fallback model loading also failed: {e2}")
            return None

# =============================================================================
# INITIALIZATION
# =============================================================================
def initialize_imports_once():
    """Initialize all imports once and cache them"""
    with _import_lock:
        # Check if import cache is disabled
        if os.environ.get("DISABLE_IMPORT_CACHE", "0") == "1":
            print("[INFO] Import cache disabled by environment variable")
            # Import numpy directly to ensure it's available
            try:
                import numpy as np
                return {
                    'torch': True,
                    'yolo': False,
                    'torchvision': True,
                    'opencv': True,
                    'numpy': np,
                    'cuda': {'available': False, 'device_name': None, 'cuda_version': None, 'memory_gb': None},
                    'initialized': True
                }
            except ImportError:
                return {
                    'torch': True,
                    'yolo': False,
                    'torchvision': True,
                    'opencv': True,
                    'numpy': None,
                    'cuda': {'available': False, 'device_name': None, 'cuda_version': None, 'memory_gb': None},
                    'initialized': True
                }
        
        if _IMPORT_CACHE['initialized']:
            return _IMPORT_CACHE
        
        print("[INIT] Setting up centralized import cache...")
        
        # Setup global warnings once
        setup_global_warnings()
        
        # Cache CUDA status
        _IMPORT_CACHE['cuda_status'] = check_cuda_availability()
        
        # Cache all critical imports (YOLO excluded for on-demand loading)
        print("[IMPORT] Importing torch...")
        _IMPORT_CACHE['torch'] = safe_import_torch()
        print("[OK] torch imported")
        
        print("[IMPORT] Importing torchvision...")
        _IMPORT_CACHE['torchvision'] = safe_import_torchvision()
        print("[OK] torchvision imported")
        
        print("[IMPORT] Importing opencv...")
        _IMPORT_CACHE['cv2'] = safe_import_opencv()
        print("[OK] opencv imported")
        
        print("[IMPORT] Importing numpy...")
        try:
            import numpy as np
            _IMPORT_CACHE['numpy'] = np
            print("[OK] numpy imported")
        except ImportError as e:
            print(f"[ERROR] NumPy import failed: {e}")
            _IMPORT_CACHE['numpy'] = None
        # YOLO will be loaded on-demand to prevent startup hanging
        
        # Mark as initialized
        _IMPORT_CACHE['initialized'] = True
        
        # Create import status summary (YOLO will be loaded on-demand)
        import_status = {
            "torch": _IMPORT_CACHE['torch'] is not None,
            "yolo": False,  # Will be loaded on-demand to prevent startup hanging
            "torchvision": _IMPORT_CACHE['torchvision'] is not None,
            "opencv": _IMPORT_CACHE['cv2'] is not None,
            "cuda": _IMPORT_CACHE['cuda_status']
        }
        
        print(f"[OK] Import status: {import_status}")
        print("[OK] Centralized import cache initialized")
        
        return _IMPORT_CACHE

def get_cached_imports() -> Dict[str, Any]:
    """Get all cached imports (initialize if needed)"""
    if not _IMPORT_CACHE['initialized']:
        initialize_imports_once()
    return _IMPORT_CACHE

def initialize_imports():
    """Legacy function for backward compatibility"""
    return initialize_imports_once()

# Initialize on import (but only once)
IMPORT_STATUS = initialize_imports_once()
