"""
Global Model Cache Manager - Optimize Model Loading Performance
==============================================================

This module provides global model caching to eliminate on-demand loading delays
and improve detection performance across all modes.

Author: AI Assistant
Date: 2025
"""

import os
import torch
import logging
import threading
import time
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class GlobalModelCache:
    """Global model cache manager for optimized performance"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.models = {}
            self.models_loaded = False
            self.loading_started = False
            self.device = self._get_optimal_device()
            self._initialized = True
    
    def _get_optimal_device(self) -> str:
        """Get optimal device for model loading"""
        # Check for force CPU mode
        if (os.environ.get("FORCE_CPU_MODE", "0") == "1" or 
            os.environ.get("CUDA_VISIBLE_DEVICES", "") == ""):
            return "cpu"
        
        # Try CUDA if available
        try:
            if torch.cuda.is_available():
                # Use centralized CUDA safety manager to avoid driver conflicts
                from backend.app.services.cuda_safety_manager import get_validated_device, is_cuda_available_global
                
                if is_cuda_available_global():
                    return get_validated_device()
                else:
                    return "cpu"
        except Exception as e:
            logger.warning(f"CUDA test failed, using CPU: {e}")
        
        return "cpu"
    
    def preload_essential_models(self):
        """Preload essential models for faster detection"""
        if self.loading_started:
            return
        
        self.loading_started = True
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Preloading essential models on {self.device}...")
            
            # 1. Load EfficientNet (most commonly used)
            self._load_efficientnet()
            
            # 2. Load YOLOv8 face detection
            self._load_yolov8_face()
            
            # 3. Load basic CNN models
            self._load_basic_cnns()
            
            self.models_loaded = True
            load_time = time.time() - start_time
            logger.info(f"✅ Essential models preloaded in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Model preloading failed: {e}")
            self.models_loaded = False
    
    def _load_efficientnet(self):
        """Load EfficientNet model"""
        try:
            from .sophisticated_efficientnet_loader import SophisticatedEfficientNetLoader
            loader = SophisticatedEfficientNetLoader(device=self.device)
            # Use the correct method name
            model = loader.load_efficientnet_model("efficientnet_b0")
            self.models["efficientnet"] = model
            logger.info("✅ EfficientNet cached")
        except Exception as e:
            logger.warning(f"⚠️ EfficientNet loading failed: {e}")
    
    def _load_yolov8_face(self):
        """Load YOLOv8 face detection model"""
        try:
            from ultralytics import YOLO
            # Use the correct model name
            model = YOLO('yolov8n.pt')
            model.to(self.device)
            self.models["yolov8_face"] = model
            logger.info("✅ YOLOv8 face detection cached")
        except Exception as e:
            logger.warning(f"⚠️ YOLOv8 face loading failed: {e}")
    
    def _load_basic_cnns(self):
        """Load basic CNN models"""
        try:
            import torchvision.models as models
            
            # Load ResNet50
            resnet = models.resnet50(pretrained=True)
            resnet.to(self.device)
            resnet.eval()
            self.models["resnet50"] = resnet
            
            logger.info("✅ Basic CNNs cached")
        except Exception as e:
            logger.warning(f"⚠️ Basic CNNs loading failed: {e}")
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get cached model"""
        return self.models.get(model_name)
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if model is loaded"""
        return model_name in self.models
    
    def get_device(self) -> str:
        """Get optimal device"""
        return self.device

# Global instance
global_model_cache = GlobalModelCache()

@lru_cache(maxsize=1)
def get_global_model_cache():
    """Get global model cache instance"""
    return global_model_cache
