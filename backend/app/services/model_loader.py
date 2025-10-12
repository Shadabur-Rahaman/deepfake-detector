"""
Model Loader for Deepfake Detection System

This module provides production-grade model loading capabilities with support
for multiple model types, error handling, and fallback mechanisms.

Design Principles:
- Lazy Loading: Models loaded only when needed
- Error Handling: Graceful fallbacks and comprehensive logging
- Memory Management: Efficient model loading and unloading
- Type Safety: Full type hints and validation
- Extensibility: Easy addition of new model types

Author: Senior ML Engineer
Date: 2024
"""

import os
import logging
import torch
import torch.nn as nn
from typing import Dict, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .mode_registry import DetectionMode, ModeConfig, get_mode_registry

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Enumeration of supported model types"""
    EFFICIENTNET_B0 = "efficientnet_b0"
    MESONET = "mesonet"
    CUSTOM = "custom"
    FALLBACK = "fallback"

@dataclass
class ModelLoadResult:
    """Result of model loading operation"""
    success: bool
    model: Optional[Any] = None
    model_type: Optional[ModelType] = None
    error_message: Optional[str] = None
    load_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None

class ModelLoader:
    """
    Production-grade model loader with support for multiple model types
    and comprehensive error handling.
    """
    
    def __init__(self):
        self._loaded_models: Dict[DetectionMode, Dict[str, Any]] = {}
        self._model_cache: Dict[str, Any] = {}
        self._device = self._get_device()
        self._mode_registry = get_mode_registry()
        
    def _get_device(self) -> torch.device:
        """Get the appropriate device for model loading"""
        try:
            if torch.cuda.is_available():
                device = torch.device("cuda")
                logger.info(f"Using CUDA device: {torch.cuda.get_device_name()}")
            else:
                device = torch.device("cpu")
                logger.info("Using CPU device")
            return device
        except Exception as e:
            logger.warning(f"Device detection failed, using CPU: {e}")
            return torch.device("cpu")
    
    def load_model_for_mode(self, mode: DetectionMode) -> ModelLoadResult:
        """
        Load the appropriate model for a specific detection mode
        
        Args:
            mode: The detection mode to load model for
            
        Returns:
            ModelLoadResult with success status and model information
        """
        try:
            # Get mode configuration
            mode_config = self._mode_registry.get_mode(mode)
            if not mode_config:
                return ModelLoadResult(
                    success=False,
                    error_message=f"Mode configuration not found for {mode.value}"
                )
            
            # Check if model is already loaded
            if mode in self._loaded_models:
                model_name = os.path.basename(mode_config.primary_model.model_path)
                logger.info(f"Running in {mode_config.display_name} using {model_name}")
                return ModelLoadResult(
                    success=True,
                    model=self._loaded_models[mode],
                    model_type=ModelType.CUSTOM,
                    load_time_ms=0.0
                )
            
            # Load primary model with clear logging
            model_name = os.path.basename(mode_config.primary_model.model_path)
            logger.info(f"Loading model for {mode_config.display_name}: {model_name}")
            
            model_result = self._load_primary_model(mode_config)
            if model_result.success:
                self._loaded_models[mode] = {
                    'model': model_result.model,
                    'model_type': model_result.model_type,
                    'config': mode_config
                }
                logger.info(f"Running in {mode_config.display_name} using {model_name}")
                return model_result
            else:
                # Try fallback models
                logger.warning(f"Primary model failed for {mode.value}, trying fallbacks")
                return self._load_fallback_model(mode_config)
                
        except Exception as e:
            logger.error(f"Failed to load model for mode {mode.value}: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"Model loading failed: {str(e)}"
            )
    
    def _load_primary_model(self, mode_config: ModeConfig) -> ModelLoadResult:
        """Load the primary model for a mode"""
        try:
            model_path = mode_config.primary_model.model_path
            
            # Check if model file exists
            if not os.path.exists(model_path):
                return ModelLoadResult(
                    success=False,
                    error_message=f"Model file not found: {model_path}"
                )
            
            # Determine model type and load accordingly
            if "efficientnet" in model_path.lower():
                return self._load_efficientnet_model(model_path, mode_config)
            elif "mesonet" in model_path.lower():
                return self._load_mesonet_model(model_path, mode_config)
            else:
                return self._load_custom_model(model_path, mode_config)
                
        except Exception as e:
            logger.error(f"Primary model loading failed: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"Primary model loading failed: {str(e)}"
            )
    
    def _load_fallback_model(self, mode_config: ModeConfig) -> ModelLoadResult:
        """Load fallback model if primary model fails"""
        try:
            logger.info("Attempting to load fallback model")
            
            # Try fallback models in order
            for fallback_model in mode_config.fallback_models:
                if os.path.exists(fallback_model.model_path):
                    result = self._load_custom_model(fallback_model.model_path, mode_config)
                    if result.success:
                        return result
            
            # If no fallback models work, create a basic fallback
            return self._create_basic_fallback_model(mode_config)
            
        except Exception as e:
            logger.error(f"Fallback model loading failed: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"All fallback models failed: {str(e)}"
            )
    
    def _load_efficientnet_model(self, model_path: str, mode_config: ModeConfig) -> ModelLoadResult:
        """Load EfficientNet-B0 model"""
        try:
            import time
            start_time = time.time()
            
            # Import EfficientNet loading function
            from .efficientnet_loader import load_efficientnet_once
            
            # Reduced logging to avoid duplicates
            model = load_efficientnet_once(model_path, device=str(self._device), num_classes=2)
            
            if model is None:
                return ModelLoadResult(
                    success=False,
                    error_message="EfficientNet model loading returned None"
                )
            
            # Set to evaluation mode
            model.eval()
            
            load_time = (time.time() - start_time) * 1000
            memory_usage = self._estimate_memory_usage(model)
            
            # Reduced logging to avoid duplicates
            
            return ModelLoadResult(
                success=True,
                model=model,
                model_type=ModelType.EFFICIENTNET_B0,
                load_time_ms=load_time,
                memory_usage_mb=memory_usage
            )
            
        except Exception as e:
            logger.error(f"EfficientNet model loading failed: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"EfficientNet loading failed: {str(e)}"
            )
    
    def _load_mesonet_model(self, model_path: str, mode_config: ModeConfig) -> ModelLoadResult:
        """Load MesoNet model"""
        try:
            import time
            start_time = time.time()
            
            # Import MesoNet detector
            from .mesonet_detector import MesoNetDetector
            
            logger.info(f"Loading MesoNet model from: {os.path.basename(model_path)}")
            detector = MesoNetDetector()
            
            # Load the model weights
            detector.load_model(model_path)
            
            load_time = (time.time() - start_time) * 1000
            memory_usage = self._estimate_memory_usage(detector.model)
            
            # Reduced logging to avoid duplicates
            
            return ModelLoadResult(
                success=True,
                model=detector,
                model_type=ModelType.MESONET,
                load_time_ms=load_time,
                memory_usage_mb=memory_usage
            )
            
        except Exception as e:
            logger.error(f"MesoNet model loading failed: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"MesoNet loading failed: {str(e)}"
            )
    
    def _load_custom_model(self, model_path: str, mode_config: ModeConfig) -> ModelLoadResult:
        """Load custom model using PyTorch"""
        try:
            import time
            start_time = time.time()
            
            # Reduced logging to avoid duplicates
            
            # Load model state dict
            checkpoint = torch.load(model_path, map_location=self._device, weights_only=False)
            
            # Determine model architecture based on checkpoint keys
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Create model based on architecture
            model = self._create_model_from_checkpoint(state_dict)
            
            if model is None:
                return ModelLoadResult(
                    success=False,
                    error_message="Could not determine model architecture from checkpoint"
                )
            
            # Load state dict
            model.load_state_dict(state_dict, strict=False)
            model.eval()
            
            load_time = (time.time() - start_time) * 1000
            memory_usage = self._estimate_memory_usage(model)
            
            # Reduced logging to avoid duplicates
            
            return ModelLoadResult(
                success=True,
                model=model,
                model_type=ModelType.CUSTOM,
                load_time_ms=load_time,
                memory_usage_mb=memory_usage
            )
            
        except Exception as e:
            logger.error(f"Custom model loading failed: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"Custom model loading failed: {str(e)}"
            )
    
    def _create_model_from_checkpoint(self, state_dict: Dict[str, Any]) -> Optional[nn.Module]:
        """Create model architecture based on checkpoint keys"""
        try:
            # Check for EfficientNet keys - FIXED: Look for backbone.features pattern
            if (any('efficientnet' in key.lower() for key in state_dict.keys()) or
                any('backbone.features' in key for key in state_dict.keys()) or
                any('features.0.0.weight' in key for key in state_dict.keys())):
                from torchvision import models
                model = models.efficientnet_b0(weights=None)
                # Modify classifier for binary classification
                num_ftrs = model.classifier[1].in_features
                model.classifier[1] = nn.Linear(num_ftrs, 1)
                logger.info("[OK] Detected EfficientNet architecture from checkpoint keys")
                return model
            
            # Check for MesoNet keys
            elif any('mesonet' in key.lower() or 'meso' in key.lower() for key in state_dict.keys()):
                from .mesonet_detector import _MesoNet
                logger.info("[OK] Detected MesoNet architecture from checkpoint keys")
                return _MesoNet()
            
            # Check for other known architectures
            elif any('xception' in key.lower() for key in state_dict.keys()):
                from torchvision import models
                model = models.xception(weights=None)
                # Modify classifier for binary classification
                num_ftrs = model.fc.in_features
                model.fc = nn.Linear(num_ftrs, 1)
                logger.info("[OK] Detected Xception architecture from checkpoint keys")
                return model
            
            # Default to a simple CNN
            else:
                logger.warning("Unknown model architecture, using default CNN")
                logger.info(f"Checkpoint keys sample: {list(state_dict.keys())[:5]}")
                return self._create_default_cnn()
                
        except Exception as e:
            logger.error(f"Failed to create model from checkpoint: {e}")
            return None
    
    def _create_default_cnn(self) -> nn.Module:
        """Create a default CNN model as fallback"""
        class DefaultCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
                self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
                self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
                self.pool = nn.AdaptiveAvgPool2d((1, 1))
                self.fc = nn.Linear(128, 1)
                self.dropout = nn.Dropout(0.5)
                
            def forward(self, x):
                x = torch.relu(self.conv1(x))
                x = torch.max_pool2d(x, 2)
                x = torch.relu(self.conv2(x))
                x = torch.max_pool2d(x, 2)
                x = torch.relu(self.conv3(x))
                x = self.pool(x)
                x = x.view(x.size(0), -1)
                x = self.dropout(x)
                x = self.fc(x)
                return x
        
        return DefaultCNN()
    
    def _create_basic_fallback_model(self, mode_config: ModeConfig) -> ModelLoadResult:
        """Create a basic fallback model when all else fails"""
        try:
            logger.warning("Creating basic fallback model")
            
            model = self._create_default_cnn()
            model.eval()
            
            return ModelLoadResult(
                success=True,
                model=model,
                model_type=ModelType.FALLBACK,
                load_time_ms=0.0,
                memory_usage_mb=10.0
            )
            
        except Exception as e:
            logger.error(f"Failed to create basic fallback model: {e}")
            return ModelLoadResult(
                success=False,
                error_message=f"All model loading attempts failed: {str(e)}"
            )
    
    def _estimate_memory_usage(self, model: Any) -> float:
        """Estimate memory usage of a model in MB"""
        try:
            if hasattr(model, 'parameters'):
                total_params = sum(p.numel() for p in model.parameters())
                # Rough estimate: 4 bytes per parameter (float32)
                memory_mb = (total_params * 4) / (1024 * 1024)
                return memory_mb
            else:
                return 50.0  # Default estimate
        except Exception:
            return 50.0  # Default estimate
    
    def get_loaded_model(self, mode: DetectionMode) -> Optional[Any]:
        """Get the loaded model for a specific mode"""
        return self._loaded_models.get(mode, {}).get('model')
    
    def is_model_loaded(self, mode: DetectionMode) -> bool:
        """Check if a model is loaded for a specific mode"""
        return mode in self._loaded_models and 'model' in self._loaded_models[mode]
    
    def unload_model(self, mode: DetectionMode) -> bool:
        """Unload a model to free memory"""
        try:
            if mode in self._loaded_models:
                del self._loaded_models[mode]
                logger.info(f"Unloaded model for mode: {mode.value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unload model for mode {mode.value}: {e}")
            return False
    
    def get_model_info(self, mode: DetectionMode) -> Dict[str, Any]:
        """Get information about a loaded model"""
        if mode not in self._loaded_models:
            return {}
        
        model_data = self._loaded_models[mode]
        return {
            "mode": mode.value,
            "model_type": model_data.get('model_type', 'unknown').value if model_data.get('model_type') else 'unknown',
            "loaded": True,
            "config": model_data.get('config')
        }
    
    def get_all_loaded_models(self) -> Dict[str, Any]:
        """Get information about all loaded models"""
        return {
            mode.value: self.get_model_info(mode)
            for mode in self._loaded_models.keys()
        }

# Global model loader instance
_model_loader: Optional[ModelLoader] = None

def get_model_loader() -> ModelLoader:
    """Get the global model loader instance (singleton pattern)"""
    global _model_loader
    if _model_loader is None:
        _model_loader = ModelLoader()
    return _model_loader

def reset_model_loader():
    """Reset the global model loader (useful for testing)"""
    global _model_loader
    _model_loader = None

def load_all_models() -> Dict[str, Any]:
    """Load all available models for ensemble detection"""
    try:
        from .enhanced_model_loader import load_all_models as enhanced_load_all_models
        return enhanced_load_all_models()
    except ImportError:
        logger.warning("Enhanced model loader not available, using fallback")
        # Fallback implementation
        loader = get_model_loader()
        return loader.get_all_loaded_models()

def get_startup_summary() -> Dict[str, Any]:
    """Get startup summary of model loading status"""
    try:
        loader = get_model_loader()
        available_modes = []
        try:
            available_modes = [mode.value for mode in loader._mode_registry.get_available_modes()]
        except AttributeError:
            # Fallback if get_available_modes doesn't exist
            available_modes = [mode.value for mode in loader._mode_registry.get_enabled_modes().keys()]
        
        # Get loaded models info
        loaded_models = loader.get_all_loaded_models()
        successful_models = list(loaded_models.keys()) if loaded_models else []
        failed_models = []
        missing_dependencies = []
        installation_hints = {}
        ensemble_models = successful_models.copy() if successful_models else []
        
        return {
            "status": "initialized",
            "loaded_models": loaded_models,
            "device": str(loader._device),
            "available_modes": available_modes,
            "successful_models": successful_models,
            "failed_models": failed_models,
            "missing_dependencies": missing_dependencies,
            "installation_hints": installation_hints,
            "ensemble_models": ensemble_models
        }
    except Exception as e:
        logger.error(f"Failed to get startup summary: {e}")
        return {
            "status": "error",
            "error": str(e),
            "loaded_models": {},
            "device": "unknown",
            "successful_models": [],
            "failed_models": [],
            "missing_dependencies": [],
            "installation_hints": {},
            "ensemble_models": []
        }