"""
Enhanced YOLO Handler - Fixes YOLO Availability and CUDA Issues
==============================================================

This module provides comprehensive YOLO handling with proper CUDA support
and error handling to ensure YOLO detection works correctly.

Author: Senior ML Engineer
Date: 2024
"""

import os
import logging
import warnings
import torch
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import cv2

logger = logging.getLogger(__name__)

# Global YOLO availability flags
YOLO_AVAILABLE = False
YOLO_MODEL = None
YOLO_DEVICE = "cpu"

def apply_yolo_environment_fixes():
    """Apply environment fixes for YOLO"""
    try:
        # Set YOLO-specific environment variables
        os.environ.setdefault("ULTRALYTICS_VERBOSE", "False")
        os.environ.setdefault("YOLO_VERBOSE", "False")
        os.environ.setdefault("TORCH_USE_CUDA_DSA", "1")
        os.environ.setdefault("CUDA_LAUNCH_BLOCKING", "0")
        
        # Suppress YOLO warnings
        warnings.filterwarnings("ignore", category=UserWarning, module="ultralytics")
        warnings.filterwarnings("ignore", category=FutureWarning, module="ultralytics")
        warnings.filterwarnings("ignore", message=".*YOLO.*")
        warnings.filterwarnings("ignore", message=".*ultralytics.*")
        
        logger.info("✅ YOLO environment fixes applied")
        return True
        
    except Exception as e:
        logger.warning(f"YOLO environment fixes failed: {e}")
        return False

def get_safe_yolo_device() -> str:
    """Get safe device for YOLO operations"""
    try:
        if torch.cuda.is_available():
            # Test CUDA device safety
            test_tensor = torch.tensor([1.0, 2.0, 3.0])
            test_tensor = test_tensor.to("cuda:0")
            result = test_tensor * 2
            del test_tensor, result
            torch.cuda.empty_cache()
            return "cuda:0"
        else:
            return "cpu"
    except Exception as e:
        logger.warning(f"CUDA device test failed: {e}")
        return "cpu"

def initialize_yolo_safely():
    """Initialize YOLO with comprehensive error handling"""
    global YOLO_AVAILABLE, YOLO_MODEL, YOLO_DEVICE
    
    # Check if YOLO should be disabled
    if os.environ.get("DISABLE_YOLO", "0") == "1" or os.environ.get("DISABLE_YOLO_ON_STARTUP", "0") == "1":
        logger.warning("⚠️ YOLO disabled by environment variable")
        YOLO_AVAILABLE = False
        YOLO_MODEL = None
        return False
    
    try:
        # Apply environment fixes
        apply_yolo_environment_fixes()
        
        # Get safe device
        YOLO_DEVICE = get_safe_yolo_device()
        
        # Try to import YOLO
        try:
            from ultralytics import YOLO
        except ImportError as e:
            logger.warning(f"YOLO import failed: {e}")
            YOLO_AVAILABLE = False
            YOLO_MODEL = None
            return False
        
        # Try to load YOLO model with aggressive memory management
        try:
            # Set aggressive memory management environment variables
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:16,expandable_segments:False"
            os.environ["OMP_NUM_THREADS"] = "1"
            os.environ["MKL_NUM_THREADS"] = "1"
            os.environ["NUMEXPR_NUM_THREADS"] = "1"
            
            # Force garbage collection before YOLO loading
            import gc
            gc.collect()
            
            # Try face-specific model first
            yolo_paths = [
                "yolov8n-face.pt",
                "yolov8n-face-lindevs.pt", 
                "yolov8n.pt"
            ]
            
            model_loaded = False
            for path in yolo_paths:
                if os.path.exists(path):
                    try:
                        YOLO_MODEL = YOLO(path)
                        model_loaded = True
                        logger.info(f"✅ YOLO loaded from {path}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load {path}: {e}")
                        continue
            
            if not model_loaded:
                # Download default model with error handling
                try:
                    YOLO_MODEL = YOLO('yolov8n.pt')
                    logger.info("✅ YOLO loaded with downloaded model")
                except Exception as e:
                    logger.error(f"Failed to load YOLO model: {e}")
                    YOLO_AVAILABLE = False
                    YOLO_MODEL = None
                    return False
            
            # Move model to safe device (FP32 for YOLOv8 - FP16 not fully supported)
            try:
                YOLO_MODEL.to(YOLO_DEVICE)
                # ✅ YOLOv8 FP16 DISABLED: YOLOv8 doesn't fully support FP16 inference
                # Keep model in FP32 to avoid dtype mismatch errors
                # Note: FP16 can cause "expected mat1 and mat2 to have the same dtype" errors
                logger.info(f"✅ YOLOv8 loaded on {YOLO_DEVICE} (FP32)")
            except Exception as device_error:
                logger.warning(f"Failed to move YOLO to {YOLO_DEVICE}: {device_error}")
                YOLO_DEVICE = "cpu"
                YOLO_MODEL.to("cpu")
                logger.info("✅ YOLOv8 moved to CPU")
            
            # Test YOLO functionality
            try:
                test_image = np.zeros((640, 640, 3), dtype=np.uint8)
                results = YOLO_MODEL(test_image, verbose=False)
                YOLO_AVAILABLE = True
                logger.info("✅ YOLO functionality test passed")
                return True
                
            except Exception as test_error:
                logger.warning(f"YOLO functionality test failed: {test_error}")
                YOLO_AVAILABLE = False
                YOLO_MODEL = None
                return False
                
        except Exception as model_error:
            logger.warning(f"YOLO model loading failed: {model_error}")
            YOLO_AVAILABLE = False
            YOLO_MODEL = None
            return False
            
    except Exception as e:
        logger.error(f"YOLO initialization failed: {e}")
        YOLO_AVAILABLE = False
        YOLO_MODEL = None
        return False

def detect_faces_yolo(image: np.ndarray) -> List[Dict[str, Any]]:
    """Detect faces using YOLO with error handling"""
    if not YOLO_AVAILABLE or YOLO_MODEL is None:
        return []
    
    try:
        # Run YOLO inference
        results = YOLO_MODEL(image, verbose=False)
        
        faces = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Check if it's a face class (class 0 in face models)
                    if len(box.cls) > 0 and box.cls[0] == 0:  # Face class
                        confidence = float(box.conf[0])
                        if confidence > 0.5:  # Confidence threshold
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                            
                            # Ensure coordinates are within image bounds
                            h, w = image.shape[:2]
                            x1 = max(0, min(x1, w))
                            y1 = max(0, min(y1, h))
                            x2 = max(0, min(x2, w))
                            y2 = max(0, min(y2, h))
                            
                            if x2 > x1 and y2 > y1:
                                face_data = {
                                    'box': [x1, y1, x2-x1, y2-y1],
                                    'confidence': confidence,
                                    'keypoints': None
                                }
                                faces.append(face_data)
        
        return faces
        
    except Exception as e:
        logger.warning(f"YOLO face detection failed: {e}")
        return []

def get_yolo_status() -> Dict[str, Any]:
    """Get YOLO status information"""
    return {
        'available': YOLO_AVAILABLE,
        'model_loaded': YOLO_MODEL is not None,
        'device': YOLO_DEVICE,
        'cuda_available': torch.cuda.is_available()
    }

# Initialize YOLO on module import
initialize_yolo_safely()
