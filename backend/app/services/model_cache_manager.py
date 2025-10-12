"""
Model Cache Manager - Global Model Loading and Caching
=====================================================

This module provides global model caching and management for faster detection processing.
It loads models once at startup and shares them across all requests.

Author: System Integration Team
Date: 2024
"""

import logging
import torch
import threading
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
import time
import gc

logger = logging.getLogger(__name__)

class ModelCacheManager:
    """Global model cache manager with GPU memory optimization"""
    
    def __init__(self):
        self._models = {}
        self._model_locks = {}
        self._initialization_lock = threading.Lock()
        self._device = self._get_optimal_device()
        self._memory_manager = GPUMemoryManager()
        
    def _get_optimal_device(self) -> str:
        """Get optimal device for model loading"""
        try:
            # Use CUDA Safety Manager if available
            from services.cuda_safety_manager import get_safe_device
            return get_safe_device()
        except ImportError:
            # Fallback device detection
            if torch.cuda.is_available():
                try:
                    # Test CUDA with small operation
                    test_tensor = torch.tensor([1.0]).cuda()
                    del test_tensor
                    torch.cuda.empty_cache()
                    return "cuda"
                except Exception:
                    return "cpu"
            return "cpu"
    
    @contextmanager
    def get_model(self, model_name: str, model_loader_func):
        """Get model from cache or load if not available"""
        with self._get_model_lock(model_name):
            if model_name not in self._models:
                logger.info(f"Loading model: {model_name}")
                try:
                    self._models[model_name] = model_loader_func(self._device)
                    logger.info(f"Model loaded successfully: {model_name}")
                except Exception as e:
                    logger.error(f"Failed to load model {model_name}: {e}")
                    raise
            
            yield self._models[model_name]
    
    def _get_model_lock(self, model_name: str):
        """Get or create lock for specific model"""
        if model_name not in self._model_locks:
            with self._initialization_lock:
                if model_name not in self._model_locks:
                    self._model_locks[model_name] = threading.Lock()
        return self._model_locks[model_name]
    
    def preload_models(self, model_configs: Dict[str, Any]):
        """Preload all specified models at startup"""
        logger.info("Starting model preloading...")
        
        for model_name, config in model_configs.items():
            try:
                with self._get_model_lock(model_name):
                    if model_name not in self._models:
                        logger.info(f"Preloading model: {model_name}")
                        loader_func = config['loader']
                        self._models[model_name] = loader_func(self._device)
                        logger.info(f"Preloaded: {model_name}")
                        
                        # Clear cache after each model load
                        self._memory_manager.optimize_memory()
                        
            except Exception as e:
                logger.warning(f"Failed to preload {model_name}: {e}")
                continue
        
        logger.info(f"Model preloading completed. Loaded {len(self._models)} models")
    
    def clear_cache(self):
        """Clear all cached models"""
        with self._initialization_lock:
            for model_name, model in self._models.items():
                try:
                    del model
                except:
                    pass
            self._models.clear()
            
            # Clear GPU cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Force garbage collection
            gc.collect()
            
            logger.info("Model cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            'loaded_models': list(self._models.keys()),
            'model_count': len(self._models),
            'device': self._device,
            'memory_usage': self._memory_manager.get_memory_info()
        }

