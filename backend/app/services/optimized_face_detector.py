#!/usr/bin/env python3
"""
Optimized Face Detection Service
===============================

Unified face detection service that combines YOLOv8, OpenCV, and other methods
with optimized error handling and performance for deepfake detection.

Author: Deepfake Detection System
Version: 2.0.0
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Any, Union
import time
import warnings

logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="cv2")

class OptimizedFaceDetector:
    """
    Optimized face detector with multiple detection methods and intelligent fallbacks
    """
    
    def __init__(self, device: str = "cpu"):
        self.device = device
        self.yolo_model = None
        self.opencv_detector = None
        self.is_initialized = False
        self.detection_stats = {
            'yolo_detections': 0,
            'opencv_detections': 0,
            'total_faces': 0,
            'failed_detections': 0
        }
        
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize all available face detection methods"""
        try:
            # Initialize YOLOv8
            self._initialize_yolo()
            
            # Initialize OpenCV detector
            self._initialize_opencv()
            
            self.is_initialized = True
            logger.info("✅ Optimized face detector initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Face detector initialization failed: {e}")
            self.is_initialized = False
    
    def _initialize_yolo(self):
        """Initialize YOLOv8 face detection"""
        try:
            from ultralytics import YOLO
            
            # Try face-specific model first
            yolo_paths = [
                "yolov8n-face.pt",
                "yolov8s-face.pt", 
                "yolov8n.pt",
                "yolov8s.pt"
            ]
            
            for path in yolo_paths:
                try:
                    self.yolo_model = YOLO(path)
                    self.yolo_model.to(self.device)
                    logger.info(f"✅ YOLOv8 initialized with {path}")
                    return
                except Exception as e:
                    logger.debug(f"Failed to load {path}: {e}")
                    continue
            
            logger.warning("⚠️ YOLOv8 initialization failed, using OpenCV fallback")
            self.yolo_model = None
            
        except ImportError:
            logger.warning("⚠️ ultralytics not available, using OpenCV fallback")
            self.yolo_model = None
        except Exception as e:
            logger.warning(f"⚠️ YOLOv8 initialization failed: {e}")
            self.yolo_model = None
    
    def _initialize_opencv(self):
        """Initialize OpenCV face detection"""
        try:
            from .enhanced_opencv_detector import enhanced_opencv_detector
            self.opencv_detector = enhanced_opencv_detector
            logger.info("✅ Enhanced OpenCV detector initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Enhanced OpenCV detector failed: {e}")
            # Fallback to basic OpenCV
            self._initialize_basic_opencv()
    
    def _initialize_basic_opencv(self):
        """Initialize basic OpenCV face detection as fallback"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.opencv_detector = cv2.CascadeClassifier(cascade_path)
            
            if self.opencv_detector.empty():
                raise RuntimeError("Failed to load OpenCV cascade")
            
            logger.info("✅ Basic OpenCV detector initialized")
            
        except Exception as e:
            logger.error(f"❌ Basic OpenCV initialization failed: {e}")
            self.opencv_detector = None
    
    def detect_faces_optimized(self, frame: np.ndarray, 
                             confidence_threshold: float = 0.5,
                             max_faces: int = 10) -> Tuple[List[np.ndarray], List[Dict]]:
        """
        Optimized face detection with intelligent method selection
        
        Args:
            frame: Input image frame
            confidence_threshold: Minimum confidence for detections
            max_faces: Maximum number of faces to return
            
        Returns:
            Tuple of (face_crops, face_metadata)
        """
        if not self.is_initialized:
            logger.warning("⚠️ Face detector not initialized")
            return [], []
        
        if frame is None or frame.size == 0:
            logger.warning("⚠️ Invalid frame provided")
            return [], []
        
        start_time = time.time()
        
        try:
            # Try YOLOv8 first (more accurate)
            if self.yolo_model is not None:
                faces, metadata = self._detect_faces_yolo(frame, confidence_threshold, max_faces)
                if faces:
                    self.detection_stats['yolo_detections'] += len(faces)
                    self.detection_stats['total_faces'] += len(faces)
                    logger.info(f"✅ YOLOv8 detected {len(faces)} faces")
                    return faces, metadata
            
            # Fallback to OpenCV
            if self.opencv_detector is not None:
                faces, metadata = self._detect_faces_opencv(frame, max_faces)
                if faces:
                    self.detection_stats['opencv_detections'] += len(faces)
                    self.detection_stats['total_faces'] += len(faces)
                    logger.info(f"✅ OpenCV detected {len(faces)} faces")
                    return faces, metadata
            
            # No faces detected
            logger.info("ℹ️ No faces detected")
            self.detection_stats['failed_detections'] += 1
            return [], []
            
        except Exception as e:
            logger.error(f"❌ Face detection failed: {e}")
            self.detection_stats['failed_detections'] += 1
            return [], []
        finally:
            detection_time = (time.time() - start_time) * 1000
            logger.debug(f"Face detection completed in {detection_time:.2f}ms")
    
    def _detect_faces_yolo(self, frame: np.ndarray, 
                          confidence_threshold: float, 
                          max_faces: int) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces using YOLOv8"""
        try:
            # Run YOLOv8 inference
            results = self.yolo_model(frame, verbose=False, device=self.device)
            
            faces = []
            metadata = []
            
            for result in results:
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    classes = result.boxes.cls.cpu().numpy()
                    
                    for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                        if conf >= confidence_threshold and cls == 0:  # Person class
                            x1, y1, x2, y2 = map(int, box[:4])
                            
                            # Validate coordinates
                            if (x1 >= 0 and y1 >= 0 and x2 < frame.shape[1] and y2 < frame.shape[0] and
                                x2 - x1 > 30 and y2 - y1 > 30):  # Minimum face size
                                
                                # Extract face crop
                                face_crop = frame[y1:y2, x1:x2]
                                
                                # Convert to RGB for consistency
                                face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                                
                                faces.append(face_rgb)
                                metadata.append({
                                    'bbox': (x1, y1, x2 - x1, y2 - y1),
                                    'confidence': float(conf),
                                    'method': 'yolo',
                                    'class': int(cls)
                                })
                                
                                if len(faces) >= max_faces:
                                    break
            
            return faces, metadata
            
        except Exception as e:
            logger.error(f"❌ YOLOv8 detection failed: {e}")
            return [], []
    
    def _detect_faces_opencv(self, frame: np.ndarray, max_faces: int) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces using OpenCV"""
        try:
            # Check if we have the enhanced detector
            if hasattr(self.opencv_detector, 'detect_faces_enhanced'):
                faces, metadata = self.opencv_detector.detect_faces_enhanced(frame)
                
                # Convert metadata format
                converted_metadata = []
                for meta in metadata:
                    converted_metadata.append({
                        'bbox': meta['bbox'],
                        'confidence': meta['confidence'],
                        'method': 'opencv_enhanced',
                        'quality': meta['quality']
                    })
                
                return faces[:max_faces], converted_metadata[:max_faces]
            
            else:
                # Use basic OpenCV detector
                return self._detect_faces_basic_opencv(frame, max_faces)
                
        except Exception as e:
            logger.error(f"❌ OpenCV detection failed: {e}")
            return [], []
    
    def _detect_faces_basic_opencv(self, frame: np.ndarray, max_faces: int) -> Tuple[List[np.ndarray], List[Dict]]:
        """Detect faces using basic OpenCV Haar cascade"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
            # Detect faces
            faces_detected = self.opencv_detector.detectMultiScale(
                gray,
                scaleFactor=1.02,  # More sensitive scaling
                minNeighbors=2,    # More permissive neighbor requirement
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            faces = []
            metadata = []
            
            for (x, y, w, h) in faces_detected:
                # Extract face crop
                face_crop = frame[y:y+h, x:x+w]
                
                # Convert to RGB for consistency
                face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                
                faces.append(face_rgb)
                metadata.append({
                    'bbox': (x, y, w, h),
                    'confidence': 0.8,  # Default confidence for OpenCV
                    'method': 'opencv_basic'
                })
                
                if len(faces) >= max_faces:
                    break
            
            return faces, metadata
            
        except Exception as e:
            logger.error(f"❌ Basic OpenCV detection failed: {e}")
            return [], []
    
    def preprocess_face_for_analysis(self, face: np.ndarray, 
                                   target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        Preprocess face for deepfake analysis
        
        Args:
            face: Input face image
            target_size: Target size for resizing
            
        Returns:
            Preprocessed face image
        """
        try:
            # Ensure input is valid
            if face is None or face.size == 0:
                raise ValueError("Invalid face input")
            
            # Convert to numpy array if needed
            if not isinstance(face, np.ndarray):
                face = np.array(face)
            
            # Ensure proper data type
            if face.dtype != np.uint8:
                if face.max() <= 1.0:
                    face = (face * 255).astype(np.uint8)
                else:
                    face = np.clip(face, 0, 255).astype(np.uint8)
            
            # Resize to target size
            resized = cv2.resize(face, target_size, interpolation=cv2.INTER_CUBIC)
            
            # Apply histogram equalization for better analysis
            if len(resized.shape) == 3:
                # Color image
                yuv = cv2.cvtColor(resized, cv2.COLOR_RGB2YUV)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                yuv[:, :, 0] = clahe.apply(yuv[:, :, 0])
                enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
            else:
                # Grayscale image
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(resized)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"❌ Face preprocessing failed: {e}")
            return face
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get comprehensive detection statistics"""
        return {
            'initialized': self.is_initialized,
            'yolo_available': self.yolo_model is not None,
            'opencv_available': self.opencv_detector is not None,
            'device': self.device,
            'stats': self.detection_stats.copy(),
            'opencv_version': cv2.__version__
        }
    
    def reset_statistics(self):
        """Reset detection statistics"""
        self.detection_stats = {
            'yolo_detections': 0,
            'opencv_detections': 0,
            'total_faces': 0,
            'failed_detections': 0
        }

# Global instance for easy access
optimized_face_detector = OptimizedFaceDetector()
