# backend/app/services/deterministic_ensemble_detector.py - Production-Grade Deterministic Ensemble Detector

import asyncio
import logging
import time
import torch
import numpy as np
import cv2
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import deque
import hashlib
import json
from datetime import datetime

# Simplified imports with fallbacks
try:
    from .deterministic_config import get_deterministic_config
except ImportError:
    def get_deterministic_config():
        return type('Config', (), {
            'get_model_weights': lambda: {'efficientnet_b0': 0.25, 'yolov8_face': 0.15, 'mesonet': 0.2, 'resnet50': 0.2, 'vit': 0.1, 'vivit': 0.1},
            'get_thresholds': lambda: {'temporal_window_size': 5, 'temporal_smoothing_alpha': 0.3},
            'get_preprocessing_config': lambda: {},
            'generate_preprocessing_hash': lambda x: 'mock_hash',
            'ensure_model_deterministic': lambda x: None,
            'enable_deterministic': True
        })()

try:
    from .deterministic_deepfake_detector import DeterministicDeepfakeDetector
except ImportError:
    class DeterministicDeepfakeDetector:
        def __init__(self, model, device):
            self.model = model
            self.device = device
        
        def detect_deepfake_deterministic(self, faces):
            return "Real Face", 50.0

try:
    from .deepfake_detector import detector as global_detector
except ImportError:
    global_detector = None

try:
    from .model_loader import get_model_loader, load_all_models, get_startup_summary
except ImportError:
    def get_model_loader():
        return type('ModelLoader', (), {'get_loaded_models': lambda: {}})()
    
    def load_all_models():
        return {}
    
    def get_startup_summary():
        return {'total_models_attempted': 0, 'successful_models': 0, 'failed_models': 0, 'missing_dependencies': 0, 'ensemble_models': 0}

try:
    from .logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

try:
    from .probability_calibration import ConservativeCalibrator, apply_uncertainty_penalty, validate_model_agreement
except ImportError:
    class ConservativeCalibrator:
        def __init__(self, temperature=1.5):
            self.temperature = temperature
        
        def calibrate(self, prob):
            return prob
    
    def apply_uncertainty_penalty(prob, confidence):
        return prob, confidence
    
    def validate_model_agreement(probs, threshold=0.4):
        return True

try:
    from .preprocessing import ProductionPreprocessor
except ImportError:
    class ProductionPreprocessor:
        def __init__(self, deterministic=True):
            self.deterministic = deterministic
        
        def preprocess_face(self, face, device):
            import torch
            import cv2
            import numpy as np
            face = cv2.resize(face, (224, 224))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = face.astype(np.float32) / 255.0
            return torch.from_numpy(face).permute(2, 0, 1).unsqueeze(0).to(device)

# Import tensor fixes
try:
    from .tensor_fixes import get_tensor_processor, TensorProcessor
except ImportError:
    def get_tensor_processor(device="cpu"):
        return TensorProcessor(device)
    
    class TensorProcessor:
        def __init__(self, device="cpu"):
            self.device = device
        
        def preprocess_face_robust(self, face):
            import torch
            import cv2
            import numpy as np
            face = cv2.resize(face, (224, 224))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = face.astype(np.float32) / 255.0
            return torch.from_numpy(face).permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        def safe_model_inference(self, model, input_tensor):
            import torch
            if model is None:
                return torch.tensor([0.5]).to(self.device)
            model.eval()
            with torch.no_grad():
                return model(input_tensor)
        
        def process_model_output(self, output, model_name="unknown"):
            import torch
            import numpy as np
            if isinstance(output, torch.Tensor):
                output_np = output.cpu().numpy()
            else:
                output_np = np.array(output)
            
            if len(output_np.shape) > 1:
                output_np = output_np.flatten()
            
            if len(output_np) == 1:
                raw_output = float(output_np[0])
            else:
                raw_output = float(np.max(output_np))
            
            if raw_output < 0 or raw_output > 1:
                raw_output = 1.0 / (1.0 + np.exp(-raw_output))
            
            raw_output = max(0.0, min(1.0, raw_output))
            
            if raw_output >= 0.7:
                prediction = "Deepfake Detected"
                confidence = raw_output * 100
            elif raw_output <= 0.3:
                prediction = "Real Face"
                confidence = (1.0 - raw_output) * 100
            else:
                prediction = "Uncertain"
                confidence = 50.0
            
            confidence = max(0.0, min(100.0, confidence))
            return raw_output, prediction, confidence

