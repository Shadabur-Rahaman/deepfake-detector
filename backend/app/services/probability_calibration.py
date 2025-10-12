# backend/app/services/probability_calibration.py - Probability Calibration Module

import numpy as np
import torch
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CalibrationResult:
    """Result of probability calibration"""
    raw_probability: float
    calibrated_probability: float
    temperature: float
    confidence_boost: float
    is_calibrated: bool

class ConservativeCalibrator:
    """Conservative probability calibrator to reduce overconfident predictions"""
    
    def __init__(self, temperature: float = 1.5, uncertainty_penalty: float = 0.1):
        """
        Initialize conservative calibrator
        
        Args:
            temperature: Temperature for scaling (T > 1 reduces confidence)
            uncertainty_penalty: Penalty for uncertain predictions
        """
        self.temperature = temperature
        self.uncertainty_penalty = uncertainty_penalty
        
        logger.info(f"[OK] ConservativeCalibrator initialized: T={temperature}, penalty={uncertainty_penalty}")
    
    def calibrate(self, probability: float) -> float:
        """
        Apply conservative calibration to probability
        
        Args:
            probability: Raw probability (0-1)
            
        Returns:
            Calibrated probability (0-1)
        """
        try:
            if probability <= 0.0 or probability >= 1.0:
                return probability
            
            # Apply temperature scaling
            calibrated_prob = self._apply_temperature_scaling(probability)
            
            # Apply uncertainty penalty
            calibrated_prob = self._apply_uncertainty_penalty(calibrated_prob)
            
            # Ensure probability stays in valid range
            calibrated_prob = np.clip(calibrated_prob, 0.001, 0.999)
            
            return float(calibrated_prob)
            
        except Exception as e:
            logger.warning(f"[WARNING] Calibration failed: {e}, using raw probability")
            return probability
    
    def _apply_temperature_scaling(self, probability: float) -> float:
        """Apply temperature scaling to reduce overconfidence"""
        try:
            # Convert probability to logit
            logit = np.log(probability / (1.0 - probability))
            
            # Apply temperature scaling
            scaled_logit = logit / self.temperature
            
            # Convert back to probability
            calibrated_prob = 1.0 / (1.0 + np.exp(-scaled_logit))
            
            return calibrated_prob
            
        except Exception as e:
            logger.warning(f"[WARNING] Temperature scaling failed: {e}")
            return probability
    
    def _apply_uncertainty_penalty(self, probability: float) -> float:
        """Apply penalty for uncertain predictions"""
        try:
            # Calculate distance from 0.5 (uncertainty)
            distance_from_uncertainty = abs(probability - 0.5)
            
            # Apply penalty proportional to uncertainty
            penalty = self.uncertainty_penalty * (1.0 - distance_from_uncertainty * 2)
            
            # Move probability towards 0.5 (uncertainty)
            if probability > 0.5:
                calibrated_prob = probability - penalty
            else:
                calibrated_prob = probability + penalty
            
            return calibrated_prob
            
        except Exception as e:
            logger.warning(f"[WARNING] Uncertainty penalty failed: {e}")
            return probability
    
    def calibrate_batch(self, probabilities: List[float]) -> List[float]:
        """Calibrate a batch of probabilities"""
        return [self.calibrate(p) for p in probabilities]
    
    def get_calibration_info(self, probability: float) -> CalibrationResult:
        """Get detailed calibration information"""
        raw_prob = probability
        calibrated_prob = self.calibrate(probability)
        confidence_boost = calibrated_prob - raw_prob
        
        return CalibrationResult(
            raw_probability=raw_prob,
            calibrated_probability=calibrated_prob,
            temperature=self.temperature,
            confidence_boost=confidence_boost,
            is_calibrated=True
        )

class TemperatureCalibrator:
    """Temperature scaling calibrator"""
    
    def __init__(self, temperature: float = 1.5):
        self.temperature = temperature
        logger.info(f"[OK] TemperatureCalibrator initialized: T={temperature}")
    
    def calibrate(self, probability: float) -> float:
        """Apply temperature scaling"""
        try:
            if probability <= 0.0 or probability >= 1.0:
                return probability
            
            # Convert to logit
            logit = np.log(probability / (1.0 - probability))
            
            # Apply temperature
            scaled_logit = logit / self.temperature
            
            # Convert back to probability
            calibrated_prob = 1.0 / (1.0 + np.exp(-scaled_logit))
            
            return float(calibrated_prob)
            
        except Exception as e:
            logger.warning(f"[WARNING] Temperature calibration failed: {e}")
            return probability

