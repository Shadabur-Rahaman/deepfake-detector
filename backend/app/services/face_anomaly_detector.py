"""
Face Anomaly Detector
====================
Detects specific facial anomalies: lip sync issues, eye inconsistencies, 
eyebrow misalignments, facial structure problems, and face swap artifacts.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FaceAnomalyReport:
    """Comprehensive face anomaly detection report"""
    lip_sync_score: float  # 0.0 = good sync, 1.0 = severe mismatch
    eye_consistency: float  # 0.0 = consistent, 1.0 = inconsistent
    eyebrow_alignment: float  # 0.0 = aligned, 1.0 = misaligned
    facial_structure: float  # 0.0 = natural, 1.0 = distorted
    face_swap_artifacts: float  # 0.0 = no swap, 1.0 = clear swap
    overall_anomaly_score: float  # 0.0 = normal, 1.0 = severe anomalies
    detected_anomalies: List[str]  # List of anomaly types detected


class FaceAnomalyDetector:
    """
    Detects specific facial anomalies that indicate deepfake manipulation:
    - Lip sync issues (mouth movements don't match speech)
    - Eye inconsistencies (size, position, blinking patterns)
    - Eyebrow misalignments
    - Facial structure distortions
    - Face swap artifacts (boundary issues, blending problems)
    """
    
    def __init__(self):
        self.logger = logger
    
    def detect_anomalies(self, faces: List[np.ndarray], frame_sequence: Optional[List[int]] = None) -> FaceAnomalyReport:
        """
        Detect facial anomalies across a sequence of faces
        
        Args:
            faces: List of face crops (H, W, C)
            frame_sequence: Optional frame indices for temporal analysis
            
        Returns:
            FaceAnomalyReport with comprehensive anomaly analysis
        """
        try:
            if len(faces) < 3:
                return self._create_default_report()
            
            # Detect specific anomalies
            lip_sync = self._detect_lip_sync_issues(faces)
            eye_consistency = self._detect_eye_inconsistencies(faces)
            eyebrow_alignment = self._detect_eyebrow_misalignment(faces)
            facial_structure = self._detect_facial_structure_distortions(faces)
            face_swap = self._detect_face_swap_artifacts(faces)
            
            # Calculate overall anomaly score (weighted)
            overall_score = (
                lip_sync * 0.25 +
                eye_consistency * 0.25 +
                eyebrow_alignment * 0.15 +
                facial_structure * 0.20 +
                face_swap * 0.15
            )
            
            # Identify specific anomalies
            detected_anomalies = []
            if lip_sync > 0.6:
                detected_anomalies.append("lip_sync_issue")
            if eye_consistency > 0.6:
                detected_anomalies.append("eye_inconsistency")
            if eyebrow_alignment > 0.6:
                detected_anomalies.append("eyebrow_misalignment")
            if facial_structure > 0.6:
                detected_anomalies.append("facial_structure_distortion")
            if face_swap > 0.6:
                detected_anomalies.append("face_swap_artifact")
            
            return FaceAnomalyReport(
                lip_sync_score=float(lip_sync),
                eye_consistency=float(eye_consistency),
                eyebrow_alignment=float(eyebrow_alignment),
                facial_structure=float(facial_structure),
                face_swap_artifacts=float(face_swap),
                overall_anomaly_score=float(overall_score),
                detected_anomalies=detected_anomalies
            )
            
        except Exception as e:
            logger.error(f"Face anomaly detection failed: {e}")
            return self._create_default_report()
    
    def _detect_lip_sync_issues(self, faces: List[np.ndarray]) -> float:
        """Detect lip sync issues by analyzing mouth region consistency"""
        try:
            mouth_scores = []
            
            for face in faces[:15]:  # Check up to 15 faces
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                if len(face.shape) == 2:  # Grayscale
                    face_bgr = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face.copy()
                
                # Resize for consistency
                if face_bgr.shape[0] < 64 or face_bgr.shape[1] < 64:
                    face_bgr = cv2.resize(face_bgr, (224, 224))
                
                h, w = face_bgr.shape[:2]
                
                # Mouth region (typically in lower 1/3 of face)
                mouth_roi = face_bgr[int(h*0.6):int(h*0.9), int(w*0.25):int(w*0.75)]
                
                if mouth_roi.size == 0:
                    continue
                
                # Convert to HSV for better color analysis
                hsv = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)
                
                # Analyze mouth region for unnatural features
                # High saturation variance might indicate artificial coloring
                sat_variance = np.var(hsv[:, :, 1])
                
                # Edge density in mouth region (unnatural edges suggest manipulation)
                gray = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                
                # Combine metrics
                anomaly_score = min(1.0, (sat_variance / 1000.0 + edge_density * 2.0) / 2.0)
                mouth_scores.append(anomaly_score)
            
            return float(np.mean(mouth_scores)) if mouth_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Lip sync detection failed: {e}")
            return 0.0
    
    def _detect_eye_inconsistencies(self, faces: List[np.ndarray]) -> float:
        """Detect eye inconsistencies (size, position, blinking patterns)"""
        try:
            eye_scores = []
            
            for face in faces[:15]:
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                if len(face.shape) == 2:
                    face_bgr = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face.copy()
                
                if face_bgr.shape[0] < 64 or face_bgr.shape[1] < 64:
                    face_bgr = cv2.resize(face_bgr, (224, 224))
                
                h, w = face_bgr.shape[:2]
                
                # Eye regions (typically in upper 1/3 of face)
                left_eye_roi = face_bgr[int(h*0.15):int(h*0.4), int(w*0.1):int(w*0.45)]
                right_eye_roi = face_bgr[int(h*0.15):int(h*0.4), int(w*0.55):int(w*0.9)]
                
                if left_eye_roi.size == 0 or right_eye_roi.size == 0:
                    continue
                
                # Compare left and right eyes for symmetry
                left_gray = cv2.cvtColor(left_eye_roi, cv2.COLOR_BGR2GRAY)
                right_gray = cv2.cvtColor(right_eye_roi, cv2.COLOR_BGR2GRAY)
                
                # Resize to same size for comparison
                min_h = min(left_gray.shape[0], right_gray.shape[0])
                min_w = min(left_gray.shape[1], right_gray.shape[1])
                left_gray = cv2.resize(left_gray, (min_w, min_h))
                right_gray = cv2.resize(right_gray, (min_w, min_h))
                
                # Flip right eye horizontally for symmetry comparison
                right_gray_flipped = cv2.flip(right_gray, 1)
                
                # Calculate symmetry difference
                symmetry_diff = np.abs(left_gray.astype(float) - right_gray_flipped.astype(float))
                asymmetry_score = np.mean(symmetry_diff) / 255.0
                
                eye_scores.append(asymmetry_score)
            
            # Also check for temporal inconsistencies
            if len(eye_scores) > 2:
                temporal_variance = np.var(eye_scores)
                temporal_anomaly = min(1.0, temporal_variance * 2.0)
                return float((np.mean(eye_scores) + temporal_anomaly) / 2.0)
            
            return float(np.mean(eye_scores)) if eye_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Eye consistency detection failed: {e}")
            return 0.0
    
    def _detect_eyebrow_misalignment(self, faces: List[np.ndarray]) -> float:
        """Detect eyebrow misalignment and inconsistencies"""
        try:
            eyebrow_scores = []
            
            for face in faces[:15]:
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                if len(face.shape) == 2:
                    face_bgr = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face.copy()
                
                if face_bgr.shape[0] < 64 or face_bgr.shape[1] < 64:
                    face_bgr = cv2.resize(face_bgr, (224, 224))
                
                h, w = face_bgr.shape[:2]
                
                # Eyebrow regions
                left_eyebrow_roi = face_bgr[int(h*0.08):int(h*0.25), int(w*0.1):int(w*0.45)]
                right_eyebrow_roi = face_bgr[int(h*0.08):int(h*0.25), int(w*0.55):int(w*0.9)]
                
                if left_eyebrow_roi.size == 0 or right_eyebrow_roi.size == 0:
                    continue
                
                # Compare eyebrow symmetry
                left_gray = cv2.cvtColor(left_eyebrow_roi, cv2.COLOR_BGR2GRAY)
                right_gray = cv2.cvtColor(right_eyebrow_roi, cv2.COLOR_BGR2GRAY)
                
                min_h = min(left_gray.shape[0], right_gray.shape[0])
                min_w = min(left_gray.shape[1], right_gray.shape[1])
                left_gray = cv2.resize(left_gray, (min_w, min_h))
                right_gray = cv2.resize(right_gray, (min_w, min_h))
                right_gray_flipped = cv2.flip(right_gray, 1)
                
                misalignment = np.mean(np.abs(left_gray.astype(float) - right_gray_flipped.astype(float))) / 255.0
                eyebrow_scores.append(misalignment)
            
            return float(np.mean(eyebrow_scores)) if eyebrow_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Eyebrow alignment detection failed: {e}")
            return 0.0
    
    def _detect_facial_structure_distortions(self, faces: List[np.ndarray]) -> float:
        """Detect facial structure distortions (unnatural proportions, warping)"""
        try:
            structure_scores = []
            
            for face in faces[:15]:
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                if len(face.shape) == 2:
                    face_bgr = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face.copy()
                
                if face_bgr.shape[0] < 64 or face_bgr.shape[1] < 64:
                    face_bgr = cv2.resize(face_bgr, (224, 224))
                
                # Analyze face proportions
                h, w = face_bgr.shape[:2]
                aspect_ratio = w / h if h > 0 else 1.0
                
                # Normal face aspect ratio is typically 0.7-0.9
                # Extreme values suggest distortion
                if aspect_ratio < 0.5 or aspect_ratio > 1.2:
                    structure_scores.append(0.8)
                elif aspect_ratio < 0.6 or aspect_ratio > 1.1:
                    structure_scores.append(0.5)
                else:
                    # Check for warping artifacts using edge detection
                    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
                    
                    # Look for unnatural edge patterns (might indicate warping)
                    edges = cv2.Canny(gray, 50, 150)
                    
                    # Analyze edge distribution
                    # Natural faces have edges distributed throughout
                    # Warped faces might have edge clusters
                    edge_clusters = self._detect_edge_clusters(edges)
                    cluster_score = min(1.0, edge_clusters * 2.0)
                    
                    structure_scores.append(cluster_score * 0.5)
            
            return float(np.mean(structure_scores)) if structure_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Facial structure detection failed: {e}")
            return 0.0
    
    def _detect_face_swap_artifacts(self, faces: List[np.ndarray]) -> float:
        """Detect face swap artifacts (blending issues, boundary problems)"""
        try:
            swap_scores = []
            
            for face in faces[:15]:
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                if len(face.shape) == 2:
                    face_bgr = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face.copy()
                
                if face_bgr.shape[0] < 64 or face_bgr.shape[1] < 64:
                    face_bgr = cv2.resize(face_bgr, (224, 224))
                
                # Check for blending artifacts around face boundaries
                h, w = face_bgr.shape[:2]
                border_region = 15  # Check 15 pixels from border
                
                # Extract border regions
                top_border = face_bgr[:border_region, :]
                bottom_border = face_bgr[-border_region:, :]
                left_border = face_bgr[:, :border_region]
                right_border = face_bgr[:, -border_region:]
                
                # Calculate color variance in border regions (high variance suggests blending issues)
                borders = [top_border, bottom_border, left_border, right_border]
                border_variances = []
                
                for border in borders:
                    if border.size > 0:
                        if len(border.shape) == 3:
                            # Calculate variance per channel
                            var_per_channel = [np.var(border[:, :, i]) for i in range(3)]
                            border_variances.append(np.mean(var_per_channel))
                        else:
                            border_variances.append(np.var(border))
                
                if border_variances:
                    avg_border_variance = np.mean(border_variances)
                    # High variance suggests blending artifacts
                    swap_score = min(1.0, avg_border_variance / 500.0)
                    swap_scores.append(swap_score)
            
            return float(np.mean(swap_scores)) if swap_scores else 0.0
            
        except Exception as e:
            logger.debug(f"Face swap detection failed: {e}")
            return 0.0
    
    def _detect_edge_clusters(self, edges: np.ndarray) -> float:
        """Detect edge clusters that might indicate warping"""
        try:
            # Divide image into grid
            h, w = edges.shape
            grid_h, grid_w = 4, 4
            cell_h, cell_w = h // grid_h, w // grid_w
            
            edge_counts = []
            for i in range(grid_h):
                for j in range(grid_w):
                    y1, y2 = i * cell_h, (i + 1) * cell_h
                    x1, x2 = j * cell_w, (j + 1) * cell_w
                    cell = edges[y1:y2, x1:x2]
                    edge_count = np.sum(cell > 0)
                    edge_counts.append(edge_count)
            
            # Calculate variance - high variance suggests clusters
            variance = np.var(edge_counts) if edge_counts else 0.0
            # Normalize
            return min(1.0, variance / 1000.0)
            
        except Exception:
            return 0.0
    
    def _create_default_report(self) -> FaceAnomalyReport:
        """Create default report when detection fails"""
        return FaceAnomalyReport(
            lip_sync_score=0.0,
            eye_consistency=0.0,
            eyebrow_alignment=0.0,
            facial_structure=0.0,
            face_swap_artifacts=0.0,
            overall_anomaly_score=0.0,
            detected_anomalies=[]
        )

# Singleton instance
_face_anomaly_detector = None

def get_face_anomaly_detector() -> FaceAnomalyDetector:
    """Get singleton instance of FaceAnomalyDetector"""
    global _face_anomaly_detector
    if _face_anomaly_detector is None:
        _face_anomaly_detector = FaceAnomalyDetector()
    return _face_anomaly_detector







