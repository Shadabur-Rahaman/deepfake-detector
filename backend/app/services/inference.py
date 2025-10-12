# backend/app/services/inference.py - Production-Grade Inference Module

import torch
import numpy as np
import logging
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class InferenceResult:
    """Structured inference result"""
    prediction: str
    confidence: float
    raw_probability: float
    calibrated_probability: float
    threshold_used: float
    is_uncertain: bool
    processing_time: float
    model_name: str

class TemperatureCalibrator:
    """Temperature scaling for probability calibration"""
    
    def __init__(self, temperature: float = 1.5):
        self.temperature = temperature
        logger.info(f"[OK] TemperatureCalibrator initialized with T={temperature}")
    
    def calibrate(self, probability: float) -> float:
        """
        Apply temperature scaling to calibrate probability
        
        Args:
            probability: Raw probability from model (0-1)
            
        Returns:
            Calibrated probability (0-1)
        """
        try:
            # Apply temperature scaling: p_calibrated = sigmoid(logit / T)
            # where logit = log(p / (1-p))
            if probability <= 0.0 or probability >= 1.0:
                return probability
            
            logit = np.log(probability / (1.0 - probability))
            calibrated_logit = logit / self.temperature
            calibrated_prob = 1.0 / (1.0 + np.exp(-calibrated_logit))
            
            return float(calibrated_prob)
            
        except Exception as e:
            logger.warning(f"[WARNING] Temperature calibration failed: {e}, using raw probability")
            return probability

