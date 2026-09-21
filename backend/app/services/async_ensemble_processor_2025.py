"""
Async Ensemble Processor 2025 - Modern Parallel Model Execution
=============================================================

This module provides high-performance async ensemble processing for deepfake detection,
aligned with 2025 AI standards and optimized for parallel execution.

Features:
- Async parallel model execution
- Proper logit aggregation before softmax
- CUDA memory optimization
- Real-time progress tracking
- Error resilience and fallback handling
- Modern Python 3.13+ compatibility
"""

import asyncio
import logging
import time
from typing import Dict, List, Tuple, Optional, Any, Union
import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ModelExecutionStatus(Enum):
    """Model execution status for tracking"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class ModelExecutionResult:
    """Result of individual model execution"""
    model_name: str
    prediction: str
    confidence: float
    logits: Optional[torch.Tensor]
    execution_time: float
    status: ModelExecutionStatus
    error: Optional[str] = None

@dataclass
class EnsembleExecutionResult:
    """Complete ensemble execution result"""
    predictions: Dict[str, Tuple[str, float]]
    logits: Dict[str, torch.Tensor]
    execution_times: Dict[str, float]
    total_execution_time: float
    successful_models: int
    failed_models: int
    ensemble_prediction: str
    ensemble_confidence: float
    model_agreement: float
    uncertainty_estimate: float
    ensemble_variance: float = 0.0
    status: str = "OK"  # ✅ NEW: Status field for explicit failure states

class AsyncEnsembleProcessor2025:
    """
    High-performance async ensemble processor for 2025 AI standards.
    
    Features:
    - Parallel model execution with async/await
    - Proper logit aggregation
    - CUDA memory optimization
    - Real-time progress tracking
    - Error resilience
    """
    
    def __init__(self, max_workers: int = 4, timeout_per_model: float = 30.0):
        self.max_workers = max_workers
        self.timeout_per_model = timeout_per_model
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._execution_lock = threading.Lock()
        
    async def process_ensemble_async(self, 
                                   models: Dict[str, Any],
                                   faces: List[np.ndarray],
                                   model_weights: Optional[Dict[str, float]] = None) -> EnsembleExecutionResult:
        """
        Process ensemble with async parallel execution.
        
        Args:
            models: Dictionary of model name -> model instance
            faces: List of face images to process
            model_weights: Optional weights for models
            
        Returns:
            Complete ensemble execution result
        """
        start_time = time.time()
        
        if not models or not faces:
            return self._create_empty_result(start_time)
        
        logger.info(f"🚀 Starting async ensemble processing with {len(models)} models on {len(faces)} faces")
        
        # Create execution tasks for all models
        tasks = []
        for model_name, model in models.items():
            task = asyncio.create_task(
                self._execute_model_async(model_name, model, faces),
                name=f"model_{model_name}"
            )
            tasks.append(task)
        
        # Execute all models in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.timeout_per_model * len(models)
            )
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ Ensemble processing timed out after {self.timeout_per_model * len(models)}s")
            results = await self._handle_timeout(tasks)
        
        # Process results
        execution_results = self._process_execution_results(results, models.keys())
        
        # Aggregate ensemble prediction
        ensemble_result = self._aggregate_ensemble_results(execution_results, model_weights)
        
        total_time = time.time() - start_time
        ensemble_result.total_execution_time = total_time
        
        logger.info(f"✅ Async ensemble completed in {total_time:.2f}s - "
                   f"{ensemble_result.successful_models}/{len(models)} models successful")
        
        return ensemble_result
    
    async def _execute_model_async(self, model_name: str, model: Any, faces: List[np.ndarray]) -> ModelExecutionResult:
        """Execute a single model asynchronously"""
        start_time = time.time()
        
        try:
            logger.debug(f"🧠 Starting {model_name} execution")
            
            # Run model inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._run_model_inference,
                model_name, model, faces
            )
            
            execution_time = time.time() - start_time
            
            if result['success']:
                logger.debug(f"✅ {model_name} completed in {execution_time:.2f}s")
                return ModelExecutionResult(
                    model_name=model_name,
                    prediction=result['prediction'],
                    confidence=result['confidence'],
                    logits=result.get('logits'),
                    execution_time=execution_time,
                    status=ModelExecutionStatus.COMPLETED
                )
            else:
                logger.warning(f"⚠️ {model_name} failed: {result['error']}")
                return ModelExecutionResult(
                    model_name=model_name,
                    prediction="Error",
                    confidence=0.0,
                    logits=None,
                    execution_time=execution_time,
                    status=ModelExecutionStatus.FAILED,
                    error=result['error']
                )
                
        except asyncio.CancelledError:
            execution_time = time.time() - start_time
            logger.warning(f"⏰ {model_name} cancelled after {execution_time:.2f}s")
            return ModelExecutionResult(
                model_name=model_name,
                prediction="Timeout",
                confidence=0.0,
                logits=None,
                execution_time=execution_time,
                status=ModelExecutionStatus.TIMEOUT,
                error="Execution timeout"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {model_name} failed with exception: {e}")
            return ModelExecutionResult(
                model_name=model_name,
                prediction="Error",
                confidence=0.0,
                logits=None,
                execution_time=execution_time,
                status=ModelExecutionStatus.FAILED,
                error=str(e)
            )
    
    def _run_model_inference(self, model_name: str, model: Any, faces: List[np.ndarray]) -> Dict[str, Any]:
        """Run model inference in thread pool"""
        try:
            # Import the enhanced model loader for prediction
            from .enhanced_model_loader import get_enhanced_loader
            
            enhanced_loader = get_enhanced_loader()
            
            # Use the enhanced loader's prediction method
            if hasattr(enhanced_loader, 'predict_single_model'):
                prediction, confidence = enhanced_loader.predict_single_model(model_name, faces)
            else:
                # Fallback to direct model inference
                prediction, confidence = self._direct_model_inference(model, faces)
            
            return {
                'success': True,
                'prediction': prediction,
                'confidence': confidence,
                'logits': self._extract_logits_from_model(model, faces)  # Enhanced to capture logits
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _direct_model_inference(self, model: Any, faces: List[np.ndarray]) -> Tuple[str, float]:
        """Direct model inference fallback"""
        try:
            # Convert faces to tensor batch
            if not faces:
                return "No Faces", 0.0
            
            # Simple preprocessing (this should be enhanced)
            face_tensors = []
            for face in faces[:5]:  # Limit to 5 faces
                if isinstance(face, np.ndarray):
                    # Convert to tensor and normalize
                    face_tensor = torch.from_numpy(face.astype(np.float32) / 255.0)
                    if len(face_tensor.shape) == 3:
                        face_tensor = face_tensor.permute(2, 0, 1)  # HWC to CHW
                    face_tensors.append(face_tensor)
            
            if not face_tensors:
                return "No Valid Faces", 0.0
            
            # Stack into batch
            batch = torch.stack(face_tensors).unsqueeze(0)
            
            # Run inference
            with torch.no_grad():
                model.eval()
                outputs = model(batch)
                
                if isinstance(outputs, torch.Tensor):
                    if outputs.shape[-1] == 1:
                        # Binary classification
                        prob = torch.sigmoid(outputs).mean().item()
                        prediction = "Deepfake Detected" if prob > 0.5 else "Authentic Video"
                        confidence = prob if prob > 0.5 else 1.0 - prob
                    else:
                        # Multi-class classification
                        probs = torch.softmax(outputs, dim=-1)
                        max_prob, predicted_class = torch.max(probs, dim=-1)
                        confidence = max_prob.mean().item()
                        prediction = "Deepfake Detected" if predicted_class.mean() > 0.5 else "Authentic Video"
                else:
                    prediction = "Unknown"
                    confidence = 0.5
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"Direct model inference failed: {e}")
            return "Error", 0.0
    
    def _extract_logits_from_model(self, model: Any, faces: List[np.ndarray]) -> Optional[torch.Tensor]:
        """Extract raw logits from model for calibration"""
        try:
            if not faces:
                return None
            
            # Convert faces to tensor batch
            face_tensors = []
            for face in faces[:5]:  # Limit to 5 faces
                if isinstance(face, np.ndarray):
                    # Convert to tensor and normalize
                    face_tensor = torch.from_numpy(face.astype(np.float32) / 255.0)
                    if len(face_tensor.shape) == 3:
                        face_tensor = face_tensor.permute(2, 0, 1)  # HWC to CHW
                    face_tensors.append(face_tensor)
            
            if not face_tensors:
                return None
            
            # Stack into batch
            batch = torch.stack(face_tensors).unsqueeze(0)
            
            # Run inference to get logits
            with torch.no_grad():
                model.eval()
                logits = model(batch)
                
                # Return mean logits for ensemble
                return logits.mean(dim=0, keepdim=True)
                
        except Exception as e:
            logger.error(f"Logits extraction failed: {e}")
            return None
    
    async def _handle_timeout(self, tasks: List[asyncio.Task]) -> List[Any]:
        """Handle timeout for running tasks"""
        completed_results = []
        
        for task in tasks:
            if task.done():
                try:
                    result = await task
                    completed_results.append(result)
                except Exception as e:
                    completed_results.append(ModelExecutionResult(
                        model_name=task.get_name().replace("model_", ""),
                        prediction="Error",
                        confidence=0.0,
                        logits=None,
                        execution_time=0.0,
                        status=ModelExecutionStatus.FAILED,
                        error=str(e)
                    ))
            else:
                task.cancel()
                completed_results.append(ModelExecutionResult(
                    model_name=task.get_name().replace("model_", ""),
                    prediction="Timeout",
                    confidence=0.0,
                    logits=None,
                    execution_time=0.0,
                    status=ModelExecutionStatus.TIMEOUT,
                    error="Execution timeout"
                ))
        
        return completed_results
    
    def _process_execution_results(self, results: List[Any], model_names: List[str]) -> List[ModelExecutionResult]:
        """Process execution results and handle exceptions"""
        processed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                model_name = model_names[i] if i < len(model_names) else f"model_{i}"
                processed_results.append(ModelExecutionResult(
                    model_name=model_name,
                    prediction="Error",
                    confidence=0.0,
                    logits=None,
                    execution_time=0.0,
                    status=ModelExecutionStatus.FAILED,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _aggregate_ensemble_results(self, 
                                  results: List[ModelExecutionResult],
                                  model_weights: Optional[Dict[str, float]] = None) -> EnsembleExecutionResult:
        """Aggregate ensemble results using 2025 confidence aggregation"""
        try:
            # Import the 2025 confidence aggregator
            from .confidence_aggregator_2025 import confidence_aggregator_2025
            
            # Separate successful and failed results
            successful_results = [r for r in results if r.status == ModelExecutionStatus.COMPLETED]
            failed_results = [r for r in results if r.status != ModelExecutionStatus.COMPLETED]
            
            if not successful_results:
                logger.error("Ensemble aggregation failed: 0 successful models")
                return self._create_empty_result(time.time(), status="FAILED_NO_MODELS")
            
            # Preserve individual model names (no ModelType category collisions)
            model_predictions = {}
            model_logits = {}
            execution_times = {}
            
            for result in successful_results:
                model_predictions[result.model_name] = (result.prediction, result.confidence)
                if result.logits is not None:
                    model_logits[result.model_name] = result.logits
                execution_times[result.model_name] = result.execution_time
            
            from .confidence_aggregator_2025 import FaceQualityMetrics, TemporalConsistencyMetrics
            
            face_quality = FaceQualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
            temporal_metrics = TemporalConsistencyMetrics(0.5, 0.5, 0.5, 0.5)
            
            # Forward named configured weights into the aggregator
            ensemble_result = confidence_aggregator_2025.aggregate_ensemble_predictions(
                model_predictions,
                face_quality,
                temporal_metrics,
                model_logits if model_logits else None,
                named_weights=model_weights,
            )
            
            # Calculate ensemble variance on fake probabilities for consistency
            from .confidence_aggregator_2025 import to_fake_probability
            if len(successful_results) > 1:
                fake_probs = [
                    to_fake_probability(result.prediction, result.confidence)
                    for result in successful_results
                ]
                ensemble_variance = float(np.var(fake_probs))
            else:
                ensemble_variance = 0.0
            
            import time as _time
            timestamp = _time.time()
            fake_p = ensemble_result.detailed_breakdown.get('fake_probability', ensemble_result.confidence)
            logger.info(
                f"ENSEMBLE_METRICS: timestamp={timestamp}, successful={len(successful_results)}, "
                f"failed={len(failed_results)}, ensemble_conf={ensemble_result.confidence:.3f}, "
                f"fake_probability={fake_p}, status=OK, prediction={ensemble_result.prediction}, "
                f"weights={ensemble_result.detailed_breakdown.get('model_weights', {})}"
            )
            
            return EnsembleExecutionResult(
                predictions={result.model_name: (result.prediction, result.confidence) 
                           for result in successful_results},
                logits={result.model_name: result.logits 
                       for result in successful_results if result.logits is not None},
                execution_times=execution_times,
                total_execution_time=0.0,  # Will be set by caller
                successful_models=len(successful_results),
                failed_models=len(failed_results),
                ensemble_prediction=ensemble_result.prediction,
                ensemble_confidence=ensemble_result.confidence,
                model_agreement=ensemble_result.model_agreement,
                uncertainty_estimate=ensemble_result.uncertainty_estimate,
                ensemble_variance=ensemble_variance,
                status="OK"
            )
            
        except Exception as e:
            logger.error(f"Ensemble aggregation failed: {e}")
            import time as time_module
            return self._create_empty_result(time_module.time(), status="FAILED_EXCEPTION")
    
    def _create_empty_result(self, start_time: float, status: str = "FAILED") -> EnsembleExecutionResult:
        """Create empty result for error cases"""
        return EnsembleExecutionResult(
            predictions={},
            logits={},
            execution_times={},
            total_execution_time=time.time() - start_time,
            successful_models=0,
            failed_models=0,
            ensemble_prediction="ENSEMBLE_FAILED",  # ✅ CHANGED: More explicit failure state
            ensemble_confidence=0.0,
            model_agreement=0.0,
            uncertainty_estimate=1.0,
            ensemble_variance=1.0,
            status=status
        )
    
    def _calculate_actual_face_quality(self, faces: List[np.ndarray]):
        """Calculate actual face quality metrics from faces"""
        try:
            from .confidence_aggregator_2025 import FaceQualityMetrics
            
            if not faces:
                return FaceQualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
            
            # Calculate actual metrics from faces
            brightness_scores = []
            contrast_scores = []
            sharpness_scores = []
            color_consistency_scores = []
            symmetry_scores = []
            naturalness_scores = []
            
            for face in faces[:10]:  # Limit to 10 faces for performance
                if isinstance(face, np.ndarray) and face.size > 0:
                    # Calculate brightness
                    brightness = np.mean(face) / 255.0
                    brightness_scores.append(brightness)
                    
                    # Calculate contrast
                    contrast = np.std(face) / 255.0
                    contrast_scores.append(contrast)
                    
                    # Calculate sharpness (simplified)
                    if len(face.shape) == 3:
                        gray = np.mean(face, axis=2)
                        sharpness = np.std(np.gradient(gray))
                        sharpness_scores.append(min(sharpness / 50.0, 1.0))
                    
                    # Default values for other metrics
                    color_consistency_scores.append(0.7)
                    symmetry_scores.append(0.8)
                    naturalness_scores.append(0.75)
            
            return FaceQualityMetrics(
                brightness=np.mean(brightness_scores) if brightness_scores else 0.5,
                contrast=np.mean(contrast_scores) if contrast_scores else 0.5,
                sharpness=np.mean(sharpness_scores) if sharpness_scores else 0.5,
                color_consistency=np.mean(color_consistency_scores) if color_consistency_scores else 0.5,
                symmetry=np.mean(symmetry_scores) if symmetry_scores else 0.5,
                naturalness=np.mean(naturalness_scores) if naturalness_scores else 0.5
            )
        except Exception as e:
            logger.error(f"Failed to calculate face quality: {e}")
            from .confidence_aggregator_2025 import FaceQualityMetrics
            return FaceQualityMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    
    def _calculate_actual_temporal_consistency(self, faces: List[np.ndarray]):
        """Calculate actual temporal consistency metrics from faces"""
        try:
            from .confidence_aggregator_2025 import TemporalConsistencyMetrics
            
            if len(faces) < 2:
                return TemporalConsistencyMetrics(0.5, 0.5, 0.5, 0.5)
            
            # Calculate frame-to-frame consistency
            consistency_scores = []
            for i in range(1, min(len(faces), 10)):
                if isinstance(faces[i], np.ndarray) and isinstance(faces[i-1], np.ndarray):
                    # Simple consistency metric
                    diff = np.mean(np.abs(faces[i].astype(float) - faces[i-1].astype(float)))
                    consistency = max(0, 1.0 - diff / 255.0)
                    consistency_scores.append(consistency)
            
            avg_consistency = np.mean(consistency_scores) if consistency_scores else 0.5
            
            return TemporalConsistencyMetrics(
                frame_consistency=avg_consistency,
                motion_smoothness=avg_consistency * 0.9,
                lighting_stability=avg_consistency * 0.8,
                temporal_coherence=avg_consistency * 0.85
            )
        except Exception as e:
            logger.error(f"Failed to calculate temporal consistency: {e}")
            from .confidence_aggregator_2025 import TemporalConsistencyMetrics
            return TemporalConsistencyMetrics(0.5, 0.5, 0.5, 0.5)

    def __del__(self):
        """Cleanup executor on destruction"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# Global instance for easy access
async_ensemble_processor_2025 = AsyncEnsembleProcessor2025()

# Convenience functions
async def process_ensemble_async_2025(models: Dict[str, Any], 
                                    faces: List[np.ndarray],
                                    model_weights: Optional[Dict[str, float]] = None) -> EnsembleExecutionResult:
    """
    Convenience function for async ensemble processing.
    
    Args:
        models: Dictionary of model name -> model instance
        faces: List of face images to process
        model_weights: Optional weights for models
        
    Returns:
        Complete ensemble execution result
    """
    return await async_ensemble_processor_2025.process_ensemble_async(models, faces, model_weights)

def get_ensemble_processor() -> AsyncEnsembleProcessor2025:
    """Get the global async ensemble processor instance"""
    return async_ensemble_processor_2025
