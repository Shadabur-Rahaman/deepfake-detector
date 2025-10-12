# app/services/advanced_temporal_analyzer.py - ULTRA-ADVANCED TEMPORAL ANALYSIS

import cv2
import numpy as np
import torch
from typing import List, Dict, Tuple, Optional
import logging
from scipy import signal
from scipy.interpolate import interp1d
from sklearn.metrics import mean_squared_error

logger = logging.getLogger(__name__)

class UltraTemporalAnalyzer:
    """Advanced temporal analysis for AI-generated video detection"""
    
    def __init__(self):
        self.ai_temporal_signatures = {
            'veo3': {'frame_consistency': 0.95, 'motion_smoothness': 0.90},
            'sora': {'frame_consistency': 0.92, 'motion_smoothness': 0.88},
            'runway': {'frame_consistency': 0.85, 'motion_smoothness': 0.82},
            'pika': {'frame_consistency': 0.80, 'motion_smoothness': 0.78}
        }
    
    def comprehensive_temporal_analysis(self, video_path: str, faces: List[torch.Tensor] = None) -> Dict:
        """Comprehensive temporal analysis using multiple algorithms"""
        
        # Extract video frames for temporal analysis
        frames, fps = self._extract_video_frames(video_path)
        
        if len(frames) < 3:
            return {'ai_probability': 0.1, 'confidence': 0.0, 'artifacts': []}
        
        # Multiple temporal analysis techniques
        analyses = {
            'optical_flow_analysis': self._optical_flow_analysis(frames),
            'frame_difference_analysis': self._frame_difference_analysis(frames),
            'motion_vector_analysis': self._motion_vector_analysis(frames),
            'temporal_frequency_analysis': self._temporal_frequency_analysis(frames),
            'face_landmark_temporal_analysis': self._face_landmark_temporal_analysis(frames),
            'edge_temporal_consistency': self._edge_temporal_consistency(frames),
            'texture_temporal_analysis': self._texture_temporal_analysis(frames),
            'color_temporal_analysis': self._color_temporal_analysis(frames)
        }
        
        if faces:
            analyses['face_temporal_consistency'] = self._face_temporal_consistency_analysis(faces)
        
        # Advanced ensemble temporal decision
        final_result = self._ensemble_temporal_decision(analyses, fps)
        
        return {
            'ai_probability': final_result['probability'],
            'confidence': final_result['confidence'],
            'detected_artifacts': final_result['artifacts'],
            'likely_generator': final_result['generator'],
            'temporal_breakdown': analyses
        }
    
    def _extract_video_frames(self, video_path: str, max_frames: int = 30) -> Tuple[List[np.ndarray], float]:
        """Extract frames from video with metadata"""
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame interval for uniform sampling
            if frame_count > max_frames:
                frame_interval = frame_count // max_frames
            else:
                frame_interval = 1
            
            frames = []
            current_frame = 0
            
            while len(frames) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if current_frame % frame_interval == 0:
                    frames.append(frame)
                
                current_frame += 1
            
            cap.release()
            return frames, fps
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return [], 30.0
    
    def _optical_flow_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Advanced optical flow analysis for motion consistency"""
        
        if len(frames) < 2:
            return {'score': 0.1, 'artifacts': []}
        
        flow_consistencies = []
        flow_magnitudes = []
        artifacts = []
        
        # Convert to grayscale
        gray_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frames]
        
        for i in range(len(gray_frames) - 1):
            try:
                # Calculate dense optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    gray_frames[i], gray_frames[i+1], 
                    np.array([[]], dtype=np.float32), None
                )[0] if False else cv2.calcOpticalFlowFarneback(
                    gray_frames[i], gray_frames[i+1], None, 
                    0.5, 3, 15, 3, 5, 1.2, 0
                )
                
                # Calculate flow magnitude
                magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                
                # Analyze flow characteristics
                mean_magnitude = np.mean(magnitude)
                std_magnitude = np.std(magnitude)
                flow_magnitudes.append(mean_magnitude)
                
                # Check for unnatural flow patterns
                # AI-generated videos often have overly smooth or inconsistent flow
                consistency = std_magnitude / (mean_magnitude + 1e-8)
                flow_consistencies.append(consistency)
                
                # Detect artifacts
                if mean_magnitude < 0.5:  # Very low motion
                    artifacts.append('low_motion_artifact')
                
                if consistency > 5.0:  # Very inconsistent flow
                    artifacts.append('inconsistent_optical_flow')
                
                # Check for periodic patterns in flow (common in AI generation)
                flow_fft = np.fft.fft2(magnitude)
                flow_power = np.abs(flow_fft)**2
                
                # Look for dominant frequencies (indicates artificial patterns)
                flow_power_1d = np.sum(flow_power, axis=0)
                peaks, _ = signal.find_peaks(flow_power_1d, height=np.mean(flow_power_1d) * 3)
                
                if len(peaks) > flow_power_1d.shape[0] * 0.05:
                    artifacts.append('periodic_flow_patterns')
                
            except Exception as e:
                logger.warning(f"Optical flow analysis failed: {e}")
                continue
        
        # Overall analysis
        if flow_consistencies:
            avg_consistency = np.mean(flow_consistencies)
            consistency_variance = np.var(flow_consistencies)
            
            ai_score = 0.0
            
            # AI videos often have unnaturally consistent flow
            if avg_consistency < 0.5:
                ai_score += 0.3
                artifacts.append('overly_consistent_flow')
            
            # Or very inconsistent flow due to generation artifacts
            if avg_consistency > 8.0:
                ai_score += 0.4
                artifacts.append('highly_inconsistent_flow')
            
            # Check flow magnitude patterns
            if flow_magnitudes:
                magnitude_trend = np.polyfit(range(len(flow_magnitudes)), flow_magnitudes, 1)[0]
                
                # Unnatural trends in motion
                if abs(magnitude_trend) > 0.1:
                    ai_score += 0.2
                    artifacts.append('unnatural_motion_trend')
        else:
            ai_score = 0.2
        
        return {
            'score': min(ai_score, 1.0),
            'artifacts': list(set(artifacts)),
            'flow_consistency': np.mean(flow_consistencies) if flow_consistencies else 0.0
        }
    
    def _frame_difference_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Advanced frame difference analysis"""
        
        if len(frames) < 3:
            return {'score': 0.1, 'artifacts': []}
        
        differences = []
        artifacts = []
        
        for i in range(len(frames) - 1):
            try:
                # Convert to grayscale for analysis
                gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY).astype(np.float32)
                gray2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY).astype(np.float32)
                
                # Calculate multiple types of differences
                absolute_diff = np.abs(gray1 - gray2)
                squared_diff = (gray1 - gray2) ** 2
                
                # Statistics
                mean_abs_diff = np.mean(absolute_diff)
                std_abs_diff = np.std(absolute_diff)
                mean_sq_diff = np.mean(squared_diff)
                
                differences.append({
                    'mean_abs': mean_abs_diff,
                    'std_abs': std_abs_diff,
                    'mean_sq': mean_sq_diff
                })
                
            except Exception as e:
                logger.warning(f"Frame difference analysis failed: {e}")
                continue
        
        if not differences:
            return {'score': 0.2, 'artifacts': []}
        
        # Analyze difference patterns
        mean_abs_diffs = [d['mean_abs'] for d in differences]
        std_abs_diffs = [d['std_abs'] for d in differences]
        
        ai_score = 0.0
        
        # Check for unnatural consistency in frame differences
        diff_variance = np.var(mean_abs_diffs)
        if diff_variance < 1.0:  # Too consistent
            ai_score += 0.3
            artifacts.append('overly_consistent_frame_differences')
        
        # Check for periodic patterns
        if len(mean_abs_diffs) > 5:
            diff_fft = np.fft.fft(mean_abs_diffs)
            diff_power = np.abs(diff_fft)**2
            
            # Look for dominant periods
            dominant_freq_power = np.max(diff_power[1:len(diff_power)//2])
            avg_power = np.mean(diff_power[1:len(diff_power)//2])
            
            if dominant_freq_power > avg_power * 5:
                ai_score += 0.4
                artifacts.append('periodic_frame_differences')
        
        # Check for unnatural smoothness
        avg_diff = np.mean(mean_abs_diffs)
        if avg_diff < 2.0:  # Very small differences
            ai_score += 0.2
            artifacts.append('minimal_frame_changes')
        
        # Check for sudden jumps (common in AI generation)
        for i in range(len(mean_abs_diffs) - 1):
            if abs(mean_abs_diffs[i+1] - mean_abs_diffs[i]) > avg_diff * 3:
                ai_score += 0.1
                artifacts.append('sudden_frame_difference_jumps')
                break
        
        return {
            'score': min(ai_score, 1.0),
            'artifacts': list(set(artifacts)),
            'avg_difference': avg_diff if 'avg_diff' in locals() else 0.0
        }
    
    def _motion_vector_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Motion vector analysis for temporal inconsistencies"""
        
        if len(frames) < 3:
            return {'score': 0.1, 'artifacts': []}
        
        try:
            # Create feature points to track
            gray_first = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
            corners = cv2.goodFeaturesToTrack(gray_first, maxCorners=100, 
                                            qualityLevel=0.3, minDistance=7, blockSize=7)
            
            if corners is None or len(corners) < 10:
                return {'score': 0.2, 'artifacts': ['insufficient_features']}
            
            # Track features across frames
            motion_vectors = []
            artifacts = []
            
            prev_gray = gray_first
            prev_corners = corners
            
            for i in range(1, len(frames)):
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate optical flow
                next_corners, status, error = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray, prev_corners, None
                )
                
                # Select good points
                good_new = next_corners[status == 1]
                good_old = prev_corners[status == 1]
                
                if len(good_new) < 5:
                    break
                
                # Calculate motion vectors
                vectors = good_new - good_old
                motion_vectors.append(vectors)
                
                prev_gray = curr_gray
                prev_corners = good_new.reshape(-1, 1, 2)
            
            if not motion_vectors:
                return {'score': 0.2, 'artifacts': ['tracking_failed']}
            
            # Analyze motion vector characteristics
            ai_score = 0.0
            
            # Check vector consistency across time
            vector_magnitudes = []
            vector_directions = []
            
            for vectors in motion_vectors:
                magnitudes = np.sqrt(vectors[:, 0]**2 + vectors[:, 1]**2)
                directions = np.arctan2(vectors[:, 1], vectors[:, 0])
                
                vector_magnitudes.append(np.mean(magnitudes))
                vector_directions.append(np.mean(directions))
            
            # Check for unnatural motion consistency
            magnitude_variance = np.var(vector_magnitudes)
            direction_variance = np.var(vector_directions)
            
            if magnitude_variance < 0.1:  # Too consistent magnitudes
                ai_score += 0.3
                artifacts.append('overly_consistent_motion_magnitude')
            
            if direction_variance < 0.1:  # Too consistent directions
                ai_score += 0.3
                artifacts.append('overly_consistent_motion_direction')
            
            # Check for abrupt changes
            for i in range(len(vector_magnitudes) - 1):
                mag_change = abs(vector_magnitudes[i+1] - vector_magnitudes[i])
                avg_mag = np.mean(vector_magnitudes)
                
                if mag_change > avg_mag * 2:  # Sudden magnitude change
                    ai_score += 0.2
                    artifacts.append('abrupt_motion_changes')
                    break
            
            return {
                'score': min(ai_score, 1.0),
                'artifacts': list(set(artifacts)),
                'tracked_features': len(motion_vectors)
            }
            
        except Exception as e:
            logger.error(f"Motion vector analysis failed: {e}")
            return {'score': 0.2, 'artifacts': ['analysis_failed']}
    
    def _temporal_frequency_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Temporal frequency domain analysis"""
        
        if len(frames) < 8:
            return {'score': 0.1, 'artifacts': []}
        
        try:
            # Convert frames to grayscale and create temporal signal
            gray_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frames]
            
            # Sample pixels for temporal analysis
            h, w = gray_frames[0].shape
            sample_points = [
                (h//4, w//4), (h//4, 3*w//4),
                (3*h//4, w//4), (3*h//4, 3*w//4),
                (h//2, w//2)
            ]
            
            temporal_signals = []
            for y, x in sample_points:
                signal_values = [frame[y, x] for frame in gray_frames]
                temporal_signals.append(signal_values)
            
            ai_score = 0.0
            artifacts = []
            
            # Analyze each temporal signal
            for i, signal_values in enumerate(temporal_signals):
                # FFT of temporal signal
                fft_signal = np.fft.fft(signal_values)
                power_spectrum = np.abs(fft_signal)**2
                
                # Check for dominant frequencies (indicates artificial patterns)
                freqs = np.fft.fftfreq(len(signal_values))
                
                # Find peaks in power spectrum
                peaks, _ = signal.find_peaks(power_spectrum[1:len(power_spectrum)//2])
                
                if len(peaks) > len(power_spectrum) * 0.1:  # Too many peaks
                    ai_score += 0.1
                    artifacts.append(f'excessive_temporal_frequencies_point_{i}')
                
                # Check for very low frequency dominance (over-smoothing)
                low_freq_power = np.sum(power_spectrum[1:3])
                total_power = np.sum(power_spectrum[1:len(power_spectrum)//2])
                
                if low_freq_power > total_power * 0.8:
                    ai_score += 0.2
                    artifacts.append(f'low_frequency_dominance_point_{i}')
            
            return {
                'score': min(ai_score, 1.0),
                'artifacts': list(set(artifacts)),
                'sample_points': len(sample_points)
            }
            
        except Exception as e:
            logger.error(f"Temporal frequency analysis failed: {e}")
            return {'score': 0.1, 'artifacts': ['analysis_failed']}
    
    def _face_landmark_temporal_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Analyze temporal consistency of facial landmarks"""
        
        try:
            # This would require a face landmark detector like MediaPipe or dlib
            # For now, return placeholder analysis
            return {'score': 0.2, 'artifacts': ['landmark_detector_unavailable']}
            
        except Exception as e:
            logger.error(f"Face landmark analysis failed: {e}")
            return {'score': 0.1, 'artifacts': ['analysis_failed']}
    
    def _edge_temporal_consistency(self, frames: List[np.ndarray]) -> Dict:
        """Analyze temporal consistency of edges"""
        
        if len(frames) < 3:
            return {'score': 0.1, 'artifacts': []}
        
        try:
            edge_consistencies = []
            artifacts = []
            
            # Extract edges from each frame
            edge_frames = []
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                edge_frames.append(edges)
            
            # Analyze edge temporal consistency
            for i in range(len(edge_frames) - 1):
                # Calculate edge similarity between consecutive frames
                edges1 = edge_frames[i].astype(np.float32)
                edges2 = edge_frames[i+1].astype(np.float32)
                
                # Normalized cross-correlation
                correlation = cv2.matchTemplate(edges1, edges2, cv2.TM_CCOEFF_NORMED)[0, 0]
                edge_consistencies.append(correlation)
            
            if edge_consistencies:
                avg_consistency = np.mean(edge_consistencies)
                consistency_std = np.std(edge_consistencies)
                
                ai_score = 0.0
                
                # AI videos often have overly consistent edges
                if avg_consistency > 0.95:
                    ai_score += 0.3
                    artifacts.append('overly_consistent_edges')
                
                # Or very inconsistent edges
                if avg_consistency < 0.5:
                    ai_score += 0.2
                    artifacts.append('inconsistent_edges')
                
                # Check for low variation
                if consistency_std < 0.02:
                    ai_score += 0.2
                    artifacts.append('low_edge_variation')
            else:
                ai_score = 0.1
            
            return {
                'score': min(ai_score, 1.0),
                'artifacts': artifacts,
                'avg_edge_consistency': avg_consistency if 'avg_consistency' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Edge temporal analysis failed: {e}")
            return {'score': 0.1, 'artifacts': ['analysis_failed']}
    
    def _texture_temporal_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Analyze temporal consistency of textures"""
        
        if len(frames) < 3:
            return {'score': 0.1, 'artifacts': []}
        
        try:
            texture_features = []
            artifacts = []
            
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Local Binary Pattern for texture analysis
                # Simplified LBP implementation
                lbp = np.zeros_like(gray)
                for i in range(1, gray.shape[0]-1):
                    for j in range(1, gray.shape[1]-1):
                        center = gray[i, j]
                        code = 0
                        code |= (gray[i-1, j-1] >= center) << 7
                        code |= (gray[i-1, j] >= center) << 6
                        code |= (gray[i-1, j+1] >= center) << 5
                        code |= (gray[i, j+1] >= center) << 4
                        code |= (gray[i+1, j+1] >= center) << 3
                        code |= (gray[i+1, j] >= center) << 2
                        code |= (gray[i+1, j-1] >= center) << 1
                        code |= (gray[i, j-1] >= center) << 0
                        lbp[i, j] = code
                
                # Calculate texture features
                hist, _ = np.histogram(lbp.flatten(), bins=256, range=(0, 256))
                texture_features.append(hist / np.sum(hist))  # Normalize
            
            # Analyze texture temporal consistency
            texture_similarities = []
            for i in range(len(texture_features) - 1):
                # Chi-square distance between histograms
                hist1, hist2 = texture_features[i], texture_features[i+1]
                chi_sq = np.sum((hist1 - hist2)**2 / (hist1 + hist2 + 1e-8))
                texture_similarities.append(1.0 / (1.0 + chi_sq))  # Convert to similarity
            
            if texture_similarities:
                avg_similarity = np.mean(texture_similarities)
                similarity_std = np.std(texture_similarities)
                
                ai_score = 0.0
                
                # AI videos often have overly consistent textures
                if avg_similarity > 0.98:
                    ai_score += 0.3
                    artifacts.append('overly_consistent_textures')
                
                # Check for low variation in texture similarity
                if similarity_std < 0.01:
                    ai_score += 0.2
                    artifacts.append('low_texture_variation')
            else:
                ai_score = 0.1
            
            return {
                'score': min(ai_score, 1.0),
                'artifacts': artifacts,
                'texture_consistency': avg_similarity if 'avg_similarity' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Texture temporal analysis failed: {e}")
            return {'score': 0.1, 'artifacts': ['analysis_failed']}
    
    def _color_temporal_analysis(self, frames: List[np.ndarray]) -> Dict:
        """Analyze temporal consistency of colors"""
        
        if len(frames) < 3:
            return {'score': 0.1, 'artifacts': []}
        
        try:
            color_histograms = []
            artifacts = []
            
            for frame in frames:
                # Calculate color histograms for each channel
                hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
                hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
                hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
                
                # Combine histograms
                combined_hist = np.concatenate([hist_b.flatten(), hist_g.flatten(), hist_r.flatten()])
                combined_hist = combined_hist / np.sum(combined_hist)  # Normalize
                
                color_histograms.append(combined_hist)
            
            # Analyze color temporal consistency
            color_similarities = []
            for i in range(len(color_histograms) - 1):
                hist1, hist2 = color_histograms[i], color_histograms[i+1]
                
                # Bhattacharyya distance
                similarity = cv2.compareHist(hist1.astype(np.float32), 
                                           hist2.astype(np.float32), 
                                           cv2.HISTCMP_BHATTACHARYYA)
                color_similarities.append(1.0 - similarity)  # Convert to similarity
            
            if color_similarities:
                avg_similarity = np.mean(color_similarities)
                similarity_std = np.std(color_similarities)
                
                ai_score = 0.0
                
                # AI videos often have overly consistent color distributions
                if avg_similarity > 0.98:
                    ai_score += 0.2
                    artifacts.append('overly_consistent_colors')
                
                # Check for sudden color changes (generation artifacts)
                for sim in color_similarities:
                    if sim < 0.7:  # Sudden color change
                        ai_score += 0.1
                        artifacts.append('sudden_color_changes')
                        break
                
                # Check for low variation
                if similarity_std < 0.01:
                    ai_score += 0.1
                    artifacts.append('low_color_variation')
            else:
                ai_score = 0.1
            
            return {
                'score': min(ai_score, 1.0),
                'artifacts': artifacts,
                'color_consistency': avg_similarity if 'avg_similarity' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Color temporal analysis failed: {e}")
            return {'score': 0.1, 'artifacts': ['analysis_failed']}
    
    def _face_temporal_consistency_analysis(self, faces: List[torch.Tensor]) -> Dict:
        """Analyze temporal consistency of face tensors"""
        
        if len(faces) < 3:
            return {'score': 0.1, 'artifacts': []}
        
        try:
            face_similarities = []
            artifacts = []
            
            for i in range(len(faces) - 1):
                try:
                    # Convert tensors to numpy
                    face1_np = self._tensor_to_numpy(faces[i])
                    face2_np = self._tensor_to_numpy(faces[i+1])
                    
                    # Calculate structural similarity
                    # Simplified SSIM calculation
                    face1_gray = cv2.cvtColor(face1_np, cv2.COLOR_RGB2GRAY) if len(face1_np.shape) == 3 else face1_np
                    face2_gray = cv2.cvtColor(face2_np, cv2.COLOR_RGB2GRAY) if len(face2_np.shape) == 3 else face2_np
                    
                    # Mean squared error
                    mse = mean_squared_error(face1_gray.flatten(), face2_gray.flatten())
                    similarity = 1.0 / (1.0 + mse / 1000.0)  # Convert to similarity
                    
                    face_similarities.append(similarity)
                    
                except Exception as e:
                    logger.warning(f"Face similarity calculation failed: {e}")
                    continue
            
            if face_similarities:
                avg_similarity = np.mean(face_similarities)
                similarity_std = np.std(face_similarities)
                
                ai_score = 0.0
                
                # AI-generated faces often have unnatural consistency
                if avg_similarity > 0.95:
                    ai_score += 0.4
                    artifacts.append('overly_consistent_faces')
                
                # Or sudden changes due to generation artifacts
                for sim in face_similarities:
                    if sim < 0.3:  # Sudden face change
                        ai_score += 0.3
                        artifacts.append('sudden_face_changes')
                        break
                
                # Check for low variation
                if similarity_std < 0.02:
                    ai_score += 0.2
                    artifacts.append('low_face_variation')
            else:
                ai_score = 0.2
            
            return {
                'score': min(ai_score, 1.0),
                'artifacts': artifacts,
                'face_consistency': avg_similarity if 'avg_similarity' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"Face temporal consistency analysis failed: {e}")
            return {'score': 0.1, 'artifacts': ['analysis_failed']}
    
    def _ensemble_temporal_decision(self, analyses: Dict, fps: float) -> Dict:
        """Ensemble decision from all temporal analyses"""
        
        # Weights for different analyses
        weights = {
            'optical_flow_analysis': 0.20,
            'frame_difference_analysis': 0.15,
            'motion_vector_analysis': 0.15,
            'temporal_frequency_analysis': 0.10,
            'face_landmark_temporal_analysis': 0.05,
            'edge_temporal_consistency': 0.10,
            'texture_temporal_analysis': 0.10,
            'color_temporal_analysis': 0.10,
            'face_temporal_consistency': 0.15
        }
        
        total_score = 0.0
        total_weight = 0.0
        all_artifacts = []
        
        for analysis_name, result in analyses.items():
            if analysis_name in weights and isinstance(result, dict):
                score = result.get('score', 0.0)
                artifacts = result.get('artifacts', [])
                
                total_score += score * weights[analysis_name]
                total_weight += weights[analysis_name]
                all_artifacts.extend(artifacts)
        
        if total_weight > 0:
            final_probability = total_score / total_weight
        else:
            final_probability = 0.1
        
        # Determine likely generator based on temporal patterns
        generator_scores = {}
        for generator, signature in self.ai_temporal_signatures.items():
            score = 0.0
            
            # Check if temporal patterns match this generator
            if 'overly_consistent' in str(all_artifacts):
                if signature['frame_consistency'] > 0.9:
                    score += 0.3
            
            if 'smooth' in str(all_artifacts):
                if signature['motion_smoothness'] > 0.85:
                    score += 0.2
            
            generator_scores[generator] = score
        
        likely_generator = max(generator_scores, key=generator_scores.get) if generator_scores else 'unknown'
        
        return {
            'probability': final_probability,
            'confidence': min(final_probability * 100 + 20, 95.0),
            'artifacts': list(set(all_artifacts)),
            'generator': likely_generator if generator_scores.get(likely_generator, 0) > 0.2 else 'unknown',
            'fps': fps
        }
    
    def _tensor_to_numpy(self, tensor: torch.Tensor) -> np.ndarray:
        """Convert tensor to numpy array"""
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
ultra_temporal_analyzer = UltraTemporalAnalyzer()