class ProductionInferenceEngine:
    """Production-grade inference engine with proper thresholding and calibration"""
    
    def __init__(self, 
                 threshold: float = 0.5,
                 temperature: float = 1.5,
                 uncertainty_threshold: float = 0.05,
                 deterministic: bool = False):
        """
        Initialize production inference engine
        
        Args:
            threshold: Binary classification threshold (0-1)
            temperature: Temperature for probability calibration
            uncertainty_threshold: Threshold for uncertain predictions
            deterministic: Whether to use deterministic inference
        """
        self.threshold = threshold
        self.uncertainty_threshold = uncertainty_threshold
        self.deterministic = deterministic
        
        # Initialize calibrator
        self.calibrator = TemperatureCalibrator(temperature)
        
        # Statistics
        self.stats = {
            'inferences_run': 0,
            'uncertain_predictions': 0,
            'calibration_applied': 0,
            'total_processing_time': 0.0
        }
        
        logger.info(f"[OK] ProductionInferenceEngine initialized: threshold={threshold}, T={temperature}, deterministic={deterministic}")
    
    def run_inference(self, 
                     model: torch.nn.Module, 
                     batch_tensor: torch.Tensor,
                     model_name: str = "unknown") -> InferenceResult:
        """
        Run inference with proper thresholding and calibration
        
        Args:
            model: PyTorch model
            batch_tensor: Preprocessed input tensor
            model_name: Name of the model for logging
            
        Returns:
            Structured inference result
        """
        start_time = time.time()
        
        try:
            # Ensure model is in eval mode
            model.eval()
            
            # Disable dropout and batch norm training behavior for deterministic inference
            if self.deterministic:
                self._set_deterministic_mode(model)
            
            # Run inference
            with torch.no_grad():
                logits = model(batch_tensor)
                
                # Apply sigmoid for binary classification
                probabilities = torch.sigmoid(logits)
                
                # Calculate average probability across batch
                avg_prob = torch.mean(probabilities).cpu().item()
            
            # Apply temperature calibration
            calibrated_prob = self.calibrator.calibrate(avg_prob)
            self.stats['calibration_applied'] += 1
            
            # Apply thresholding logic
            prediction, confidence, is_uncertain = self._apply_thresholding(calibrated_prob)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['inferences_run'] += 1
            self.stats['total_processing_time'] += processing_time
            if is_uncertain:
                self.stats['uncertain_predictions'] += 1
            
            # Create result
            result = InferenceResult(
                prediction=prediction,
                confidence=confidence,
                raw_probability=avg_prob,
                calibrated_probability=calibrated_prob,
                threshold_used=self.threshold,
                is_uncertain=is_uncertain,
                processing_time=processing_time,
                model_name=model_name
            )
            
            # Log result
            self._log_inference_result(result)
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Inference failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return InferenceResult(
                prediction="Inference Failed",
                confidence=0.0,
                raw_probability=0.5,
                calibrated_probability=0.5,
                threshold_used=self.threshold,
                is_uncertain=True,
                processing_time=processing_time,
                model_name=model_name
            )
    
    def _set_deterministic_mode(self, model: torch.nn.Module):
        """Set model to deterministic mode"""
        for module in model.modules():
            if isinstance(module, (torch.nn.Dropout, torch.nn.Dropout2d, torch.nn.Dropout3d)):
                module.eval()
            elif isinstance(module, (torch.nn.BatchNorm1d, torch.nn.BatchNorm2d, torch.nn.BatchNorm3d)):
                module.eval()
                module.training = False
    
    def _apply_thresholding(self, probability: float) -> Tuple[str, float, bool]:
        """
        Apply proper binary classification thresholding
        
        Args:
            probability: Calibrated probability (0-1)
            
        Returns:
            Tuple of (prediction, confidence, is_uncertain)
        """
        try:
            # CORRECTED: Proper binary classification logic
            # probability represents likelihood of being REAL (class 0)
            # threshold = 0.5 means: prob >= 0.5 → Real, prob < 0.5 → Fake
            
            if probability >= self.threshold:
                prediction = "Real Face"
                confidence = probability * 100  # Real confidence
            else:
                prediction = "Deepfake Detected"
                confidence = (1.0 - probability) * 100  # Fake confidence
            
            # Check for uncertain cases (close to threshold)
            distance_from_threshold = abs(probability - self.threshold)
            is_uncertain = distance_from_threshold < self.uncertainty_threshold
            
            if is_uncertain:
                prediction = "Uncertain"
                confidence = 50.0  # Neutral confidence
                logger.warning(f"[WARNING] Uncertain prediction: prob={probability:.4f}, threshold={self.threshold:.4f}, distance={distance_from_threshold:.4f}")
            
            return prediction, confidence, is_uncertain
            
        except Exception as e:
            logger.error(f"[ERROR] Thresholding failed: {e}")
            return "Uncertain", 50.0, True
    
    def _log_inference_result(self, result: InferenceResult):
        """Log structured inference result"""
        try:
            logger.info(f"🔍 {result.model_name} Inference Result:")
            logger.info(f"  Raw probability: {result.raw_probability:.4f}")
            logger.info(f"  Calibrated probability: {result.calibrated_probability:.4f}")
            logger.info(f"  Threshold: {result.threshold_used:.4f}")
            logger.info(f"  Prediction: {result.prediction}")
            logger.info(f"  Confidence: {result.confidence:.3f}%")
            logger.info(f"  Uncertain: {result.is_uncertain}")
            logger.info(f"  Processing time: {result.processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to log inference result: {e}")
    
    def set_threshold(self, threshold: float):
        """Update classification threshold"""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
            logger.info(f"[OK] Threshold updated to {threshold}")
        else:
            logger.error(f"[ERROR] Invalid threshold: {threshold}, must be in [0, 1]")
    
    def set_temperature(self, temperature: float):
        """Update calibration temperature"""
        if temperature > 0:
            self.calibrator.temperature = temperature
            logger.info(f"[OK] Temperature updated to {temperature}")
        else:
            logger.error(f"[ERROR] Invalid temperature: {temperature}, must be > 0")
    
    def get_stats(self) -> Dict:
        """Get inference statistics"""
        avg_time = (self.stats['total_processing_time'] / max(self.stats['inferences_run'], 1))
        uncertain_rate = (self.stats['uncertain_predictions'] / max(self.stats['inferences_run'], 1)) * 100
        
        return {
            **self.stats,
            'average_processing_time': avg_time,
            'uncertain_prediction_rate': uncertain_rate,
            'threshold': self.threshold,
            'temperature': self.calibrator.temperature,
            'deterministic': self.deterministic
        }

