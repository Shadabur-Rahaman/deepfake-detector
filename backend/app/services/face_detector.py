# backend/app/services/face_detector.py - Enhanced Face Detection

import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
import warnings

logger = logging.getLogger(__name__)

# Suppress OpenCV warnings
warnings.filterwarnings("ignore", category=UserWarning, module="cv2")

class FaceDetector:
    """Enhanced face detector with multiple detection methods"""
    
    def __init__(self):
        self.face_cascade = None
        self.profile_cascade = None
        self.eye_cascade = None
        self._initialize_cascades()
    
    def _initialize_cascades(self):
        """Initialize OpenCV cascades with error handling"""
        try:
            # Primary frontal face cascade
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Profile face cascade
            try:
                self.profile_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_profileface.xml'
                )
            except:
                self.profile_cascade = None
                logger.warning("Profile face cascade not available")
            
            # Eye cascade for validation
            try:
                self.eye_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_eye.xml'
                )
            except:
                self.eye_cascade = None
                logger.warning("Eye cascade not available")
            
            if self.face_cascade.empty():
                raise RuntimeError("Failed to load frontal face cascade")
            
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize face cascades: {e}")
            raise
    
    def detect_faces_enhanced(self, frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Enhanced face detection with multiple methods and validation"""
        try:
            if frame is None or frame.size == 0:
                return [], []
            
            # Validate input
            if not isinstance(frame, np.ndarray):
                frame = np.array(frame)
            
            if frame.ndim != 3 or frame.shape[2] not in [1, 3]:
                logger.warning(f"Invalid frame shape: {frame.shape}")
                return [], []
            
            # Convert to grayscale
            if frame.shape[2] == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame.copy()
            
            # Enhance image for better detection
            gray = cv2.equalizeHist(gray)
            
            # Detect faces using multiple methods
            faces = []
            coordinates = []
            
            # Method 1: Primary frontal face detection
            frontal_faces = self._detect_frontal_faces(gray)
            for (x, y, w, h) in frontal_faces:
                face_crop = self._extract_face_crop(frame, x, y, w, h)
                if face_crop is not None:
                    faces.append(face_crop)
                    coordinates.append({
                        'x': int(x), 'y': int(y), 
                        'width': int(w), 'height': int(h),
                        'confidence': 0.8, 'type': 'frontal'
                    })
            
            # Method 2: Profile face detection if no frontal faces found
            if not faces and self.profile_cascade:
                profile_faces = self._detect_profile_faces(gray)
                for (x, y, w, h) in profile_faces:
                    face_crop = self._extract_face_crop(frame, x, y, w, h)
                    if face_crop is not None:
                        faces.append(face_crop)
                        coordinates.append({
                            'x': int(x), 'y': int(y), 
                            'width': int(w), 'height': int(h),
                            'confidence': 0.6, 'type': 'profile'
                        })
            
            # Method 3: Ultra-sensitive detection as fallback
            if not faces:
                sensitive_faces = self._detect_sensitive_faces(gray)
                for (x, y, w, h) in sensitive_faces:
                    face_crop = self._extract_face_crop(frame, x, y, w, h)
                    if face_crop is not None:
                        faces.append(face_crop)
                        coordinates.append({
                            'x': int(x), 'y': int(y), 
                            'width': int(w), 'height': int(h),
                            'confidence': 0.4, 'type': 'sensitive'
                        })
            
            # Validate and filter faces
            validated_faces, validated_coords = self._validate_faces(faces, coordinates, gray)
            
            if self.face_cascade and len(validated_faces) > 0:
                logger.debug(f"Detected {len(validated_faces)} faces")
            
            return validated_faces, validated_coords
            
        except Exception as e:
            logger.error(f"[ERROR] Face detection failed: {e}")
            return [], []
    
    def _detect_frontal_faces(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect frontal faces with optimized parameters"""
        try:
            if self.face_cascade is None or self.face_cascade.empty():
                return []
            
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(40, 40),
                maxSize=(400, 400),
                flags=cv2.CASCADE_SCALE_IMAGE | cv2.CASCADE_DO_CANNY_PRUNING
            )
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            logger.error(f"Frontal face detection failed: {e}")
            return []
    
    def _detect_profile_faces(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect profile faces"""
        try:
            if self.profile_cascade is None or self.profile_cascade.empty():
                return []
            
            faces = self.profile_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(40, 40),
                maxSize=(400, 400)
            )
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            logger.error(f"Profile face detection failed: {e}")
            return []
    
    def _detect_sensitive_faces(self, gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Ultra-sensitive face detection as fallback"""
        try:
            if self.face_cascade is None or self.face_cascade.empty():
                return []
            
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.02,
                minNeighbors=2,
                minSize=(30, 30),
                maxSize=(500, 500),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            logger.error(f"Sensitive face detection failed: {e}")
            return []
    
    def _extract_face_crop(self, frame: np.ndarray, x: int, y: int, w: int, h: int) -> Optional[np.ndarray]:
        """Extract and validate face crop"""
        try:
            # Ensure coordinates are within frame bounds
            height, width = frame.shape[:2]
            x = max(0, min(x, width - 1))
            y = max(0, min(y, height - 1))
            w = max(1, min(w, width - x))
            h = max(1, min(h, height - y))
            
            # Add padding
            padding = min(w, h) // 10
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(width, x + w + padding)
            y2 = min(height, y + h + padding)
            
            # Extract crop
            face_crop = frame[y1:y2, x1:x2]
            
            # Validate crop
            if face_crop.size == 0 or face_crop.shape[0] < 20 or face_crop.shape[1] < 20:
                return None
            
            return face_crop
            
        except Exception as e:
            logger.error(f"Face crop extraction failed: {e}")
            return None
    
    def _validate_faces(self, faces: List[np.ndarray], coordinates: List[Dict], gray: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
        """Validate detected faces and remove duplicates"""
        try:
            if not faces:
                return [], []
            
            validated_faces = []
            validated_coords = []
            
            for i, (face, coord) in enumerate(zip(faces, coordinates)):
                # Basic validation
                if face is None or face.size == 0:
                    continue
                
                if face.shape[0] < 20 or face.shape[1] < 20:
                    continue
                
                # Check for duplicates (simple overlap check)
                is_duplicate = False
                for j, existing_coord in enumerate(validated_coords):
                    if self._faces_overlap(coord, existing_coord):
                        # Keep the one with higher confidence
                        if coord['confidence'] > existing_coord['confidence']:
                            validated_faces[j] = face
                            validated_coords[j] = coord
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    validated_faces.append(face)
                    validated_coords.append(coord)
            
            return validated_faces, validated_coords
            
        except Exception as e:
            logger.error(f"Face validation failed: {e}")
            return faces, coordinates
    
    def _faces_overlap(self, coord1: Dict, coord2: Dict, threshold: float = 0.3) -> bool:
        """Check if two face coordinates overlap significantly"""
        try:
            x1, y1, w1, h1 = coord1['x'], coord1['y'], coord1['width'], coord1['height']
            x2, y2, w2, h2 = coord2['x'], coord2['y'], coord2['width'], coord2['height']
            
            # Calculate intersection
            x_left = max(x1, x2)
            y_top = max(y1, y2)
            x_right = min(x1 + w1, x2 + w2)
            y_bottom = min(y1 + h1, y2 + h2)
            
            if x_right < x_left or y_bottom < y_top:
                return False
            
            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            area1 = w1 * h1
            area2 = w2 * h2
            union_area = area1 + area2 - intersection_area
            
            overlap_ratio = intersection_area / union_area if union_area > 0 else 0
            return overlap_ratio > threshold
            
        except Exception as e:
            logger.error(f"Face overlap check failed: {e}")
            return False

# Global face detector instance
face_detector = FaceDetector()

def detect_faces_enhanced(frame: np.ndarray) -> Tuple[List[np.ndarray], List[Dict]]:
    """Global function for enhanced face detection"""
    return face_detector.detect_faces_enhanced(frame)