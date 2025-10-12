# app/services/temporal_analyzer.py
import cv2
import numpy as np
import torch
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TemporalConsistencyAnalyzer:
    """Basic temporal analysis for video diffusion detection"""
    
    def analyze_video_temporal_consistency(self, video_path: str) -> Dict:
        """Analyze temporal consistency in video"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            
            frame_count = 0
            while frame_count < 10:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_resized = cv2.resize(frame, (224, 224))
                frames.append(frame_resized)
                frame_count += 1
            
            cap.release()
            
            if len(frames) < 3:
                return {'inconsistency_score': 0.3}
            
            # Calculate frame differences
            differences = []
            for i in range(len(frames) - 1):
                diff = cv2.absdiff(frames[i], frames[i + 1])
                diff_magnitude = np.mean(diff)
                differences.append(diff_magnitude)
            
            variance = np.var(differences) if differences else 0
            inconsistency_score = min(variance / 1000.0, 1.0)
            
            return {
                'inconsistency_score': float(inconsistency_score),
                'frames_analyzed': len(frames),
                'avg_difference': float(np.mean(differences)) if differences else 0
            }
            
        except Exception as e:
            logger.error(f"Temporal analysis failed: {e}")
            return {'inconsistency_score': 0.4}
