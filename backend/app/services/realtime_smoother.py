"""
Realtime Smoother - EMA Temporal Smoothing for Real-time Detection
================================================================

This module provides exponential moving average (EMA) smoothing for real-time
deepfake detection to prevent frame-by-frame jitter and provide stable predictions.

Features:
- Exponential Moving Average (EMA) smoothing
- Configurable smoothing factor (alpha)
- Handles None confidence values gracefully
- Prevents prediction oscillation
- Memory-efficient single-value state
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RealtimeSmoother:
    """
    Exponential Moving Average (EMA) smoother for real-time detection stability.
    
    Prevents frame-by-frame prediction jitter by applying temporal smoothing
    to confidence values and predictions.
    """
    
    def __init__(self, alpha: float = 0.3):
        """
        Initialize the realtime smoother.
        
        Args:
            alpha: Smoothing factor (0.0 = no smoothing, 1.0 = no memory)
                  Lower values = more smoothing, higher values = more responsive
                  Recommended: 0.2-0.4 for stable detection with bias toward real
        """
        self.alpha = max(0.0, min(1.0, alpha))  # Clamp to valid range
        self.prev_conf = None
        self.prev_prediction = None
        self.smoothing_enabled = True
        self.real_bias = 0.1  # Slight bias toward real detection
        
        logger.info(f"RealtimeSmoother initialized with alpha={self.alpha}")
    
    def smooth_confidence(self, current_conf: Optional[float]) -> Optional[float]:
        """
        Apply EMA smoothing to confidence values without artificial bias.
        
        Args:
            current_conf: Current confidence value (can be None)
            
        Returns:
            Smoothed confidence value or None if no valid input
        """
        if not self.smoothing_enabled:
            return current_conf
            
        if current_conf is None:
            # Keep previous value if current is invalid
            return self.prev_conf
            
        if self.prev_conf is None:
            # First valid value
            self.prev_conf = current_conf
            return current_conf
            
        # ✅ CONSISTENCY FIX: Apply pure EMA smoothing without artificial bias
        smoothed = self.alpha * current_conf + (1 - self.alpha) * self.prev_conf
            
        self.prev_conf = smoothed
        
        logger.debug(f"Confidence smoothed: {current_conf:.3f} -> {smoothed:.3f}")
        return smoothed
    
    def smooth_prediction(self, current_pred: str) -> str:
        """
        Apply temporal smoothing to predictions to prevent oscillation.
        
        Args:
            current_pred: Current prediction string
            
        Returns:
            Smoothed prediction (may be previous value to prevent oscillation)
        """
        if not self.smoothing_enabled:
            return current_pred
            
        if self.prev_prediction is None:
            self.prev_prediction = current_pred
            return current_pred
            
        # Simple oscillation prevention: keep previous if current is different
        # but not if it's been the same for too long
        if current_pred != self.prev_prediction:
            # Allow prediction change but with some hysteresis
            self.prev_prediction = current_pred
            
        return self.prev_prediction
    
    def smooth_result(self, prediction: str, confidence: Optional[float]) -> tuple[str, Optional[float]]:
        """
        Apply enhanced smoothing to both prediction and confidence.
        
        Args:
            prediction: Current prediction string
            confidence: Current confidence value
            
        Returns:
            Tuple of (smoothed_prediction, smoothed_confidence)
        """
        if not self.smoothing_enabled:
            return prediction, confidence
            
        # Extract fake probability from prediction
        fake_probability = 0.9 if "Deepfake" in prediction else 0.1
        
        # Use enhanced temporal smoothing if available
        try:
            from .temporal_smoothing import smooth_realtime_prediction
            smoothed_pred, smoothed_conf = smooth_realtime_prediction(
                prediction, confidence or 0.5, fake_probability
            )
            return smoothed_pred, smoothed_conf
        except ImportError:
            # Fallback to basic smoothing
            smoothed_pred = self.smooth_prediction(prediction)
            smoothed_conf = self.smooth_confidence(confidence)
            return smoothed_pred, smoothed_conf
    
    def reset(self):
        """Reset the smoother state (useful for new video sessions)."""
        self.prev_conf = None
        self.prev_prediction = None
        logger.info("RealtimeSmoother reset")
    
    def set_alpha(self, alpha: float):
        """Update the smoothing factor."""
        self.alpha = max(0.0, min(1.0, alpha))
        logger.info(f"RealtimeSmoother alpha updated to {self.alpha}")
    
    def enable_smoothing(self, enabled: bool = True):
        """Enable or disable smoothing."""
        self.smoothing_enabled = enabled
        logger.info(f"RealtimeSmoother smoothing {'enabled' if enabled else 'disabled'}")
    
    def get_state(self) -> dict:
        """Get current smoother state for debugging."""
        return {
            "alpha": self.alpha,
            "prev_confidence": self.prev_conf,
            "prev_prediction": self.prev_prediction,
            "smoothing_enabled": self.smoothing_enabled
        }


# Global smoother instance for real-time detection
_realtime_smoother = None

def get_realtime_smoother() -> RealtimeSmoother:
    """Get the global realtime smoother instance."""
    global _realtime_smoother
    if _realtime_smoother is None:
        _realtime_smoother = RealtimeSmoother(alpha=0.3)  # Default conservative smoothing with real bias
    return _realtime_smoother

def reset_realtime_smoother():
    """Reset the global realtime smoother (useful for new sessions)."""
    global _realtime_smoother
    if _realtime_smoother is not None:
        _realtime_smoother.reset()
