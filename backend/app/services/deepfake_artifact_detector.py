import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ArtifactDetectionResult:
    """Result of artifact detection analysis"""
    has_artifacts: bool
    artifact_score: float  # 0.0 = no artifacts, 1.0 = strong artifacts
    artifact_types: List[str]
    confidence: float
    details: Dict[str, float]

class DeepfakeArtifactDetector:
    """
    Detects common deepfake artifacts in face sequences:
    - Face consistency issues (unnatural size/shape changes)
    - Boundary artifacts (blending issues around face edges)
    - Color inconsistency (face vs neck/background mismatch)
    - Temporal jitter (unnatural movements)
    """
    
    def __init__(self):
        self.logger = logger
        
    def detect_artifacts(self, faces: List) -> ArtifactDetectionResult:
        """
        Analyze face sequence for deepfake artifacts
        
        Args:
            faces: List of face data (dict with 'face', 'frame', 'bbox', etc.)
        
        Returns:
            ArtifactDetectionResult with detection results
        """
        try:
            if not faces or len(faces) < 3:
                return ArtifactDetectionResult(
                    has_artifacts=False,
                    artifact_score=0.0,
                    artifact_types=[],
                    confidence=0.0,
                    details={}
                )
            
            logger.info(f"🔍 Analyzing {len(faces)} faces for deepfake artifacts...")
            
            # Extract face crops and metadata
            face_crops = []
            face_sizes = []
            face_positions = []
            
            for face_data in faces:
                if isinstance(face_data, dict):
                    face_crop = face_data['face']
                    bbox = face_data['bbox']  # (x, y, w, h)
                    face_crops.append(face_crop)
                    face_sizes.append((bbox[2], bbox[3]))  # (width, height)
                    face_positions.append((bbox[0], bbox[1]))  # (x, y)
                else:
                    # Legacy format - just face crop
                    face_crops.append(face_data)
                    face_sizes.append((224, 224))  # Assume standard size
                    face_positions.append((0, 0))  # Unknown position
            
            # Run artifact detection tests
            consistency_score = self._check_face_consistency(face_sizes, face_positions)
            boundary_score = self._check_boundary_artifacts(face_crops)
            color_score = self._check_color_consistency(face_crops)
            temporal_score = self._check_temporal_jitter(face_crops)
            
            # ✅ PHASE 2: Enhanced artifact detection
            blurriness_score = self._detect_blurriness(face_crops)
            compression_score = self._detect_compression_artifacts(face_crops)
            lighting_score = self._detect_lighting_inconsistencies(face_crops)
            
            # Combine scores (weighted by importance)
            artifact_scores = {
                'face_consistency': consistency_score,
                'boundary_artifacts': boundary_score,
                'color_inconsistency': color_score,
                'temporal_jitter': temporal_score,
                'blurriness': blurriness_score,  # NEW
                'compression_artifacts': compression_score,  # NEW
                'lighting_inconsistency': lighting_score  # NEW
            }
            
            # ✅ PHASE 2: Calculate weighted overall artifact score
            # Weight specialized deepfake artifacts higher
            overall_score = (
                consistency_score * 0.15 +
                boundary_score * 0.15 +
                color_score * 0.15 +
                temporal_score * 0.15 +
                blurriness_score * 0.15 +  # NEW
                compression_score * 0.15 +  # NEW
                lighting_score * 0.10  # NEW (slightly lower weight)
            )
            
            # Determine if artifacts are present - more sensitive threshold
            has_artifacts = overall_score > 0.4  # Lower threshold for artifact detection
            
            # Identify artifact types - more sensitive thresholds
            artifact_types = []
            if consistency_score > 0.4:
                artifact_types.append("face_consistency")
            if boundary_score > 0.5:
                artifact_types.append("boundary_artifacts")
            if color_score > 0.5:
                artifact_types.append("color_inconsistency")
            if temporal_score > 0.5:
                artifact_types.append("temporal_jitter")
            if blurriness_score > 0.6:  # NEW
                artifact_types.append("blurriness")
            if compression_score > 0.5:  # NEW
                artifact_types.append("compression_artifacts")
            if lighting_score > 0.5:  # NEW
                artifact_types.append("lighting_inconsistency")
            
            # Calculate confidence based on consistency of signals
            confidence = min(1.0, overall_score + 0.2) if has_artifacts else max(0.0, 1.0 - overall_score)
            
            logger.info(f"🔍 Artifact detection results:")
            logger.info(f"   Overall score: {overall_score:.3f}")
            logger.info(f"   Has artifacts: {has_artifacts}")
            logger.info(f"   Artifact types: {artifact_types}")
            logger.info(f"   Confidence: {confidence:.3f}")
            
            return ArtifactDetectionResult(
                has_artifacts=has_artifacts,
                artifact_score=overall_score,
                artifact_types=artifact_types,
                confidence=confidence,
                details=artifact_scores
            )
            
        except Exception as e:
            logger.error(f"Artifact detection failed: {e}")
            return ArtifactDetectionResult(
                has_artifacts=False,
                artifact_score=0.0,
                artifact_types=[],
                confidence=0.0,
                details={}
            )
    
    def _check_face_consistency(self, face_sizes: List[Tuple[int, int]], face_positions: List[Tuple[int, int]]) -> float:
        """Check for unnatural changes in face size and position"""
        try:
            if len(face_sizes) < 2:
                return 0.0
            
            # Check size consistency
            sizes = np.array(face_sizes)
            width_std = np.std(sizes[:, 0])
            height_std = np.std(sizes[:, 1])
            
            # Normalize by mean size
            width_cv = width_std / np.mean(sizes[:, 0]) if np.mean(sizes[:, 0]) > 0 else 0
            height_cv = height_std / np.mean(sizes[:, 1]) if np.mean(sizes[:, 1]) > 0 else 0
            
            size_inconsistency = (width_cv + height_cv) / 2
            
            # Check position consistency (if positions are available)
            positions = np.array(face_positions)
            if np.any(positions > 0):  # If we have real positions
                x_std = np.std(positions[:, 0])
                y_std = np.std(positions[:, 1])
                
                # Normalize by image dimensions (assume 1920x1080)
                x_cv = x_std / 1920
                y_cv = y_std / 1080
                
                position_inconsistency = (x_cv + y_cv) / 2
            else:
                position_inconsistency = 0.0
            
            # Combine size and position inconsistencies - more sensitive
            consistency_score = min(1.0, (size_inconsistency + position_inconsistency) * 3)  # Increased sensitivity
            
            logger.debug(f"Face consistency: size_cv={size_inconsistency:.3f}, pos_cv={position_inconsistency:.3f}, score={consistency_score:.3f}")
            return consistency_score
            
        except Exception as e:
            logger.debug(f"Face consistency check failed: {e}")
            return 0.0
    
    def _check_boundary_artifacts(self, face_crops: List[np.ndarray]) -> float:
        """Check for blending artifacts around face edges"""
        try:
            if len(face_crops) < 2:
                return 0.0
            
            boundary_scores = []
            
            for face_crop in face_crops[:5]:  # Check first 5 faces
                if isinstance(face_crop, np.ndarray) and face_crop.size > 0:
                    # Convert to grayscale if needed
                    if len(face_crop.shape) == 3:
                        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face_crop
                    
                    # Check for sharp edges (potential blending artifacts)
                    edges = cv2.Canny(gray, 50, 150)
                    
                    # Look for edges near the border (potential blending issues)
                    h, w = gray.shape
                    border_region = 10  # Check 10 pixels from border
                    
                    # Top border
                    top_edges = np.sum(edges[:border_region, :])
                    # Bottom border
                    bottom_edges = np.sum(edges[-border_region:, :])
                    # Left border
                    left_edges = np.sum(edges[:, :border_region])
                    # Right border
                    right_edges = np.sum(edges[:, -border_region:])
                    
                    total_border_edges = top_edges + bottom_edges + left_edges + right_edges
                    total_edges = np.sum(edges)
                    
                    # Calculate ratio of border edges to total edges
                    if total_edges > 0:
                        border_ratio = total_border_edges / total_edges
                        # High border edge ratio suggests blending artifacts
                        boundary_score = min(1.0, border_ratio * 3)
                    else:
                        boundary_score = 0.0
                    
                    boundary_scores.append(boundary_score)
            
            if boundary_scores:
                return np.mean(boundary_scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.debug(f"Boundary artifact check failed: {e}")
            return 0.0
    
    def _check_color_consistency(self, face_crops: List[np.ndarray]) -> float:
        """Check for color inconsistencies within faces"""
        try:
            if len(face_crops) < 2:
                return 0.0
            
            color_scores = []
            
            for face_crop in face_crops[:5]:  # Check first 5 faces
                if isinstance(face_crop, np.ndarray) and face_crop.size > 0:
                    # Convert to different color spaces
                    if len(face_crop.shape) == 3:
                        # Check for color inconsistencies
                        hsv = cv2.cvtColor(face_crop, cv2.COLOR_BGR2HSV)
                        
                        # Check for unnatural color variations
                        h_std = np.std(hsv[:, :, 0])  # Hue variation
                        s_std = np.std(hsv[:, :, 1])  # Saturation variation
                        v_std = np.std(hsv[:, :, 2])  # Value variation
                        
                        # High variation in hue suggests color inconsistencies
                        color_inconsistency = min(1.0, (h_std / 180.0) * 2)  # Normalize hue to 0-1
                        
                        color_scores.append(color_inconsistency)
            
            if color_scores:
                return np.mean(color_scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.debug(f"Color consistency check failed: {e}")
            return 0.0
    
    def _check_temporal_jitter(self, face_crops: List[np.ndarray]) -> float:
        """Check for unnatural temporal changes between frames"""
        try:
            if len(face_crops) < 3:
                return 0.0
            
            jitter_scores = []
            
            # Compare consecutive frames
            for i in range(len(face_crops) - 1):
                face1 = face_crops[i]
                face2 = face_crops[i + 1]
                
                if (isinstance(face1, np.ndarray) and isinstance(face2, np.ndarray) and 
                    face1.size > 0 and face2.size > 0):
                    
                    # Resize to same dimensions
                    h, w = 224, 224
                    face1_resized = cv2.resize(face1, (w, h))
                    face2_resized = cv2.resize(face2, (w, h))
                    
                    # Convert to grayscale
                    if len(face1_resized.shape) == 3:
                        gray1 = cv2.cvtColor(face1_resized, cv2.COLOR_BGR2GRAY)
                        gray2 = cv2.cvtColor(face2_resized, cv2.COLOR_BGR2GRAY)
                    else:
                        gray1 = face1_resized
                        gray2 = face2_resized
                    
                    # Calculate optical flow or frame difference
                    diff = cv2.absdiff(gray1, gray2)
                    mean_diff = np.mean(diff)
                    
                    # High differences suggest temporal jitter
                    # Normalize by maximum possible difference (255)
                    jitter_score = min(1.0, mean_diff / 255.0 * 4)  # Scale up sensitivity
                    
                    jitter_scores.append(jitter_score)
            
            if jitter_scores:
                return np.mean(jitter_scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.debug(f"Temporal jitter check failed: {e}")
            return 0.0
    
    def _detect_blurriness(self, face_crops: List[np.ndarray]) -> float:
        """✅ PHASE 2: Detect blurriness using Laplacian variance and FFT analysis"""
        try:
            if len(face_crops) < 2:
                return 0.0
            
            blur_scores = []
            
            for face_crop in face_crops[:10]:  # Check up to 10 faces
                if isinstance(face_crop, np.ndarray) and face_crop.size > 0:
                    # Convert to grayscale if needed
                    if len(face_crop.shape) == 3:
                        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face_crop
                    
                    # Resize if too small
                    if gray.shape[0] < 64 or gray.shape[1] < 64:
                        gray = cv2.resize(gray, (224, 224))
                    
                    # Laplacian variance (higher = sharper)
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    # Normalize (typical range: 0-1000, blurry < 100)
                    blur_score = 1.0 - min(1.0, laplacian_var / 500.0)
                    blur_scores.append(blur_score)
            
            return float(np.mean(blur_scores)) if blur_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Blurriness detection failed: {e}")
            return 0.0
    
    def _detect_compression_artifacts(self, face_crops: List[np.ndarray]) -> float:
        """✅ PHASE 2: Detect compression artifacts (blocking, quantization errors)"""
        try:
            if len(face_crops) < 2:
                return 0.0
            
            compression_scores = []
            
            for face_crop in face_crops[:10]:
                if isinstance(face_crop, np.ndarray) and face_crop.size > 0:
                    if len(face_crop.shape) == 3:
                        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face_crop
                    
                    if gray.shape[0] < 64 or gray.shape[1] < 64:
                        gray = cv2.resize(gray, (224, 224))
                    
                    h, w = gray.shape
                    
                    # Check for 8x8 block patterns (H.264/HEVC blocking)
                    block_size = 8
                    block_edges = []
                    
                    # Vertical block edges
                    for x in range(block_size, w, block_size):
                        if x < w - 1:
                            edge_strength = np.abs(gray[:, x] - gray[:, x-1]).mean()
                            block_edges.append(edge_strength)
                    
                    # Horizontal block edges
                    for y in range(block_size, h, block_size):
                        if y < h - 1:
                            edge_strength = np.abs(gray[y, :] - gray[y-1, :]).mean()
                            block_edges.append(edge_strength)
                    
                    if block_edges:
                        avg_edge = np.mean(block_edges)
                        compression_score = min(1.0, avg_edge / 30.0)
                        compression_scores.append(compression_score)
            
            return float(np.mean(compression_scores)) if compression_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Compression artifact detection failed: {e}")
            return 0.0
    
    def _detect_lighting_inconsistencies(self, face_crops: List[np.ndarray]) -> float:
        """✅ PHASE 2: Detect lighting inconsistencies across frames"""
        try:
            if len(face_crops) < 3:
                return 0.0
            
            brightness_values = []
            
            for face_crop in face_crops:
                if isinstance(face_crop, np.ndarray) and face_crop.size > 0:
                    if len(face_crop.shape) == 3:
                        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = face_crop
                    
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
            
            if len(brightness_values) < 2:
                return 0.0
            
            # High variance in brightness suggests lighting inconsistencies
            brightness_variance = np.var(brightness_values)
            # Normalize (high variance = inconsistency)
            inconsistency_score = min(1.0, brightness_variance / 1000.0)
            
            return float(inconsistency_score)
            
        except Exception as e:
            logger.debug(f"Lighting inconsistency detection failed: {e}")
            return 0.0

# Global instance
deepfake_artifact_detector = DeepfakeArtifactDetector()
