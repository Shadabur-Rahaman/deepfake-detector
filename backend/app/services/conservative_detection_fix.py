"""
Conservative Deepfake Detection Fix
==================================

This module provides conservative detection logic to prevent false positives
on real videos. It applies bias correction and conservative thresholds.
"""

import logging
import numpy as np
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ConservativeDetectionFix:
    """Conservative detection logic to prevent false positives on real content"""
    
    def __init__(self):
        self.bias_tracker = {}
        self.conservative_threshold = 0.7  # Only classify as fake if >70% confidence
        
    def apply_conservative_correction(self, 
                                    model_name: str, 
                                    fake_prob: float, 
                                    real_prob: float) -> Tuple[str, float]:
        """
        Apply conservative correction to prevent false positives
        
        Args:
            model_name: Name of the model
            fake_prob: Probability of being fake
            real_prob: Probability of being real
            
        Returns:
            Tuple of (prediction, confidence)
        """
        # Track model bias
        if model_name not in self.bias_tracker:
            self.bias_tracker[model_name] = 0
            
        # Apply conservative correction based on bias level
        if fake_prob > 0.9:
            # High bias detected - apply strong correction
            logger.warning(f"High bias detected in {model_name}: fake_prob={fake_prob:.3f}")
            self.bias_tracker[model_name] += 1
            
            # Apply 50% reduction in fake confidence
            corrected_fake_prob = fake_prob * 0.5
            corrected_real_prob = 1.0 - corrected_fake_prob
            
            if corrected_real_prob > corrected_fake_prob:
                return "Real Face", corrected_real_prob
            else:
                return "Deepfake Detected", corrected_fake_prob
                
        elif fake_prob > 0.8:
            # Moderate bias - apply light correction
            logger.warning(f"Moderate bias detected in {model_name}: fake_prob={fake_prob:.3f}")
            self.bias_tracker[model_name] += 0.5
            
            # Apply 20% reduction in fake confidence
            corrected_fake_prob = fake_prob * 0.8
            corrected_real_prob = 1.0 - corrected_fake_prob
            
            if corrected_real_prob > corrected_fake_prob:
                return "Real Face", corrected_real_prob
            else:
                return "Deepfake Detected", corrected_fake_prob
                
        else:
            # Normal case - use conservative threshold
            if fake_prob >= self.conservative_threshold and fake_prob > real_prob:
                return "Deepfake Detected", fake_prob
            else:
                return "Real Face", real_prob
    
    def is_model_biased(self, model_name: str) -> bool:
        """Check if a model is consistently biased"""
        return self.bias_tracker.get(model_name, 0) > 3
    
    def get_bias_info(self) -> Dict[str, Any]:
        """Get information about model bias"""
        return {
            'bias_tracker': self.bias_tracker.copy(),
            'conservative_threshold': self.conservative_threshold,
            'biased_models': [name for name, count in self.bias_tracker.items() if count > 3]
        }

# Global instance
conservative_fix = ConservativeDetectionFix()

def apply_conservative_detection(model_name: str, fake_prob: float, real_prob: float) -> Tuple[str, float]:
    """Apply conservative detection logic"""
    return conservative_fix.apply_conservative_correction(model_name, fake_prob, real_prob)

def is_model_biased(model_name: str) -> bool:
    """Check if a model is biased"""
    return conservative_fix.is_model_biased(model_name)

def get_bias_info() -> Dict[str, Any]:
    """Get bias information"""
    return conservative_fix.get_bias_info()
