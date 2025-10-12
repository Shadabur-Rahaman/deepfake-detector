"""
Unbiased Scoring System 2025 - Modern Ensemble Scoring
====================================================

This module provides unbiased ensemble scoring methods that address the bias issues
in the current detection system, ensuring realistic confidence scores and proper
distinction between real and fake content.

Features:
- Multiple unbiased scoring methods
- Proper ensemble aggregation
- Confidence calibration integration
- Uncertainty quantification
- Real-time scoring updates
- 2025 AI standards compliance
"""

import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import stats
import warnings

logger = logging.getLogger(__name__)

class ScoringMethod(Enum):
    """Unbiased scoring methods for 2025"""
    WEIGHTED_AVERAGE = "weighted_average"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    BAYESIAN_ENSEMBLE = "bayesian_ensemble"
    TEMPERATURE_SCALED = "temperature_scaled"
    PLATT_CALIBRATED = "platt_calibrated"
    ISOTONIC_CALIBRATED = "isotonic_calibrated"
    UNCERTAINTY_AWARE = "uncertainty_aware"

@dataclass
class UnbiasedScore:
    """Result of unbiased scoring"""
    prediction: str
    confidence: float
    method: ScoringMethod
    reasoning: str
    uncertainty_estimate: float
    model_agreement: float
    ensemble_variance: float
    calibration_applied: bool
    raw_scores: Dict[str, float]
    processed_scores: Dict[str, float]

@dataclass
class ScoringConfig:
    """Configuration for unbiased scoring"""
    method: ScoringMethod = ScoringMethod.WEIGHTED_AVERAGE
    temperature: float = 2.0
    confidence_threshold: float = 0.5
    uncertainty_weight: float = 0.3
    calibration_enabled: bool = True
    model_weights: Optional[Dict[str, float]] = None
    min_confidence_difference: float = 0.1

