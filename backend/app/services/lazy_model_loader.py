#!/usr/bin/env python3
"""
Lazy Model Loader - Load models only when needed to reduce startup time
"""

import asyncio
import logging
import time
import threading
from typing import Dict, Any, Optional, Callable, Set, List
from functools import lru_cache
import gc

logger = logging.getLogger(__name__)

class LazyModelLoader:
    """
    Enhanced lazy loading system for AI models with deduplication and priority queue
    """
    
    def __init__(self):
        self._loaded_models: Dict[str, Any] = {}
        self._loading_promises: Dict[str, asyncio.Task] = {}
        self._model_loaders: Dict[str, Callable] = {}
        
        # Enhanced features
        self._model_priorities: Dict[str, int] = {}
        self._loading_queue: List[str] = []
        self._duplicate_check: Set[str] = set()
        self._warmup_cache: Dict[str, Any] = {}
        self._loading_lock = threading.Lock()
        self._background_loading_active = False
        
    def register_model_loader(self, model_name: str, loader_func: Callable, priority: int = 50):
        """Register a model loader function with priority - prevents duplicates"""
        with self._loading_lock:
            # Check for duplicates using singleton pattern
            if model_name in self._registered_models:
                logger.warning(f"⚠️ Duplicate model registration detected: {model_name}")
                return False
            
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
                logger.warning("No critical models to preload")
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

    def register_all_23_models(self):
        """Register all 23 deepfake detection models with proper priorities"""
        # Critical models (1-7)
        critical_models = [
            ('yolo_face', 1),
            ('efficientnet_b0', 2),
            ('efficientnet_b7', 3),
            ('resnet50', 4),
            ('densenet121', 5),
            ('inception_v3', 6),
            ('vgg16', 7)
        ]
        
        # Important models (8-15)
        important_models = [
            ('mesonet', 8),
            ('capsule_net', 9),
            ('f3net', 10),
            ('ffd', 11),
            ('srm', 12),
            ('recce', 13),
            ('spsl', 14),
            ('vision_transformer', 15)
        ]
        
        # Optional models (16-23)
        optional_models = [
            ('swin_transformer', 16),
            ('beit', 17),
            ('convnext', 18),
            ('efficientnetv2', 19),
            ('regnet', 20),
            ('resnext', 21),
            ('wide_resnet', 22),
            ('densenet201', 23)
        ]
        
        all_models = critical_models + important_models + optional_models
        
        logger.info(f"📋 Registering {len(all_models)} models for lazy loading")
        
        # Register with placeholder loaders (to be replaced with actual loaders)
        for model_name, priority in all_models:
            placeholder_loader = lambda name=model_name: self._placeholder_loader(name)
            self.register_model_loader(model_name, placeholder_loader, priority)
        
        logger.info("✅ All 23 models registered for lazy loading")

    def _placeholder_loader(self, model_name: str):
        """Placeholder loader - to be replaced with actual model loaders"""
        logger.warning(f"⚠️ Using placeholder loader for {model_name}")
        return None

# Global lazy loader instance
lazy_loader = LazyModelLoader()

