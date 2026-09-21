"""
Aggressive Deepfake Detector - Enhanced sensitivity for deepfake detection
========================================================================

This module provides aggressive deepfake detection with:
- Lower detection thresholds
- Enhanced artifact detection
- Multiple validation layers
- Bias towards flagging suspicious content
- Advanced pattern recognition

Features:
- Aggressive threshold settings
- Enhanced artifact detection
- Multiple validation passes
- Suspicious content flagging
- Advanced pattern analysis
"""

import asyncio
import logging
import time
import numpy as np
import cv2
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)

# Import face data validator for type conversion
try:
    from .face_data_validator import FaceDataValidator
    FACE_VALIDATOR_AVAILABLE = True
except ImportError:
    FACE_VALIDATOR_AVAILABLE = False
    logger.warning("FaceDataValidator not available")

@dataclass
class AggressiveDetectionResult:
    """Result from aggressive deepfake detection"""
    prediction: str
    confidence: float
    suspicious_score: float
    artifacts_detected: List[str]
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AggressiveDeepfakeDetector:
    """Aggressive deepfake detector with enhanced sensitivity"""
    
    def __init__(self):
        self.initialized = False
        self.device = self._get_optimal_device()
        
        # Aggressive detection parameters
        self.aggressive_threshold = 0.3  # Much lower than normal 0.5
        self.suspicious_threshold = 0.4  # Flag as suspicious
        self.artifact_threshold = 0.2   # Very sensitive to artifacts
        
        # Enhanced detection weights
        self.detection_weights = {
            'artifact_detection': 0.4,
            'texture_analysis': 0.3,
            'edge_analysis': 0.2,
            'color_analysis': 0.1
        }
        
        logger.info(f"[AggressiveDetector] Initialized on device: {self.device}")
        self.initialized = True
    
    def _get_optimal_device(self) -> str:
        """Get optimal device for detection"""
        try:
            from .cuda_safety_manager import get_safe_device
            return get_safe_device()
        except ImportError:
            return "cuda" if torch.cuda.is_available() else "cpu"
    
    def _detect_artifacts(self, face: np.ndarray) -> Dict[str, float]:
        """Detect various artifacts in face images"""
        artifacts = {}
        
        try:
            # Validate face
            if FACE_VALIDATOR_AVAILABLE:
                validated_face = FaceDataValidator.validate_face_for_opencv(face, "aggressive_artifact_detection")
                if validated_face is None:
                    return {'validation_failed': 1.0}
                face = validated_face
            
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            
            # 1. Laplacian variance (blur detection)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            artifacts['blur_artifact'] = min(1.0, max(0.0, (1000 - laplacian_var) / 1000))
            
            # 2. Edge density analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            artifacts['edge_artifact'] = min(1.0, max(0.0, abs(edge_density - 0.1) * 10))
            
            # 3. Frequency domain analysis
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            # Check for high-frequency artifacts
            h, w = magnitude_spectrum.shape
            center_h, center_w = h // 2, w // 2
            
            # High frequency region
            high_freq_region = magnitude_spectrum[center_h-h//4:center_h+h//4, center_w-w//4:center_w+w//4]
            high_freq_mean = np.mean(high_freq_region)
            artifacts['frequency_artifact'] = min(1.0, max(0.0, (high_freq_mean - 3) / 2))
            
            # 4. Color consistency analysis
            # Check for unnatural color patterns
            hsv = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
            h_channel = hsv[:, :, 0]
            s_channel = hsv[:, :, 1]
            v_channel = hsv[:, :, 2]
            
            # Check for color inconsistencies
            h_std = np.std(h_channel)
            s_std = np.std(s_channel)
            v_std = np.std(v_channel)
            
            artifacts['color_artifact'] = min(1.0, max(0.0, (h_std + s_std + v_std) / 100))
            
            # 5. Texture analysis using LBP-like features
            # Simple texture analysis
            texture_variance = np.var(gray)
            artifacts['texture_artifact'] = min(1.0, max(0.0, abs(texture_variance - 1000) / 1000))
            
            # 6. Face symmetry analysis
            h, w = gray.shape
            left_half = gray[:, :w//2]
            right_half = cv2.flip(gray[:, w//2:], 1)
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            symmetry_diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))
            artifacts['symmetry_artifact'] = min(1.0, max(0.0, symmetry_diff / 50))
            
            # 7. Eye region analysis
            # Simple eye detection and analysis
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            eyes = eye_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(eyes) >= 2:
                # Analyze eye regions for artifacts
                eye_artifacts = []
                for (ex, ey, ew, eh) in eyes:
                    eye_region = gray[ey:ey+eh, ex:ex+ew]
                    eye_variance = np.var(eye_region)
                    eye_artifacts.append(eye_variance)
                
                avg_eye_variance = np.mean(eye_artifacts)
                artifacts['eye_artifact'] = min(1.0, max(0.0, abs(avg_eye_variance - 500) / 500))
            else:
                artifacts['eye_artifact'] = 0.8  # High suspicion if eyes not detected properly
            
            # 8. Mouth region analysis
            mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            mouths = mouth_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(mouths) > 0:
                mouth_region = gray[mouths[0][1]:mouths[0][1]+mouths[0][3], mouths[0][0]:mouths[0][0]+mouths[0][2]]
                mouth_variance = np.var(mouth_region)
                artifacts['mouth_artifact'] = min(1.0, max(0.0, abs(mouth_variance - 300) / 300))
            else:
                artifacts['mouth_artifact'] = 0.5  # Medium suspicion if mouth not detected
            
            # 9. Overall image quality
            # Check for compression artifacts
            # Simple quality metric based on gradient
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            quality_score = np.mean(gradient_magnitude)
            artifacts['quality_artifact'] = min(1.0, max(0.0, (100 - quality_score) / 100))
            
            # 10. Noise analysis
            # Check for unnatural noise patterns
            noise_level = np.std(cv2.Laplacian(gray, cv2.CV_64F))
            artifacts['noise_artifact'] = min(1.0, max(0.0, (noise_level - 10) / 20))
            
        except Exception as e:
            logger.warning(f"[AggressiveDetector] Artifact detection failed: {e}")
            artifacts['detection_error'] = 1.0
        
        return artifacts
    
    def _calculate_suspicious_score(self, artifacts: Dict[str, float]) -> float:
        """Calculate overall suspicious score from artifacts"""
        if not artifacts:
            return 0.0
        
        # Weight different artifacts
        weights = {
            'blur_artifact': 0.15,
            'edge_artifact': 0.10,
            'frequency_artifact': 0.15,
            'color_artifact': 0.10,
            'texture_artifact': 0.15,
            'symmetry_artifact': 0.10,
            'eye_artifact': 0.10,
            'mouth_artifact': 0.10,
            'quality_artifact': 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for artifact, score in artifacts.items():
            if artifact in weights:
                total_score += score * weights[artifact]
                total_weight += weights[artifact]
            elif artifact in ['validation_failed', 'detection_error']:
                return 1.0  # Maximum suspicion for errors
        
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0.0
    
    def _get_artifact_descriptions(self, artifacts: Dict[str, float]) -> List[str]:
        """Get human-readable descriptions of detected artifacts"""
        descriptions = []
        
        for artifact, score in artifacts.items():
            if score > self.artifact_threshold:
                if artifact == 'blur_artifact':
                    descriptions.append(f"Excessive blur detected (score: {score:.2f})")
                elif artifact == 'edge_artifact':
                    descriptions.append(f"Unnatural edge patterns (score: {score:.2f})")
                elif artifact == 'frequency_artifact':
                    descriptions.append(f"Frequency domain anomalies (score: {score:.2f})")
                elif artifact == 'color_artifact':
                    descriptions.append(f"Color inconsistencies (score: {score:.2f})")
                elif artifact == 'texture_artifact':
                    descriptions.append(f"Texture irregularities (score: {score:.2f})")
                elif artifact == 'symmetry_artifact':
                    descriptions.append(f"Facial asymmetry (score: {score:.2f})")
                elif artifact == 'eye_artifact':
                    descriptions.append(f"Eye region anomalies (score: {score:.2f})")
                elif artifact == 'mouth_artifact':
                    descriptions.append(f"Mouth region irregularities (score: {score:.2f})")
                elif artifact == 'quality_artifact':
                    descriptions.append(f"Image quality issues (score: {score:.2f})")
                elif artifact == 'noise_artifact':
                    descriptions.append(f"Unnatural noise patterns (score: {score:.2f})")
        
        return descriptions
    
    async def detect_deepfake(self, faces: List[np.ndarray]) -> AggressiveDetectionResult:
        """Aggressively detect deepfakes in face images"""
        start_time = time.time()
        
        try:
            # Validate faces
            validated_faces = faces
            if FACE_VALIDATOR_AVAILABLE:
                validated_faces = FaceDataValidator.validate_face_list(faces, "aggressive_detector")
                if not validated_faces:
                    return AggressiveDetectionResult(
                        prediction="Face Validation Failed",
                        confidence=0.0,
                        suspicious_score=1.0,
                        artifacts_detected=["Face validation failed"],
                        processing_time=time.time() - start_time,
                        success=False,
                        error_message="No valid faces after validation"
                    )
            
            # Analyze each face
            all_artifacts = {}
            total_suspicious_score = 0.0
            face_count = 0
            
            for i, face in enumerate(validated_faces[:10]):  # Limit to first 10 faces
                try:
                    artifacts = self._detect_artifacts(face)
                    suspicious_score = self._calculate_suspicious_score(artifacts)
                    
                    # Accumulate artifacts
                    for artifact, score in artifacts.items():
                        if artifact not in all_artifacts:
                            all_artifacts[artifact] = []
                        all_artifacts[artifact].append(score)
                    
                    total_suspicious_score += suspicious_score
                    face_count += 1
                    
                except Exception as e:
                    logger.warning(f"[AggressiveDetector] Face {i} analysis failed: {e}")
                    continue
            
            if face_count == 0:
                return AggressiveDetectionResult(
                    prediction="No Valid Faces",
                    confidence=0.0,
                    suspicious_score=1.0,
                    artifacts_detected=["No valid faces analyzed"],
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message="No faces could be analyzed"
                )
            
            # Calculate average suspicious score
            avg_suspicious_score = total_suspicious_score / face_count
            
            # Calculate average artifacts
            avg_artifacts = {}
            for artifact, scores in all_artifacts.items():
                avg_artifacts[artifact] = np.mean(scores)
            
            # Get artifact descriptions
            artifact_descriptions = self._get_artifact_descriptions(avg_artifacts)
            
            # Make prediction with aggressive thresholds
            if avg_suspicious_score >= self.aggressive_threshold:
                prediction = "AI-Generated Content Detected"
                confidence = min(0.95, avg_suspicious_score + 0.1)  # Boost confidence for detected deepfakes
            elif avg_suspicious_score >= self.suspicious_threshold:
                prediction = "Suspicious Content - Likely AI-Generated"
                confidence = avg_suspicious_score
            else:
                prediction = "Real Video"
                confidence = 1.0 - avg_suspicious_score
            
            # Additional bias towards flagging suspicious content
            if len(artifact_descriptions) >= 3:  # Multiple artifacts detected
                if prediction == "Real Video":
                    prediction = "Suspicious Content - Multiple Artifacts Detected"
                    confidence = max(confidence, 0.6)
            
            return AggressiveDetectionResult(
                prediction=prediction,
                confidence=confidence,
                suspicious_score=avg_suspicious_score,
                artifacts_detected=artifact_descriptions,
                processing_time=time.time() - start_time,
                success=True,
                metadata={
                    'face_count': face_count,
                    'avg_artifacts': avg_artifacts,
                    'thresholds': {
                        'aggressive': self.aggressive_threshold,
                        'suspicious': self.suspicious_threshold,
                        'artifact': self.artifact_threshold
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"[AggressiveDetector] Detection failed: {e}")
            return AggressiveDetectionResult(
                prediction="Detection Failed",
                confidence=0.0,
                suspicious_score=1.0,
                artifacts_detected=[f"Detection error: {str(e)}"],
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get detector status"""
        return {
            'initialized': self.initialized,
            'device': self.device,
            'aggressive_threshold': self.aggressive_threshold,
            'suspicious_threshold': self.suspicious_threshold,
            'artifact_threshold': self.artifact_threshold,
            'face_validator_available': FACE_VALIDATOR_AVAILABLE
        }

# Global detector instance
aggressive_deepfake_detector = AggressiveDeepfakeDetector()

# Convenience functions
def get_aggressive_detector():
    """Get the global aggressive deepfake detector instance"""
    return aggressive_deepfake_detector

async def detect_with_aggressive_detector(faces: List[np.ndarray]) -> AggressiveDetectionResult:
    """Detect deepfakes using aggressive detection"""
    return await aggressive_deepfake_detector.detect_deepfake(faces)




