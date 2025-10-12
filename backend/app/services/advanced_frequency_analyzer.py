import numpy as np
import cv2
import torch
from scipy import signal
from scipy.fftpack import fft2, fftshift
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class AdvancedFrequencyAnalyzer:
    """Advanced frequency domain analysis for modern AI detection"""
    
    def __init__(self, device=None):
        self.device = device or "cpu"
        self.ai_signatures = {
            'veo3': {'low_freq_ratio': (0.02, 0.08), 'high_freq_anomaly': 0.15},
            'sora': {'low_freq_ratio': (0.03, 0.09), 'high_freq_anomaly': 0.12},
            'midjourney': {'low_freq_ratio': (0.01, 0.06), 'high_freq_anomaly': 0.18},
            'runway': {'low_freq_ratio': (0.025, 0.075), 'high_freq_anomaly': 0.14},
            'stable_diffusion': {'low_freq_ratio': (0.02, 0.07), 'high_freq_anomaly': 0.16}
        }
    
    def ultra_frequency_analysis(self, faces: List[torch.Tensor], video_path: str = None) -> Dict:
        """Multi-algorithm frequency analysis targeting modern AI"""
        
        if not faces:
            return {'ai_probability': 0.1, 'detected_artifacts': [], 'likely_generator': 'none'}
        
        results = {
            'fft_analysis': self._advanced_fft_analysis(faces),
            'dct_analysis': self._dct_analysis(faces),
            'spectral_residual': self._spectral_residual_analysis(faces)
        }
        
        # Add wavelet analysis if available
        try:
            import pywt
            results['wavelet_analysis'] = self._wavelet_analysis(faces)
        except ImportError:
            logger.warning("PyWavelets not available for wavelet analysis")
        
        return self._ensemble_frequency_decision(results)
    
    def _advanced_fft_analysis(self, faces: List[torch.Tensor]) -> Dict:
        """Multi-band FFT analysis optimized for diffusion models"""
        
        ai_scores = []
        artifacts = []
        
        for face in faces[:5]:
            try:
                face_np = self._tensor_to_numpy(face)
                gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)
                
                # 2D FFT analysis
                f_transform = fft2(gray)
                f_shift = fftshift(f_transform)
                magnitude_spectrum = np.log(np.abs(f_shift) + 1)
                
                h, w = magnitude_spectrum.shape
                center_h, center_w = h // 2, w // 2
                
                # Multi-band energy analysis
                bands = {
                    'very_low': (center_h-5, center_h+5, center_w-5, center_w+5),
                    'low': (center_h-15, center_h+15, center_w-15, center_w+15),
                    'high': (0, h, 0, w)
                }
                
                band_energies = {}
                for band_name, (y1, y2, x1, x2) in bands.items():
                    if band_name == 'high':
                        band_region = magnitude_spectrum.copy()
                        band_region[center_h-15:center_h+15, center_w-15:center_w+15] = 0
                    else:
                        band_region = magnitude_spectrum[y1:y2, x1:x2]
                    band_energies[band_name] = np.sum(band_region)
                
                total_energy = sum(band_energies.values())
                band_ratios = {k: v/total_energy for k, v in band_energies.items()}
                
                ai_score = 0.0
                
                # More conservative diffusion model signatures - only flag extreme cases
                if band_ratios['high'] < 0.02:  # Much more restrictive
                    ai_score += 0.2  # Reduced from 0.4
                    artifacts.append('high_frequency_suppression')
                
                if band_ratios['very_low'] > 0.8:  # Much more restrictive  
                    ai_score += 0.15  # Reduced from 0.3
                    artifacts.append('low_frequency_dominance')
                
                ai_scores.append(min(ai_score, 1.0))
                
            except Exception as e:
                logger.warning(f"FFT analysis failed: {e}")
                ai_scores.append(0.2)
        
        return {
            'score': np.mean(ai_scores) if ai_scores else 0.2,
            'artifacts': list(set(artifacts))
        }
    