def apply_uncertainty_penalty(probability: float, confidence: float) -> Tuple[float, float]:
    """
    Apply uncertainty penalty to reduce overconfident predictions
    
    Args:
        probability: Raw probability (0-1)
        confidence: Raw confidence (0-100)
        
    Returns:
        Tuple of (calibrated_probability, calibrated_confidence)
    """
    try:
        # Calculate uncertainty penalty
        distance_from_uncertainty = abs(probability - 0.5)
        penalty_factor = 1.0 - (distance_from_uncertainty * 2)  # 0 at 0.5, 1 at 0.0/1.0
        
        # Apply penalty
        penalty = 0.1 * penalty_factor  # 10% max penalty
        if probability > 0.5:
            calibrated_prob = probability - penalty
        else:
            calibrated_prob = probability + penalty
        
        # Calibrate confidence proportionally
        confidence_factor = calibrated_prob / max(probability, 0.001)
        calibrated_confidence = confidence * confidence_factor
        
        # Ensure values stay in valid ranges
        calibrated_prob = np.clip(calibrated_prob, 0.001, 0.999)
        calibrated_confidence = np.clip(calibrated_confidence, 1.0, 99.0)
        
        return float(calibrated_prob), float(calibrated_confidence)
        
    except Exception as e:
        logger.warning(f"[WARNING] Uncertainty penalty failed: {e}")
        return probability, confidence

def validate_model_agreement(model_probabilities: Dict[str, float], threshold: float = 0.4) -> bool:
    """
    Validate if models agree on their predictions
    
    Args:
        model_probabilities: Dictionary of model names to probabilities
        threshold: Agreement threshold (0-1)
        
    Returns:
        True if models agree, False otherwise
    """
    try:
        if len(model_probabilities) < 2:
            return True  # Single model, no disagreement possible
        
        probabilities = list(model_probabilities.values())
        
        # Calculate standard deviation of probabilities
        std_dev = np.std(probabilities)
        
        # Models agree if standard deviation is below threshold
        models_agree = std_dev < threshold
        
        if not models_agree:
            logger.warning(f"[WARNING] Model disagreement detected: std={std_dev:.4f}, threshold={threshold}")
            logger.warning(f"   Model probabilities: {model_probabilities}")
        
        return models_agree
        
    except Exception as e:
        logger.warning(f"[WARNING] Model agreement validation failed: {e}")
        return True  # Assume agreement on error

def calibrate_ensemble_probability(probabilities: List[float], 
                                 weights: List[float],
                                 temperature: float = 1.5) -> float:
    """
    Calibrate ensemble probability with temperature scaling
    
    Args:
        probabilities: List of model probabilities
        weights: List of model weights
        temperature: Temperature for calibration
        
    Returns:
        Calibrated ensemble probability
    """
    try:
        if not probabilities or not weights:
            return 0.5
        
        # Ensure weights sum to 1
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(probabilities)] * len(probabilities)
        
        # Calculate weighted average
        weighted_prob = sum(p * w for p, w in zip(probabilities, weights))
        
        # Apply temperature scaling
        calibrator = TemperatureCalibrator(temperature)
        calibrated_prob = calibrator.calibrate(weighted_prob)
        
        return calibrated_prob
        
    except Exception as e:
        logger.warning(f"[WARNING] Ensemble calibration failed: {e}")
        return 0.5

def get_calibration_statistics(calibrator: ConservativeCalibrator, 
                             test_probabilities: List[float]) -> Dict[str, float]:
    """
    Get calibration statistics for a set of test probabilities
    
    Args:
        calibrator: Calibrator instance
        test_probabilities: List of test probabilities
        
    Returns:
        Dictionary of calibration statistics
    """
    try:
        raw_probs = np.array(test_probabilities)
        calibrated_probs = np.array([calibrator.calibrate(p) for p in test_probabilities])
        
        # Calculate statistics
        mean_raw = np.mean(raw_probs)
        mean_calibrated = np.mean(calibrated_probs)
        std_raw = np.std(raw_probs)
        std_calibrated = np.std(calibrated_probs)
        
        # Calculate calibration improvement
        raw_confidence = np.mean(np.abs(raw_probs - 0.5) * 2)  # Average distance from 0.5
        calibrated_confidence = np.mean(np.abs(calibrated_probs - 0.5) * 2)
        confidence_reduction = raw_confidence - calibrated_confidence
        
        return {
            'mean_raw_probability': mean_raw,
            'mean_calibrated_probability': mean_calibrated,
            'std_raw_probability': std_raw,
            'std_calibrated_probability': std_calibrated,
            'confidence_reduction': confidence_reduction,
            'calibration_effectiveness': confidence_reduction / max(raw_confidence, 0.001)
        }
        
    except Exception as e:
        logger.warning(f"[WARNING] Calibration statistics failed: {e}")
        return {}

# Global calibrator instances
conservative_calibrator = ConservativeCalibrator()
temperature_calibrator = TemperatureCalibrator()

def get_conservative_calibrator() -> ConservativeCalibrator:
    """Get the global conservative calibrator"""
    return conservative_calibrator

def get_temperature_calibrator() -> TemperatureCalibrator:
    """Get the global temperature calibrator"""
    return temperature_calibrator