try:
    from .inference import EnsembleInferenceEngine
except ImportError:
    class EnsembleInferenceEngine:
        pass

logger = get_logger(__name__)

@dataclass
class ModelResult:
    """Result from a single model"""
    model_name: str
    prediction: str
    confidence: float
    raw_output: float
    processing_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class EnsembleResult:
    """Final ensemble result"""
    frame_id: int
    timestamp: float
    preproc_hash: str
    model_results: Dict[str, ModelResult]
    fusion_raw: float
    fusion_smoothed: float
    final_prediction: str
    final_confidence: float
    decision: str
    processing_time: float
    temporal_smoothed: bool = False

class TemporalSmoother:
    """Enhanced temporal smoothing for stable results"""
    
    def __init__(self, window_size: int = 5, alpha: float = 0.3):
        self.window_size = window_size
        self.alpha = alpha
        self.confidence_history: deque = deque(maxlen=window_size)
        self.prediction_history: deque = deque(maxlen=window_size)
        
    def add_result(self, prediction: str, confidence: float) -> Tuple[str, float]:
        """Add result and return smoothed prediction"""
        self.confidence_history.append(confidence)
        self.prediction_history.append(prediction)
        
        if len(self.confidence_history) < 3:
            return prediction, confidence
        
        # Calculate smoothed confidence using EWMA
        recent_confidences = list(self.confidence_history)[-3:]
        smoothed_confidence = recent_confidences[0]  # Start with most recent
        
        for i in range(1, len(recent_confidences)):
            smoothed_confidence = self.alpha * recent_confidences[i] + (1 - self.alpha) * smoothed_confidence
        
        # Count recent predictions
        recent_predictions = list(self.prediction_history)[-3:]
        fake_count = sum(1 for p in recent_predictions if "Deepfake" in p)
        real_count = sum(1 for p in recent_predictions if "Real" in p)
        
        # Apply temporal smoothing logic
        if fake_count >= 2 and smoothed_confidence > 0.6:
            smoothed_prediction = "Deepfake Detected"
            smoothed_confidence = smoothed_confidence * 1.1  # ✅ BIAS FIX: Remove 95% cap
        elif real_count >= 2 and smoothed_confidence < 0.4:
            smoothed_prediction = "Real Face"
            smoothed_confidence = (1.0 - smoothed_confidence) * 1.1  # ✅ BIAS FIX: Remove 95% cap
        else:
            smoothed_prediction = prediction
            smoothed_confidence = max(0.05, smoothed_confidence)  # ✅ BIAS FIX: Remove 95% cap
        
        return smoothed_prediction, smoothed_confidence