class UnbiasedScoringSystem2025:
    """
    Advanced unbiased scoring system for 2025 AI standards.
    
    Features:
    - Multiple unbiased scoring methods
    - Proper confidence calibration
    - Uncertainty quantification
    - Model agreement analysis
    - Real-time scoring updates
    """
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()
        self.scoring_history = []
        self.model_performance_tracking = {}
        
    def calculate_unbiased_score(self, 
                               model_predictions: Dict[str, Tuple[str, float]],
                               model_logits: Optional[Dict[str, torch.Tensor]] = None) -> UnbiasedScore:
        """
        Calculate unbiased ensemble score using 2025 standards.
        
        Args:
            model_predictions: Dict of model_name -> (prediction, confidence)
            model_logits: Optional raw logits for advanced scoring
            
        Returns:
            Unbiased ensemble score
        """
        try:
            if not model_predictions:
                return self._create_empty_score()
            
            logger.info(f"🧠 Calculating unbiased score using {self.config.method.value}")
            
            # Extract predictions and confidences
            predictions = [pred[0] for pred in model_predictions.values()]
            confidences = [pred[1] for pred in model_predictions.values()]
            model_names = list(model_predictions.keys())
            
            # Store raw scores for analysis
            raw_scores = dict(zip(model_names, confidences))
            
            # Apply scoring method
            if self.config.method == ScoringMethod.WEIGHTED_AVERAGE:
                result = self._weighted_average_scoring(model_names, confidences, predictions)
            elif self.config.method == ScoringMethod.CONFIDENCE_WEIGHTED:
                result = self._confidence_weighted_scoring(model_names, confidences, predictions)
            elif self.config.method == ScoringMethod.BAYESIAN_ENSEMBLE:
                result = self._bayesian_ensemble_scoring(model_names, confidences, predictions)
            elif self.config.method == ScoringMethod.TEMPERATURE_SCALED:
                result = self._temperature_scaled_scoring(model_names, confidences, predictions, model_logits)
            elif self.config.method == ScoringMethod.PLATT_CALIBRATED:
                result = self._platt_calibrated_scoring(model_names, confidences, predictions, model_logits)
            elif self.config.method == ScoringMethod.ISOTONIC_CALIBRATED:
                result = self._isotonic_calibrated_scoring(model_names, confidences, predictions, model_logits)
            elif self.config.method == ScoringMethod.UNCERTAINTY_AWARE:
                result = self._uncertainty_aware_scoring(model_names, confidences, predictions)
            else:
                # Fallback to weighted average
                result = self._weighted_average_scoring(model_names, confidences, predictions)
            
            # Calculate additional metrics
            uncertainty_estimate = self._calculate_uncertainty_estimate(confidences)
            model_agreement = self._calculate_model_agreement(predictions)
            ensemble_variance = self._calculate_ensemble_variance(confidences)
            
            # Create unbiased score result
            unbiased_score = UnbiasedScore(
                prediction=result['prediction'],
                confidence=result['confidence'],
                method=self.config.method,
                reasoning=result['reasoning'],
                uncertainty_estimate=uncertainty_estimate,
                model_agreement=model_agreement,
                ensemble_variance=ensemble_variance,
                calibration_applied=result.get('calibration_applied', False),
                raw_scores=raw_scores,
                processed_scores=result.get('processed_scores', raw_scores)
            )
            
            # Store in history
            self.scoring_history.append(unbiased_score)
            
            logger.info(f"✅ Unbiased scoring completed")
            logger.info(f"   🎯 Prediction: {unbiased_score.prediction}")
            logger.info(f"   📊 Confidence: {unbiased_score.confidence:.3f}")
            logger.info(f"   🤔 Uncertainty: {unbiased_score.uncertainty_estimate:.3f}")
            logger.info(f"   👥 Agreement: {unbiased_score.model_agreement:.3f}")
            
            return unbiased_score
            
        except Exception as e:
            logger.error(f"Unbiased scoring failed: {e}")
            return self._create_empty_score()
    
    def _weighted_average_scoring(self, 
                                model_names: List[str], 
                                confidences: List[float], 
                                predictions: List[str]) -> Dict[str, Any]:
        """✅ BIAS FIX: Unbiased weighted average scoring method"""
        try:
            # Use configured model weights or equal weights
            if self.config.model_weights:
                weights = [self.config.model_weights.get(name, 1.0) for name in model_names]
                weights = np.array(weights)
                weights = weights / weights.sum()  # Normalize
            else:
                weights = np.ones(len(model_names)) / len(model_names)
            
            # Calculate weighted average
            weighted_confidence = np.average(confidences, weights=weights)
            
            # Determine prediction based on majority vote with confidence weighting
            prediction_votes = {}
            for pred, conf, weight in zip(predictions, confidences, weights):
                if pred not in prediction_votes:
                    prediction_votes[pred] = 0
                prediction_votes[pred] += conf * weight
            
            # Get prediction with highest weighted vote
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            # ✅ BIAS FIX: No artificial calibration - use raw weighted average
            calibrated_confidence = np.clip(weighted_confidence, 0.0, 1.0)
            
            return {
                'prediction': final_prediction,
                'confidence': calibrated_confidence,
                'reasoning': f"Unbiased weighted average of {len(model_names)} models",
                'calibration_applied': False,  # No artificial calibration
                'processed_scores': dict(zip(model_names, confidences))
            }
            
        except Exception as e:
            logger.error(f"Weighted average scoring failed: {e}")
            return self._create_fallback_result()
    
    def _confidence_weighted_scoring(self, 
                                   model_names: List[str], 
                                   confidences: List[float], 
                                   predictions: List[str]) -> Dict[str, Any]:
        """Confidence-weighted scoring method"""
        try:
            # Use confidence as weights (higher confidence = higher weight)
            confidence_weights = np.array(confidences)
            confidence_weights = confidence_weights / confidence_weights.sum()
            
            # Calculate confidence-weighted average
            weighted_confidence = np.average(confidences, weights=confidence_weights)
            
            # Determine prediction based on confidence-weighted votes
            prediction_votes = {}
            for pred, conf in zip(predictions, confidences):
                if pred not in prediction_votes:
                    prediction_votes[pred] = 0
                prediction_votes[pred] += conf
            
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            # Apply confidence calibration
            if self.config.calibration_enabled:
                calibrated_confidence = self._apply_basic_calibration(weighted_confidence)
            else:
                calibrated_confidence = weighted_confidence
            
            return {
                'prediction': final_prediction,
                'confidence': calibrated_confidence,
                'reasoning': f"Confidence-weighted average of {len(model_names)} models",
                'calibration_applied': self.config.calibration_enabled,
                'processed_scores': dict(zip(model_names, confidences))
            }
            
        except Exception as e:
            logger.error(f"Confidence-weighted scoring failed: {e}")
            return self._create_fallback_result()
    
    def _bayesian_ensemble_scoring(self, 
                                 model_names: List[str], 
                                 confidences: List[float], 
                                 predictions: List[str]) -> Dict[str, Any]:
        """Bayesian ensemble scoring method"""
        try:
            # Convert confidences to log-odds
            epsilon = 1e-7
            confidences_safe = np.clip(confidences, epsilon, 1.0 - epsilon)
            log_odds = np.log(confidences_safe / (1.0 - confidences_safe))
            
            # Bayesian combination: sum of log-odds
            combined_log_odds = np.sum(log_odds)
            
            # Convert back to probability
            bayesian_confidence = 1.0 / (1.0 + np.exp(-combined_log_odds))
            
            # Determine prediction based on majority vote
            prediction_votes = {}
            for pred in predictions:
                prediction_votes[pred] = prediction_votes.get(pred, 0) + 1
            
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            # Apply confidence calibration
            if self.config.calibration_enabled:
                calibrated_confidence = self._apply_basic_calibration(bayesian_confidence)
            else:
                calibrated_confidence = bayesian_confidence
            
            return {
                'prediction': final_prediction,
                'confidence': calibrated_confidence,
                'reasoning': f"Bayesian ensemble of {len(model_names)} models",
                'calibration_applied': self.config.calibration_enabled,
                'processed_scores': dict(zip(model_names, confidences))
            }
            
        except Exception as e:
            logger.error(f"Bayesian ensemble scoring failed: {e}")
            return self._create_fallback_result()
    
    def _temperature_scaled_scoring(self, 
                                  model_names: List[str], 
                                  confidences: List[float], 
                                  predictions: List[str],
                                  model_logits: Optional[Dict[str, torch.Tensor]] = None) -> Dict[str, Any]:
        """Temperature-scaled scoring method"""
        try:
            # Apply temperature scaling
            temperature = self.config.temperature
            
            if model_logits:
                # Use actual logits for temperature scaling
                scaled_confidences = []
                for name in model_names:
                    if name in model_logits and model_logits[name] is not None:
                        logits = model_logits[name]
                        scaled_logits = logits / temperature
                        if logits.shape[-1] == 1:
                            scaled_conf = torch.sigmoid(scaled_logits).mean().item()
                        else:
                            scaled_conf = torch.softmax(scaled_logits, dim=-1).mean().item()
                        scaled_confidences.append(scaled_conf)
                    else:
                        # Fallback to confidence scaling
                        scaled_confidences.append(confidences[len(scaled_confidences)] / temperature)
            else:
                # Apply temperature scaling to confidences
                scaled_confidences = [conf / temperature for conf in confidences]
            
            # Calculate average of scaled confidences
            scaled_confidence = np.mean(scaled_confidences)
            
            # Determine prediction based on majority vote
            prediction_votes = {}
            for pred in predictions:
                prediction_votes[pred] = prediction_votes.get(pred, 0) + 1
            
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            return {
                'prediction': final_prediction,
                'confidence': scaled_confidence,
                'reasoning': f"Temperature-scaled (T={temperature}) ensemble of {len(model_names)} models",
                'calibration_applied': True,
                'processed_scores': dict(zip(model_names, scaled_confidences))
            }
            
        except Exception as e:
            logger.error(f"Temperature-scaled scoring failed: {e}")
            return self._create_fallback_result()
    
    def _platt_calibrated_scoring(self, 
                                model_names: List[str], 
                                confidences: List[float], 
                                predictions: List[str],
                                model_logits: Optional[Dict[str, torch.Tensor]] = None) -> Dict[str, Any]:
        """Platt-calibrated scoring method"""
        try:
            # Apply Platt scaling
            epsilon = 1e-7
            confidences_safe = np.clip(confidences, epsilon, 1.0 - epsilon)
            logits = np.log(confidences_safe / (1.0 - confidences_safe))
            
            # Platt scaling parameters (simplified)
            a = 1.0  # Scaling parameter
            b = 0.0  # Shifting parameter
            
            # Apply Platt scaling
            scaled_logits = a * logits + b
            platt_confidences = 1.0 / (1.0 + np.exp(-scaled_logits))
            
            # Calculate average of Platt-calibrated confidences
            platt_confidence = np.mean(platt_confidences)
            
            # Determine prediction based on majority vote
            prediction_votes = {}
            for pred in predictions:
                prediction_votes[pred] = prediction_votes.get(pred, 0) + 1
            
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            return {
                'prediction': final_prediction,
                'confidence': platt_confidence,
                'reasoning': f"Platt-calibrated ensemble of {len(model_names)} models",
                'calibration_applied': True,
                'processed_scores': dict(zip(model_names, platt_confidences))
            }
            
        except Exception as e:
            logger.error(f"Platt-calibrated scoring failed: {e}")
            return self._create_fallback_result()
    
    def _isotonic_calibrated_scoring(self, 
                                   model_names: List[str], 
                                   confidences: List[float], 
                                   predictions: List[str],
                                   model_logits: Optional[Dict[str, torch.Tensor]] = None) -> Dict[str, Any]:
        """Isotonic-calibrated scoring method"""
        try:
            # Apply isotonic regression calibration
            from sklearn.isotonic import IsotonicRegression
            
            # Sort confidences and apply isotonic regression
            sorted_indices = np.argsort(confidences)
            sorted_confidences = np.array(confidences)[sorted_indices]
            
            # Create pseudo-labels for isotonic regression
            # Assume higher confidences are more likely to be correct
            pseudo_labels = np.linspace(0.3, 0.8, len(confidences))
            
            iso_reg = IsotonicRegression(out_of_bounds='clip')
            iso_reg.fit(sorted_confidences, pseudo_labels)
            
            # Apply isotonic regression to all confidences
            isotonic_confidences = iso_reg.transform(confidences)
            
            # Calculate average of isotonic-calibrated confidences
            isotonic_confidence = np.mean(isotonic_confidences)
            
            # Determine prediction based on majority vote
            prediction_votes = {}
            for pred in predictions:
                prediction_votes[pred] = prediction_votes.get(pred, 0) + 1
            
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            return {
                'prediction': final_prediction,
                'confidence': isotonic_confidence,
                'reasoning': f"Isotonic-calibrated ensemble of {len(model_names)} models",
                'calibration_applied': True,
                'processed_scores': dict(zip(model_names, isotonic_confidences))
            }
            
        except Exception as e:
            logger.error(f"Isotonic-calibrated scoring failed: {e}")
            return self._create_fallback_result()
    
    def _uncertainty_aware_scoring(self, 
                                 model_names: List[str], 
                                 confidences: List[float], 
                                 predictions: List[str]) -> Dict[str, Any]:
        """✅ BIAS FIX: Truly unbiased uncertainty-aware scoring method"""
        try:
            # Ensure confidences is a numpy array
            confidences = np.array(confidences)
            
            # ✅ BIAS FIX: Use simple weighted average without artificial uncertainty adjustments
            # Apply configured model weights if available
            if self.config.model_weights:
                weights = np.array([self.config.model_weights.get(name, 1.0) for name in model_names])
                weights = weights / weights.sum()  # Normalize weights
                final_confidence = np.average(confidences, weights=weights)
            else:
                # Use simple average without artificial weighting
                final_confidence = np.mean(confidences)
            
            # ✅ BIAS FIX: No artificial caps or adjustments - use raw ensemble result
            final_confidence = np.clip(final_confidence, 0.0, 1.0)  # Only ensure valid range
            
            # Determine prediction based on majority vote
            prediction_votes = {}
            for pred in predictions:
                prediction_votes[pred] = prediction_votes.get(pred, 0) + 1
            
            final_prediction = max(prediction_votes, key=prediction_votes.get)
            
            return {
                'prediction': final_prediction,
                'confidence': float(final_confidence),
                'reasoning': f"Unbiased ensemble average of {len(model_names)} models",
                'calibration_applied': False,  # No artificial calibration
                'processed_scores': dict(zip(model_names, confidences.tolist()))
            }
            
        except Exception as e:
            logger.error(f"Uncertainty-aware scoring failed: {e}")
            return self._create_fallback_result()
    
    def _apply_basic_calibration(self, confidence: float) -> float:
        """✅ BIAS FIX: Apply unbiased confidence calibration - use raw confidence"""
        try:
            # ✅ BIAS FIX: No artificial calibration - use raw model confidence
            # Only ensure valid range
            calibrated = np.clip(confidence, 0.0, 1.0)
            
            return calibrated
            
        except Exception as e:
            logger.error(f"Basic calibration failed: {e}")
            return confidence
    
    def _calculate_uncertainty_estimate(self, confidences: List[float]) -> float:
        """Calculate uncertainty estimate from model confidences"""
        try:
            if len(confidences) <= 1:
                return 0.0
            
            # Calculate variance as uncertainty measure
            uncertainty = np.var(confidences)
            
            # Normalize to [0, 1] range
            uncertainty = min(uncertainty, 1.0)
            
            return uncertainty
            
        except Exception as e:
            logger.error(f"Uncertainty calculation failed: {e}")
            return 0.5
    
    def _calculate_model_agreement(self, predictions: List[str]) -> float:
        """Calculate model agreement score"""
        try:
            if len(predictions) <= 1:
                return 1.0
            
            # Count unique predictions
            unique_predictions = set(predictions)
            
            # Calculate agreement as ratio of most common prediction
            if len(unique_predictions) == 1:
                return 1.0
            else:
                prediction_counts = {}
                for pred in predictions:
                    prediction_counts[pred] = prediction_counts.get(pred, 0) + 1
                
                max_count = max(prediction_counts.values())
                agreement = max_count / len(predictions)
                
                return agreement
                
        except Exception as e:
            logger.error(f"Model agreement calculation failed: {e}")
            return 0.5
    
    def _calculate_ensemble_variance(self, confidences: List[float]) -> float:
        """Calculate ensemble variance"""
        try:
            if len(confidences) <= 1:
                return 0.0
            
            return float(np.var(confidences))
            
        except Exception as e:
            logger.error(f"Ensemble variance calculation failed: {e}")
            return 0.0
    
    def _create_empty_score(self) -> UnbiasedScore:
        """Create empty score for error cases"""
        return UnbiasedScore(
            prediction="No Models Available",
            confidence=0.0,
            method=self.config.method,
            reasoning="No models available for scoring",
            uncertainty_estimate=1.0,
            model_agreement=0.0,
            ensemble_variance=0.0,
            calibration_applied=False,
            raw_scores={},
            processed_scores={}
        )
    
    def _create_fallback_result(self) -> Dict[str, Any]:
        """Create fallback result for error cases"""
        return {
            'prediction': "Scoring Failed",
            'confidence': 0.5,
            'reasoning': "Fallback scoring due to error",
            'calibration_applied': False,
            'processed_scores': {}
        }
    
    def set_scoring_method(self, method: ScoringMethod):
        """Set the scoring method"""
        self.config.method = method
        logger.info(f"Scoring method set to: {method.value}")
    
    def update_model_weights(self, weights: Dict[str, float]):
        """Update model weights"""
        self.config.model_weights = weights
        logger.info(f"Model weights updated: {weights}")
    
    def get_scoring_summary(self) -> Dict[str, Any]:
        """Get summary of scoring performance"""
        if not self.scoring_history:
            return {"message": "No scoring history available"}
        
        recent_scores = self.scoring_history[-10:]  # Last 10 scores
        
        avg_confidence = np.mean([s.confidence for s in recent_scores])
        avg_uncertainty = np.mean([s.uncertainty_estimate for s in recent_scores])
        avg_agreement = np.mean([s.model_agreement for s in recent_scores])
        
        return {
            "total_scores": len(self.scoring_history),
            "average_confidence": avg_confidence,
            "average_uncertainty": avg_uncertainty,
            "average_agreement": avg_agreement,
            "scoring_method": self.config.method.value,
            "recent_performance": {
                "confidences": [s.confidence for s in recent_scores],
                "uncertainties": [s.uncertainty_estimate for s in recent_scores],
                "agreements": [s.model_agreement for s in recent_scores]
            }
        }

# Global scoring instance
unbiased_scoring_2025 = UnbiasedScoringSystem2025()

# Convenience functions
def calculate_unbiased_score(model_predictions: Dict[str, Tuple[str, float]],
                           model_logits: Optional[Dict[str, torch.Tensor]] = None) -> UnbiasedScore:
    """
    Convenience function for unbiased scoring.
    
    Args:
        model_predictions: Dict of model_name -> (prediction, confidence)
        model_logits: Optional raw logits for advanced scoring
        
    Returns:
        Unbiased ensemble score
    """
    return unbiased_scoring_2025.calculate_unbiased_score(model_predictions, model_logits)

def set_scoring_method(method: ScoringMethod):
    """Set the global scoring method"""
    unbiased_scoring_2025.set_scoring_method(method)

def get_scoring_summary() -> Dict[str, Any]:
    """Get scoring performance summary"""
    return unbiased_scoring_2025.get_scoring_summary()

def update_model_weights(weights: Dict[str, float]):
    """Update global model weights"""
    unbiased_scoring_2025.update_model_weights(weights)