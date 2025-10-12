# cuda_safety.py - Comprehensive CUDA safety measures to prevent segmentation faults

import os
import sys
import logging
import warnings
from contextlib import contextmanager
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class CUDASafetyManager:
    """Manages CUDA initialization safely to prevent segmentation faults"""
    
    def __init__(self):
        self.cuda_initialized = False
        self.original_env = {}
        self.safety_measures_applied = False
    
    def apply_safety_measures(self):
        """Apply comprehensive CUDA safety measures"""
        if self.safety_measures_applied:
            return
        
        logger.info("🛡️  Applying CUDA safety measures...")
        
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Set CUDA safety environment variables
        cuda_safety_env = {
            'CUDA_VISIBLE_DEVICES': '-1',  # Disable CUDA initially
            'TF_CPP_MIN_LOG_LEVEL': '3',   # Suppress TensorFlow logs
            'TF_ENABLE_ONEDNN_OPTS': '0',  # Disable oneDNN optimizations
            'TF_DISABLE_MKL': '1',         # Disable MKL
            'TF_FORCE_GPU_ALLOW_GROWTH': 'true',  # Allow GPU memory growth
            'TF_GPU_THREAD_MODE': 'gpu_private',  # Use private GPU threads
            'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:128',  # Limit CUDA memory splits
            'CUDA_LAUNCH_BLOCKING': '0',   # Non-blocking CUDA launches
            'CUDA_CACHE_DISABLE': '1',     # Disable CUDA cache
            'CUDA_CACHE_MAXSIZE': '0',     # Set cache size to 0
        }
        
        for key, value in cuda_safety_env.items():
            os.environ[key] = value
        
        # Suppress CUDA warnings
        self._suppress_cuda_warnings()
        
        self.safety_measures_applied = True
        logger.info("[OK] CUDA safety measures applied")
    
    def _suppress_cuda_warnings(self):
        """Suppress CUDA-related warnings"""
        warning_patterns = [
            ".*Unable to register cuDNN factory.*",
            ".*Unable to register cuBLAS factory.*",
            ".*computation placer already registered.*",
            ".*Duplicate PluggableDeviceFactory.*",
            ".*factory already been registered.*",
            ".*duplicate registration.*",
            ".*Unable to register.*factory.*",
            ".*cuDNN.*",
            ".*cuBLAS.*",
            ".*Skipping registering GPU devices.*",
            ".*could not load the CUDA driver.*",
        ]
        
        for pattern in warning_patterns:
            warnings.filterwarnings("ignore", message=pattern)
        
        # Suppress specific warning categories
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    @contextmanager
    def safe_cuda_context(self, enable_cuda: bool = False):
        """Context manager for safe CUDA operations"""
        if enable_cuda:
            # Temporarily enable CUDA
            original_cuda_devices = os.environ.get('CUDA_VISIBLE_DEVICES', '')
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Enable first GPU
        else:
            # Ensure CUDA is disabled
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        
        try:
            yield
        except Exception as e:
            logger.error(f"CUDA context error: {e}")
            raise
        finally:
            # Restore CUDA visibility
            if enable_cuda:
                os.environ['CUDA_VISIBLE_DEVICES'] = original_cuda_devices
            else:
                os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    
    def safe_import_torch(self) -> Optional[Any]:
        """Safely import PyTorch"""
        try:
            with self.safe_cuda_context(enable_cuda=False):
                import torch
                logger.info("[OK] PyTorch imported safely (CPU mode)")
                return torch
        except Exception as e:
            logger.error(f"[ERROR] Failed to import PyTorch: {e}")
            return None
    
    def safe_import_tensorflow(self) -> Optional[Any]:
        """Safely import TensorFlow"""
        try:
            with self.safe_cuda_context(enable_cuda=False):
                import tensorflow as tf
                # Configure TensorFlow for CPU-only mode
                tf.config.set_visible_devices([], 'GPU')
                logger.info("[OK] TensorFlow imported safely (CPU mode)")
                return tf
        except Exception as e:
            logger.error(f"[ERROR] Failed to import TensorFlow: {e}")
            return None
    
    def safe_import_cv2(self) -> Optional[Any]:
        """Safely import OpenCV"""
        try:
            import cv2
            logger.info("[OK] OpenCV imported safely")
            return cv2
        except Exception as e:
            logger.error(f"[ERROR] Failed to import OpenCV: {e}")
            return None
    
    def check_cuda_availability(self) -> Dict[str, bool]:
        """Check CUDA availability safely"""
        results = {
            'cuda_available': False,
            'torch_cuda': False,
            'tensorflow_gpu': False,
            'cuda_devices': 0
        }
        
        try:
            # Check PyTorch CUDA
            torch = self.safe_import_torch()
            if torch and torch.cuda.is_available():
                results['torch_cuda'] = True
                results['cuda_devices'] = torch.cuda.device_count()
                logger.info(f"[OK] PyTorch CUDA available: {results['cuda_devices']} devices")
            
            # Check TensorFlow GPU
            tf = self.safe_import_tensorflow()
            if tf and len(tf.config.list_physical_devices('GPU')) > 0:
                results['tensorflow_gpu'] = True
                logger.info("[OK] TensorFlow GPU available")
            
            results['cuda_available'] = results['torch_cuda'] or results['tensorflow_gpu']
            
        except Exception as e:
            logger.error(f"[ERROR] CUDA availability check failed: {e}")
        
        return results
    
    def enable_cuda_safely(self) -> bool:
        """Enable CUDA safely after initial setup"""
        try:
            logger.info("[FIX] Enabling CUDA safely...")
            
            # Check if CUDA is available
            cuda_info = self.check_cuda_availability()
            if not cuda_info['cuda_available']:
                logger.warning("[WARNING]  CUDA not available, staying in CPU mode")
                return False
            
            # Enable CUDA
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
            self.cuda_initialized = True
            
            logger.info("[OK] CUDA enabled safely")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to enable CUDA: {e}")
            return False
    
    def restore_environment(self):
        """Restore original environment"""
        if self.original_env:
            os.environ.clear()
            os.environ.update(self.original_env)
            logger.info("[OK] Environment restored")

# Global CUDA safety manager
cuda_safety = CUDASafetyManager()

def initialize_cuda_safety():
    """Initialize CUDA safety measures"""
    cuda_safety.apply_safety_measures()
    return cuda_safety

def get_cuda_safety_manager() -> CUDASafetyManager:
    """Get the global CUDA safety manager"""
    return cuda_safety

# Initialize on import
initialize_cuda_safety()
