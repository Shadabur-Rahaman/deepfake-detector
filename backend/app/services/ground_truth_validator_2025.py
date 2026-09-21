"""
Ground Truth Validator 2025 - JARVIS-Level Authentic Content Detection
====================================================================

This module implements advanced ground truth validation to prevent
authentic content from being misclassified as fake. It uses multiple
validation techniques to ensure authentic content is properly recognized.

Author: JARVIS AI Assistant
Date: 2025
"""

import numpy as np
import cv2
import torch
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationMethod(Enum):
    """Validation methods for authentic content detection"""
    NATURAL_MOTION = "natural_motion"
    FACE_CONSISTENCY = "face_consistency"
    LIGHTING_ANALYSIS = "lighting_analysis"
    TEXTURE_AUTHENTICITY = "texture_authenticity"
    TEMPORAL_COHERENCE = "temporal_coherence"
    COMPREHENSIVE = "comprehensive"

@dataclass
class ValidationResult:
    """Result of ground truth validation"""
    is_authentic: bool
    confidence: float
    validation_method: ValidationMethod
    detailed_analysis: Dict[str, Any]
    reasoning: str
    warnings: List[str]
    metadata: Dict[str, Any]

class GroundTruthValidator2025:
    """
    Advanced ground truth validator for authentic content detection
    
    Features:
    - Natural motion analysis
    - Face consistency validation
    - Lighting pattern analysis
    - Texture authenticity checks
    - Temporal coherence validation
    - Multi-modal validation
    """
    
    def __init__(self):
        self.validation_methods = [
            ValidationMethod.NATURAL_MOTION,
            ValidationMethod.FACE_CONSISTENCY,
            ValidationMethod.LIGHTING_ANALYSIS,
            ValidationMethod.TEXTURE_AUTHENTICITY,
            ValidationMethod.TEMPORAL_COHERENCE
        ]
        
        # Validation thresholds
        self.natural_motion_threshold = 0.7
        self.face_consistency_threshold = 0.8
        self.lighting_consistency_threshold = 0.6
        self.texture_authenticity_threshold = 0.7
        self.temporal_coherence_threshold = 0.8
        
        logger.info("🔍 Ground Truth Validator 2025 initialized")
    
    def validate_authentic_content(self, 
                                 faces: List[np.ndarray],
                                 video_path: Optional[str] = None,
                                 title: Optional[str] = None) -> ValidationResult:
        """
        Comprehensive validation of authentic content
        
        Args:
            faces: List of extracted face images
            video_path: Path to video file (optional)
            title: Video title (optional)
            
        Returns:
            ValidationResult with authenticity assessment
        """
        logger.info("🔍 Starting comprehensive authentic content validation")
        
        try:
            validation_results = {}
            overall_authentic_score = 0.0
            total_validations = 0
            
            # Method 1: Natural Motion Analysis
            if len(faces) >= 3:
                motion_result = self._validate_natural_motion(faces)
                validation_results['natural_motion'] = motion_result
                overall_authentic_score += motion_result.confidence
                total_validations += 1
                logger.info(f"   🏃 Natural motion score: {motion_result.confidence:.3f}")
            
            # Method 2: Face Consistency Analysis
            if len(faces) >= 2:
                consistency_result = self._validate_face_consistency(faces)
                validation_results['face_consistency'] = consistency_result
                overall_authentic_score += consistency_result.confidence
                total_validations += 1
                logger.info(f"   👤 Face consistency score: {consistency_result.confidence:.3f}")
            
            # Method 3: Lighting Analysis
            lighting_result = self._validate_lighting_patterns(faces)
            validation_results['lighting_analysis'] = lighting_result
            overall_authentic_score += lighting_result.confidence
            total_validations += 1
            logger.info(f"   💡 Lighting analysis score: {lighting_result.confidence:.3f}")
            
            # Method 4: Texture Authenticity
            texture_result = self._validate_texture_authenticity(faces)
            validation_results['texture_authenticity'] = texture_result
            overall_authentic_score += texture_result.confidence
            total_validations += 1
            logger.info(f"   🎨 Texture authenticity score: {texture_result.confidence:.3f}")
            
            # Method 5: Temporal Coherence
            if len(faces) >= 5:
                temporal_result = self._validate_temporal_coherence(faces)
                validation_results['temporal_coherence'] = temporal_result
                overall_authentic_score += temporal_result.confidence
                total_validations += 1
                logger.info(f"   ⏰ Temporal coherence score: {temporal_result.confidence:.3f}")
            
            # Calculate overall authenticity score
            if total_validations > 0:
                overall_authentic_score /= total_validations
            else:
                overall_authentic_score = 0.5  # Neutral if no validations
            
            # ✅ BIAS FIX: Balanced threshold for proper deepfake detection
            # Use standard threshold for accurate validation
            is_authentic = overall_authentic_score >= 0.5  # Standard threshold for proper detection
            
            # Generate reasoning
            reasoning = self._generate_reasoning(validation_results, overall_authentic_score)
            
            # Generate warnings
            warnings = self._generate_warnings(validation_results)
            
            result = ValidationResult(
                is_authentic=is_authentic,
                confidence=overall_authentic_score,
                validation_method=ValidationMethod.COMPREHENSIVE,
                detailed_analysis=validation_results,
                reasoning=reasoning,
                warnings=warnings,
                metadata={
                    'total_validations': total_validations,
                    'faces_analyzed': len(faces),
                    'video_path': video_path,
                    'title': title
                }
            )
            
            logger.info(f"🔍 Validation completed: {'AUTHENTIC' if is_authentic else 'SUSPICIOUS'}")
            logger.info(f"   📊 Overall score: {overall_authentic_score:.3f}")
            logger.info(f"   🧠 Reasoning: {reasoning}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ground truth validation failed: {e}")
            return ValidationResult(
                is_authentic=False,
                confidence=0.0,
                validation_method=ValidationMethod.COMPREHENSIVE,
                detailed_analysis={},
                reasoning=f"Validation failed: {str(e)}",
                warnings=[f"Validation error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _validate_natural_motion(self, faces: List[np.ndarray]) -> ValidationResult:
        """Validate natural motion patterns in face sequence"""
        try:
            if len(faces) < 3:
                # ✅ BIAS FIX: Neutral default for insufficient frames
                return ValidationResult(
                    is_authentic=False,  # ✅ BIAS FIX: Default to suspicious for insufficient frames
                    confidence=0.3,    # ✅ BIAS FIX: Low confidence for insufficient data
                    validation_method=ValidationMethod.NATURAL_MOTION,
                    detailed_analysis={},
                    reasoning="Insufficient frames for motion analysis - defaulting to suspicious",
                    warnings=["Need at least 3 frames for motion analysis"],
                    metadata={}
                )
            
            # Convert faces to grayscale for motion analysis with proper validation
            gray_faces = []
            for face in faces:
                # ✅ JARVIS FIX: Validate input before OpenCV operations
                if face is None:
                    continue
                    
                # ✅ Ensure it's a numpy array
                if not isinstance(face, np.ndarray):
                    if hasattr(face, 'cpu'):
                        face = face.cpu().numpy()
                    else:
                        face = np.array(face)
                
                # ✅ Ensure proper data type and range
                if face.dtype != np.uint8:
                    face = np.clip(face, 0, 255).astype(np.uint8)
                
                # ✅ Ensure proper shape
                if face.ndim != 3 or face.shape[2] not in [1, 3]:
                    continue
                
                # ✅ Convert to grayscale safely
                if len(face.shape) == 3 and face.shape[2] == 3:
                    # Check if RGB or BGR and convert appropriately
                    if np.mean(face[:, :, 0]) > np.mean(face[:, :, 2]):
                        # Likely RGB, convert to BGR then to grayscale
                        face_bgr = cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
                        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
                    else:
                        # Likely BGR, convert directly
                        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                else:
                    gray = face
                gray_faces.append(gray)
            
            # Calculate optical flow between consecutive frames
            flow_scores = []
            for i in range(len(gray_faces) - 1):
                flow = cv2.calcOpticalFlowPyrLK(
                    gray_faces[i], gray_faces[i + 1], 
                    np.array([[face.shape[1]//2, face.shape[0]//2]], dtype=np.float32).reshape(-1, 1, 2),
                    None
                )[0]
                
                if flow is not None and len(flow) > 0:
                    # Calculate motion magnitude
                    motion_magnitude = np.linalg.norm(flow[0])
                    flow_scores.append(motion_magnitude)
            
            if not flow_scores:
                return ValidationResult(
                    is_authentic=False,
                    confidence=0.3,
                    validation_method=ValidationMethod.NATURAL_MOTION,
                    detailed_analysis={'flow_scores': []},
                    reasoning="No detectable motion",
                    warnings=["No optical flow detected"],
                    metadata={}
                )
            
            # ✅ JARVIS FIX: Analyze motion patterns with more realistic thresholds
            avg_motion = np.mean(flow_scores)
            motion_variance = np.var(flow_scores)
            motion_range = np.max(flow_scores) - np.min(flow_scores)
            
            # ✅ JARVIS FIX: More realistic natural motion scoring that can actually detect fake content
            # Start with neutral score and adjust based on motion characteristics
            natural_motion_score = 0.5  # Start neutral, not biased toward authentic
            
            # ✅ BIAS FIX: Proper motion analysis that can detect both real and fake content
            # Apply penalties for unnatural motion patterns that indicate fake content
            if avg_motion < 0.05:  # Extremely static motion - likely fake
                natural_motion_score = 0.2  # Strong indication of fake content
            elif avg_motion < 0.1:  # Very static motion - suspicious
                natural_motion_score = 0.3  # Moderate indication of fake content
            elif avg_motion < 0.5:  # Low motion - could be real or fake
                natural_motion_score = 0.4  # Neutral-low score
            elif avg_motion < 2.0:  # Normal motion range - likely real
                natural_motion_score = 0.7  # Good score for natural motion
            elif avg_motion < 5.0:  # Higher motion - still likely real
                natural_motion_score = 0.6  # Still good for natural motion
            else:  # Very high motion - could be artificial
                natural_motion_score = 0.3  # Suspicious high motion
            
            # Apply penalties for motion variance patterns that indicate artificial content
            if motion_variance < 0.001:  # Extremely uniform motion - very suspicious
                natural_motion_score *= 0.3  # Strong penalty for artificial uniformity
            elif motion_variance < 0.01:  # Very uniform motion - suspicious
                natural_motion_score *= 0.5  # Significant penalty for uniform motion
            elif motion_variance < 0.05:  # Low variance
                natural_motion_score *= 0.7  # Moderate penalty
            elif motion_variance > 2.0:  # High variance motion - could be artificial
                natural_motion_score *= 0.6  # Penalty for erratic variance
            
            # ✅ JARVIS FIX: Reward natural motion patterns
            # Good motion range (not too static, not too erratic)
            if 0.2 <= motion_range <= 3.0:
                natural_motion_score *= 1.1  # Bonus for natural motion range
            elif 0.1 <= motion_range <= 5.0:
                natural_motion_score *= 1.05  # Small bonus
            
            # ✅ BIAS FIX: Allow full range of scores without artificial minimum
            natural_motion_score = np.clip(natural_motion_score, 0.0, 1.0)
            
            # ✅ BIAS FIX: Proper threshold for deepfake detection
            is_authentic = natural_motion_score >= 0.5  # Standard threshold for proper detection
            
            return ValidationResult(
                is_authentic=is_authentic,
                confidence=natural_motion_score,
                validation_method=ValidationMethod.NATURAL_MOTION,
                detailed_analysis={
                    'avg_motion': avg_motion,
                    'motion_variance': motion_variance,
                    'flow_scores': flow_scores
                },
                reasoning=f"Motion analysis: avg={avg_motion:.2f}, var={motion_variance:.2f}",
                warnings=[],
                metadata={'frames_analyzed': len(faces)}
            )
            
        except Exception as e:
            logger.error(f"Natural motion validation failed: {e}")
            return ValidationResult(
                is_authentic=False,
                confidence=0.0,
                validation_method=ValidationMethod.NATURAL_MOTION,
                detailed_analysis={},
                reasoning=f"Motion analysis failed: {str(e)}",
                warnings=[f"Motion analysis error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _validate_face_consistency(self, faces: List[np.ndarray]) -> ValidationResult:
        """✅ JARVIS FIX: Validate face consistency across frames with improved algorithm"""
        try:
            if len(faces) < 2:
                # ✅ BIAS FIX: Neutral default for insufficient frames
                return ValidationResult(
                    is_authentic=False,  # ✅ BIAS FIX: Default to suspicious for insufficient frames
                    confidence=0.3,    # ✅ BIAS FIX: Low confidence for insufficient data
                    validation_method=ValidationMethod.FACE_CONSISTENCY,
                    detailed_analysis={},
                    reasoning="Insufficient frames for consistency analysis - defaulting to suspicious",
                    warnings=["Need at least 2 frames for consistency analysis"],
                    metadata={}
                )
            
            # ✅ JARVIS FIX: Improved face consistency algorithm
            target_size = (64, 64)  # Smaller size for better performance
            resized_faces = []
            for face in faces:
                try:
                    # ✅ Validate input before OpenCV operations
                    if face is None:
                        continue
                        
                    # ✅ Ensure it's a numpy array
                    if not isinstance(face, np.ndarray):
                        if hasattr(face, 'cpu'):
                            face = face.cpu().numpy()
                        else:
                            face = np.array(face)
                    
                    # ✅ Ensure proper data type and range
                    if face.dtype != np.uint8:
                        face = np.clip(face, 0, 255).astype(np.uint8)
                    
                    # ✅ Ensure proper shape
                    if face.ndim != 3 or face.shape[2] not in [1, 3]:
                        continue
                    
                    # ✅ Now safely resize
                    resized = cv2.resize(face, target_size, interpolation=cv2.INTER_LINEAR)
                    resized_faces.append(resized)
                except Exception as e:
                    logger.warning(f"Face preprocessing failed: {e}")
                    continue
            
            if len(resized_faces) < 2:
                return ValidationResult(
                    is_authentic=True,  # ✅ JARVIS FIX: Default to authentic
                    confidence=0.8,    # ✅ JARVIS FIX: High confidence for insufficient data
                    validation_method=ValidationMethod.FACE_CONSISTENCY,
                    detailed_analysis={'similarity_scores': []},
                    reasoning="Insufficient valid faces for consistency analysis - defaulting to authentic",
                    warnings=["Failed to preprocess sufficient faces"],
                    metadata={'faces_attempted': len(faces)}
                )
            
            # ✅ JARVIS FIX: Multiple similarity metrics for robust consistency analysis
            similarity_scores = []
            for i in range(len(resized_faces) - 1):
                try:
                    # ✅ Safe grayscale conversion
                    if len(resized_faces[i].shape) == 3 and resized_faces[i].shape[2] == 3:
                        # Check if RGB or BGR and convert appropriately
                        if np.mean(resized_faces[i][:, :, 0]) > np.mean(resized_faces[i][:, :, 2]):
                            gray1 = cv2.cvtColor(resized_faces[i], cv2.COLOR_RGB2GRAY)
                        else:
                            gray1 = cv2.cvtColor(resized_faces[i], cv2.COLOR_BGR2GRAY)
                    else:
                        gray1 = resized_faces[i]
                    
                    if len(resized_faces[i + 1].shape) == 3 and resized_faces[i + 1].shape[2] == 3:
                        # Check if RGB or BGR and convert appropriately
                        if np.mean(resized_faces[i + 1][:, :, 0]) > np.mean(resized_faces[i + 1][:, :, 2]):
                            gray2 = cv2.cvtColor(resized_faces[i + 1], cv2.COLOR_RGB2GRAY)
                        else:
                            gray2 = cv2.cvtColor(resized_faces[i + 1], cv2.COLOR_BGR2GRAY)
                    else:
                        gray2 = resized_faces[i + 1]
                    
                    # ✅ JARVIS FIX: Multiple similarity metrics for robust analysis
                    # Method 1: Normalized cross-correlation
                    ncc = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
                    
                    # Method 2: Histogram correlation
                    hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
                    hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
                    hist_corr = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
                    
                    # Method 3: Structural similarity (SSIM approximation)
                    # Calculate mean and variance
                    mean1, mean2 = np.mean(gray1), np.mean(gray2)
                    var1, var2 = np.var(gray1), np.var(gray2)
                    covar = np.mean((gray1 - mean1) * (gray2 - mean2))
                    
                    # SSIM approximation
                    c1, c2 = 0.01**2, 0.03**2
                    ssim = ((2*mean1*mean2 + c1) * (2*covar + c2)) / ((mean1**2 + mean2**2 + c1) * (var1 + var2 + c2))
                    ssim = max(0, min(1, ssim))  # Clamp to [0, 1]
                    
                    # ✅ JARVIS FIX: Combine multiple metrics for robust similarity
                    combined_similarity = (ncc * 0.4 + hist_corr * 0.3 + ssim * 0.3)
                    similarity_scores.append(combined_similarity)
                    
                except Exception as e:
                    logger.warning(f"Similarity calculation failed: {e}")
                    continue
            
            if not similarity_scores:
                return ValidationResult(
                    is_authentic=False,  # ✅ BIAS FIX: Default to suspicious
                    confidence=0.3,    # ✅ BIAS FIX: Low confidence for calculation failure
                    validation_method=ValidationMethod.FACE_CONSISTENCY,
                    detailed_analysis={'similarity_scores': []},
                    reasoning="Similarity calculation failed - defaulting to suspicious",
                    warnings=["Failed to calculate similarity scores"],
                    metadata={'faces_attempted': len(faces)}
                )
            
            # ✅ JARVIS FIX: Improved consistency analysis with more lenient thresholds
            avg_similarity = np.mean(similarity_scores)
            similarity_variance = np.var(similarity_scores)
            min_similarity = np.min(similarity_scores)
            
            # ✅ JARVIS FIX: More realistic consistency scoring for real faces
            # Real faces can have natural variations, so be more lenient
            consistency_score = 1.0
            
            # ✅ BIAS FIX: Proper similarity requirements for face consistency
            if avg_similarity > 0.8:
                consistency_score = 1.0  # High consistency
            elif avg_similarity > 0.6:
                consistency_score = 0.8  # Good consistency
            elif avg_similarity > 0.4:
                consistency_score = 0.6  # Moderate consistency
            elif avg_similarity > 0.2:
                consistency_score = 0.4  # Low consistency - suspicious
            else:
                consistency_score = 0.2  # Very low consistency - likely fake
            
            # ✅ BIAS FIX: Apply proper penalties for variance - high variance indicates inconsistency
            if similarity_variance > 0.15:  # High variance
                consistency_score *= 0.6  # Strong penalty for high variance
            elif similarity_variance > 0.08:  # Moderate variance
                consistency_score *= 0.8  # Moderate penalty
            
            # ✅ JARVIS FIX: Reward minimum similarity consistency
            if min_similarity > 0.2:
                consistency_score *= 1.1  # Bonus for consistent minimum similarity
            elif min_similarity > 0.1:
                consistency_score *= 1.05  # Small bonus
            
            # ✅ JARVIS FIX: Ensure score is in valid range
            consistency_score = np.clip(consistency_score, 0.1, 1.0)
            
            # ✅ BIAS FIX: Standard threshold for face consistency authenticity
            is_authentic = consistency_score >= 0.5  # Standard threshold for proper detection
            
            return ValidationResult(
                is_authentic=is_authentic,
                confidence=consistency_score,
                validation_method=ValidationMethod.FACE_CONSISTENCY,
                detailed_analysis={
                    'avg_similarity': avg_similarity,
                    'similarity_variance': similarity_variance,
                    'min_similarity': min_similarity,
                    'similarity_scores': similarity_scores
                },
                reasoning=f"Face consistency: avg_sim={avg_similarity:.3f}, var={similarity_variance:.3f}, min={min_similarity:.3f}",
                warnings=[],
                metadata={'frames_compared': len(resized_faces) - 1}
            )
            
        except Exception as e:
            logger.error(f"Face consistency validation failed: {e}")
            return ValidationResult(
                is_authentic=False,
                confidence=0.0,
                validation_method=ValidationMethod.FACE_CONSISTENCY,
                detailed_analysis={},
                reasoning=f"Consistency analysis failed: {str(e)}",
                warnings=[f"Consistency analysis error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _validate_lighting_patterns(self, faces: List[np.ndarray]) -> ValidationResult:
        """✅ JARVIS FIX: Validate natural lighting patterns with NaN prevention"""
        try:
            if not faces:
                return ValidationResult(
                    is_authentic=True,  # ✅ JARVIS FIX: Default to authentic if no faces
                    confidence=0.7,    # ✅ JARVIS FIX: Reasonable default confidence
                    validation_method=ValidationMethod.LIGHTING_ANALYSIS,
                    detailed_analysis={},
                    reasoning="No faces for lighting analysis - defaulting to authentic",
                    warnings=["No faces available for lighting analysis"],
                    metadata={}
                )
            
            # ✅ JARVIS FIX: Analyze lighting consistency with proper validation and NaN prevention
            lighting_scores = []
            for face in faces:
                try:
                    # ✅ Validate input before OpenCV operations
                    if face is None:
                        continue
                        
                    # ✅ Ensure it's a numpy array
                    if not isinstance(face, np.ndarray):
                        if hasattr(face, 'cpu'):
                            face = face.cpu().numpy()
                        else:
                            face = np.array(face)
                    
                    # ✅ Ensure proper data type and range
                    if face.dtype != np.uint8:
                        face = np.clip(face, 0, 255).astype(np.uint8)
                    
                    # ✅ Ensure proper shape
                    if face.ndim != 3 or face.shape[2] not in [1, 3]:
                        continue
                    
                    # ✅ Ensure minimum size
                    if face.shape[0] < 10 or face.shape[1] < 10:
                        continue
                    
                    # ✅ Safe grayscale conversion for lighting analysis
                    if len(face.shape) == 3 and face.shape[2] == 3:
                        # Check if RGB or BGR and convert appropriately
                        if np.mean(face[:, :, 0]) > np.mean(face[:, :, 2]):
                            gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face
                    
                    # ✅ JARVIS FIX: Safe lighting analysis with NaN prevention
                    # Calculate lighting gradient with safe parameters
                    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                    
                    # ✅ JARVIS FIX: Safe calculation with NaN prevention
                    mean_gradient = np.mean(gradient_magnitude)
                    if np.isnan(mean_gradient) or np.isinf(mean_gradient):
                        mean_gradient = 50.0  # Safe default
                    
                    # ✅ JARVIS FIX: More conservative lighting smoothness calculation
                    # Natural lighting should have moderate gradients
                    if mean_gradient < 10.0:
                        smoothness = 0.9  # Very smooth (natural)
                    elif mean_gradient < 50.0:
                        smoothness = 0.8  # Moderate smoothness (natural)
                    elif mean_gradient < 100.0:
                        smoothness = 0.6  # Some roughness (still natural)
                    else:
                        smoothness = 0.4  # High gradients (possibly artificial)
                    
                    # ✅ JARVIS FIX: Ensure valid score
                    smoothness = np.clip(smoothness, 0.1, 1.0)
                    lighting_scores.append(smoothness)
                    
                except Exception as face_error:
                    logger.warning(f"Face lighting analysis failed: {face_error}")
                    continue
            
            # ✅ JARVIS FIX: Handle empty scores gracefully
            if not lighting_scores:
                return ValidationResult(
                    is_authentic=True,  # ✅ JARVIS FIX: Default to authentic
                    confidence=0.7,    # ✅ JARVIS FIX: Reasonable default
                    validation_method=ValidationMethod.LIGHTING_ANALYSIS,
                    detailed_analysis={'lighting_scores': []},
                    reasoning="No valid lighting scores - defaulting to authentic",
                    warnings=["Failed to calculate lighting scores for all faces"],
                    metadata={'faces_attempted': len(faces)}
                )
            
            # ✅ JARVIS FIX: Safe statistical calculations with NaN prevention
            avg_lighting_score = np.mean(lighting_scores)
            lighting_variance = np.var(lighting_scores)
            
            # ✅ JARVIS FIX: Ensure no NaN values
            if np.isnan(avg_lighting_score):
                avg_lighting_score = 0.7
            if np.isnan(lighting_variance):
                lighting_variance = 0.05
            
            # ✅ JARVIS FIX: More conservative consistency scoring
            consistency_score = avg_lighting_score
            if lighting_variance > 0.1:
                consistency_score *= 0.9  # ✅ JARVIS FIX: Less harsh penalty for variance
            
            # ✅ JARVIS FIX: Ensure valid final score
            consistency_score = np.clip(consistency_score, 0.1, 1.0)
            
            is_authentic = consistency_score >= 0.5  # ✅ BIAS FIX: Standard threshold for proper detection
            
            return ValidationResult(
                is_authentic=is_authentic,
                confidence=consistency_score,
                validation_method=ValidationMethod.LIGHTING_ANALYSIS,
                detailed_analysis={
                    'avg_lighting_score': avg_lighting_score,
                    'lighting_variance': lighting_variance,
                    'lighting_scores': lighting_scores
                },
                reasoning=f"Lighting analysis: avg={avg_lighting_score:.3f}, var={lighting_variance:.3f}",
                warnings=[],
                metadata={'faces_analyzed': len(lighting_scores)}
            )
            
        except Exception as e:
            logger.error(f"Lighting analysis validation failed: {e}")
            return ValidationResult(
                is_authentic=False,
                confidence=0.0,
                validation_method=ValidationMethod.LIGHTING_ANALYSIS,
                detailed_analysis={},
                reasoning=f"Lighting analysis failed: {str(e)}",
                warnings=[f"Lighting analysis error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _validate_texture_authenticity(self, faces: List[np.ndarray]) -> ValidationResult:
        """✅ JARVIS FIX: Validate texture authenticity with NaN prevention"""
        try:
            if not faces:
                return ValidationResult(
                    is_authentic=True,  # ✅ JARVIS FIX: Default to authentic if no faces
                    confidence=0.7,    # ✅ JARVIS FIX: Reasonable default confidence
                    validation_method=ValidationMethod.TEXTURE_AUTHENTICITY,
                    detailed_analysis={},
                    reasoning="No faces for texture analysis - defaulting to authentic",
                    warnings=["No faces available for texture analysis"],
                    metadata={}
                )
            
            # ✅ JARVIS FIX: Analyze texture authenticity with proper validation and NaN prevention
            texture_scores = []
            for face in faces:
                try:
                    # ✅ Validate input before OpenCV operations
                    if face is None:
                        continue
                        
                    # ✅ Ensure it's a numpy array
                    if not isinstance(face, np.ndarray):
                        if hasattr(face, 'cpu'):
                            face = face.cpu().numpy()
                        else:
                            face = np.array(face)
                    
                    # ✅ Ensure proper data type and range
                    if face.dtype != np.uint8:
                        face = np.clip(face, 0, 255).astype(np.uint8)
                    
                    # ✅ Ensure proper shape
                    if face.ndim != 3 or face.shape[2] not in [1, 3]:
                        continue
                    
                    # ✅ Ensure minimum size
                    if face.shape[0] < 10 or face.shape[1] < 10:
                        continue
                    
                    # ✅ Safe grayscale conversion for texture analysis
                    if len(face.shape) == 3 and face.shape[2] == 3:
                        # Check if RGB or BGR and convert appropriately
                        if np.mean(face[:, :, 0]) > np.mean(face[:, :, 2]):
                            gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face
                    
                    # ✅ JARVIS FIX: Safe texture analysis with NaN prevention
                    # Calculate Local Binary Pattern (LBP) for texture analysis
                    lbp = self._calculate_lbp(gray)
                    
                    # ✅ JARVIS FIX: Safe texture uniformity calculation
                    if len(lbp) == 0:
                        texture_score = 0.7  # Default for empty LBP
                    else:
                        lbp_mean = np.mean(lbp)
                        lbp_std = np.std(lbp)
                        
                        # ✅ JARVIS FIX: Prevent division by zero and NaN
                        if lbp_mean <= 0 or np.isnan(lbp_mean) or np.isnan(lbp_std):
                            texture_score = 0.7  # Safe default
                        else:
                            texture_uniformity = lbp_std / lbp_mean
                            if np.isnan(texture_uniformity) or np.isinf(texture_uniformity):
                                texture_score = 0.7  # Safe default
                            else:
                                # ✅ FIX: Invert texture scoring logic - higher variation = more authentic
                                # Real faces have natural texture variation (uniformity ~0.15-0.45)
                                # Deepfakes have artificial uniformity (uniformity <0.1)
                                # Scale up to proper range: uniformity 0.15-0.45 → score 0.30-0.90
                                texture_score = min(1.0, texture_uniformity * 2.0)  # Scale up for proper range
                    
                    # ✅ BIAS FIX: Allow full range of scores without artificial minimum
                    texture_score = np.clip(texture_score, 0.0, 1.0)
                    texture_scores.append(texture_score)
                    
                except Exception as face_error:
                    logger.warning(f"Face texture analysis failed: {face_error}")
                    continue
            
            # ✅ JARVIS FIX: Handle empty scores gracefully
            if not texture_scores:
                return ValidationResult(
                    is_authentic=True,  # ✅ JARVIS FIX: Default to authentic
                    confidence=0.7,    # ✅ JARVIS FIX: Reasonable default
                    validation_method=ValidationMethod.TEXTURE_AUTHENTICITY,
                    detailed_analysis={'texture_scores': []},
                    reasoning="No valid texture scores - defaulting to authentic",
                    warnings=["Failed to calculate texture scores for all faces"],
                    metadata={'faces_attempted': len(faces)}
                )
            
            # ✅ JARVIS FIX: Safe statistical calculations with NaN prevention
            avg_texture_score = np.mean(texture_scores)
            
            # ✅ JARVIS FIX: Ensure no NaN values
            if np.isnan(avg_texture_score):
                avg_texture_score = 0.7
            
            # ✅ BIAS FIX: Allow full range of scores without artificial minimum
            avg_texture_score = np.clip(avg_texture_score, 0.0, 1.0)
            
            is_authentic = avg_texture_score >= 0.5  # ✅ BIAS FIX: Standard threshold for proper detection
            
            return ValidationResult(
                is_authentic=is_authentic,
                confidence=avg_texture_score,
                validation_method=ValidationMethod.TEXTURE_AUTHENTICITY,
                detailed_analysis={
                    'avg_texture_score': avg_texture_score,
                    'texture_scores': texture_scores
                },
                reasoning=f"Texture authenticity: avg={avg_texture_score:.3f}",
                warnings=[],
                metadata={'faces_analyzed': len(texture_scores)}
            )
            
        except Exception as e:
            logger.error(f"Texture authenticity validation failed: {e}")
            return ValidationResult(
                is_authentic=False,
                confidence=0.0,
                validation_method=ValidationMethod.TEXTURE_AUTHENTICITY,
                detailed_analysis={},
                reasoning=f"Texture analysis failed: {str(e)}",
                warnings=[f"Texture analysis error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _validate_temporal_coherence(self, faces: List[np.ndarray]) -> ValidationResult:
        """Validate temporal coherence across frames"""
        try:
            if len(faces) < 5:
                # ✅ BIAS FIX: Neutral default for insufficient frames
                return ValidationResult(
                    is_authentic=False,  # ✅ BIAS FIX: Default to suspicious for insufficient frames
                    confidence=0.3,    # ✅ BIAS FIX: Low confidence for insufficient data
                    validation_method=ValidationMethod.TEMPORAL_COHERENCE,
                    detailed_analysis={},
                    reasoning="Insufficient frames for temporal analysis - defaulting to suspicious",
                    warnings=["Need at least 5 frames for temporal analysis"],
                    metadata={}
                )
            
            # ✅ JARVIS FIX: Analyze temporal patterns with proper validation
            # Check for sudden changes that might indicate artificial generation
            change_scores = []
            validated_faces = []
            
            # ✅ First, validate all faces
            for face in faces:
                if face is None:
                    continue
                    
                # ✅ Ensure it's a numpy array
                if not isinstance(face, np.ndarray):
                    if hasattr(face, 'cpu'):
                        face = face.cpu().numpy()
                    else:
                        face = np.array(face)
                
                # ✅ Ensure proper data type and range
                if face.dtype != np.uint8:
                    face = np.clip(face, 0, 255).astype(np.uint8)
                
                # ✅ Ensure proper shape
                if face.ndim != 3 or face.shape[2] not in [1, 3]:
                    continue
                
                validated_faces.append(face)
            
            # ✅ Now calculate differences between consecutive validated frames
            for i in range(1, len(validated_faces)):
                # Calculate difference between consecutive frames
                diff = cv2.absdiff(validated_faces[i-1], validated_faces[i])
                change_magnitude = np.mean(diff)
                change_scores.append(change_magnitude)
            
            # Analyze change patterns
            avg_change = np.mean(change_scores)
            change_variance = np.var(change_scores)
            
            # Temporal coherence characteristics:
            # - Gradual changes (not sudden jumps)
            # - Consistent change patterns
            # - Reasonable change magnitude
            
            coherence_score = 1.0
            
            # Penalize too sudden changes
            if avg_change > 50:
                coherence_score *= 0.6
            
            # Penalize too uniform changes (suggests artificial)
            if change_variance < 10:
                coherence_score *= 0.7
            
            # Penalize too variable changes (suggests artificial)
            if change_variance > 200:
                coherence_score *= 0.8
            
            is_authentic = coherence_score >= self.temporal_coherence_threshold
            
            return ValidationResult(
                is_authentic=is_authentic,
                confidence=coherence_score,
                validation_method=ValidationMethod.TEMPORAL_COHERENCE,
                detailed_analysis={
                    'avg_change': avg_change,
                    'change_variance': change_variance,
                    'change_scores': change_scores
                },
                reasoning=f"Temporal coherence: avg_change={avg_change:.1f}, var={change_variance:.1f}",
                warnings=[],
                metadata={'frames_analyzed': len(faces)}
            )
            
        except Exception as e:
            logger.error(f"Temporal coherence validation failed: {e}")
            return ValidationResult(
                is_authentic=False,
                confidence=0.0,
                validation_method=ValidationMethod.TEMPORAL_COHERENCE,
                detailed_analysis={},
                reasoning=f"Temporal analysis failed: {str(e)}",
                warnings=[f"Temporal analysis error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _calculate_lbp(self, image: np.ndarray) -> np.ndarray:
        """Calculate Local Binary Pattern for texture analysis"""
        try:
            # Simple LBP implementation
            rows, cols = image.shape
            lbp = np.zeros_like(image)
            
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    center = image[i, j]
                    binary_string = ""
                    
                    # Check 8 neighbors
                    neighbors = [
                        image[i-1, j-1], image[i-1, j], image[i-1, j+1],
                        image[i, j+1], image[i+1, j+1], image[i+1, j],
                        image[i+1, j-1], image[i, j-1]
                    ]
                    
                    for neighbor in neighbors:
                        binary_string += "1" if neighbor >= center else "0"
                    
                    lbp[i, j] = int(binary_string, 2)
            
            return lbp
            
        except Exception as e:
            logger.error(f"LBP calculation failed: {e}")
            return np.zeros_like(image)
    
    def _generate_reasoning(self, validation_results: Dict[str, ValidationResult], overall_score: float) -> str:
        """Generate human-readable reasoning for validation results"""
        try:
            reasoning_parts = []
            
            if overall_score >= 0.8:
                reasoning_parts.append("High authenticity confidence")
            elif overall_score >= 0.6:
                reasoning_parts.append("Moderate authenticity confidence")
            else:
                reasoning_parts.append("Low authenticity confidence")
            
            # Add specific validation details
            for method, result in validation_results.items():
                if result.is_authentic:
                    reasoning_parts.append(f"{method} indicates authentic content")
                else:
                    reasoning_parts.append(f"{method} shows suspicious patterns")
            
            return "; ".join(reasoning_parts)
            
        except Exception as e:
            return f"Reasoning generation failed: {str(e)}"
    
    def _generate_warnings(self, validation_results: Dict[str, ValidationResult]) -> List[str]:
        """Generate warnings based on validation results"""
        warnings = []
        
        for method, result in validation_results.items():
            if result.confidence < 0.5:
                warnings.append(f"Low confidence in {method}: {result.confidence:.2f}")
            
            if result.warnings:
                warnings.extend(result.warnings)
        
        return warnings

# Global instance for easy access
ground_truth_validator_2025 = GroundTruthValidator2025()

def validate_authentic_content(faces: List[np.ndarray], 
                             video_path: Optional[str] = None,
                             title: Optional[str] = None) -> ValidationResult:
    """Convenience function for authentic content validation"""
    return ground_truth_validator_2025.validate_authentic_content(faces, video_path, title)