class EnsembleInferenceEngine:
    """Ensemble inference engine for multiple models"""
    
    def __init__(self, 
                 model_weights: Dict[str, float],
                 threshold: float = 0.5,
                 temperature: float = 1.5,
                 uncertainty_threshold: float = 0.05,
                 deterministic: bool = False):
        """
        Initialize ensemble inference engine
        
        Args:
            model_weights: Dictionary of model names to weights
            threshold: Binary classification threshold
            temperature: Temperature for calibration
            uncertainty_threshold: Threshold for uncertain predictions
            deterministic: Whether to use deterministic inference
        """
        self.model_weights = model_weights
        self.uncertainty_threshold = uncertainty_threshold
        self.deterministic = deterministic
        
        # Initialize individual inference engines
        self.inference_engines = {}
        for model_name in model_weights.keys():
            self.inference_engines[model_name] = ProductionInferenceEngine(
                threshold=threshold,
                temperature=temperature,
                uncertainty_threshold=uncertainty_threshold,
                deterministic=deterministic
            )
        
        # Ensemble calibrator
        self.ensemble_calibrator = TemperatureCalibrator(temperature)
        
        logger.info(f"[OK] EnsembleInferenceEngine initialized with {len(model_weights)} models")
    
    def run_ensemble_inference(self, 
                              models: Dict[str, torch.nn.Module], 
                              batch_tensor: torch.Tensor) -> InferenceResult:
        """
        Run ensemble inference across multiple models
        
        Args:
            models: Dictionary of model names to models
            batch_tensor: Preprocessed input tensor
            
        Returns:
            Ensemble inference result
        """
        try:
            # Run individual model inferences
            individual_results = {}
            for model_name, model in models.items():
                if model_name in self.inference_engines:
                    result = self.inference_engines[model_name].run_inference(
                        model, batch_tensor, model_name
                    )
                    individual_results[model_name] = result
            
            # Fuse results
            ensemble_result = self._fuse_results(individual_results)
            
            return ensemble_result
            
        except Exception as e:
            logger.error(f"[ERROR] Ensemble inference failed: {e}")
            return InferenceResult(
                prediction="Ensemble Failed",
                confidence=0.0,
                raw_probability=0.5,
                calibrated_probability=0.5,
                threshold_used=0.5,
                is_uncertain=True,
                processing_time=0.0,
                model_name="ensemble"
            )
    
    def _fuse_results(self, individual_results: Dict[str, InferenceResult]) -> InferenceResult:
        """Fuse individual model results into ensemble result"""
        try:
            # Calculate weighted average of calibrated probabilities
            total_weight = 0.0
            weighted_sum = 0.0
            successful_models = 0
            
            for model_name, result in individual_results.items():
                if model_name in self.model_weights and not result.is_uncertain:
                    weight = self.model_weights[model_name]
                    total_weight += weight
                    weighted_sum += result.calibrated_probability * weight
                    successful_models += 1
            
            if total_weight == 0:
                return InferenceResult(
                    prediction="No Models Available",
                    confidence=0.0,
                    raw_probability=0.5,
                    calibrated_probability=0.5,
                    threshold_used=0.5,
                    is_uncertain=True,
                    processing_time=0.0,
                    model_name="ensemble"
                )
            
            # Calculate ensemble probability
            ensemble_prob = weighted_sum / total_weight
            
            # Apply ensemble calibration
            calibrated_prob = self.ensemble_calibrator.calibrate(ensemble_prob)
            
            # Apply thresholding
            if calibrated_prob >= 0.5:
                prediction = "Real Face"
                confidence = calibrated_prob * 100
            else:
                prediction = "Deepfake Detected"
                confidence = (1.0 - calibrated_prob) * 100
            
            # Check for uncertainty
            distance_from_threshold = abs(calibrated_prob - 0.5)
            is_uncertain = distance_from_threshold < self.uncertainty_threshold
            
            if is_uncertain:
                prediction = "Uncertain"
                confidence = 50.0
            
            # Calculate average processing time
            avg_processing_time = sum(r.processing_time for r in individual_results.values()) / len(individual_results)
            
            return InferenceResult(
                prediction=prediction,
                confidence=confidence,
                raw_probability=ensemble_prob,
                calibrated_probability=calibrated_prob,
                threshold_used=0.5,
                is_uncertain=is_uncertain,
                processing_time=avg_processing_time,
                model_name="ensemble"
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Result fusion failed: {e}")
            return InferenceResult(
                prediction="Fusion Failed",
                confidence=0.0,
                raw_probability=0.5,
                calibrated_probability=0.5,
                threshold_used=0.5,
                is_uncertain=True,
                processing_time=0.0,
                model_name="ensemble"
            )

# Global inference engines
production_inference_engine = ProductionInferenceEngine()

def run_inference_production(model: torch.nn.Module, 
                           batch_tensor: torch.Tensor,
                           model_name: str = "unknown") -> InferenceResult:
    """Run production inference"""
    return production_inference_engine.run_inference(model, batch_tensor, model_name)

def get_production_inference_engine() -> ProductionInferenceEngine:
    """Get the global production inference engine"""
    return production_inference_engine
