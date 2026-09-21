#!/usr/bin/env python3
"""
Adaptive Threshold Calculator - Consensus-based threshold adjustment
Calculates optimal thresholds based on model agreement and confidence levels
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class ConsensusResult:
    """Result from consensus analysis"""
    agreement_score: float  # 0.0 to 1.0
    consensus_level: str  # "high", "medium", "low"
    models_agreeing: int
    total_models: int
    disagreement_details: Dict[str, Any]
    recommended_threshold: float
    confidence_adjustment: float

@dataclass
class ThresholdDecision:
    """Final threshold decision with reasoning"""
    threshold: float
    reasoning: str
    consensus_level: str
    confidence_boost: float
    uncertainty_flag: bool
    fallback_recommendation: str

class AdaptiveThresholdCalculator:
    """
    Calculates adaptive thresholds based on model consensus and confidence
    """
    
    def __init__(self):
        self.consensus_thresholds = {
            'high': 0.75,    # >75% agreement
            'medium': 0.50,  # 50-75% agreement
            'low': 0.25      # <50% agreement
        }
        
        self.threshold_levels = {
            'high_consensus': 0.5,      # Standard threshold
            'medium_consensus': 0.6,    # Conservative threshold
            'low_consensus': 0.7,       # Very conservative threshold
            'uncertain': 0.8            # Maximum conservative threshold
        }
        
        logger.info("🎯 AdaptiveThresholdCalculator initialized")
    
    def calculate_consensus(self, model_predictions: Dict[str, str], model_scores: Dict[str, float]) -> ConsensusResult:
        """
        Calculate consensus among models
        
        Args:
            model_predictions: Dict of model_name -> prediction ("Real Video" or "Deepfake Detected")
            model_scores: Dict of model_name -> confidence score (0.0 to 1.0)
        
        Returns:
            ConsensusResult with agreement analysis
        """
        if not model_predictions or not model_scores:
            return ConsensusResult(
                agreement_score=0.0,
                consensus_level="low",
                models_agreeing=0,
                total_models=0,
                disagreement_details={},
                recommended_threshold=self.threshold_levels['uncertain'],
                confidence_adjustment=-0.2
            )
        
        # Count predictions by type
        real_count = 0
        fake_count = 0
        total_models = len(model_predictions)
        
        prediction_details = {}
        
        for model_name, prediction in model_predictions.items():
            score = model_scores.get(model_name, 0.5)
            
            if "Real" in prediction:
                real_count += 1
                prediction_details[model_name] = {
                    'prediction': 'real',
                    'confidence': score,
                    'weight': 1.0
                }
            elif "Deepfake" in prediction or "Fake" in prediction:
                fake_count += 1
                prediction_details[model_name] = {
                    'prediction': 'fake',
                    'confidence': score,
                    'weight': 1.0
                }
            else:
                # Unknown prediction, treat as neutral
                prediction_details[model_name] = {
                    'prediction': 'unknown',
                    'confidence': 0.5,
                    'weight': 0.5
                }
        
        # Calculate agreement score
        max_agreement = max(real_count, fake_count)
        agreement_score = max_agreement / total_models if total_models > 0 else 0.0
        
        # Determine consensus level
        if agreement_score >= self.consensus_thresholds['high']:
            consensus_level = "high"
        elif agreement_score >= self.consensus_thresholds['medium']:
            consensus_level = "medium"
        else:
            consensus_level = "low"
        
        # Analyze disagreements
        disagreement_details = {
            'real_predictions': real_count,
            'fake_predictions': fake_count,
            'unknown_predictions': total_models - real_count - fake_count,
            'dominant_prediction': 'real' if real_count > fake_count else 'fake' if fake_count > real_count else 'tie',
            'confidence_variance': np.var(list(model_scores.values())) if model_scores else 0.0
        }
        
        # Calculate recommended threshold based on consensus
        if consensus_level == "high":
            recommended_threshold = self.threshold_levels['high_consensus']
            confidence_adjustment = 0.1  # Boost confidence
        elif consensus_level == "medium":
            recommended_threshold = self.threshold_levels['medium_consensus']
            confidence_adjustment = 0.0  # No adjustment
        else:
            recommended_threshold = self.threshold_levels['low_consensus']
            confidence_adjustment = -0.1  # Reduce confidence
        
        result = ConsensusResult(
            agreement_score=agreement_score,
            consensus_level=consensus_level,
            models_agreeing=max_agreement,
            total_models=total_models,
            disagreement_details=disagreement_details,
            recommended_threshold=recommended_threshold,
            confidence_adjustment=confidence_adjustment
        )
        
        logger.info(f"📊 Consensus Analysis:")
        logger.info(f"   Agreement: {agreement_score:.2f} ({consensus_level} consensus)")
        logger.info(f"   Models agreeing: {max_agreement}/{total_models}")
        logger.info(f"   Recommended threshold: {recommended_threshold}")
        
        return result
    
    def analyze_model_confidence(self, model_scores: Dict[str, float], model_predictions: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze confidence levels across models
        """
        if not model_scores:
            return {'avg_confidence': 0.5, 'confidence_variance': 0.0, 'high_confidence_models': 0}
        
        scores = list(model_scores.values())
        avg_confidence = np.mean(scores)
        confidence_variance = np.var(scores)
        
        # Count high confidence models (>0.8)
        high_confidence_models = sum(1 for score in scores if score > 0.8)
        
        # Check for extreme confidence (very high or very low)
        extreme_confidence = any(score > 0.95 or score < 0.05 for score in scores)
        
        return {
            'avg_confidence': avg_confidence,
            'confidence_variance': confidence_variance,
            'high_confidence_models': high_confidence_models,
            'extreme_confidence': extreme_confidence,
            'confidence_range': (min(scores), max(scores))
        }
    
    def calculate_adaptive_threshold(self, 
                                   model_predictions: Dict[str, str], 
                                   model_scores: Dict[str, float],
                                   trained_model_score: Optional[float] = None,
                                   trained_model_prediction: Optional[str] = None) -> ThresholdDecision:
        """
        Calculate adaptive threshold based on consensus and confidence analysis
        """
        logger.info("🎯 Calculating adaptive threshold...")
        
        # Calculate consensus
        consensus_result = self.calculate_consensus(model_predictions, model_scores)
        
        # Analyze confidence
        confidence_analysis = self.analyze_model_confidence(model_scores, model_predictions)
        
        # Base threshold from consensus
        base_threshold = consensus_result.recommended_threshold
        
        # Adjust for confidence variance
        confidence_variance = confidence_analysis['confidence_variance']
        if confidence_variance > 0.1:  # High variance in confidence
            base_threshold += 0.05  # More conservative
            logger.info("   High confidence variance detected, increasing threshold")
        
        # Special case: Trained model high confidence override
        if trained_model_score and trained_model_prediction:
            if trained_model_score > 0.90:  # Very high confidence threshold
                logger.info(f"🎯 TRAINED MODEL VERY HIGH CONFIDENCE: {trained_model_score:.3f}")
                # Trust trained model completely when it's very confident
                if "Real" in trained_model_prediction:
                    # FIX: Don't completely trust trained model for Real predictions - check other models
                    uncertainty_flag = True  # Mark as uncertain to allow other models to influence
                    fallback_recommendation = "consider_ensemble_consensus"
                    base_threshold = 0.60  # Lower threshold to allow other models to override
                    logger.info(f"🎯 TRAINED MODEL REAL: Considering ensemble consensus despite Real prediction with {trained_model_score:.3f} confidence")
                else:
                    # If trained model says Fake with high confidence, trust it more
                    uncertainty_flag = False
                    fallback_recommendation = "trust_trained_model"
                    base_threshold = 0.50
                    logger.info(f"🎯 TRAINED MODEL FAKE: Trusting Fake prediction with {trained_model_score:.3f} confidence")
            elif trained_model_score > 0.8:  # High confidence threshold
                # Check if other models disagree
                other_models_agree = 0
                other_models_total = 0
                
                for model_name, prediction in model_predictions.items():
                    if model_name != 'trained_model':
                        other_models_total += 1
                        if ("Real" in trained_model_prediction and "Real" in prediction) or \
                           ("Deepfake" in trained_model_prediction and ("Deepfake" in prediction or "Fake" in prediction)):
                            other_models_agree += 1
                
                if other_models_total > 0:
                    other_agreement = other_models_agree / other_models_total
                    if other_agreement < 0.5:  # Other models disagree
                        logger.warning(f"⚠️ Trained model high confidence ({trained_model_score:.3f}) but other models disagree ({other_agreement:.2f})")
                        
                        # If trained model is very confident (>0.8), trust it over others
                        logger.info(f"🎯 TRAINED MODEL HIGH CONFIDENCE OVERRIDE: Trusting trained model over {other_models_total - other_models_agree} disagreeing models")
                        base_threshold = 0.75  # High threshold to favor trained model
                        uncertainty_flag = False
                        fallback_recommendation = "trust_trained_model_high_confidence"
                    else:
                        uncertainty_flag = False
                        fallback_recommendation = "trust_trained_model"
                else:
                    uncertainty_flag = False
                    fallback_recommendation = "trust_trained_model"
            else:
                uncertainty_flag = False
                fallback_recommendation = "standard_processing"
        else:
            uncertainty_flag = False
            fallback_recommendation = "standard_processing"
        
        # Final threshold adjustment
        final_threshold = min(0.9, max(0.3, base_threshold))  # Clamp between 0.3 and 0.9
        
        # Generate reasoning
        reasoning_parts = []
        reasoning_parts.append(f"Consensus: {consensus_result.consensus_level} ({consensus_result.agreement_score:.2f})")
        reasoning_parts.append(f"Base threshold: {base_threshold:.2f}")
        
        if confidence_variance > 0.1:
            reasoning_parts.append("High confidence variance adjustment")
        
        if uncertainty_flag:
            reasoning_parts.append("Trained model disagreement detected")
        
        reasoning = "; ".join(reasoning_parts)
        
        # Calculate confidence boost
        confidence_boost = consensus_result.confidence_adjustment
        if consensus_result.consensus_level == "high":
            confidence_boost += 0.05  # Additional boost for high consensus
        elif consensus_result.consensus_level == "low":
            confidence_boost -= 0.05  # Additional penalty for low consensus
        
        decision = ThresholdDecision(
            threshold=final_threshold,
            reasoning=reasoning,
            consensus_level=consensus_result.consensus_level,
            confidence_boost=confidence_boost,
            uncertainty_flag=uncertainty_flag,
            fallback_recommendation=fallback_recommendation
        )
        
        logger.info(f"🎯 Final threshold decision:")
        logger.info(f"   Threshold: {final_threshold:.3f}")
        logger.info(f"   Reasoning: {reasoning}")
        logger.info(f"   Confidence boost: {confidence_boost:+.3f}")
        logger.info(f"   Uncertainty flag: {uncertainty_flag}")
        
        return decision
    
    def should_bias_toward_real(self, threshold_decision: ThresholdDecision, 
                               model_predictions: Dict[str, str]) -> bool:
        """
        Determine if we should bias toward "Real" classification to reduce false positives
        """
        # Always bias toward real if uncertainty flag is set
        if threshold_decision.uncertainty_flag:
            return True
        
        # Bias toward real if low consensus and no strong evidence of fake
        if threshold_decision.consensus_level == "low":
            fake_models = sum(1 for pred in model_predictions.values() 
                            if "Deepfake" in pred or "Fake" in pred)
            total_models = len(model_predictions)
            
            if fake_models / total_models < 0.6:  # Less than 60% say fake
                return True
        
        return False
    
    def get_fallback_prediction(self, threshold_decision: ThresholdDecision,
                               model_predictions: Dict[str, str],
                               model_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Get fallback prediction when models strongly disagree
        """
        if threshold_decision.fallback_recommendation == "bias_toward_real":
            return "Real Video", 0.6  # Conservative real prediction
        
        elif threshold_decision.fallback_recommendation == "trust_trained_model":
            # Find trained model prediction
            for model_name, prediction in model_predictions.items():
                if model_name == 'trained_model':
                    confidence = model_scores.get(model_name, 0.6)
                    return prediction, confidence
        
        # Default: count votes
        real_count = sum(1 for pred in model_predictions.values() if "Real" in pred)
        fake_count = sum(1 for pred in model_predictions.values() if "Deepfake" in pred or "Fake" in pred)
        
        if real_count > fake_count:
            return "Real Video", 0.6
        elif fake_count > real_count:
            return "Deepfake Detected", 0.6
        else:
            return "Real Video", 0.5  # Default to real to reduce false positives

# Global instance
adaptive_threshold_calculator = AdaptiveThresholdCalculator()

def calculate_adaptive_threshold(model_predictions: Dict[str, str], 
                               model_scores: Dict[str, float],
                               trained_model_score: Optional[float] = None,
                               trained_model_prediction: Optional[str] = None) -> ThresholdDecision:
    """
    Calculate adaptive threshold based on model consensus
    """
    return adaptive_threshold_calculator.calculate_adaptive_threshold(
        model_predictions, model_scores, trained_model_score, trained_model_prediction
    )