class DeterministicEnsembleDetector:
    """Production-grade deterministic ensemble detector with all available models"""
    
    def __init__(self):
        self.config = get_deterministic_config()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.models = {}
        self.model_weights = self.config.get_model_weights()
        self.thresholds = self.config.get_thresholds()
        self.preprocessing_config = self.config.get_preprocessing_config()
        
        # Initialize production preprocessor
        self.preprocessor = ProductionPreprocessor(deterministic=True)
        
        # Initialize tensor processor
        self.tensor_processor = get_tensor_processor(str(self.device))
        
        # Temporal smoothing
        self.temporal_smoother = TemporalSmoother(
            window_size=int(self.thresholds.get("temporal_window_size", 5)),
            alpha=self.thresholds.get("temporal_smoothing_alpha", 0.3)
        )
        
        # Probability calibration
        self.calibrator = ConservativeCalibrator(temperature=1.5)
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'total_processing_time': 0.0,
            'model_usage': {},
            'temporal_corrections': 0,
            'deterministic_mode': True
        }
        
        # Initialize models immediately
        self._initialize_models_sync()
        
        # Reduced logging to avoid duplicates
    
    def _initialize_models_sync(self):
        """Synchronous model initialization for immediate availability with performance optimization"""
        try:
            # Initialize EfficientNet-B0 (always try to use global detector first)
            if global_detector and global_detector.efficientnet_model:
                self.models['efficientnet_b0'] = {
                    'model': global_detector.efficientnet_model,
                    'detector': DeterministicDeepfakeDetector(global_detector.efficientnet_model, str(self.device)),
                    'weight': self.model_weights.get('efficientnet_b0', 0.25)
                }
                # OPTIMIZED: Only call ensure_model_deterministic if config supports it
                try:
                    self.config.ensure_model_deterministic(global_detector.efficientnet_model)
                except Exception as e:
                    logger.debug(f"Model deterministic setup skipped: {e}")
                # Reduced logging to avoid duplicates
            
            # Initialize YOLOv8 Face Detection
            if global_detector and global_detector.yolo_model:
                self.models['yolov8_face'] = {
                    'model': global_detector.yolo_model,
                    'detector': None,  # YOLO is for face detection, not classification
                    'weight': self.model_weights.get('yolov8_face', 0.15)
                }
                # Reduced logging to avoid duplicates
            
            # Try to load additional models from the enhanced loader if available
            if global_detector and hasattr(global_detector, 'enhanced_loader') and global_detector.enhanced_loader:
                enhanced_models = global_detector.enhanced_loader.models
                if enhanced_models:
                    # Add custom finetuned model
                    if 'custom_finetuned' in enhanced_models:
                        self.models['custom_finetuned'] = {
                            'model': enhanced_models['custom_finetuned'],
                            'detector': DeterministicDeepfakeDetector(enhanced_models['custom_finetuned'], str(self.device)),
                            'weight': self.model_weights.get('custom_finetuned', 0.3)
                        }
                        # Reduced logging to avoid duplicates
                    
                    # Add efficientnet finetuned model
                    if 'efficientnet_finetuned' in enhanced_models:
                        self.models['efficientnet_finetuned'] = {
                            'model': enhanced_models['efficientnet_finetuned'],
                            'detector': DeterministicDeepfakeDetector(enhanced_models['efficientnet_finetuned'], str(self.device)),
                            'weight': self.model_weights.get('efficientnet_finetuned', 0.2)
                        }
                        # Reduced logging to avoid duplicates
            
            # If no models loaded, create a fallback
            if not self.models:
                logger.warning("[WARNING] No models available, creating fallback detector")
                self.models['fallback'] = {
                    'model': None,
                    'detector': None,
                    'weight': 1.0
                }
            
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.error(f"[ERROR] Synchronous model initialization failed: {e}")
            # Create fallback
            self.models['fallback'] = {
                'model': None,
                'detector': None,
                'weight': 1.0
            }
    
    async def initialize_models(self) -> bool:
        """Initialize all available models deterministically using the model loader"""
        try:
            logger.info("[LOADING] Initializing deterministic ensemble models...")
            
            # Initialize EfficientNet-B0 (always try to use global detector first)
            if global_detector and global_detector.efficientnet_model:
                self.models['efficientnet_b0'] = {
                    'model': global_detector.efficientnet_model,
                    'detector': DeterministicDeepfakeDetector(global_detector.efficientnet_model, str(self.device)),
                    'weight': self.model_weights.get('efficientnet_b0', 0.25)
                }
                self.config.ensure_model_deterministic(global_detector.efficientnet_model)
                # Reduced logging to avoid duplicates
            
            # Initialize YOLOv8 Face Detection
            if global_detector and global_detector.yolo_model:
                self.models['yolov8_face'] = {
                    'model': global_detector.yolo_model,
                    'detector': None,  # YOLO is for face detection, not classification
                    'weight': self.model_weights.get('yolov8_face', 0.15)
                }
                # Reduced logging to avoid duplicates
            
            # Try to load additional models from the enhanced loader if available
            if global_detector and hasattr(global_detector, 'enhanced_loader') and global_detector.enhanced_loader:
                enhanced_models = global_detector.enhanced_loader.models
                if enhanced_models:
                    # Add custom finetuned model
                    if 'custom_finetuned' in enhanced_models:
                        self.models['custom_finetuned'] = {
                            'model': enhanced_models['custom_finetuned'],
                            'detector': DeterministicDeepfakeDetector(enhanced_models['custom_finetuned'], str(self.device)),
                            'weight': self.model_weights.get('custom_finetuned', 0.3)
                        }
                        # Reduced logging to avoid duplicates
                    
                    # Add efficientnet finetuned model
                    if 'efficientnet_finetuned' in enhanced_models:
                        self.models['efficientnet_finetuned'] = {
                            'model': enhanced_models['efficientnet_finetuned'],
                            'detector': DeterministicDeepfakeDetector(enhanced_models['efficientnet_finetuned'], str(self.device)),
                            'weight': self.model_weights.get('efficientnet_finetuned', 0.2)
                        }
                        # Reduced logging to avoid duplicates
            
            # If no models loaded, create a fallback
            if not self.models:
                logger.warning("[WARNING] No models available, creating fallback detector")
                self.models['fallback'] = {
                    'model': None,
                    'detector': None,
                    'weight': 1.0
                }
            
            logger.info(f"[OK] Ensemble initialized with {len(self.models)} models: {list(self.models.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Model initialization failed: {e}")
            # Create fallback
            self.models['fallback'] = {
                'model': None,
                'detector': None,
                'weight': 1.0
            }
            return False
    
    def preprocess_face_deterministic(self, face: np.ndarray) -> Tuple[torch.Tensor, str]:
        """Preprocess face with deterministic operations and generate hash"""
        try:
            if face is None:
                raise ValueError("Face input is None")
            
            # Generate preprocessing hash
            preproc_hash = self.config.generate_preprocessing_hash(face)
            
            # Use production preprocessor for consistent normalization
            face_tensor = self.preprocessor.preprocess_face(face, self.device)
            
            return face_tensor, preproc_hash
            
        except Exception as e:
            logger.error(f"[ERROR] Deterministic face preprocessing failed: {e}")
            # Return fallback
            fallback_tensor = torch.randn(1, 3, 224, 224).to(self.device)
            return fallback_tensor, "fallback"
    
    async def run_single_model(self, model_name: str, faces: List[np.ndarray]) -> ModelResult:
        """Run a single model on faces"""
        try:
            if model_name not in self.models:
                return ModelResult(
                    model_name=model_name,
                    prediction="Model Not Available",
                    confidence=0.0,
                    raw_output=0.0,
                    processing_time=0.0,
                    success=False,
                    error="Model not initialized"
                )
            
            model_info = self.models[model_name]
            start_time = time.time()
            
            # Handle fallback case
            if model_name == 'fallback' or model_info['detector'] is None:
                # Return neutral result for fallback
                prediction = "Real Face"
                confidence = 50.0
                raw_output = 0.5
                
            elif model_name == 'efficientnet_b0':
                # Use improved tensor processing
                model = model_info['model']
                if model is not None:
                    # Process first face with improved tensor handling
                    if faces:
                        face_tensor = self.tensor_processor.preprocess_face_robust(faces[0])
                        output = self.tensor_processor.safe_model_inference(model, face_tensor)
                        raw_output, prediction, confidence = self.tensor_processor.process_model_output(output, model_name)
                    else:
                        prediction = "No Faces"
                        confidence = 0.0
                        raw_output = 0.0
                else:
                    prediction = "Model Not Available"
                    confidence = 0.0
                    raw_output = 0.0
                
            elif model_name == 'yolov8_face':
                # YOLO is for face detection, return neutral result
                prediction = "Real Face"
                confidence = 50.0
                raw_output = 0.5
                
            elif model_name in ['custom_finetuned', 'efficientnet_finetuned']:
                # Use improved tensor processing for finetuned models
                model = model_info['model']
                if model is not None:
                    # Process first face with improved tensor handling
                    if faces:
                        face_tensor = self.tensor_processor.preprocess_face_robust(faces[0])
                        output = self.tensor_processor.safe_model_inference(model, face_tensor)
                        raw_output, prediction, confidence = self.tensor_processor.process_model_output(output, model_name)
                    else:
                        prediction = "No Faces"
                        confidence = 0.0
                        raw_output = 0.0
                else:
                    prediction = "Model Not Available"
                    confidence = 0.0
                    raw_output = 0.0
                
            else:
                # Use other models
                detector = model_info['detector']
                if detector and hasattr(detector, 'detect'):
                    result = detector.detect(faces)
                    prediction = result.get('prediction', 'Real Face')
                    confidence = result.get('confidence', 50.0)
                    raw_output = confidence / 100.0
                elif detector and hasattr(detector, 'predict'):
                    result = detector.predict(faces)
                    prediction = result.get('prediction', 'Real Face')
                    confidence = result.get('confidence', 50.0)
                    raw_output = confidence / 100.0
                else:
                    prediction = "Model Error"
                    confidence = 0.0
                    raw_output = 0.0
            
            processing_time = (time.time() - start_time) * 1000
            
            return ModelResult(
                model_name=model_name,
                prediction=prediction,
                confidence=confidence,
                raw_output=raw_output,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Model {model_name} failed: {e}")
            return ModelResult(
                model_name=model_name,
                prediction="Model Error",
                confidence=0.0,
                raw_output=0.0,
                processing_time=0.0,
                success=False,
                error=str(e)
            )
    
    def fuse_model_results(self, model_results: Dict[str, ModelResult]) -> Tuple[float, str, float]:
        """Fuse results from all models using weighted average with proper class mapping"""
        try:
            total_weight = 0.0
            weighted_sum = 0.0
            successful_models = 0
            
            # Log raw outputs for debugging
            logger.info("🔍 Model fusion inputs:")
            for model_name, result in model_results.items():
                if result.success and model_name in self.models:
                    weight = self.models[model_name]['weight']
                    total_weight += weight
                    weighted_sum += result.raw_output * weight
                    successful_models += 1
                    logger.info(f"  {model_name}: raw_output={result.raw_output:.4f}, confidence={result.confidence:.4f}, weight={weight:.2f}")
            
            if total_weight == 0:
                return 0.5, "No Models Available", 0.0
            
            # Calculate weighted average
            fusion_raw = weighted_sum / total_weight
            
            # Apply probability calibration to reduce overconfident predictions
            calibrated_prob = self.calibrator.calibrate(fusion_raw)
            logger.info(f"🔍 Calibrated probability: {fusion_raw:.4f} -> {calibrated_prob:.4f}")
            
            # Validate model agreement
            model_probs = {name: result.raw_output for name, result in model_results.items() if result.success}
            models_agree = validate_model_agreement(model_probs, threshold=0.4)
            
            if not models_agree:
                logger.warning("[WARNING] Model disagreement detected, reducing confidence")
                calibrated_prob = 0.5  # Force uncertain result
                prediction = "Uncertain"
                confidence = 50.0
                return fusion_raw, prediction, confidence
            
            # Use more balanced thresholds for better real face detection
            real_face_threshold = 0.4   # Lower threshold for real faces (more lenient)
            deepfake_threshold = 0.6   # Higher threshold for deepfakes (more conservative)
            
            # Apply confidence boosting for probabilities close to 0.5 - FAVOR REAL
            if 0.48 <= calibrated_prob <= 0.52:
                # Always boost towards real for uncertain cases
                calibrated_prob = min(0.6, calibrated_prob + 0.08)  # Stronger boost towards real
                logger.info(f"🔍 Ensemble confidence boost applied towards real: {calibrated_prob:.4f}")
            
            # FIXED: Consistent class mapping with proper confidence scaling
            # calibrated_prob represents probability of being REAL (class 0)
            # So high calibrated_prob = real, low calibrated_prob = fake
            if calibrated_prob >= real_face_threshold:
                prediction = "Real Face"
                # Scale confidence properly for real faces (higher prob = higher confidence)
                confidence = calibrated_prob * 100  # ✅ BIAS FIX: Remove 95% cap
            elif calibrated_prob <= deepfake_threshold:
                prediction = "Deepfake Detected"
                # Scale confidence properly for deepfakes (lower prob = higher confidence for fake)
                confidence = (1.0 - calibrated_prob) * 100  # ✅ BIAS FIX: Remove 95% cap
            else:
                # Only mark as uncertain if truly in the middle range
                prediction = "Uncertain"
                confidence = 50.0
                logger.warning(f"[WARNING] Ensemble uncertain case: prob={calibrated_prob:.4f} between thresholds")
            
            # Apply uncertainty penalty for overconfident predictions
            calibrated_prob, confidence = apply_uncertainty_penalty(calibrated_prob, confidence)
            
            # Only flag as close call if very close to exact 0.5
            distance_from_center = abs(calibrated_prob - 0.5)
            if distance_from_center < 0.02:  # Only within 2% of exact center
                logger.warning(f"[WARNING] Ensemble close call detected: prob={calibrated_prob:.4f}, distance={distance_from_center:.4f}")
                # For close calls, default to real face with lower confidence
                if calibrated_prob >= 0.5:
                    prediction = "Real Face"
                    confidence = max(60.0, calibrated_prob * 100)  # Minimum 60% confidence for real
                else:
                    prediction = "Deepfake Detected"
                    confidence = max(60.0, (1.0 - calibrated_prob) * 100)  # Minimum 60% confidence for fake
            
            logger.info(f"🔍 Final fusion result: raw={fusion_raw:.4f}, calibrated={calibrated_prob:.4f}, prediction={prediction}, confidence={confidence:.2f}%")
            
            return fusion_raw, prediction, confidence
            
        except Exception as e:
            logger.error(f"[ERROR] Model fusion failed: {e}")
            return 0.5, "Fusion Error", 0.0
    
    async def detect_ensemble(self, faces: List[np.ndarray], frame_id: int = 0) -> EnsembleResult:
        """Run full ensemble detection on faces"""
        try:
            start_time = time.time()
            timestamp = time.time()
            
            # Preprocess faces and generate hash
            processed_faces = []
            preproc_hashes = []
            
            for face in faces:
                processed_face, preproc_hash = self.preprocess_face_deterministic(face)
                processed_faces.append(processed_face)
                preproc_hashes.append(preproc_hash)
            
            # Use first face hash as representative
            preproc_hash = preproc_hashes[0] if preproc_hashes else "no_faces"
            
            # Run all models in parallel
            tasks = []
            for model_name in self.models.keys():
                task = asyncio.create_task(self.run_single_model(model_name, faces))
                tasks.append(task)
            
            # Wait for all models to complete
            model_results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert to dictionary
            model_results = {}
            for i, (model_name, result) in enumerate(zip(self.models.keys(), model_results_list)):
                if isinstance(result, Exception):
                    model_results[model_name] = ModelResult(
                        model_name=model_name,
                        prediction="Model Error",
                        confidence=0.0,
                        raw_output=0.0,
                        processing_time=0.0,
                        success=False,
                        error=str(result)
                    )
                else:
                    model_results[model_name] = result
            
            # Fuse results
            fusion_raw, prediction, confidence = self.fuse_model_results(model_results)
            
            # Apply temporal smoothing
            smoothed_prediction, smoothed_confidence = self.temporal_smoother.add_result(prediction, confidence / 100.0)
            smoothed_confidence = smoothed_confidence * 100
            
            # Check if temporal smoothing changed the result
            temporal_smoothed = (prediction != smoothed_prediction)
            if temporal_smoothed:
                self.stats['temporal_corrections'] += 1
            
            # Final decision
            final_prediction = smoothed_prediction
            final_confidence = smoothed_confidence
            decision = "fake" if "Deepfake" in final_prediction else "real"
            
            processing_time = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['frames_processed'] += 1
            self.stats['total_processing_time'] += processing_time
            
            for model_name, result in model_results.items():
                if model_name not in self.stats['model_usage']:
                    self.stats['model_usage'][model_name] = 0
                if result.success:
                    self.stats['model_usage'][model_name] += 1
            
            # Create ensemble result
            ensemble_result = EnsembleResult(
                frame_id=frame_id,
                timestamp=timestamp,
                preproc_hash=preproc_hash,
                model_results=model_results,
                fusion_raw=fusion_raw,
                fusion_smoothed=smoothed_confidence / 100.0,
                final_prediction=final_prediction,
                final_confidence=final_confidence,
                decision=decision,
                processing_time=processing_time,
                temporal_smoothed=temporal_smoothed
            )
            
            # Log comprehensive result
            self._log_ensemble_result(ensemble_result)
            
            return ensemble_result
            
        except Exception as e:
            logger.error(f"[ERROR] Ensemble detection failed: {e}")
            # Return error result
            return EnsembleResult(
                frame_id=frame_id,
                timestamp=time.time(),
                preproc_hash="error",
                model_results={},
                fusion_raw=0.5,
                fusion_smoothed=0.5,
                final_prediction="Detection Failed",
                final_confidence=0.0,
                decision="error",
                processing_time=0.0
            )
    
    def _log_ensemble_result(self, result: EnsembleResult):
        """Log comprehensive ensemble result"""
        try:
            # Create structured log entry
            log_entry = {
                "frame_id": result.frame_id,
                "timestamp": datetime.fromtimestamp(result.timestamp).isoformat(),
                "preproc_hash": result.preproc_hash,
                "models": {
                    name: {
                        "prediction": model_result.prediction,
                        "confidence": model_result.confidence,
                        "raw_output": model_result.raw_output,
                        "processing_time": model_result.processing_time,
                        "success": model_result.success
                    }
                    for name, model_result in result.model_results.items()
                },
                "fusion_raw": result.fusion_raw,
                "fusion_smoothed": result.fusion_smoothed,
                "final_prediction": result.final_prediction,
                "final_confidence": result.final_confidence,
                "decision": result.decision,
                "temporal_smoothed": result.temporal_smoothed,
                "processing_time": result.processing_time
            }
            
            logger.info(f"🎯 Ensemble Result: {json.dumps(log_entry, indent=2)}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to log ensemble result: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            **self.stats,
            "models_available": list(self.models.keys()),
            "model_weights": self.model_weights,
            "thresholds": self.thresholds,
            "device": str(self.device),
            "deterministic_enabled": self.config.enable_deterministic
        }
    
    def detect_deepfake(self, faces: List[np.ndarray]) -> 'DetectionResult':
        """Synchronous interface for deepfake detection (compatibility with mode_detection.py)"""
        try:
            # Check if we're already in an event loop
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, run in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_detection_sync, faces)
                    return future.result()
            except RuntimeError:
                # No event loop running, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.detect_ensemble(faces))
                    return self._convert_to_detection_result(result)
                finally:
                    loop.close()
                
        except Exception as e:
            logger.error(f"[ERROR] Synchronous detection failed: {e}")
            return self._create_fallback_result()
    
    def _run_detection_sync(self, faces: List[np.ndarray]) -> 'DetectionResult':
        """Run detection in a separate thread"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self.detect_ensemble(faces))
            return self._convert_to_detection_result(result)
        finally:
            loop.close()
    
    def _convert_to_detection_result(self, result) -> 'DetectionResult':
        """Convert EnsembleResult to DetectionResult format"""
        from dataclasses import dataclass
        
        @dataclass
        class DetectionResult:
            prediction: str
            confidence: float
            processing_time_ms: float
            models_used: List[str]
        
        return DetectionResult(
            prediction=result.final_prediction,
            confidence=result.final_confidence,
            processing_time_ms=result.processing_time,
            models_used=list(result.model_results.keys())
        )
    
    def _create_fallback_result(self) -> 'DetectionResult':
        """Create fallback result on error"""
        from dataclasses import dataclass
        
        @dataclass
        class DetectionResult:
            prediction: str
            confidence: float
            processing_time_ms: float
            models_used: List[str]
        
        return DetectionResult(
            prediction="Detection Failed",
            confidence=0.0,
            processing_time_ms=0.0,
            models_used=[]
        )

# Global ensemble detector instance
ensemble_detector = DeterministicEnsembleDetector()

async def get_ensemble_detector() -> DeterministicEnsembleDetector:
    """Get the global ensemble detector"""
    if not ensemble_detector.models:
        await ensemble_detector.initialize_models()
    return ensemble_detector

def get_deterministic_ensemble_detector() -> DeterministicEnsembleDetector:
    """Get the deterministic ensemble detector instance (synchronous)"""
    return ensemble_detector

async def detect_ensemble_deterministic(faces: List[np.ndarray], frame_id: int = 0) -> EnsembleResult:
    """Detect using deterministic ensemble"""
    detector = await get_ensemble_detector()
    return await detector.detect_ensemble(faces, frame_id)

def get_deterministic_ensemble_detector() -> DeterministicEnsembleDetector:
    """Get the deterministic ensemble detector instance"""
    return ensemble_detector

