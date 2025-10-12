"""
Temporal Smoothing for Real-time Deepfake Detection
==================================================

This module implements temporal smoothing to reduce prediction noise
in real-time webcam detection by averaging predictions across consecutive frames.

Author: AI Assistant
Date: 2025
"""

import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Any
from collections import deque
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PredictionRecord:
    """Record of a single prediction for temporal smoothing"""
    frame_id: int
    prediction: str
    confidence: float
    fake_probability: float
    timestamp: float

class TemporalSmoother:
    """
    Temporal smoothing for real-time deepfake detection
    
    Features:
    - Exponential Moving Average (EMA) for smooth transitions
    - Rolling window for consistency checking
    - Confidence-based weighting
    - Webcam-specific bias toward real faces
    """
    
    def __init__(self, 
                 window_size: int = 10,
                 ema_alpha: float = 0.3,
                 consistency_threshold: float = 0.7,
                 webcam_bias_real: float = 0.1):
        """
        Initialize temporal smoother
        
        Args:
            window_size: Number of recent predictions to keep
            ema_alpha: EMA smoothing factor (0-1, higher = more responsive)
            consistency_threshold: Required agreement ratio for confident prediction
            webcam_bias_real: Bias toward real faces for webcam (0-1)
        """
        self.window_size = window_size
        self.ema_alpha = ema_alpha
        self.consistency_threshold = consistency_threshold
        self.webcam_bias_real = webcam_bias_real
        
        # Prediction history
        self.prediction_history = deque(maxlen=window_size)
        self.frame_id = 0
        
        # EMA state
        self.ema_fake_probability = 0.5  # Start neutral
        self.ema_confidence = 0.5
        
        logger.info(f"🔧 TemporalSmoother initialized: window={window_size}, ema_alpha={ema_alpha}")
    
    def add_prediction(self, 
                      prediction: str, 
                      confidence: float, 
                      fake_probability: float,
                      timestamp: Optional[float] = None) -> Tuple[str, float]:
        """
        Add a new prediction and return smoothed result
        
        Args:
            prediction: Raw prediction ("Real Face" or "Deepfake Detected")
            confidence: Raw confidence (0-1)
            fake_probability: Raw fake probability (0-1)
            timestamp: Optional timestamp
            
        Returns:
            Tuple of (smoothed_prediction, smoothed_confidence)
        """
        if timestamp is None:
            import time
            timestamp = time.time()
        
        # Create prediction record
        record = PredictionRecord(
            frame_id=self.frame_id,
            prediction=prediction,
            confidence=confidence,
            fake_probability=fake_probability,
            timestamp=timestamp
        )
        
        # Add to history
        self.prediction_history.append(record)
        self.frame_id += 1
        
        # Apply temporal smoothing
        smoothed_prediction, smoothed_confidence = self._apply_smoothing(record)
        
        logger.debug(f"🔍 Frame {self.frame_id}: Raw={prediction}({confidence:.3f}) → Smooth={smoothed_prediction}({smoothed_confidence:.3f})")
        
        return smoothed_prediction, smoothed_confidence
    
    def _apply_smoothing(self, current_record: PredictionRecord) -> Tuple[str, float]:
        """Apply temporal smoothing to current prediction"""
        
        # Update EMA
        self.ema_fake_probability = (
            self.ema_alpha * current_record.fake_probability + 
            (1 - self.ema_alpha) * self.ema_fake_probability
        )
        
        self.ema_confidence = (
            self.ema_alpha * current_record.confidence + 
            (1 - self.ema_alpha) * self.ema_confidence
        )
        
        # Apply webcam bias toward real faces
        adjusted_fake_prob = self._apply_webcam_bias(self.ema_fake_probability)
        
        # Check for consistency in recent predictions
        if len(self.prediction_history) >= 5:  # Need at least 5 frames for consistency check
            consistency_ratio = self._calculate_consistency()
            
            if consistency_ratio >= self.consistency_threshold:
                # High consistency - use EMA result
                final_prediction = self._prob_to_prediction(adjusted_fake_prob)
                final_confidence = min(self.ema_confidence * 1.2, 1.0)  # Boost confidence for consistency
            else:
                # Low consistency - be more conservative
                if adjusted_fake_prob > 0.7:
                    final_prediction = "Deepfake Detected"
                    final_confidence = adjusted_fake_prob * 0.8  # Reduce confidence for inconsistency
                elif adjusted_fake_prob < 0.3:
                    final_prediction = "Real Face"
                    final_confidence = (1.0 - adjusted_fake_prob) * 0.8
                else:
                    # Uncertain range - bias toward real for webcam
                    final_prediction = "Real Face"
                    final_confidence = 0.6
        else:
            # Not enough history - use EMA with conservative confidence
            final_prediction = self._prob_to_prediction(adjusted_fake_prob)
            final_confidence = min(self.ema_confidence * 0.8, 0.8)  # Conservative confidence
        
        return final_prediction, final_confidence
    
    def _apply_webcam_bias(self, fake_probability: float) -> float:
        """Apply webcam-specific bias toward real faces"""
        # Shift probability toward real faces
        adjusted_prob = fake_probability - self.webcam_bias_real
        return max(0.0, min(1.0, adjusted_prob))
    
    def _calculate_consistency(self) -> float:
        """Calculate consistency ratio in recent predictions"""
        if len(self.prediction_history) < 3:
            return 1.0  # Perfect consistency if not enough data
        
        # Get recent predictions (last 5 frames or all available)
        recent_count = min(5, len(self.prediction_history))
        recent_predictions = list(self.prediction_history)[-recent_count:]
        
        # Count real vs fake predictions
        real_count = sum(1 for p in recent_predictions if "Real" in p.prediction)
        fake_count = recent_count - real_count
        
        # Calculate consistency ratio
        max_count = max(real_count, fake_count)
        consistency_ratio = max_count / recent_count
        
        return consistency_ratio
    
    def _prob_to_prediction(self, fake_probability: float) -> str:
        """Convert fake probability to prediction string"""
        if fake_probability >= 0.5:
            return "Deepfake Detected"
        else:
            return "Real Face"
    
    def get_smoothing_stats(self) -> Dict[str, Any]:
        """Get current smoothing statistics"""
        if not self.prediction_history:
            return {"status": "No predictions yet"}
        
        recent_predictions = list(self.prediction_history)[-5:]
        consistency_ratio = self._calculate_consistency()
        
        return {
            "total_frames": len(self.prediction_history),
            "current_ema_fake_prob": self.ema_fake_probability,
            "current_ema_confidence": self.ema_confidence,
            "consistency_ratio": consistency_ratio,
            "recent_predictions": [p.prediction for p in recent_predictions],
            "window_size": self.window_size
        }
    
    def reset(self):
        """Reset smoothing state"""
        self.prediction_history.clear()
        self.frame_id = 0
        self.ema_fake_probability = 0.5
        self.ema_confidence = 0.5
        logger.info("🔄 TemporalSmoother reset")


# Global instance for real-time detection
_realtime_smoother = None

def get_realtime_smoother() -> TemporalSmoother:
    """Get global real-time smoother instance"""
    global _realtime_smoother
    if _realtime_smoother is None:
        _realtime_smoother = TemporalSmoother(
            window_size=10,
            ema_alpha=0.3,
            consistency_threshold=0.7,
            webcam_bias_real=0.1
        )
    return _realtime_smoother

def smooth_realtime_prediction(prediction: str, 
                             confidence: float, 
                             fake_probability: float) -> Tuple[str, float]:
    """
    Apply temporal smoothing to real-time prediction
    
    Args:
        prediction: Raw prediction from model
        confidence: Raw confidence
        fake_probability: Raw fake probability
        
    Returns:
        Tuple of (smoothed_prediction, smoothed_confidence)
    """
    smoother = get_realtime_smoother()
    return smoother.add_prediction(prediction, confidence, fake_probability)
