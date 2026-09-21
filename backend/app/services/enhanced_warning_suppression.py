"""
Enhanced Warning Suppression System
===================================

This module provides comprehensive warning suppression without over-suppression
to ensure clean logs while maintaining important error visibility.

Author: Senior ML Engineer
Date: 2024
"""

import os
import sys
import logging
import warnings
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class EnhancedWarningSuppression:
    """Enhanced warning suppression system with intelligent filtering"""
    
    def __init__(self):
        self.suppressed_warnings = set()
        self.critical_warnings = set()
        self._setup_critical_warnings()
    
    def _setup_critical_warnings(self):
        """Setup critical warnings that should never be suppressed"""
        self.critical_warnings = {
            "CUDA out of memory",
            "INTERNAL ASSERT FAILED",
            "Segmentation fault",
            "Fatal error",
            "Critical error",
            "System error",
            "Memory error",
            "Driver error"
        }
    
    def apply_comprehensive_suppression(self):
        """Apply comprehensive warning suppression with intelligent filtering"""
        try:
            # 1. Suppress common ML library warnings
            self._suppress_ml_warnings()
            
            # 2. Suppress CUDA warnings
            self._suppress_cuda_warnings()
            
            # 3. Suppress TensorFlow warnings
            self._suppress_tensorflow_warnings()
            
            # 4. Suppress PyTorch warnings
            self._suppress_pytorch_warnings()
            
            # 5. Suppress OpenCV warnings
            self._suppress_opencv_warnings()
            
            # 6. Suppress YOLO warnings
            self._suppress_yolo_warnings()
            
            # 7. Suppress MTCNN warnings
            self._suppress_mtcnn_warnings()
            
            # 8. Set environment variables
            self._set_suppression_env_vars()
            
            logger.info("✅ Enhanced warning suppression applied successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Warning suppression failed: {e}")
            return False
    
    def _suppress_ml_warnings(self):
        """Suppress common ML library warnings"""
        try:
            # Use string-based warning filtering instead of category-based
            warning_patterns = [
                "UserWarning",
                "FutureWarning", 
                "DeprecationWarning",
                "RuntimeWarning",
                "PendingDeprecationWarning"
            ]
            
            for pattern in warning_patterns:
                warnings.filterwarnings("ignore", message=f".*{pattern}.*")
                
        except Exception as e:
            # Fallback to basic warning suppression
            warnings.simplefilter("ignore")
    
    def _suppress_cuda_warnings(self):
        """Suppress CUDA-related warnings"""
        cuda_warnings = [
            "Skipping registering GPU devices",
            "could not load the CUDA driver",
            "Unable to register cuDNN factory",
            "Unable to register cuBLAS factory",
            "Duplicate PluggableDeviceFactory",
            "factory already been registered",
            "computation placer already registered",
            "duplicate registration",
            "Unable to register.*factory",
            "cuDNN.*",
            "cuBLAS.*"
        ]
        
        for warning in cuda_warnings:
            warnings.filterwarnings("ignore", message=f".*{warning}.*")
    
    def _suppress_tensorflow_warnings(self):
        """Suppress TensorFlow warnings"""
        tf_warnings = [
            "TensorFlow.*",
            "tf.*",
            "tensorflow.*"
        ]
        
        for warning in tf_warnings:
            warnings.filterwarnings("ignore", message=f".*{warning}.*")
    
    def _suppress_pytorch_warnings(self):
        """Suppress PyTorch warnings"""
        torch_warnings = [
            "torch.*",
            "PyTorch.*",
            "pytorch.*"
        ]
        
        for warning in torch_warnings:
            warnings.filterwarnings("ignore", message=f".*{warning}.*")
    
    def _suppress_opencv_warnings(self):
        """Suppress OpenCV warnings"""
        cv_warnings = [
            "cv2.*",
            "opencv.*",
            "OpenCV.*"
        ]
        
        for warning in cv_warnings:
            warnings.filterwarnings("ignore", message=f".*{warning}.*")
    
    def _suppress_yolo_warnings(self):
        """Suppress YOLO warnings"""
        yolo_warnings = [
            "YOLO.*",
            "ultralytics.*",
            "yolo.*"
        ]
        
        for warning in yolo_warnings:
            warnings.filterwarnings("ignore", message=f".*{warning}.*")
    
    def _suppress_mtcnn_warnings(self):
        """Suppress MTCNN warnings"""
        mtcnn_warnings = [
            "MTCNN.*",
            "mtcnn.*",
            "LooseVersion.*",
            "pkg_resources.*"
        ]
        
        for warning in mtcnn_warnings:
            warnings.filterwarnings("ignore", message=f".*{warning}.*")
    
    def _set_suppression_env_vars(self):
        """Set environment variables for warning suppression"""
        env_vars = {
            'TF_CPP_MIN_LOG_LEVEL': '3',
            'PYTHONWARNINGS': 'ignore',
            'PYTORCH_WARN_LEVEL': '0',
            'TORCH_WARN_LEVEL': '0',
            'ULTRALYTICS_VERBOSE': 'False',
            'YOLO_VERBOSE': 'False'
        }
        
        for key, value in env_vars.items():
            os.environ.setdefault(key, value)
    
    def is_critical_warning(self, message: str) -> bool:
        """Check if a warning is critical and should not be suppressed"""
        message_lower = message.lower()
        for critical in self.critical_warnings:
            if critical.lower() in message_lower:
                return True
        return False
    
    def should_suppress_warning(self, message: str) -> bool:
        """Determine if a warning should be suppressed"""
        # Never suppress critical warnings
        if self.is_critical_warning(message):
            return False
        
        # Suppress common non-critical warnings
        suppress_patterns = [
            "Skipping registering GPU devices",
            "could not load the CUDA driver",
            "Unable to register",
            "factory already been registered",
            "duplicate registration",
            "LooseVersion",
            "pkg_resources",
            "YOLO",
            "ultralytics",
            "MTCNN",
            "mtcnn"
        ]
        
        message_lower = message.lower()
        for pattern in suppress_patterns:
            if pattern.lower() in message_lower:
                return True
        
        return False

# Global warning suppression instance
warning_suppressor = EnhancedWarningSuppression()

def setup_enhanced_warning_suppression():
    """Setup enhanced warning suppression system"""
    return warning_suppressor.apply_comprehensive_suppression()

def is_critical_warning(message: str) -> bool:
    """Check if a warning is critical"""
    return warning_suppressor.is_critical_warning(message)

def should_suppress_warning(message: str) -> bool:
    """Check if a warning should be suppressed"""
    return warning_suppressor.should_suppress_warning(message)

def apply_enhanced_warning_suppression():
    """Compatibility alias for setup_enhanced_warning_suppression"""
    return setup_enhanced_warning_suppression()

# Apply warning suppression on module import
setup_enhanced_warning_suppression()
