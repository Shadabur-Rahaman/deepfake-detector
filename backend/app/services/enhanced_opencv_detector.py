#!/usr/bin/env python3
"""
Enhanced OpenCV Face Detector
=============================

Optimized OpenCV face detection with improved error handling, performance,
and reliability for deepfake detection systems.

Author: Deepfake Detection System
Version: 2.0.0
"""

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Any
import warnings

logger = logging.getLogger(__name__)

# Suppress OpenCV warnings
warnings.filterwarnings("ignore", category=UserWarning, module="cv2")

class EnhancedOpenCVDetector:
    """
    Enhanced OpenCV face detector with multiple cascades and optimized parameters
    """
    
    def __init__(self):
        self.face_cascade = None
        self.profile_cascade = None
        self.eye_cascade = None
        self.is_initialized = False
        self._initialize_cascades()
    
    def _initialize_cascades(self):
        """Initialize OpenCV cascades with comprehensive error handling"""
        try:
            # Primary frontal face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                raise RuntimeError("Failed to load frontal face cascade")
            
            # Profile face cascade (optional)
            try:
                profile_path = cv2.data.haarcascades + 'haarcascade_profileface.xml'
                self.profile_cascade = cv2.CascadeClassifier(profile_path)
                if self.profile_cascade.empty():
                    self.profile_cascade = None
                    logger.warning("Profile face cascade not available")
            except Exception:
                self.profile_cascade = None
                logger.warning("Profile face cascade not available")
            
            # Eye cascade for validation (optional)
            try:
                eye_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
                self.eye_cascade = cv2.CascadeClassifier(eye_path)
                if self.eye_cascade.empty():
                    self.eye_cascade = None
                    logger.warning("Eye cascade not available")
            except Exception:
                self.eye_cascade = None
                logger.warning("Eye cascade not available")
            
            self.is_initialized = True
            logger.info("✅ Enhanced OpenCV detector initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenCV cascades: {e}")
            self.is_initialized = False
            raise
    
    def detect_faces_enhanced(self, frame: np.ndarray, 
                            min_face_size: Tuple[int, int] = (30, 30),
                            scale_factor: float = 1.02,  # More sensitive scaling
                            min_neighbors: int = 2) -> Tuple[List[np.ndarray], List[Dict]]:  # More permissive
        """
        Enhanced face detection with multiple cascades and quality assessment
        
        Args:
            frame: Input image frame (BGR format)
            min_face_size: Minimum face size (width, height)
            scale_factor: Scale factor for image pyramid
            min_neighbors: Minimum neighbors for detection
            
        Returns:
            Tuple of (face_crops, face_metadata)
        """
        if not self.is_initialized:
            logger.warning("⚠️ OpenCV detector not initialized")
            return [], []
        
        if frame is None or frame.size == 0:
            logger.warning("⚠️ Empty or invalid frame provided")
            return [], []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for better detection
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            
            # Apply Gaussian blur to reduce noise
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Detect faces with multiple cascades
            all_faces = []
            all_metadata = []
            
            # 1. Frontal face detection
            frontal_faces = self._detect_frontal_faces(gray, min_face_size, scale_factor, min_neighbors)
            all_faces.extend(frontal_faces['faces'])
            all_metadata.extend(frontal_faces['metadata'])
            
            # 2. Profile face detection (if available)
            if self.profile_cascade is not None:
                profile_faces = self._detect_profile_faces(gray, min_face_size, scale_factor, min_neighbors)
                all_faces.extend(profile_faces['faces'])
                all_metadata.extend(profile_faces['metadata'])
            
            # 3. Remove duplicate detections
            unique_faces, unique_metadata = self._remove_duplicate_detections(all_faces, all_metadata)
            
            # 4. Validate faces with eye detection (if available)
            if self.eye_cascade is not None:
                validated_faces, validated_metadata = self._validate_faces_with_eyes(
                    unique_faces, unique_metadata, gray
                )
            else:
                validated_faces, validated_metadata = unique_faces, unique_metadata
            
            logger.info(f"🔍 Enhanced OpenCV detected {len(validated_faces)} faces")
            return validated_faces, validated_metadata
            
        except Exception as e:
            logger.error(f"❌ Enhanced face detection failed: {e}")
            return [], []
    
    def _detect_frontal_faces(self, gray: np.ndarray, min_face_size: Tuple[int, int], 
                            scale_factor: float, min_neighbors: int) -> Dict[str, Any]:
        """Detect frontal faces using Haar cascade"""
        try:
            faces_detected = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_face_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            faces = []
            metadata = []
            
            for (x, y, w, h) in faces_detected:
                # Extract face crop
                face_crop = gray[y:y+h, x:x+w]
                
                # Calculate quality metrics
                quality_metrics = self._calculate_face_quality(face_crop)
                
                faces.append(face_crop)
                metadata.append({
                    'bbox': (x, y, w, h),
                    'type': 'frontal',
                    'quality': quality_metrics,
                    'confidence': quality_metrics['overall_score']
                })
            
            return {'faces': faces, 'metadata': metadata}
            
        except Exception as e:
            logger.error(f"❌ Frontal face detection failed: {e}")
            return {'faces': [], 'metadata': []}
    
    def _detect_profile_faces(self, gray: np.ndarray, min_face_size: Tuple[int, int], 
                            scale_factor: float, min_neighbors: int) -> Dict[str, Any]:
        """Detect profile faces using Haar cascade"""
        try:
            faces_detected = self.profile_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_face_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            faces = []
            metadata = []
            
            for (x, y, w, h) in faces_detected:
                # Extract face crop
                face_crop = gray[y:y+h, x:x+w]
                
                # Calculate quality metrics
                quality_metrics = self._calculate_face_quality(face_crop)
                
                faces.append(face_crop)
                metadata.append({
                    'bbox': (x, y, w, h),
                    'type': 'profile',
                    'quality': quality_metrics,
                    'confidence': quality_metrics['overall_score']
                })
            
            return {'faces': faces, 'metadata': metadata}
            
        except Exception as e:
            logger.error(f"❌ Profile face detection failed: {e}")
            return {'faces': [], 'metadata': []}
    
    def _calculate_face_quality(self, face_crop: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive face quality metrics"""
        try:
            # Sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(face_crop, cv2.CV_64F).var()
            
            # Brightness
            brightness = np.mean(face_crop)
            
            # Contrast
            contrast = np.std(face_crop)
            
            # Edge density
            edges = cv2.Canny(face_crop, 50, 150)
            edge_density = np.sum(edges > 0) / (face_crop.shape[0] * face_crop.shape[1])
            
            # Symmetry (basic horizontal symmetry)
            left_half = face_crop[:, :face_crop.shape[1]//2]
            right_half = cv2.flip(face_crop[:, face_crop.shape[1]//2:], 1)
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            if min_width > 0:
                left_half = cv2.resize(left_half, (min_width, left_half.shape[0]))
                right_half = cv2.resize(right_half, (min_width, right_half.shape[0]))
                symmetry = 1.0 - np.mean(np.abs(left_half.astype(float) - right_half.astype(float))) / 255.0
            else:
                symmetry = 0.5
            
            # Normalize metrics
            sharpness_norm = min(1.0, sharpness / 1000.0)
            brightness_norm = brightness / 255.0
            contrast_norm = min(1.0, contrast / 100.0)
            edge_density_norm = min(1.0, edge_density * 10.0)
            symmetry_norm = max(0.0, min(1.0, symmetry))
            
            # Calculate overall quality score
            overall_score = (
                sharpness_norm * 0.25 +
                brightness_norm * 0.15 +
                contrast_norm * 0.25 +
                edge_density_norm * 0.20 +
                symmetry_norm * 0.15
            )
            
            return {
                'sharpness': sharpness_norm,
                'brightness': brightness_norm,
                'contrast': contrast_norm,
                'edge_density': edge_density_norm,
                'symmetry': symmetry_norm,
                'overall_score': overall_score
            }
            
        except Exception as e:
            logger.error(f"❌ Face quality calculation failed: {e}")
            return {
                'sharpness': 0.0,
                'brightness': 0.0,
                'contrast': 0.0,
                'edge_density': 0.0,
                'symmetry': 0.0,
                'overall_score': 0.0
            }
    
    def _remove_duplicate_detections(self, faces: List[np.ndarray], 
                                   metadata: List[Dict], 
                                   overlap_threshold: float = 0.3) -> Tuple[List[np.ndarray], List[Dict]]:
        """Remove duplicate face detections based on bounding box overlap"""
        if len(faces) <= 1:
            return faces, metadata
        
        unique_faces = []
        unique_metadata = []
        used_indices = set()
        
        for i, (face, meta) in enumerate(zip(faces, metadata)):
            if i in used_indices:
                continue
            
            # Keep this detection
            unique_faces.append(face)
            unique_metadata.append(meta)
            used_indices.add(i)
            
            # Check for overlaps with remaining detections
            bbox1 = meta['bbox']
            for j, (_, meta2) in enumerate(zip(faces, metadata)):
                if j <= i or j in used_indices:
                    continue
                
                bbox2 = meta2['bbox']
                overlap = self._calculate_bbox_overlap(bbox1, bbox2)
                
                if overlap > overlap_threshold:
                    # Mark as duplicate
                    used_indices.add(j)
        
        return unique_faces, unique_metadata
    
    def _calculate_bbox_overlap(self, bbox1: Tuple[int, int, int, int], 
                              bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        union_area = w1 * h1 + w2 * h2 - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0
    
    def _validate_faces_with_eyes(self, faces: List[np.ndarray], 
                                metadata: List[Dict], 
                                gray: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Validate faces by detecting eyes within the face region"""
        validated_faces = []
        validated_metadata = []
        
        for face, meta in zip(faces, metadata):
            x, y, w, h = meta['bbox']
            
            # Extract face region from original image
            face_region = gray[y:y+h, x:x+w]
            
            # Detect eyes within the face region
            eyes = self.eye_cascade.detectMultiScale(
                face_region,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(10, 10)
            )
            
            # If eyes are detected, consider it a valid face
            if len(eyes) > 0:
                # Update metadata with eye information
                meta['eyes_detected'] = len(eyes)
                meta['eye_positions'] = [(ex + x, ey + y, ew, eh) for ex, ey, ew, eh in eyes]
                
                validated_faces.append(face)
                validated_metadata.append(meta)
            else:
                # No eyes detected, but still keep the face (might be profile or partial)
                meta['eyes_detected'] = 0
                meta['eye_positions'] = []
                
                validated_faces.append(face)
                validated_metadata.append(meta)
        
        return validated_faces, validated_metadata
    
    def preprocess_face_for_detection(self, face: np.ndarray, 
                                    target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """
        Preprocess face image for better detection
        
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
            
            # Convert to grayscale if needed
            if len(face.shape) == 3:
                gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            else:
                gray = face.copy()
            
            # Resize to target size
            resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_CUBIC)
            
            # Apply histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(resized)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            return blurred
            
        except Exception as e:
            logger.error(f"❌ Face preprocessing failed: {e}")
            return face
    
    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics and status"""
        return {
            'initialized': self.is_initialized,
            'face_cascade_available': self.face_cascade is not None and not self.face_cascade.empty(),
            'profile_cascade_available': self.profile_cascade is not None and not self.profile_cascade.empty(),
            'eye_cascade_available': self.eye_cascade is not None and not self.eye_cascade.empty(),
            'opencv_version': cv2.__version__
        }

# Global instance for easy access
enhanced_opencv_detector = EnhancedOpenCVDetector()
