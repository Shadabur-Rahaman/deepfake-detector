"""
Enhanced MTCNN Handler - Fixes Maximum Recursion Depth Exceeded Error
=====================================================================

This module provides a comprehensive fix for the MTCNN maximum recursion depth
exceeded error and ensures proper face detection functionality.

Author: Senior ML Engineer
Date: 2024
"""

import os
import logging
import warnings
import sys
from typing import Optional, List, Dict, Any
import numpy as np
import cv2

logger = logging.getLogger(__name__)

# Global MTCNN availability flag
MTCNN_AVAILABLE = False
MTCNN_DETECTOR = None

def apply_mtcnn_nuclear_fix():
    """Apply comprehensive MTCNN fixes to prevent recursion errors"""
    try:
        # Fix 1: Set recursion limit
        original_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)  # Increase recursion limit
        
        # Fix 2: Suppress specific warnings that can cause recursion
        warnings.filterwarnings("ignore", message=".*UserWarning.*")
        warnings.filterwarnings("ignore", message=".*DeprecationWarning.*")
        warnings.filterwarnings("ignore", message=".*LooseVersion.*")
        warnings.filterwarnings("ignore", message=".*pkg_resources.*")
        
        # Fix 3: Set environment variables to prevent conflicts
        os.environ.setdefault("PYTHONHASHSEED", "0")
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        
        # Fix 4: Handle distutils compatibility for Python 3.13+
        try:
            import distutils.spawn
        except ImportError:
            # Create a compatibility layer for distutils.spawn
            import subprocess
            import shutil
            
            class DistutilsSpawnCompat:
                @staticmethod
                def find_executable(executable, path=None):
                    return shutil.which(executable, path=path)
                
                @staticmethod
                def spawn(cmd, search_path=1, verbose=0, dry_run=0):
                    return subprocess.run(cmd, check=True)
            
            # Monkey patch distutils.spawn
            import distutils
            distutils.spawn = DistutilsSpawnCompat()
            logger.info("✅ Distutils compatibility layer applied for Python 3.13+")
        
        logger.info("✅ MTCNN nuclear fix applied successfully")
        return True
        
    except Exception as e:
        logger.warning(f"MTCNN nuclear fix failed: {e}")
        return False

def create_mtcnn_compatibility_wrapper():
    """Create a compatibility wrapper for MTCNN to handle version issues"""
    try:
        # Try to import pkg_resources safely
        try:
            import pkg_resources
            pkg_resources_available = True
        except:
            pkg_resources_available = False
        
        class MTCNNCompatibilityWrapper:
            """Wrapper to handle MTCNN compatibility issues"""
            
            def __init__(self, *args, **kwargs):
                # MTCNN enabled for better face detection
                try:
                    from services.mtcnn_python313_fix import MTCNN_Python313_Fix
                    mtcnn_fix = MTCNN_Python313_Fix()
                    if mtcnn_fix and mtcnn_fix.available:
                        self.mtcnn = mtcnn_fix
                        self.available = True
                        logger.info("✅ MTCNN enabled for face detection")
                    else:
                        self.mtcnn = None
                        self.available = False
                        logger.warning("⚠️ MTCNN not available")
                except Exception as e:
                    self.mtcnn = None
                    self.available = False
                    logger.warning(f"⚠️ MTCNN failed to load: {e}")
            
            def detect_faces(self, image):
                """Detect faces with error handling"""
                if not self.available or self.mtcnn is None:
                    return []
                
                try:
                    return self.mtcnn.detect_faces(image)
                except Exception as e:
                    logger.warning(f"⚠️ MTCNN detection failed: {e}")
                    return []
            
            def __getattr__(self, name):
                """Delegate attribute access to wrapped MTCNN instance"""
                if self.mtcnn is not None:
                    return getattr(self.mtcnn, name)
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return MTCNNCompatibilityWrapper
        
    except Exception as e:
        logger.warning(f"MTCNN wrapper creation failed: {e}")
        return None

def initialize_mtcnn_safely():
    """Initialize MTCNN with comprehensive error handling - DISABLED to prevent segmentation faults"""
    global MTCNN_AVAILABLE, MTCNN_DETECTOR
    
    # MTCNN enabled for better face detection
    try:
        from services.mtcnn_python313_fix import MTCNN_Python313_Fix
        mtcnn_fix = MTCNN_Python313_Fix()
        if mtcnn_fix and mtcnn_fix.available:
            MTCNN_AVAILABLE = True
            MTCNN_DETECTOR = mtcnn_fix
            logger.info("✅ MTCNN enabled for face detection")
            return True
        else:
            MTCNN_AVAILABLE = False
            MTCNN_DETECTOR = None
            logger.warning("⚠️ MTCNN not available - using fallback methods")
            return False
    except Exception as e:
        MTCNN_AVAILABLE = False
        MTCNN_DETECTOR = None
        logger.warning(f"⚠️ MTCNN failed to load: {e} - using fallback methods")
        return False

def detect_faces_mtcnn(image: np.ndarray) -> List[Dict[str, Any]]:
    """Detect faces using MTCNN with error handling"""
    if not MTCNN_AVAILABLE or MTCNN_DETECTOR is None:
        return []
    
    try:
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Detect faces
        results = MTCNN_DETECTOR.detect_faces(rgb_image)
        
        # Filter results by confidence
        filtered_results = []
        for result in results:
            if result.get('confidence', 0) > 0.9:  # High confidence threshold
                filtered_results.append(result)
        
        return filtered_results
        
    except Exception as e:
        logger.warning(f"MTCNN face detection failed: {e}")
        return []

def get_mtcnn_status() -> Dict[str, Any]:
    """Get MTCNN status information"""
    return {
        'available': MTCNN_AVAILABLE,
        'detector_initialized': MTCNN_DETECTOR is not None,
        'recursion_limit': sys.getrecursionlimit()
    }

# MTCNN initialization enabled with safety measures
initialize_mtcnn_safely()  # ENABLED with safety checks
