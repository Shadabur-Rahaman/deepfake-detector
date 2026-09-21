"""
YOLOv8 Detection Scorer
=======================

Face quality assessment using YOLOv8 for deepfake detection.
Provides confidence scores, face size metrics, and blur detection.

Author: Deepfake Detection System
Version: 1.0.0
"""

import logging
import numpy as np
import cv2
from typing import List, Dict, Any, Optional
from .face_data_validator import FaceDataValidator

logger = logging.getLogger(__name__)

class YOLOv8DetectionScorer:
    """
    YOLOv8-based face quality scorer for deepfake detection
    """
    
    def __init__(self):
        self.face_validator = FaceDataValidator()
        self.is_initialized = False
        self._initialize_yolo()
    
    def _initialize_yolo(self):
        """Initialize YOLOv8 model for face detection"""
        try:
            # Try to import ultralytics YOLOv8
            from ultralytics import YOLO
            
            # Load YOLOv8 face detection model
            self.yolo_model = YOLO('yolov8n.pt')  # Use nano for speed
            self.is_initialized = True
            logger.info("✅ YOLOv8 Detection Scorer initialized successfully")
            
        except ImportError:
            logger.warning("⚠️ ultralytics not available, using OpenCV fallback")
            self._initialize_opencv_fallback()
        except Exception as e:
            logger.warning(f"⚠️ YOLOv8 initialization failed: {e}, using OpenCV fallback")
            self._initialize_opencv_fallback()
    
    def _initialize_opencv_fallback(self):
        """Initialize OpenCV-based face detection as fallback"""
        try:
            # Load OpenCV Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.error("❌ Failed to load OpenCV Haar cascade")
                self.is_initialized = False
            else:
                self.is_initialized = True
                logger.info("✅ YOLOv8 Detection Scorer initialized with OpenCV fallback")
                
        except Exception as e:
            logger.error(f"❌ OpenCV fallback initialization failed: {e}")
            self.is_initialized = False
    
    def score_faces(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """
        Score face quality using YOLOv8 or OpenCV fallback
        
        Args:
            faces: List of face images as numpy arrays
            
        Returns:
            Dictionary with quality scores and metrics including prediction
        """
        if not self.is_initialized:
            logger.warning("⚠️ YOLOv8 Detection Scorer not initialized")
            return self._get_default_scores(len(faces))
        
        # Validate all faces first
        validated_faces = self.face_validator.validate_face_list(faces, "yolov8_scorer")
        
        if not validated_faces:
            logger.warning("⚠️ No valid faces provided to YOLOv8 scorer")
            return self._get_default_scores(len(faces))
        
        try:
            if hasattr(self, 'yolo_model'):
                scores = self._score_with_yolo(validated_faces)
            else:
                scores = self._score_with_opencv(validated_faces)
            
            # Add prediction based on quality scores
            prediction_result = self.get_quality_prediction(scores)
            scores.update(prediction_result)
            
            return scores
                
        except Exception as e:
            logger.error(f"❌ Face scoring failed: {e}")
            return self._get_default_scores(len(validated_faces))
    
    def _score_with_yolo(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """Score faces using YOLOv8 model"""
        try:
            scores = []
            confidences = []
            face_sizes = []
            blur_scores = []
            
            for face in faces:
                # Resize face for YOLOv8 (640x640)
                face_resized = cv2.resize(face, (640, 640))
                
                # Run YOLOv8 detection
                results = self.yolo_model(face_resized, verbose=False)
                
                # Extract face detection results
                face_detections = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            # Filter for person class (class 0 in COCO)
                            if int(box.cls) == 0:  # Person class
                                conf = float(box.conf)
                                if conf > 0.3:  # Minimum confidence threshold
                                    face_detections.append(conf)
                
                # Calculate metrics
                if face_detections:
                    max_conf = max(face_detections)
                    confidences.append(max_conf)
                    
                    # Face size score (larger faces are better)
                    face_area = face.shape[0] * face.shape[1]
                    size_score = min(1.0, face_area / (224 * 224))  # Normalize to 224x224
                    face_sizes.append(size_score)
                    
                    # Blur detection using Laplacian variance
                    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if len(face.shape) == 3 else face
                    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                    blur_scores.append(min(1.0, blur_score / 1000))  # Normalize
                    
                    # Overall quality score
                    quality_score = (max_conf * 0.4 + size_score * 0.3 + blur_score * 0.3)
                    scores.append(quality_score)
                else:
                    # No face detected
                    confidences.append(0.0)
                    face_sizes.append(0.0)
                    blur_scores.append(0.0)
                    scores.append(0.0)
            
            return {
                'model': 'YOLOv8',
                'face_count': len(faces),
                'detected_faces': sum(1 for c in confidences if c > 0.3),
                'avg_confidence': np.mean(confidences) if confidences else 0.0,
                'avg_face_size': np.mean(face_sizes) if face_sizes else 0.0,
                'avg_blur_score': np.mean(blur_scores) if blur_scores else 0.0,
                'avg_quality_score': np.mean(scores) if scores else 0.0,
                'individual_scores': scores,
                'detection_rate': sum(1 for c in confidences if c > 0.3) / len(faces) if faces else 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ YOLOv8 scoring failed: {e}")
            return self._get_default_scores(len(faces))
    
    def _score_with_opencv(self, faces: List[np.ndarray]) -> Dict[str, Any]:
        """Score faces using OpenCV Haar cascade fallback"""
        try:
            scores = []
            confidences = []
            face_sizes = []
            blur_scores = []
            
            for face in faces:
                # Convert to grayscale for OpenCV
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if len(face.shape) == 3 else face
                
                # Enhance image for better detection
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                
                # Detect faces
                detected_faces = self.face_cascade.detectMultiScale(
                    enhanced,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(20, 20)
                )
                
                if len(detected_faces) > 0:
                    # Use the largest detected face
                    largest_face = max(detected_faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = largest_face
                    
                    # Confidence based on face size and detection quality
                    face_area = w * h
                    conf = min(1.0, face_area / (100 * 100))  # Normalize
                    confidences.append(conf)
                    
                    # Face size score
                    size_score = min(1.0, face_area / (224 * 224))
                    face_sizes.append(size_score)
                    
                    # Blur detection
                    face_roi = gray[y:y+h, x:x+w]
                    blur_score = cv2.Laplacian(face_roi, cv2.CV_64F).var()
                    blur_scores.append(min(1.0, blur_score / 1000))
                    
                    # Overall quality score
                    quality_score = (conf * 0.4 + size_score * 0.3 + blur_score * 0.3)
                    scores.append(quality_score)
                else:
                    # No face detected
                    confidences.append(0.0)
                    face_sizes.append(0.0)
                    blur_scores.append(0.0)
                    scores.append(0.0)
            
            return {
                'model': 'OpenCV_Haar',
                'face_count': len(faces),
                'detected_faces': sum(1 for c in confidences if c > 0.1),
                'avg_confidence': np.mean(confidences) if confidences else 0.0,
                'avg_face_size': np.mean(face_sizes) if face_sizes else 0.0,
                'avg_blur_score': np.mean(blur_scores) if blur_scores else 0.0,
                'avg_quality_score': np.mean(scores) if scores else 0.0,
                'individual_scores': scores,
                'detection_rate': sum(1 for c in confidences if c > 0.1) / len(faces) if faces else 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ OpenCV scoring failed: {e}")
            return self._get_default_scores(len(faces))
    
    def _get_default_scores(self, face_count: int) -> Dict[str, Any]:
        """Return default scores when scoring fails"""
        return {
            'model': 'Default',
            'face_count': face_count,
            'detected_faces': 0,
            'avg_confidence': 0.0,
            'avg_face_size': 0.0,
            'avg_blur_score': 0.0,
            'avg_quality_score': 0.0,
            'individual_scores': [0.0] * face_count,
            'detection_rate': 0.0,
            'prediction': 'uncertain',
            'confidence': 0.5,
            'quality_score': 0.0
        }
    
    def get_quality_prediction(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert quality scores to deepfake prediction
        
        Args:
            scores: Quality scores from score_faces()
            
        Returns:
            Prediction with confidence
        """
        try:
            avg_quality = scores.get('avg_quality_score', 0.0)
            detection_rate = scores.get('detection_rate', 0.0)
            avg_confidence = scores.get('avg_confidence', 0.0)
            
            # Combine metrics for prediction
            # Lower quality scores and detection rates suggest potential deepfakes
            if detection_rate < 0.3 or avg_quality < 0.3:
                prediction = 'deepfake'
                confidence = min(0.9, 0.5 + (0.3 - avg_quality) * 2)
            elif detection_rate > 0.7 and avg_quality > 0.6:
                prediction = 'real'
                confidence = min(0.9, 0.5 + (avg_quality - 0.6) * 2)
            else:
                prediction = 'uncertain'
                confidence = 0.5
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'quality_score': avg_quality,
                'detection_rate': detection_rate,
                'model': scores.get('model', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ Quality prediction failed: {e}")
            return {
                'prediction': 'uncertain',
                'confidence': 0.5,
                'quality_score': 0.0,
                'detection_rate': 0.0,
                'model': 'Error'
            }