# Find the wavelet analysis section and replace with:
    def _wavelet_analysis(self, faces: List[torch.Tensor]) -> Dict:
        """Wavelet decomposition analysis"""
        try:
            import pywt
            ai_scores = []
            artifacts = []

            for face in faces[:3]:
                try:
                    face_np = self._tensor_to_numpy(face)
                    gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)

                    # FIXED: Use correct parameter name 'level' instead of 'levels'
                    coeffs = pywt.wavedec2(gray, 'db4', level=4)  # Changed from levels=4
                    detail_coeffs = coeffs[1:]

                    ai_score = 0.0
                    for level, (cH, cV, cD) in enumerate(detail_coeffs):
                        for coeff_type, coeff in [('horizontal', cH), ('vertical', cV), ('diagonal', cD)]:
                            coeff_std = np.std(coeff)
                            if coeff_std < 0.01:
                                ai_score += 0.1
                                artifacts.append(f'uniform_wavelets_{coeff_type}_L{level}')

                    ai_scores.append(min(ai_score, 1.0))

                except Exception as e:
                    logger.warning(f"Wavelet analysis failed for face: {e}")
                    ai_scores.append(0.1)

            return {
                'score': np.mean(ai_scores) if ai_scores else 0.1,
                'artifacts': list(set(artifacts))
            }

        except ImportError:
            return {'score': 0.0, 'artifacts': ['pywavelets_not_available']}
    
    def _dct_analysis(self, faces: List[torch.Tensor]) -> Dict:
        """DCT analysis for compression artifacts"""
        
        ai_scores = []
        artifacts = []
        
        for face in faces[:3]:
            try:
                face_np = self._tensor_to_numpy(face)
                gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)
                
                # Apply DCT in 8x8 blocks
                h, w = gray.shape
                ai_score = 0.0
                
                for i in range(0, h-8, 8):
                    for j in range(0, w-8, 8):
                        block = gray[i:i+8, j:j+8].astype(np.float32)
                        dct_block = cv2.dct(block)
                        
                        # Analyze AC coefficients
                        ac_coeffs = dct_block.flatten()[1:]
                        ac_energy = np.sum(np.square(ac_coeffs))
                        
                        if ac_energy < 100:  # Very low AC energy
                            ai_score += 0.01
                
                # Normalize by number of blocks
                num_blocks = ((h-8)//8) * ((w-8)//8)
                if num_blocks > 0:
                    ai_score /= num_blocks
                
                if ai_score > 0.3:
                    artifacts.append('dct_over_smoothing')
                
                ai_scores.append(min(ai_score * 5, 1.0))
                
            except Exception as e:
                logger.warning(f"DCT analysis failed: {e}")
                ai_scores.append(0.1)
        
        return {
            'score': np.mean(ai_scores) if ai_scores else 0.1,
            'artifacts': list(set(artifacts))
        }
    
    def _spectral_residual_analysis(self, faces: List[torch.Tensor]) -> Dict:
        """Spectral residual analysis"""
        
        ai_scores = []
        artifacts = []
        
        for face in faces[:3]:
            try:
                face_np = self._tensor_to_numpy(face)
                gray = cv2.cvtColor(face_np, cv2.COLOR_RGB2GRAY)
                
                # FFT
                f_transform = np.fft.fft2(gray)
                magnitude = np.abs(f_transform)
                phase = np.angle(f_transform)
                
                # Log magnitude spectrum
                log_magnitude = np.log(magnitude + 1)
                
                # Spectral residual
                smoothed_log_magnitude = cv2.GaussianBlur(log_magnitude, (3, 3), 1)
                spectral_residual = log_magnitude - smoothed_log_magnitude
                
                # Analyze saliency patterns
                saliency_std = np.std(spectral_residual)
                ai_score = 0.0
                
                if saliency_std < 0.05:  # Much more restrictive
                    ai_score += 0.2  # Reduced from 0.4
                    artifacts.append('uniform_saliency')
                
                ai_scores.append(min(ai_score, 1.0))
                
            except Exception as e:
                logger.warning(f"Spectral residual analysis failed: {e}")
                ai_scores.append(0.1)
        
        return {
            'score': np.mean(ai_scores) if ai_scores else 0.1,
            'artifacts': list(set(artifacts))
        }
    
    def _ensemble_frequency_decision(self, results: Dict) -> Dict:
        """Ensemble decision from frequency analyses"""
        
        weights = {'fft_analysis': 0.4, 'dct_analysis': 0.3, 'spectral_residual': 0.3}
        
        total_score = 0.0
        total_weight = 0.0
        all_artifacts = []
        
        for analysis_name, result in results.items():
            if analysis_name in weights and isinstance(result, dict):
                score = result.get('score', 0.0)
                artifacts = result.get('artifacts', [])
                
                total_score += score * weights[analysis_name]
                total_weight += weights[analysis_name]
                all_artifacts.extend(artifacts)
        
        final_probability = total_score / total_weight if total_weight > 0 else 0.1
        
        # Apply conservative bias - reduce AI probability by 30% to favor real content
        conservative_probability = final_probability * 0.7
        
        return {
            'ai_probability': conservative_probability,
            'detected_artifacts': list(set(all_artifacts)),
            'likely_generator': self._identify_generator(all_artifacts),
            'confidence': min(conservative_probability * 100 + 10, 85.0)  # Reduced confidence boost
        }
    
    def _identify_generator(self, artifacts: List[str]) -> str:
        """Identify likely AI generator from artifacts"""
        if 'high_frequency_suppression' in artifacts:
            return 'diffusion_model'
        elif 'low_frequency_dominance' in artifacts:
            return 'stable_diffusion'
        return 'unknown'
    
    def _tensor_to_numpy(self, tensor: torch.Tensor) -> np.ndarray:
        """Convert tensor to numpy for analysis"""
        if isinstance(tensor, torch.Tensor):
            numpy_array = tensor.detach().cpu().numpy()
            if len(numpy_array.shape) == 3 and numpy_array.shape[0] == 3:
                numpy_array = np.transpose(numpy_array, (1, 2, 0))
            if numpy_array.min() < 0:
                mean = np.array([0.485, 0.456, 0.406])
                std = np.array([0.229, 0.224, 0.225])
                numpy_array = numpy_array * std + mean
            numpy_array = np.clip(numpy_array, 0, 1)
            numpy_array = (numpy_array * 255).astype(np.uint8)
            return numpy_array
        return tensor

# Global instance
advanced_frequency_analyzer = AdvancedFrequencyAnalyzer()

# Export the analyzer method that can be called directly
ultra_frequency_analyzer = advanced_frequency_analyzer.ultra_frequency_analysis

def get_frequency_analyzer():
    """Get the global frequency analyzer instance"""
    return advanced_frequency_analyzer