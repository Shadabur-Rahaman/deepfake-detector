"""
Advanced Model Registry - Centralized Management of All Advanced Models
=====================================================================

This module provides centralized management for all advanced deepfake detection models:
- ResNet50, ResNet101, ResNet152
- LSTM with temporal analysis
- Vision Transformers (ViT)
- MesoNet architecture
- YOLOv8 face detection
- Custom ensemble models

Features:
- Load all models at startup
- Standardized prediction interface
- Per-model face validation using FaceDataValidator
- Graceful error handling with fallbacks
- Model availability tracking
"""

import asyncio
import logging
import time
import torch
import numpy as np
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import face data validator for type conversion
try:
    from .face_data_validator import FaceDataValidator
    FACE_VALIDATOR_AVAILABLE = True
except ImportError:
    FACE_VALIDATOR_AVAILABLE = False
    logger.warning("FaceDataValidator not available")

@dataclass
class ModelResult:
    """Standardized model prediction result"""
    model_name: str
    prediction: str
    confidence: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AdvancedModelRegistry:
    """Centralized registry for all advanced deepfake detection models"""
    
    def __init__(self):
        self.models = {}
        self.availability = {}
        self.initialized = False
        self.device = self._get_optimal_device()
        
        # Model configuration
        self.model_configs = {
            'resnet50': {'weight': 0.10, 'priority': 1},
            'resnet101': {'weight': 0.05, 'priority': 2},
            'resnet152': {'weight': 0.03, 'priority': 3},
            'lstm': {'weight': 0.05, 'priority': 4},
            'mesonet': {'weight': 0.04, 'priority': 5},
            'yolov8_face': {'weight': 0.08, 'priority': 6}
        }
        
        logger.info(f"[AdvancedModelRegistry] Initialized on device: {self.device}")
    
    def _get_optimal_device(self) -> str:
        """Get optimal device for model loading"""
        try:
            from .cuda_safety_manager import get_safe_device
            return get_safe_device()
        except ImportError:
            return "cuda" if torch.cuda.is_available() else "cpu"
    
    async def initialize_all_models(self):
        """Initialize only essential models at startup, others load on demand"""
        logger.info("[AdvancedModelRegistry] Starting essential model initialization...")
        start_time = time.time()
        
        # ✅ STARTUP OPTIMIZATION: Load only essential models at startup
        init_tasks = []
        
        # Only load YOLOv8 (essential for face detection)
        init_tasks.append(self._initialize_yolov8_model())
        
        # Mark other models for lazy loading
        self._lazy_models = ['resnet50', 'resnet101', 'resnet152', 'lstm', 'mesonet']
        
        # Wait for essential initializations to complete
        try:
            await asyncio.wait_for(
                asyncio.gather(*init_tasks, return_exceptions=True),
                timeout=30.0  # 30 second timeout for model loading
            )
        except asyncio.TimeoutError:
            logger.warning("[AdvancedModelRegistry] Model initialization timeout - some models may not be available")
        
        # Count successful models
        successful_models = sum(1 for available in self.availability.values() if available)
        total_models = len(self.model_configs)
        
        self.initialized = True
        init_time = time.time() - start_time
        
        logger.info(f"[AdvancedModelRegistry] Essential initialization completed in {init_time:.2f}s")
        logger.info(f"[AdvancedModelRegistry] Models loaded: {successful_models}/{total_models}")
        logger.info(f"[AdvancedModelRegistry] Available models: {[name for name, avail in self.availability.items() if avail]}")
        
        return successful_models > 0
    
    async def load_model_on_demand(self, model_name: str):
        """Load a specific model on demand for better startup performance"""
        if model_name in self.models and self.availability.get(model_name, False):
            return True  # Already loaded
        
        logger.info(f"[AdvancedModelRegistry] Loading {model_name} on demand...")
        
        try:
            if model_name in ['resnet50', 'resnet101', 'resnet152']:
                await self._initialize_resnet_models()
            elif model_name == 'lstm':
                await self._initialize_lstm_model()
            elif model_name == 'mesonet':
                await self._initialize_mesonet_model()
            elif model_name == 'yolov8_face':
                await self._initialize_yolov8_model()
            
            logger.info(f"[AdvancedModelRegistry] {model_name} loaded successfully")
            return True
        except Exception as e:
            logger.warning(f"[AdvancedModelRegistry] {model_name} failed to load: {e}")
            return False
    
    async def _initialize_resnet_models(self):
        """Initialize ResNet variants"""
        try:
            from .advanced_models_integration import ResNetDetector
            
            # Initialize ResNet50
            try:
                self.models['resnet50'] = ResNetDetector('resnet50', self.device)
                self.availability['resnet50'] = self.models['resnet50'].model is not None
                logger.info(f"[AdvancedModelRegistry] ResNet50: {'✅' if self.availability['resnet50'] else '❌'}")
            except Exception as e:
                logger.warning(f"[AdvancedModelRegistry] ResNet50 failed: {e}")
                self.availability['resnet50'] = False
            
            # Initialize ResNet101
            try:
                self.models['resnet101'] = ResNetDetector('resnet101', self.device)
                self.availability['resnet101'] = self.models['resnet101'].model is not None
                logger.info(f"[AdvancedModelRegistry] ResNet101: {'✅' if self.availability['resnet101'] else '❌'}")
            except Exception as e:
                logger.warning(f"[AdvancedModelRegistry] ResNet101 failed: {e}")
                self.availability['resnet101'] = False
            
            # Initialize ResNet152
            try:
                self.models['resnet152'] = ResNetDetector('resnet152', self.device)
                self.availability['resnet152'] = self.models['resnet152'].model is not None
                logger.info(f"[AdvancedModelRegistry] ResNet152: {'✅' if self.availability['resnet152'] else '❌'}")
            except Exception as e:
                logger.warning(f"[AdvancedModelRegistry] ResNet152 failed: {e}")
                self.availability['resnet152'] = False
                
        except Exception as e:
            logger.error(f"[AdvancedModelRegistry] ResNet models initialization failed: {e}")
            for variant in ['resnet50', 'resnet101', 'resnet152']:
                self.availability[variant] = False
    
    async def _initialize_lstm_model(self):
        """Initialize LSTM model"""
        try:
            from .advanced_models_integration import LSTMDetector
            
            self.models['lstm'] = LSTMDetector(device=self.device)
            self.availability['lstm'] = (self.models['lstm'].model is not None and 
                                       self.models['lstm'].feature_extractor is not None)
            logger.info(f"[AdvancedModelRegistry] LSTM: {'✅' if self.availability['lstm'] else '❌'}")
            
        except Exception as e:
            logger.warning(f"[AdvancedModelRegistry] LSTM failed: {e}")
            self.availability['lstm'] = False
    
    async def _initialize_mesonet_model(self):
        """Initialize MesoNet model"""
        try:
            from .advanced_models_integration import MesoNetDetector
            
            self.models['mesonet'] = MesoNetDetector(device=self.device)
            self.availability['mesonet'] = self.models['mesonet'].model is not None
            logger.info(f"[AdvancedModelRegistry] MesoNet: {'✅' if self.availability['mesonet'] else '❌'}")
            
        except Exception as e:
            logger.warning(f"[AdvancedModelRegistry] MesoNet failed: {e}")
            self.availability['mesonet'] = False
    
    async def _initialize_yolov8_model(self):
        """Initialize YOLOv8 model"""
        try:
            from .advanced_models_integration import YOLOv8Detector
            
            self.models['yolov8_face'] = YOLOv8Detector(device=self.device)
            self.availability['yolov8_face'] = self.models['yolov8_face'].model is not None
            logger.info(f"[AdvancedModelRegistry] YOLOv8: {'✅' if self.availability['yolov8_face'] else '❌'}")
            
        except Exception as e:
            logger.warning(f"[AdvancedModelRegistry] YOLOv8 failed: {e}")
            self.availability['yolov8_face'] = False
    
    def get_model(self, model_name: str):
        """Get model instance if available"""
        if model_name in self.models and self.availability.get(model_name, False):
            return self.models[model_name]
        return None
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if model is available"""
        return self.availability.get(model_name, False)
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return [name for name, available in self.availability.items() if available]
    
    def get_model_weight(self, model_name: str) -> float:
        """Get model weight for ensemble"""
        return self.model_configs.get(model_name, {}).get('weight', 0.0)
    
    async def predict_with_model(self, model_name: str, faces: List[np.ndarray]) -> ModelResult:
        """Make prediction using specified model with face validation"""
        start_time = time.time()
        
        try:
            # Check if model is available
            if not self.is_model_available(model_name):
                return ModelResult(
                    model_name=model_name,
                    prediction="Model Not Available",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"Model {model_name} is not available"
                )
            
            # Validate faces using FaceDataValidator
            validated_faces = faces
            if FACE_VALIDATOR_AVAILABLE:
                validated_faces = FaceDataValidator.validate_face_list(faces, f"registry_{model_name}")
                if not validated_faces:
                    return ModelResult(
                        model_name=model_name,
                        prediction="Face Validation Failed",
                        confidence=0.0,
                        processing_time=time.time() - start_time,
                        success=False,
                        error_message="No valid faces after validation"
                    )
            else:
                logger.warning(f"[AdvancedModelRegistry] FaceDataValidator not available for {model_name}")
            
            # Get model and make prediction
            model = self.get_model(model_name)
            if model is None:
                return ModelResult(
                    model_name=model_name,
                    prediction="Model Instance Not Found",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"Model instance for {model_name} not found"
                )
            
            # Run model prediction
            if hasattr(model, 'predict'):
                # For models with predict method
                prediction_result = model.predict(validated_faces)
                
                # Convert to standardized format
                if hasattr(prediction_result, 'prediction'):
                    # ModelPrediction format
                    return ModelResult(
                        model_name=model_name,
                        prediction=prediction_result.prediction,
                        confidence=prediction_result.confidence,
                        processing_time=time.time() - start_time,
                        success=prediction_result.success,
                        error_message=prediction_result.error_message,
                        metadata={'raw_output': getattr(prediction_result, 'raw_output', None)}
                    )
                else:
                    # Direct result format
                    return ModelResult(
                        model_name=model_name,
                        prediction=str(prediction_result),
                        confidence=0.5,
                        processing_time=time.time() - start_time,
                        success=True
                    )
            else:
                return ModelResult(
                    model_name=model_name,
                    prediction="No Predict Method",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    success=False,
                    error_message=f"Model {model_name} has no predict method"
                )
                
        except Exception as e:
            logger.error(f"[AdvancedModelRegistry] Prediction failed for {model_name}: {e}")
            return ModelResult(
                model_name=model_name,
                prediction="Prediction Failed",
                confidence=0.0,
                processing_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    async def predict_with_all_models(self, faces: List[np.ndarray]) -> Dict[str, ModelResult]:
        """Make predictions using all available models"""
        if not self.initialized:
            logger.warning("[AdvancedModelRegistry] Registry not initialized")
            return {}
        
        # Get available models
        available_models = self.get_available_models()
        if not available_models:
            logger.warning("[AdvancedModelRegistry] No models available")
            return {}
        
        # Run predictions in parallel
        tasks = []
        for model_name in available_models:
            task = asyncio.create_task(self.predict_with_model(model_name, faces))
            tasks.append((model_name, task))
        
        # Wait for all predictions
        results = {}
        for model_name, task in tasks:
            try:
                result = await task
                results[model_name] = result
            except Exception as e:
                logger.error(f"[AdvancedModelRegistry] Task failed for {model_name}: {e}")
                results[model_name] = ModelResult(
                    model_name=model_name,
                    prediction="Task Failed",
                    confidence=0.0,
                    processing_time=0.0,
                    success=False,
                    error_message=str(e)
                )
        
        return results
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status"""
        return {
            'initialized': self.initialized,
            'device': self.device,
            'total_models': len(self.model_configs),
            'available_models': len(self.get_available_models()),
            'model_availability': self.availability.copy(),
            'model_weights': {name: config['weight'] for name, config in self.model_configs.items()},
            'face_validator_available': FACE_VALIDATOR_AVAILABLE
        }

# Global registry instance
advanced_model_registry = AdvancedModelRegistry()

# Convenience functions
async def initialize_advanced_models():
    """Initialize all advanced models"""
    return await advanced_model_registry.initialize_all_models()

def get_advanced_model_registry():
    """Get the global advanced model registry instance"""
    return advanced_model_registry

def is_advanced_model_available(model_name: str) -> bool:
    """Check if specific advanced model is available"""
    return advanced_model_registry.is_model_available(model_name)

async def predict_with_advanced_model(model_name: str, faces: List[np.ndarray]) -> ModelResult:
    """Make prediction with specific advanced model"""
    return await advanced_model_registry.predict_with_model(model_name, faces)