class GPUMemoryManager:
    """GPU memory management for model optimization"""
    
    def __init__(self):
        self._memory_threshold = 0.85  # 85% memory usage threshold
        
    def optimize_memory(self):
        """Optimize GPU memory usage"""
        try:
            if torch.cuda.is_available():
                # Get current memory usage
                current_memory = torch.cuda.memory_allocated()
                max_memory = torch.cuda.max_memory_allocated()
                
                # If memory usage is high, clear cache
                if current_memory > 0 and max_memory > 0:
                    usage_ratio = current_memory / max_memory
                    if usage_ratio > self._memory_threshold:
                        torch.cuda.empty_cache()
                        gc.collect()
                        logger.debug("GPU memory optimized")
                        
        except Exception as e:
            logger.debug(f"Memory optimization failed: {e}")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get GPU memory information"""
        try:
            if torch.cuda.is_available():
                return {
                    'allocated': torch.cuda.memory_allocated(),
                    'reserved': torch.cuda.memory_reserved(),
                    'max_allocated': torch.cuda.max_memory_allocated(),
                    'device_count': torch.cuda.device_count()
                }
            else:
                return {'status': 'CUDA not available'}
        except Exception as e:
            return {'error': str(e)}

# Model loader functions
def load_resnet50_model(device: str):
    """Load ResNet50 model"""
    try:
        from services.advanced_models_integration import ResNetDetector
        detector = ResNetDetector(variant='resnet50', device=device)
        return detector
    except Exception as e:
        logger.error(f"ResNet50 loader failed: {e}")
        raise

def load_resnet101_model(device: str):
    """Load ResNet101 model"""
    try:
        from services.advanced_models_integration import ResNetDetector
        detector = ResNetDetector(variant='resnet101', device=device)
        return detector
    except Exception as e:
        logger.error(f"ResNet101 loader failed: {e}")
        raise

def load_yolov8_model(device: str):
    """Load YOLOv8 model"""
    try:
        from services.advanced_models_integration import YOLOv8Detector
        detector = YOLOv8Detector(device=device)
        return detector
    except Exception as e:
        logger.error(f"YOLOv8 loader failed: {e}")
        raise

def load_mesonet_model(device: str):
    """Load MesoNet model"""
    try:
        from services.advanced_models_integration import MesoNetDetector
        detector = MesoNetDetector(device=device)
        return detector
    except Exception as e:
        logger.error(f"MesoNet loader failed: {e}")
        raise

def load_vit_model(device: str):
    """Load Vision Transformer model"""
    try:
        from services.advanced_models_integration import VisionTransformerDetector
        detector = VisionTransformerDetector(device=device)
        return detector
    except Exception as e:
        logger.error(f"ViT loader failed: {e}")
        raise

def load_lstm_model(device: str):
    """Load LSTM model"""
    try:
        from services.advanced_models_integration import LSTMDetector
        detector = LSTMDetector(device=device)
        return detector
    except Exception as e:
        logger.error(f"LSTM loader failed: {e}")
        raise

def load_deepfake_detector(device: str):
    """Load main deepfake detector"""
    try:
        from services.deepfake_detector import DeepfakeDetector
        detector = DeepfakeDetector()
        return detector
    except Exception as e:
        logger.error(f"Deepfake detector loader failed: {e}")
        raise

def load_yolov8_deepfake_detector(device: str):
    """Load YOLOv8 deepfake detector"""
    try:
        from services.yolov8_deepfake_detector import YOLOv8DeepfakeDetector
        detector = YOLOv8DeepfakeDetector(device=device)
        return detector
    except Exception as e:
        logger.error(f"YOLOv8 deepfake detector loader failed: {e}")
        raise

# Model configuration for preloading
MODEL_CONFIGS = {
    'resnet50': {'loader': load_resnet50_model, 'priority': 1},
    'resnet101': {'loader': load_resnet101_model, 'priority': 2},
    'yolov8': {'loader': load_yolov8_model, 'priority': 1},
    'mesonet': {'loader': load_mesonet_model, 'priority': 2},
    'vit': {'loader': load_vit_model, 'priority': 2},
    'lstm': {'loader': load_lstm_model, 'priority': 3},
    'deepfake_detector': {'loader': load_deepfake_detector, 'priority': 1},
    'yolov8_deepfake': {'loader': load_yolov8_deepfake_detector, 'priority': 1}
}

# Global model cache manager instance
model_cache = ModelCacheManager()

def get_cached_model(model_name: str):
    """Get cached model by name"""
    return model_cache.get_model(model_name, MODEL_CONFIGS[model_name]['loader'])

def initialize_model_cache():
    """Initialize model cache with preloading"""
    try:
        # Sort models by priority (lower number = higher priority)
        sorted_configs = dict(sorted(
            MODEL_CONFIGS.items(),
            key=lambda x: x[1]['priority']
        ))
        
        model_cache.preload_models(sorted_configs)
        return True
    except Exception as e:
        logger.error(f"Model cache initialization failed: {e}")
        return False

def clear_model_cache():
    """Clear all cached models"""
    model_cache.clear_cache()

def get_cache_info():
    """Get model cache information"""
    return model_cache.get_cache_info()
