#!/usr/bin/env python3
"""
Unified Model Loader - Fixes duplicate registrations and ensures clean model loading
"""

import asyncio
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, Set, List
from functools import lru_cache
import gc

logger = logging.getLogger(__name__)

class UnifiedModelLoader:
    """
    Unified model loader with singleton pattern to prevent duplicate registrations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UnifiedModelLoader, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._loaded_models: Dict[str, Any] = {}
        self._loading_promises: Dict[str, asyncio.Task] = {}
        self._model_loaders: Dict[str, Callable] = {}
        
        # Enhanced features
        self._model_priorities: Dict[str, int] = {}
        self._loading_queue: List[str] = []
        self._registered_models: Set[str] = set()  # Track registered models
        self._warmup_cache: Dict[str, Any] = {}
        self._loading_lock = threading.Lock()
        self._background_loading_active = False
        
        self._initialized = True
    
    def register_model_loader(self, model_name: str, loader_func: Callable, priority: int = 50) -> bool:
        """Register a model loader function with priority - prevents duplicates"""
        with self._loading_lock:
            # Check for duplicates using singleton pattern
            if model_name in self._registered_models:
                logger.debug(f"Model {model_name} already registered, skipping duplicate")
                return True  # Return True since model is already registered
            
            self._registered_models.add(model_name)
            self._model_loaders[model_name] = loader_func
            self._model_priorities[model_name] = priority
            
            # Add to priority queue (avoid duplicates)
            if model_name not in self._loading_queue:
                self._loading_queue.append(model_name)
                self._loading_queue.sort(key=lambda x: self._model_priorities.get(x, 99))
            
            logger.info(f"✅ Registered lazy loader for {model_name} (priority: {priority})")
            return True
    
    async def get_model(self, model_name: str) -> Any:
        """Get a model, loading it if not already loaded"""
        if model_name in self._loaded_models:
            return self._loaded_models[model_name]
        
        if model_name in self._loading_promises:
            # Model is currently loading, wait for it
            return await self._loading_promises[model_name]
        
        if model_name not in self._model_loaders:
            raise ValueError(f"No loader registered for model: {model_name}")
        
        # Start loading the model
        logger.info(f"Lazy loading model: {model_name}")
        start_time = time.time()
        
        loading_task = asyncio.create_task(self._load_model(model_name))
        self._loading_promises[model_name] = loading_task
        
        try:
            model = await loading_task
            load_time = time.time() - start_time
            logger.info(f"Model {model_name} loaded in {load_time:.2f}s")
            return model
        finally:
            # Clean up the promise
            if model_name in self._loading_promises:
                del self._loading_promises[model_name]
    
    async def _load_model(self, model_name: str) -> Any:
        """Actually load the model"""
        loader_func = self._model_loaders[model_name]
        model = await loader_func()
        self._loaded_models[model_name] = model
        return model
    
    def preload_critical_models(self, max_models: int = 7) -> asyncio.Task:
        """Preload only the most critical models (default: 7)"""
        async def preload():
            # Get top priority models
            critical_models = [model for model in self._loading_queue[:max_models] 
                             if model in self._model_loaders]
            
            if not critical_models:
                logger.info("No background models to load")
                return
            
            logger.info(f"🚀 Preloading {len(critical_models)} critical models: {critical_models}")
            
            tasks = []
            for model_name in critical_models:
                tasks.append(self.get_model(model_name))
            
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful = sum(1 for r in results if not isinstance(r, Exception))
                logger.info(f"✅ Preloaded {successful}/{len(critical_models)} critical models")
            except Exception as e:
                logger.error(f"❌ Critical model preloading failed: {e}")
        
        return asyncio.create_task(preload())
    
    def start_background_loading(self):
        """Start background loading of non-critical models"""
        if self._background_loading_active:
            return
        
        self._background_loading_active = True
        
        async def background_load():
            # Load remaining models in background
            remaining_models = [model for model in self._loading_queue[7:] 
                              if model in self._model_loaders and model not in self._loaded_models]
            
            if not remaining_models:
                logger.info("No background models to load")
                self._background_loading_active = False
                return
            
            logger.info(f"🔄 Background loading {len(remaining_models)} models...")
            
            for model_name in remaining_models:
                try:
                    await self.get_model(model_name)
                    await asyncio.sleep(0.1)  # Small delay to prevent overload
                except Exception as e:
                    logger.warning(f"Background loading failed for {model_name}: {e}")
            
            logger.info("✅ Background model loading completed")
            self._background_loading_active = False
        
        asyncio.create_task(background_load())
    
    def warmup_model(self, model_name: str, dummy_input: Any = None):
        """Warm up a model with dummy inference"""
        if model_name not in self._loaded_models:
            logger.warning(f"Cannot warmup {model_name}: not loaded")
            return
        
        try:
            model = self._loaded_models[model_name]
            
            # Create dummy input if not provided
            if dummy_input is None:
                import torch
                dummy_input = torch.randn(1, 3, 224, 224)
            
            # Warmup inference
            with torch.no_grad():
                _ = model(dummy_input)
            
            self._warmup_cache[model_name] = time.time()
            logger.info(f"🔥 Model {model_name} warmed up")
            
        except Exception as e:
            logger.warning(f"Warmup failed for {model_name}: {e}")
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory"""
        with self._loading_lock:
            if model_name not in self._loaded_models:
                return False
            
            # Remove from loaded models
            del self._loaded_models[model_name]
            
            # Clean up warmup cache
            if model_name in self._warmup_cache:
                del self._warmup_cache[model_name]
            
            # Force garbage collection
            gc.collect()
            
            logger.info(f"🗑️ Unloaded model: {model_name}")
            return True
    
    def get_loading_status(self) -> Dict[str, Any]:
        """Get comprehensive loading status"""
        return {
            'total_registered': len(self._model_loaders),
            'loaded_models': len(self._loaded_models),
            'pending_models': len(self._loading_queue) - len(self._loaded_models),
            'background_loading': self._background_loading_active,
            'loaded_model_names': list(self._loaded_models.keys()),
            'priority_queue': self._loading_queue,
            'warmup_cache_size': len(self._warmup_cache)
        }
    
    def register_critical_models(self):
        """Register critical models with proper loaders"""
        # Critical models (1-7) - only register if not already registered
        critical_models = [
            ('yolo_face', 1),
            ('efficientnet_b0', 2),
            ('efficientnet_b7', 3),
            ('resnet50', 4),
            ('densenet121', 5),
            ('inception_v3', 6),
            ('vgg16', 7)
        ]
        
        registered_count = 0
        for model_name, priority in critical_models:
            if model_name not in self._registered_models:
                # Create actual loader based on model type
                loader_func = self._create_actual_loader(model_name)
                if self.register_model_loader(model_name, loader_func, priority):
                    registered_count += 1
        
        logger.info(f"✅ {registered_count} critical models registered with unified loader")
    
    def _create_actual_loader(self, model_name: str):
        """Create actual model loader based on model name"""
        async def loader():
            try:
                if model_name == 'yolo_face':
                    return await self._load_yolo_model()
                elif model_name.startswith('efficientnet'):
                    return await self._load_efficientnet_model(model_name)
                elif model_name in ['resnet50', 'densenet121', 'inception_v3', 'vgg16']:
                    return await self._load_torchvision_model(model_name)
                else:
                    logger.warning(f"No loader implemented for {model_name}")
                    return None
            except Exception as e:
                logger.error(f"Failed to load {model_name}: {e}")
                return None
        return loader
    
    async def _load_yolo_model(self):
        """Load YOLO face detection model"""
        try:
            from ultralytics import YOLO
            model = YOLO('yolov8n-face.pt')  # or appropriate face detection model
            return model
        except Exception as e:
            logger.error(f"YOLO loader failed: {e}")
            return None
    
    async def _load_efficientnet_model(self, model_name: str):
        """Load EfficientNet model"""
        try:
            import timm
            if model_name == 'efficientnet_b0':
                model = timm.create_model('efficientnet_b0', pretrained=True)
                # Load custom weights if available
                custom_path = "models/efficientnet_b0.pth"
                if os.path.exists(custom_path):
                    import torch
                    custom_weights = torch.load(custom_path, map_location='cpu')
                    model.load_state_dict(custom_weights)
                return model
            elif model_name == 'efficientnet_b7':
                model = timm.create_model('efficientnet_b7', pretrained=True)
                return model
        except Exception as e:
            logger.error(f"EfficientNet loader failed for {model_name}: {e}")
            return None
    
    async def _load_torchvision_model(self, model_name: str):
        """Load torchvision model"""
        try:
            import torch
            from torchvision import models
            
            if model_name == 'resnet50':
                model = models.resnet50(pretrained=True)
            elif model_name == 'densenet121':
                model = models.densenet121(pretrained=True)
            elif model_name == 'inception_v3':
                model = models.inception_v3(pretrained=True)
            elif model_name == 'vgg16':
                model = models.vgg16(pretrained=True)
            else:
                return None
            
            return model
        except Exception as e:
            logger.error(f"Torchvision loader failed for {model_name}: {e}")
            return None

# Global unified model loader instance (singleton)
unified_model_loader = UnifiedModelLoader()

# Backward compatibility
lazy_loader = unified_model_loader
