# backend/app/services/deterministic_face_detector.py - Deterministic Face Detection

import cv2
import numpy as np
import torch
import logging
from typing import List, Dict, Tuple, Optional
from .deterministic_config import get_deterministic_config

logger = logging.getLogger(__name__)

class DeterministicFaceDetector:
    """Deterministic face detection for consistent results"""
    
    def __init__(self):
        self.config = get_deterministic_config()
        self.face_cascade = None
        self.yolo_model = None
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize face detection models deterministically"""
        try:
            # Initialize Haar Cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.warning("[WARNING] Haar cascade not loaded properly")
            else:
                logger.info("[OK] Haar cascade initialized")
            
            # Initialize YOLOv8 if available
            try:
                from ultralytics import YOLO
                yolo_path = "yolov8n-face.pt"  # Try face-specific model first
                self.yolo_model = YOLO(yolo_path)
                logger.info("[OK] YOLOv8 face detection initialized")
            except ImportError:
                logger.warning("[WARNING] YOLOv8 not available")
            except Exception as e:
                logger.warning(f"[WARNING] YOLOv8 initialization failed: {e}")
                # Try fallback to general YOLO model
                try:
                    self.yolo_model = YOLO('yolov8n.pt')
                    logger.info("[OK] YOLOv8 general model initialized")
                except Exception as e2:
                    logger.warning(f"[WARNING] YOLOv8 fallback failed: {e2}")
                    self.yolo_model = None
            
        except Exception as e:
            logger.error(f"[ERROR] Face detector initialization failed: {e}")
    
    def detect_faces_haar(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces using Haar cascade with deterministic parameters"""
        try:
            if self.face_cascade is None or self.face_cascade.empty():
                return [], []
            
            # Convert to grayscale for Haar cascade
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Use deterministic parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            face_crops = []
            coordinates = []
            
            for (x, y, w, h) in faces:
                # Ensure coordinates are within frame bounds
                x = max(0, x)
                y = max(0, y)
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)
                
                if w > 0 and h > 0:
                    face_crop = frame[y:y+h, x:x+w]
                    if face_crop.size > 0:
                        face_crops.append(face_crop)
                        coordinates.append({
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h),
                            'method': 'haar'
                        })
            
            return face_crops, coordinates
            
        except Exception as e:
            logger.error(f"[ERROR] Haar face detection failed: {e}")
            return [], []
    
    def detect_faces_yolo(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces using YOLOv8 with deterministic parameters"""
        try:
            if self.yolo_model is None:
                return [], []
            
            # Run YOLO inference with deterministic parameters
            results = self.yolo_model(
                frame,
                conf=0.5,  # Confidence threshold
                iou=0.45,  # IoU threshold
                verbose=False,
                device='cpu'  # Use CPU for deterministic results
            )
            
            face_crops = []
            coordinates = []
            
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    
                    for box, conf in zip(boxes, confidences):
                        x1, y1, x2, y2 = map(int, box[:4])
                        
                        # Ensure coordinates are within frame bounds
                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(x2, frame.shape[1])
                        y2 = min(y2, frame.shape[0])
                        
                        if x2 > x1 and y2 > y1:
                            face_crop = frame[y1:y2, x1:x2]
                            if face_crop.size > 0:
                                face_crops.append(face_crop)
                                coordinates.append({
                                    'x': int(x1),
                                    'y': int(y1),
                                    'width': int(x2 - x1),
                                    'height': int(y2 - y1),
                                    'confidence': float(conf),
                                    'method': 'yolo'
                                })
            
            return face_crops, coordinates
            
        except Exception as e:
            logger.error(f"[ERROR] YOLO face detection failed: {e}")
            return [], []
    
    def detect_faces_deterministic(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces using deterministic approach with fallback"""
        try:
            if frame is None or frame.size == 0:
                return [], []
            
            # Ensure frame is in correct format
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                logger.warning(f"[WARNING] Unexpected frame shape: {frame.shape}")
                return [], []
            
            # Try YOLO first (more accurate)
            if self.yolo_model is not None:
                face_crops, coordinates = self.detect_faces_yolo(frame)
                if face_crops:
                    logger.info(f"[OK] YOLO detected {len(face_crops)} faces")
                    return face_crops, coordinates
            
            # Fallback to Haar cascade
            face_crops, coordinates = self.detect_faces_haar(frame)
            if face_crops:
                logger.info(f"[OK] Haar detected {len(face_crops)} faces")
                return face_crops, coordinates
            
            logger.info("ℹ️ No faces detected")
            return [], []
            
        except Exception as e:
            logger.error(f"[ERROR] Deterministic face detection failed: {e}")
            return [], []
    
    def preprocess_face_deterministic(self, face: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """Preprocess face with deterministic operations"""
        try:
            if face is None or face.size == 0:
                raise ValueError("Empty face input")
            
            # Ensure face is in correct format
            if len(face.shape) != 3 or face.shape[2] != 3:
                raise ValueError(f"Unexpected face shape: {face.shape}")
            
            # Resize with deterministic interpolation
            face_resized = cv2.resize(
                face, 
                target_size, 
                interpolation=cv2.INTER_LINEAR
            )
            
            # Ensure RGB format
            if face_resized.shape[2] == 3:
                face_resized = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
            
            return face_resized
            
        except Exception as e:
            logger.error(f"[ERROR] Face preprocessing failed: {e}")
            # Return a fallback face
            return np.zeros((target_size[0], target_size[1], 3), dtype=np.uint8)

# Global face detector instance
face_detector = DeterministicFaceDetector()

def detect_faces_deterministic(frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
    """Detect faces deterministically"""
    return face_detector.detect_faces_deterministic(frame)

def preprocess_face_deterministic(face: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """Preprocess face deterministically"""
    return face_detector.preprocess_face_deterministic(face, target_size)