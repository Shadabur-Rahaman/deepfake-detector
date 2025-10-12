import torch
import cv2
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class YouTubeOptimizedDetector:
    """YouTube-optimized detector with minimal bias"""
    
    def __init__(self):
        self.compression_threshold = 0.3
        self.youtube_bias = 0.02  # MINIMAL bias
        
    def detect_with_youtube_optimization(self, faces: List[torch.Tensor], 
                                       is_youtube: bool = False) -> Dict:
        """Detection optimized for YouTube compression artifacts"""
        
        if not faces:
            return {'score': 0.1, 'artifacts': []}
        
        base_scores = []
        for face in faces[:5]:
            try:
                face_np = self._tensor_to_numpy(face)
                
                # FIXED: More balanced analysis  
                smoothing_score = self._detect_over_smoothing_youtube_optimized(face_np)
                freq_score = self._analyze_frequency_youtube_optimized(face_np)
                
                # FIXED: Minimal bias toward real
                face_score = (smoothing_score * 0.5 + freq_score * 0.5) * 0.95  # Minimal reduction
                base_scores.append(face_score)
                
            except Exception as e:
                logger.warning(f"YouTube face analysis failed: {e}")
                base_scores.append(0.25)  # Conservative fallback
        
        final_score = np.mean(base_scores) if base_scores else 0.25
        
        # FIXED: Minimal YouTube bias
        if is_youtube:
            final_score = final_score * 0.95  # Minimal reduction
            final_score += self.youtube_bias
            final_score = min(final_score, 0.8)  # Allow higher scores
        
        return {
            'score': float(final_score),
            'artifacts': ['compression_artifacts'] if final_score > 0.4 else [],
            'youtube_optimized': is_youtube,
            'bias_applied': self.youtube_bias if is_youtube else 0.0
        }
    
    def _tensor_to_numpy(self, tensor: torch.Tensor) -> np.ndarray:
        """FIXED: Convert tensor to numpy array for analysis"""
        try:
            if isinstance(tensor, torch.Tensor):
                numpy_array = tensor.detach().cpu().numpy()
                
                # Handle different tensor formats
                if len(numpy_array.shape) == 3 and numpy_array.shape[0] == 3:
                    numpy_array = np.transpose(numpy_array, (1, 2, 0))
                
                # Denormalize if needed
                if numpy_array.min() < 0:
                    mean = np.array([0.485, 0.456, 0.406])
                    std = np.array([0.229, 0.224, 0.225])
                    numpy_array = numpy_array * std + mean
                
                numpy_array = np.clip(numpy_array, 0, 1)
                numpy_array = (numpy_array * 255).astype(np.uint8)
                
                return numpy_array
            else:
                return tensor
                
        except Exception as e:
            logger.error(f"Tensor to numpy conversion failed: {e}")
            return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    def _detect_over_smoothing_youtube_optimized(self, face_np: np.ndarray) -> float:
        """FIXED: Balanced smoothing detection"""
        try:
            gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # FIXED: More sensitive thresholds
            if laplacian_var < 20:  # Very aggressive smoothing
                return 0.7  # High suspicion
            elif laplacian_var < 60:  # Moderate smoothing
                return 0.4  # Moderate suspicion
            else:
                return 0.15  # Low suspicion
                
        except Exception:
            return 0.25
    
    def _analyze_frequency_youtube_optimized(self, face_np: np.ndarray) -> float:
        """FIXED: Balanced frequency analysis"""
        try:
            gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)
            
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.log(np.abs(f_shift) + 1)
            
            h, w = magnitude_spectrum.shape
            center_h, center_w = h // 2, w // 2
            
            high_freq_region = magnitude_spectrum.copy()
            high_freq_region[center_h-15:center_h+15, center_w-15:center_w+15] = 0
            
            high_freq_energy = np.sum(high_freq_region)
            total_energy = np.sum(magnitude_spectrum)
            freq_ratio = high_freq_energy / (total_energy + 1e-8)
            
            # FIXED: More sensitive thresholds
            if freq_ratio < 0.015:  # Very low high-freq
                return 0.65  # High suspicion
            elif freq_ratio < 0.06:  # Low high-freq
                return 0.35  # Moderate suspicion
            else:
                return 0.1  # Low suspicion
                
        except Exception:
            return 0.2
