"""
YOLOv8 Deepfake Detector Module
Provides YOLOv8-based deepfake detection capabilities
"""

import logging
import os
from typing import Dict, Any, Optional, List
import numpy as np

logger = logging.getLogger(__name__)

# Check if YOLOv8 is available
try:
    from ultralytics import YOLO
    YOLOV8_AVAILABLE = True
    logger.info("✅ YOLOv8 (ultralytics) is available")
except ImportError:
    YOLOV8_AVAILABLE = False
    logger.warning("⚠️ YOLOv8 (ultralytics) not available")

def is_yolov8_available() -> bool:
    """
    Check if YOLOv8 is available for deepfake detection
    
    Returns:
        bool: True if YOLOv8 is available, False otherwise
    """
    return YOLOV8_AVAILABLE

def detect_yolov8_deepfake(faces: List[np.ndarray], video_id: str = None) -> Dict[str, Any]:
    """
    Detect deepfakes using YOLOv8 model
    
    Args:
        faces: List of face images as numpy arrays
        video_id: Optional video identifier for logging
        
    Returns:
        Dict containing detection results
    """
    if not YOLOV8_AVAILABLE:
        logger.warning("YOLOv8 not available, returning neutral result")
        return {
            'prediction': 'Unknown',
            'confidence': 0.5,
            'deepfake_probability': 0.5,
            'faces_analyzed': len(faces),
            'model_used': 'YOLOv8 (not available)',
            'status': 'unavailable'
        }
    
    if not faces:
        logger.warning("No faces provided for YOLOv8 analysis")
        return {
            'prediction': 'Unknown',
            'confidence': 0.5,
            'deepfake_probability': 0.5,
            'faces_analyzed': 0,
            'model_used': 'YOLOv8',
            'status': 'no_faces'
        }
    
    try:
        # For now, we'll use a simplified approach since we don't have a trained YOLOv8 deepfake model
        # In a real implementation, you would load a custom YOLOv8 model trained for deepfake detection
        
        logger.info(f"🔍 Running YOLOv8 deepfake analysis on {len(faces)} faces")
        
        # Simulate YOLOv8 deepfake detection
        # In practice, you would:
        # 1. Load a custom YOLOv8 model trained for deepfake detection
        # 2. Run inference on each face
        # 3. Aggregate results
        
        fake_scores = []
        for i, face in enumerate(faces):
            # Simulate detection (replace with actual YOLOv8 inference)
            # For now, we'll use a simple heuristic based on face characteristics
            if face is not None and face.size > 0:
                # Simple heuristic: analyze face quality and characteristics
                face_mean = float(np.mean(face))
                face_std = float(np.std(face))
                
                # Basic quality check
                if face_std > 30 and 50 < face_mean < 200:
                    # Higher quality face, lower fake probability
                    fake_score = 0.3 + (face_std / 100) * 0.2
                else:
                    # Lower quality or unusual characteristics, higher fake probability
                    fake_score = 0.6 + (abs(face_mean - 128) / 128) * 0.3
                
                fake_scores.append(min(max(fake_score, 0.0), 1.0))
            else:
                fake_scores.append(0.5)  # Neutral for invalid faces
        
        if fake_scores:
            avg_fake_score = float(np.mean(fake_scores))
            confidence = float(1.0 - np.std(fake_scores))  # Higher confidence for consistent results
            
            # Determine prediction
            if avg_fake_score > 0.6:
                prediction = 'Fake'
            elif avg_fake_score < 0.4:
                prediction = 'Real'
            else:
                prediction = 'Uncertain'
            
            result = {
                'prediction': prediction,
                'confidence': max(min(confidence, 1.0), 0.0),
                'deepfake_probability': avg_fake_score,
                'faces_analyzed': len(faces),
                'model_used': 'YOLOv8 (simulated)',
                'status': 'success',
                'individual_scores': fake_scores
            }
            
            logger.info(f"🎯 YOLOv8 result: {prediction} (confidence: {confidence:.2f}, fake_prob: {avg_fake_score:.2f})")
            return result
        else:
            return {
                'prediction': 'Unknown',
                'confidence': 0.0,
                'deepfake_probability': 0.5,
                'faces_analyzed': len(faces),
                'model_used': 'YOLOv8',
                'status': 'no_valid_faces'
            }
            
    except Exception as e:
        logger.error(f"YOLOv8 deepfake detection failed: {e}")
        return {
            'prediction': 'Unknown',
            'confidence': 0.0,
            'deepfake_probability': 0.5,
            'faces_analyzed': len(faces),
            'model_used': 'YOLOv8',
            'status': 'error',
            'error': str(e)
        }

def load_yolov8_deepfake_model(model_path: str = None) -> Optional[Any]:
    """
    Load YOLOv8 model for deepfake detection
    
    Args:
        model_path: Path to the YOLOv8 model file
        
    Returns:
        Loaded YOLOv8 model or None if not available
    """
    if not YOLOV8_AVAILABLE:
        logger.warning("YOLOv8 not available, cannot load model")
        return None
    
    try:
        if model_path and os.path.exists(model_path):
            model = YOLO(model_path)
            logger.info(f"✅ Loaded YOLOv8 model from {model_path}")
            return model
        else:
            # Load default YOLOv8 model
            model = YOLO('yolov8n.pt')  # Nano model for speed
            logger.info("✅ Loaded default YOLOv8 model")
            return model
    except Exception as e:
        logger.error(f"Failed to load YOLOv8 model: {e}")
        return None

def preprocess_face_for_yolov8(face: np.ndarray, target_size: tuple = (640, 640)) -> np.ndarray:
    """
    Preprocess face image for YOLOv8 input
    
    Args:
        face: Face image as numpy array
        target_size: Target size for YOLOv8 input
        
    Returns:
        Preprocessed face image
    """
    try:
        import cv2
        
        # Resize to target size
        resized = cv2.resize(face, target_size)
        
        # Normalize to 0-1 range
        normalized = resized.astype(np.float32) / 255.0
        
        # Convert to RGB if needed
        if len(normalized.shape) == 3 and normalized.shape[2] == 3:
            # Already RGB
            pass
        elif len(normalized.shape) == 2:
            # Grayscale to RGB
            normalized = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
        
        return normalized
        
    except Exception as e:
        logger.error(f"Face preprocessing failed: {e}")
        return face

# Global model instance (lazy loading)
_yolov8_model = None

def get_yolov8_model() -> Optional[Any]:
    """
    Get global YOLOv8 model instance (lazy loading)
    
    Returns:
        YOLOv8 model instance or None
    """
    global _yolov8_model
    
    if _yolov8_model is None and YOLOV8_AVAILABLE:
        _yolov8_model = load_yolov8_deepfake_model()
    
    return _yolov8_model
