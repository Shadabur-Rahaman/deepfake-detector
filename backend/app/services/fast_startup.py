#!/usr/bin/env python3
"""
Fast Startup Mode - Load only essential models for quick startup
"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from .lazy_model_loader import lazy_loader

logger = logging.getLogger(__name__)

class FastStartupMode:
    """
    Fast startup mode that loads only essential models
    """
    
    def __init__(self):
        self.essential_models = [
            "yolo_face_detector",
            "basic_deepfake_detector", 
            "efficientnet_b0"
        ]
        
        self.optional_models = [
            "ultra_ensemble_25_models",
            "production_advanced_detector",
            "neural_texture_analyzer",
            "vision_transformer_models",
            "clip_models"
        ]
    
    async def initialize_essential_only(self) -> Dict[str, Any]:
        """Initialize only essential models for fast startup"""
        logger.info("🚀 Starting FAST STARTUP MODE - Loading essential models only")
        start_time = time.time()
        
        results = {
            'startup_time': start_time,
            'mode': 'fast',
            'models_loaded': {},
            'models_skipped': [],
            'total_time': 0
        }
        
        try:
            # Load only essential models
            essential_tasks = []
            for model_name in self.essential_models:
                if model_name in lazy_loader._model_loaders:
                    essential_tasks.append(self._load_essential_model(model_name, results))
            
            if essential_tasks:
                await asyncio.gather(*essential_tasks, return_exceptions=True)
            
            # Mark optional models as skipped
            results['models_skipped'] = self.optional_models.copy()
            
            results['total_time'] = time.time() - start_time
            logger.info(f"✅ Fast startup completed in {results['total_time']:.2f}s")
            logger.info(f"📊 Loaded {len(results['models_loaded'])} essential models")
            logger.info(f"⏭️  Skipped {len(results['models_skipped'])} optional models")
            
        except Exception as e:
            logger.error(f"Fast startup failed: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _load_essential_model(self, model_name: str, results: Dict[str, Any]):
        """Load an essential model"""
        try:
            model = await lazy_loader.get_model(model_name)
            results['models_loaded'][model_name] = {
                'status': 'loaded',
                'type': 'essential'
            }
            logger.info(f"✅ Essential model loaded: {model_name}")
        except Exception as e:
            logger.warning(f"⚠️  Essential model failed: {model_name} - {e}")
            results['models_loaded'][model_name] = {
                'status': 'failed',
                'error': str(e)
            }
    
    async def load_optional_model_on_demand(self, model_name: str) -> Any:
        """Load an optional model when actually needed"""
        if model_name in self.optional_models:
            logger.info(f"🔄 Loading optional model on demand: {model_name}")
            return await lazy_loader.get_model(model_name)
        else:
            raise ValueError(f"Model {model_name} is not in optional models list")

# Global fast startup instance
fast_startup = FastStartupMode()

