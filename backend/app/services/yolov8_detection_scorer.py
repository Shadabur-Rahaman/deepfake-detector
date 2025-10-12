"""
YOLOv8 Detection Scorer - Deepfake Detection Using Face Quality Analysis
======================================================================

This module uses YOLOv8 face detection quality scores to detect deepfake content.
The key insight is that deepfake generation often produces faces with lower detection
confidence or inconsistent detection patterns compared to authentic faces.

Author: AI Assistant
Date: 2025
"""

import numpy as np
import cv2
import torch
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class YOLOv8DetectionResult:
    """Result of YOLOv8-based deepfake detection"""
    prediction: str
    confidence: float
    face_quality_scores: List[float]
    detection_consistency: float
    average_detection_confidence: float
    quality_variance: float
    reasoning: str
    metadata: Dict[str, Any]

class YOLOv8DetectionScorer:
    """
    YOLOv8-based deepfake detection using face quality analysis
    
    Features:
    - Face detection quality analysis
    - Detection consistency across frames
    - Quality variance analysis
    - Confidence pattern analysis
    """
    
    def __init__(self):
        self.yolo_model = None
        self.quality_threshold = 0.7  # Threshold for high-quality face detection
        self.consistency_threshold = 0.8  # Threshold for detection consistency
        self.quality_weight = 0.4  # Weight for face quality
        self.consistency_weight = 0.3  # Weight for detection consistency
        self.variance_weight = 0.3  # Weight for quality variance
        
        # Initialize YOLOv8 if available
        self._initialize_yolo()
    
    def _initialize_yolo(self):
        """Initialize YOLOv8 face detection model"""
        try:
            # Try to import and load YOLOv8 face detection
            from ultralytics import YOLO
            
            # Load YOLOv8 face detection model with CPU device
            self.yolo_model = YOLO('yolov8n-face.pt')
            # Force CPU mode to avoid CUDA driver errors
            self.yolo_model.to('cpu')
            logger.info("✅ YOLOv8 face detection model loaded successfully on CPU")
            
        except ImportError:
            logger.warning("⚠️ YOLOv8 not available, using OpenCV fallback")
            self.yolo_model = None
        except Exception as e:
            logger.warning(f"⚠️ Failed to load YOLOv8: {e}, using OpenCV fallback")
            self.yolo_model = None
    
    def analyze_faces_for_deepfake(self, faces: List[np.ndarray], video_path: Optional[str] = None) -> YOLOv8DetectionResult:
        """
        Analyze faces using YOLOv8 detection quality for deepfake detection
        
        Args:
            faces: List of face images
            video_path: Optional video path for additional context
            
        Returns:
            YOLOv8DetectionResult with deepfake analysis
        """
        try:
            if not faces:
                return self._create_empty_result("No faces provided")
            
            logger.info(f"🔍 YOLOv8 Detection Analysis: Processing {len(faces)} faces")
            
            # Analyze face detection quality
            quality_scores = []
            detection_confidences = []
            
            for i, face in enumerate(faces):
                try:
                    # Convert face to proper format
                    face_processed = self._preprocess_face(face)
                    if face_processed is None:
                        continue
                    
                    # Get detection quality score
                    quality_score, detection_conf = self._analyze_face_quality(face_processed)
                    quality_scores.append(quality_score)
                    detection_confidences.append(detection_conf)
                    
                    logger.debug(f"Face {i}: quality={quality_score:.3f}, conf={detection_conf:.3f}")
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze face {i}: {e}")
                    continue
            
            if not quality_scores:
                return self._create_empty_result("No valid face analysis")
            
            # Calculate detection metrics
            avg_quality = np.mean(quality_scores)
            avg_confidence = np.mean(detection_confidences)
            quality_variance = np.var(quality_scores)
            detection_consistency = self._calculate_detection_consistency(detection_confidences)
            
            # Calculate deepfake probability based on quality analysis
            deepfake_probability = self._calculate_deepfake_probability(
                avg_quality, avg_confidence, quality_variance, detection_consistency
            )
            
            # Determine prediction
            if deepfake_probability >= 0.5:
                prediction = "Deepfake Detected"
                confidence = deepfake_probability
            else:
                prediction = "Real Face"
                confidence = 1.0 - deepfake_probability
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                avg_quality, avg_confidence, quality_variance, detection_consistency, deepfake_probability
            )
            
            result = YOLOv8DetectionResult(
                prediction=prediction,
                confidence=confidence,
                face_quality_scores=quality_scores,
                detection_consistency=detection_consistency,
                average_detection_confidence=avg_confidence,
                quality_variance=quality_variance,
                reasoning=reasoning,
                metadata={
                    'faces_analyzed': len(faces),
                    'valid_analyses': len(quality_scores),
                    'deepfake_probability': deepfake_probability,
                    'yolo_model_used': self.yolo_model is not None
                }
            )
            
            logger.info(f"🎯 YOLOv8 Analysis Result: {prediction} (confidence: {confidence:.3f})")
            logger.info(f"   📊 Quality: {avg_quality:.3f}, Consistency: {detection_consistency:.3f}")
            logger.info(f"   📈 Variance: {quality_variance:.3f}, Deepfake Prob: {deepfake_probability:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"YOLOv8 detection analysis failed: {e}")
            return self._create_empty_result(f"Analysis failed: {str(e)}")
    
    def _preprocess_face(self, face) -> Optional[np.ndarray]:
        """Preprocess face for YOLOv8 analysis"""
        try:
            # Convert tensor to numpy if needed
            if isinstance(face, torch.Tensor):
                face = face.detach().cpu().numpy()
                # Handle CHW to HWC if needed
                if len(face.shape) == 3 and face.shape[0] == 3:
                    face = np.transpose(face, (1, 2, 0))
                # Denormalize if normalized
                if face.max() <= 1.0:
                    face = (face * 255).astype(np.uint8)
            
            # Ensure it's a numpy array
            if not isinstance(face, np.ndarray):
                logger.warning(f"Face is not numpy array: {type(face)}")
                return None
            
            # Ensure proper data type
            if face.dtype != np.uint8:
                face = np.clip(face, 0, 255).astype(np.uint8)
            
            # Ensure proper shape
            if len(face.shape) == 3 and face.shape[2] == 3:
                # Already RGB/BGR
                return face
            elif len(face.shape) == 2:
                # Grayscale, convert to RGB
                return cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
            else:
                logger.warning(f"Invalid face shape: {face.shape}")
                return None
                
        except Exception as e:
            logger.warning(f"Face preprocessing failed: {e}")
            return None
    
    def _analyze_face_quality(self, face: np.ndarray) -> Tuple[float, float]:
        """Analyze face quality using YOLOv8 or OpenCV fallback"""
        try:
            if self.yolo_model is not None:
                return self._analyze_with_yolo(face)
            else:
                return self._analyze_with_opencv(face)
                
        except Exception as e:
            logger.warning(f"Face quality analysis failed: {e}")
            return 0.5, 0.5  # Neutral fallback
    
    def _analyze_with_yolo(self, face: np.ndarray) -> Tuple[float, float]:
        """Analyze face quality using YOLOv8"""
        try:
            # Run YOLOv8 detection
            results = self.yolo_model(face, verbose=False)
            
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None and len(result.boxes) > 0:
                    # Get face detection confidence
                    confidences = result.boxes.conf.cpu().numpy()
                    max_confidence = np.max(confidences)
                    
                    # Calculate quality score based on detection confidence and face properties
                    quality_score = self._calculate_yolo_quality_score(face, max_confidence, result)
                    
                    return quality_score, max_confidence
                else:
                    # No face detected - potentially suspicious
                    return 0.2, 0.0
            else:
                # No results - potentially suspicious
                return 0.2, 0.0
                
        except Exception as e:
            logger.warning(f"YOLOv8 analysis failed: {e}")
            return 0.5, 0.5
    
    def _calculate_yolo_quality_score(self, face: np.ndarray, confidence: float, result) -> float:
        """Calculate quality score from YOLOv8 results"""
        try:
            # Base quality from detection confidence
            base_quality = confidence
            
            # Additional quality factors
            face_area = face.shape[0] * face.shape[1]
            size_factor = min(1.0, face_area / 10000)  # Larger faces are generally better quality
            
            # Sharpness factor
            gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY) if len(face.shape) == 3 else face
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_factor = min(1.0, laplacian_var / 1000)
            
            # Combine factors
            quality_score = (base_quality * 0.6 + size_factor * 0.2 + sharpness_factor * 0.2)
            
            return np.clip(quality_score, 0.0, 1.0)
            
        except Exception as e:
            logger.warning(f"YOLOv8 quality calculation failed: {e}")
            return confidence
    
    def _analyze_with_opencv(self, face: np.ndarray) -> Tuple[float, float]:
        """Fallback analysis using OpenCV face detection"""
        try:
            # Load OpenCV face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY) if len(face.shape) == 3 else face
            
            # Detect faces
            faces_detected = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces_detected) > 0:
                # Calculate quality based on detection parameters
                # More faces detected with higher confidence suggests better quality
                face_count = len(faces_detected)
                confidence = min(0.9, face_count * 0.3)  # Approximate confidence
                
                # Calculate quality score
                quality_score = self._calculate_opencv_quality_score(face, faces_detected)
                
                return quality_score, confidence
            else:
                # No face detected
                return 0.2, 0.0
                
        except Exception as e:
            logger.warning(f"OpenCV analysis failed: {e}")
            return 0.5, 0.5
    
    def _calculate_opencv_quality_score(self, face: np.ndarray, faces_detected) -> float:
        """Calculate quality score from OpenCV detection results"""
        try:
            # Base quality from face count (more faces = better detection)
            face_count = len(faces_detected)
            base_quality = min(0.8, face_count * 0.4)
            
            # Size factor
            face_area = face.shape[0] * face.shape[1]
            size_factor = min(1.0, face_area / 10000)
            
            # Sharpness factor
            gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY) if len(face.shape) == 3 else face
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_factor = min(1.0, laplacian_var / 1000)
            
            # Combine factors
            quality_score = (base_quality * 0.4 + size_factor * 0.3 + sharpness_factor * 0.3)
            
            return np.clip(quality_score, 0.0, 1.0)
            
        except Exception as e:
            logger.warning(f"OpenCV quality calculation failed: {e}")
            return 0.5
    
    def _calculate_detection_consistency(self, confidences: List[float]) -> float:
        """Calculate consistency of detection confidences across frames"""
        try:
            if len(confidences) <= 1:
                return 1.0
            
            # Calculate coefficient of variation (lower = more consistent)
            mean_conf = np.mean(confidences)
            std_conf = np.std(confidences)
            
            if mean_conf == 0:
                return 1.0
            
            cv = std_conf / mean_conf
            consistency = 1.0 - min(cv, 1.0)  # Convert to consistency score
            
            return np.clip(consistency, 0.0, 1.0)
            
        except Exception as e:
            logger.warning(f"Consistency calculation failed: {e}")
            return 0.5
    
    def _calculate_deepfake_probability(self, avg_quality: float, avg_confidence: float, 
                                      quality_variance: float, detection_consistency: float) -> float:
        """Calculate deepfake probability based on quality metrics with conservative bias"""
        try:
            # Lower quality and confidence suggest deepfake
            quality_factor = 1.0 - avg_quality  # Invert quality (lower quality = higher fake probability)
            confidence_factor = 1.0 - avg_confidence  # Invert confidence
            
            # Higher variance suggests inconsistency (potential deepfake) - but be more restrictive
            variance_factor = min(quality_variance * 3, 1.0)  # Increased multiplier for more sensitivity
            
            # Lower consistency suggests deepfake
            consistency_factor = 1.0 - detection_consistency
            
            # Weighted combination with reduced weights to favor real content
            deepfake_prob = (
                quality_factor * self.quality_weight * 0.7 +  # 30% reduction
                confidence_factor * 0.15 +  # Reduced from 0.2
                variance_factor * self.variance_weight * 0.8 +  # 20% reduction
                consistency_factor * self.consistency_weight * 0.7  # 30% reduction
            )
            
            # Apply additional conservative bias - reduce final probability by 25%
            conservative_prob = deepfake_prob * 0.75
            
            return np.clip(conservative_prob, 0.0, 1.0)
            
        except Exception as e:
            logger.warning(f"Deepfake probability calculation failed: {e}")
            return 0.5
    
    def _generate_reasoning(self, avg_quality: float, avg_confidence: float, 
                          quality_variance: float, detection_consistency: float, 
                          deepfake_probability: float) -> str:
        """Generate human-readable reasoning for the detection result"""
        try:
            reasoning_parts = []
            
            # Quality analysis
            if avg_quality >= 0.8:
                reasoning_parts.append("high face detection quality")
            elif avg_quality >= 0.6:
                reasoning_parts.append("moderate face detection quality")
            else:
                reasoning_parts.append("low face detection quality")
            
            # Confidence analysis
            if avg_confidence >= 0.8:
                reasoning_parts.append("high detection confidence")
            elif avg_confidence >= 0.6:
                reasoning_parts.append("moderate detection confidence")
            else:
                reasoning_parts.append("low detection confidence")
            
            # Consistency analysis
            if detection_consistency >= 0.8:
                reasoning_parts.append("consistent detection patterns")
            elif detection_consistency >= 0.6:
                reasoning_parts.append("moderate detection consistency")
            else:
                reasoning_parts.append("inconsistent detection patterns")
            
            # Variance analysis
            if quality_variance <= 0.1:
                reasoning_parts.append("low quality variance")
            elif quality_variance <= 0.3:
                reasoning_parts.append("moderate quality variance")
            else:
                reasoning_parts.append("high quality variance")
            
            # Combine reasoning
            reasoning = f"YOLOv8 analysis shows {', '.join(reasoning_parts)} (deepfake probability: {deepfake_probability:.3f})"
            
            return reasoning
            
        except Exception as e:
            logger.warning(f"Reasoning generation failed: {e}")
            return f"YOLOv8 analysis completed (deepfake probability: {deepfake_probability:.3f})"
    
    def _create_empty_result(self, reason: str) -> YOLOv8DetectionResult:
        """Create empty result for error cases"""
        return YOLOv8DetectionResult(
            prediction="Analysis Failed",
            confidence=0.0,
            face_quality_scores=[],
            detection_consistency=0.0,
            average_detection_confidence=0.0,
            quality_variance=0.0,
            reasoning=reason,
            metadata={'error': reason}
        )

# Global instance for easy access
yolov8_detection_scorer = YOLOv8DetectionScorer()
