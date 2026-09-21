"""
Bias-Aware Correction for Deepfake Detection
===========================================

This module provides subtle bias correction that preserves the model's
intelligence while adjusting for systematic bias toward false positives.
"""

import logging
import numpy as np
from typing import Tuple, Dict, Any
import time

logger = logging.getLogger(__name__)

class BiasAwareCorrection:
    """Subtle bias correction that preserves model intelligence"""
    
    def __init__(self):
        self.bias_history = {}
        self.correction_factor = 0.15  # Subtle 15% adjustment
        self.confidence_threshold = 0.75  # Only adjust if very confident
        
    def should_apply_correction(self, model_name: str, fake_prob: float) -> bool:
        """Check if subtle correction should be applied"""
        # Only apply correction if:
        # 1. Model is very confident (>75%) about fake prediction
        # 2. This is a pattern (not just one-off)
        return fake_prob > self.confidence_threshold
    
    def apply_subtle_correction(self, model_name: str, fake_prob: float, real_prob: float) -> Tuple[str, float]:
        """Apply subtle bias correction that preserves model logic"""
        
        # Track bias patterns
        if model_name not in self.bias_history:
            self.bias_history[model_name] = []
        
        self.bias_history[model_name].append(fake_prob)
        
        # Keep only recent history (last 10 predictions)
        if len(self.bias_history[model_name]) > 10:
            self.bias_history[model_name] = self.bias_history[model_name][-10:]
        
        # Check if this is a systematic bias pattern
        recent_predictions = self.bias_history[model_name]
        if len(recent_predictions) >= 3:
            avg_fake_prob = np.mean(recent_predictions)
            if avg_fake_prob > 0.85:  # Systematic high fake predictions
                logger.warning(f"🔍 Systematic bias detected in {model_name}: avg_fake_prob={avg_fake_prob:.3f}")
                
                # Apply subtle correction: reduce fake confidence by 15%
                corrected_fake_prob = fake_prob * (1.0 - self.correction_factor)
                corrected_real_prob = 1.0 - corrected_fake_prob
                
                # Only flip if correction makes real more likely
                if corrected_real_prob > corrected_fake_prob:
                    logger.info(f"✅ Subtle correction: {fake_prob:.3f} → {corrected_fake_prob:.3f} (Real: {corrected_real_prob:.3f})")
                    return "Real Face", corrected_real_prob
                else:
                    # Keep original prediction but with reduced confidence
                    logger.info(f"✅ Confidence adjustment: {fake_prob:.3f} → {corrected_fake_prob:.3f}")
                    return "Deepfake Detected", corrected_fake_prob
        
        # For single high-confidence predictions, apply lighter correction
        if fake_prob > 0.9:
            logger.info(f"🔍 High confidence prediction: {fake_prob:.3f}")
            
            # Apply lighter correction (10% instead of 15%)
            corrected_fake_prob = fake_prob * 0.9
            corrected_real_prob = 1.0 - corrected_fake_prob
            
            # Only flip if it makes sense
            if corrected_real_prob > corrected_fake_prob:
                logger.info(f"✅ Light correction: {fake_prob:.3f} → {corrected_fake_prob:.3f} (Real: {corrected_real_prob:.3f})")
                return "Real Face", corrected_real_prob
            else:
                logger.info(f"✅ Confidence reduction: {fake_prob:.3f} → {corrected_fake_prob:.3f}")
                return "Deepfake Detected", corrected_fake_prob
        
        # No correction needed - use original prediction
        if fake_prob >= 0.7:
            return "Deepfake Detected", fake_prob
        else:
            return "Real Face", real_prob
    
    def get_bias_stats(self) -> Dict[str, Any]:
        """Get bias statistics"""
        stats = {}
        for model_name, history in self.bias_history.items():
            if history:
                stats[model_name] = {
                    'avg_fake_prob': np.mean(history),
                    'max_fake_prob': np.max(history),
                    'prediction_count': len(history),
                    'systematic_bias': np.mean(history) > 0.85
                }
        return stats

# Global instance
bias_correction = BiasAwareCorrection()

def apply_bias_aware_correction(model_name: str, fake_prob: float, real_prob: float) -> Tuple[str, float]:
    """Apply bias-aware correction that preserves model intelligence"""
    return bias_correction.apply_subtle_correction(model_name, fake_prob, real_prob)

def get_bias_stats() -> Dict[str, Any]:
    """Get bias statistics"""
    return bias_correction.get_bias_stats()
