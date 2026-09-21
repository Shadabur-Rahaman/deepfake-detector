"""
Video Quality Analyzer
======================
Comprehensive video quality and artifact detection for deepfake detection.
Extracts blurriness, compression artifacts, lighting inconsistencies, and more.
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VideoQualityReport:
    """Comprehensive video quality analysis report"""
    blurriness_score: float  # 0.0 = sharp, 1.0 = very blurry
    compression_artifacts: float  # 0.0 = no artifacts, 1.0 = heavy artifacts
    lighting_consistency: float  # 0.0 = inconsistent, 1.0 = consistent
    color_consistency: float  # 0.0 = inconsistent, 1.0 = consistent
    blocking_artifacts: float  # H.264/HEVC blocking (0.0 = none, 1.0 = heavy)
    ringing_artifacts: float  # Compression ringing (0.0 = none, 1.0 = heavy)
    overall_quality: float  # Overall video quality (0.0 = poor, 1.0 = excellent)
    artifact_summary: Dict[str, float]  # Summary of all artifact scores


class VideoQualityAnalyzer:
    """
    Analyzes video quality and detects artifacts that may indicate manipulation:
    - Blurriness detection (Laplacian variance, FFT analysis)
    - Compression artifacts (blocking, ringing, quantization errors)
    - Lighting inconsistencies across frames
    - Color space inconsistencies
    - Edge artifacts
    """
    
    def __init__(self):
        self.logger = logger
    
    def analyze_video(self, video_path: str, max_frames: int = 30) -> VideoQualityReport:
        """
        Analyze video for quality metrics and artifacts
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to analyze
            
        Returns:
            VideoQualityReport with comprehensive analysis
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Cannot open video: {video_path}")
                return self._create_default_report()
            
            frames = []
            frame_indices = []
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, total_frames // max_frames)
            
            # Extract frames
            frame_idx = 0
            while len(frames) < max_frames and frame_idx < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % frame_interval == 0:
                    frames.append(frame)
                    frame_indices.append(frame_idx)
                
                frame_idx += 1
            
            cap.release()
            
            if len(frames) < 3:
                logger.warning(f"Too few frames extracted: {len(frames)}")
                return self._create_default_report()
            
            # Analyze frames
            blurriness_scores = []
            blocking_scores = []
            ringing_scores = []
            brightness_values = []
            color_stats = []
            
            for frame in frames:
                # Blurriness detection
                blur_score = self._detect_blurriness(frame)
                blurriness_scores.append(blur_score)
                
                # Compression artifacts
                blocking = self._detect_blocking_artifacts(frame)
                blocking_scores.append(blocking)
                
                ringing = self._detect_ringing_artifacts(frame)
                ringing_scores.append(ringing)
                
                # Brightness (for lighting consistency)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
                
                # Color statistics (for color consistency)
                color_stats.append(self._extract_color_statistics(frame))
            
            # Calculate aggregate metrics
            avg_blurriness = np.mean(blurriness_scores)
            avg_blocking = np.mean(blocking_scores)
            avg_ringing = np.mean(ringing_scores)
            
            # Lighting consistency (lower variance = more consistent)
            brightness_variance = np.var(brightness_values)
            lighting_consistency = 1.0 / (1.0 + brightness_variance / 1000.0)  # Normalize to [0, 1]
            
            # Color consistency
            color_consistency = self._calculate_color_consistency(color_stats)
            
            # Overall compression artifacts (combination of blocking and ringing)
            compression_artifacts = max(avg_blocking, avg_ringing) * 0.7 + min(avg_blocking, avg_ringing) * 0.3
            
            # Overall quality (inverse of artifacts, normalized)
            overall_quality = 1.0 - min(1.0, (avg_blurriness * 0.3 + compression_artifacts * 0.4 + (1.0 - lighting_consistency) * 0.2 + (1.0 - color_consistency) * 0.1))
            
            artifact_summary = {
                'blurriness': float(avg_blurriness),
                'blocking': float(avg_blocking),
                'ringing': float(avg_ringing),
                'lighting_variance': float(brightness_variance),
                'color_variance': float(np.var([s['variance'] for s in color_stats]) if color_stats else 0.0)
            }
            
            return VideoQualityReport(
                blurriness_score=float(avg_blurriness),
                compression_artifacts=float(compression_artifacts),
                lighting_consistency=float(lighting_consistency),
                color_consistency=float(color_consistency),
                blocking_artifacts=float(avg_blocking),
                ringing_artifacts=float(avg_ringing),
                overall_quality=float(overall_quality),
                artifact_summary=artifact_summary
            )
            
        except Exception as e:
            logger.error(f"Video quality analysis failed: {e}")
            return self._create_default_report()
    
    def analyze_faces(self, faces: List[np.ndarray]) -> Dict[str, float]:
        """
        Analyze face crops for quality and artifacts
        
        Args:
            faces: List of face arrays (H, W, C)
            
        Returns:
            Dictionary with artifact scores
        """
        try:
            if not faces or len(faces) == 0:
                return self._get_default_face_artifacts()
            
            blur_scores = []
            blocking_scores = []
            color_scores = []
            
            for face in faces:
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                # Ensure face is in correct format
                if len(face.shape) == 2:  # Grayscale
                    face_bgr = cv2.cvtColor(face, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face.copy()
                
                # Resize if too small
                if face_bgr.shape[0] < 64 or face_bgr.shape[1] < 64:
                    face_bgr = cv2.resize(face_bgr, (224, 224))
                
                # Blurriness
                blur = self._detect_blurriness(face_bgr)
                blur_scores.append(blur)
                
                # Blocking artifacts
                blocking = self._detect_blocking_artifacts(face_bgr)
                blocking_scores.append(blocking)
                
                # Color statistics
                color_stats = self._extract_color_statistics(face_bgr)
                color_scores.append(color_stats['variance'])
            
            return {
                'blurriness': float(np.mean(blur_scores)) if blur_scores else 0.0,
                'blocking_artifacts': float(np.mean(blocking_scores)) if blocking_scores else 0.0,
                'color_variance': float(np.mean(color_scores)) if color_scores else 0.0,
                'face_count': len(faces)
            }
            
        except Exception as e:
            logger.error(f"Face quality analysis failed: {e}")
            return self._get_default_face_artifacts()
    
    def _detect_blurriness(self, frame: np.ndarray) -> float:
        """Detect blurriness using Laplacian variance and FFT analysis"""
        try:
            # Convert to grayscale if needed
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # Method 1: Laplacian variance (higher = sharper)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Method 2: FFT analysis (high frequencies = sharp)
            fft = np.fft.fft2(gray)
            fft_shift = np.fft.fftshift(fft)
            magnitude = np.abs(fft_shift)
            
            # High frequency energy (edges/details)
            h, w = gray.shape
            center_h, center_w = h // 2, w // 2
            # Extract outer ring (high frequencies)
            mask = np.ones((h, w), dtype=np.float32)
            cv2.circle(mask, (center_w, center_h), min(h, w) // 4, 0, -1)
            high_freq_energy = np.sum(magnitude * mask) / np.sum(mask)
            
            # Combine metrics
            # Normalize Laplacian variance (typical range: 0-1000, blurry < 100)
            laplacian_norm = min(1.0, laplacian_var / 500.0)
            
            # Normalize FFT energy (typical range varies, normalize by image size)
            fft_norm = min(1.0, high_freq_energy / (h * w * 0.1))
            
            # Blurriness is inverse of sharpness
            sharpness = (laplacian_norm * 0.6 + fft_norm * 0.4)
            blurriness = 1.0 - sharpness
            
            return float(max(0.0, min(1.0, blurriness)))
            
        except Exception as e:
            logger.warning(f"Blurriness detection failed: {e}")
            return 0.5  # Neutral
    
    def _detect_blocking_artifacts(self, frame: np.ndarray) -> float:
        """Detect H.264/HEVC blocking artifacts (8x8 block boundaries)"""
        try:
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            h, w = gray.shape
            
            # Check for 8x8 block patterns (common in H.264/HEVC compression)
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
            
            if not block_edges:
                return 0.0
            
            # High edge strength at block boundaries indicates blocking artifacts
            avg_edge_strength = np.mean(block_edges)
            # Normalize (typical range: 0-50)
            blocking_score = min(1.0, avg_edge_strength / 30.0)
            
            return float(blocking_score)
            
        except Exception as e:
            logger.warning(f"Blocking artifact detection failed: {e}")
            return 0.0
    
    def _detect_ringing_artifacts(self, frame: np.ndarray) -> float:
        """Detect ringing artifacts (oscillations near edges)"""
        try:
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # Use Canny edges to find strong edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges to get neighborhood
            kernel = np.ones((3, 3), np.uint8)
            edge_neighborhood = cv2.dilate(edges, kernel, iterations=1)
            edge_neighborhood = edge_neighborhood - edges  # Remove edge pixels
            
            # Look for oscillations (alternating bright/dark) near edges
            if np.sum(edge_neighborhood) == 0:
                return 0.0
            
            neighborhood_values = gray[edge_neighborhood > 0]
            if len(neighborhood_values) == 0:
                return 0.0
            
            # High variance near edges indicates ringing
            variance = np.var(neighborhood_values)
            # Normalize
            ringing_score = min(1.0, variance / 500.0)
            
            return float(ringing_score)
            
        except Exception as e:
            logger.warning(f"Ringing artifact detection failed: {e}")
            return 0.0
    
    def _extract_color_statistics(self, frame: np.ndarray) -> Dict[str, float]:
        """Extract color statistics for consistency analysis"""
        try:
            if len(frame.shape) != 3:
                return {'mean': 0.0, 'std': 0.0, 'variance': 0.0}
            
            # Convert to LAB color space for perceptual analysis
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            
            # Calculate statistics for each channel
            l_mean = np.mean(lab[:, :, 0])
            a_mean = np.mean(lab[:, :, 1])
            b_mean = np.mean(lab[:, :, 2])
            
            l_std = np.std(lab[:, :, 0])
            a_std = np.std(lab[:, :, 1])
            b_std = np.std(lab[:, :, 2])
            
            # Overall variance
            variance = (l_std**2 + a_std**2 + b_std**2) / 3.0
            
            return {
                'mean': float((l_mean + a_mean + b_mean) / 3.0),
                'std': float((l_std + a_std + b_std) / 3.0),
                'variance': float(variance)
            }
            
        except Exception as e:
            logger.warning(f"Color statistics extraction failed: {e}")
            return {'mean': 0.0, 'std': 0.0, 'variance': 0.0}
    
    def _calculate_color_consistency(self, color_stats_list: List[Dict[str, float]]) -> float:
        """Calculate color consistency across frames"""
        try:
            if len(color_stats_list) < 2:
                return 0.5  # Neutral if not enough frames
            
            # Calculate variance of means across frames
            means = [s['mean'] for s in color_stats_list]
            mean_variance = np.var(means)
            
            # Lower variance = more consistent
            consistency = 1.0 / (1.0 + mean_variance / 100.0)
            
            return float(max(0.0, min(1.0, consistency)))
            
        except Exception as e:
            logger.warning(f"Color consistency calculation failed: {e}")
            return 0.5
    
    def _create_default_report(self) -> VideoQualityReport:
        """Create default report when analysis fails"""
        return VideoQualityReport(
            blurriness_score=0.5,
            compression_artifacts=0.0,
            lighting_consistency=0.5,
            color_consistency=0.5,
            blocking_artifacts=0.0,
            ringing_artifacts=0.0,
            overall_quality=0.5,
            artifact_summary={}
        )
    
    def _get_default_face_artifacts(self) -> Dict[str, float]:
        """Get default artifact scores when analysis fails"""
        return {
            'blurriness': 0.5,
            'blocking_artifacts': 0.0,
            'color_variance': 0.0,
            'face_count': 0
        }

# Singleton instance
_video_quality_analyzer = None

def get_video_quality_analyzer() -> VideoQualityAnalyzer:
    """Get singleton instance of VideoQualityAnalyzer"""
    global _video_quality_analyzer
    if _video_quality_analyzer is None:
        _video_quality_analyzer = VideoQualityAnalyzer()
    return _video_quality_analyzer







