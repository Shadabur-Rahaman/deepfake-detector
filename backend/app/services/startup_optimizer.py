"""
Startup Optimizer - Fast Model Pre-loading
==========================================

This module optimizes startup time by:
- Pre-loading only essential models
- Using background loading for non-essential models
- Providing fast fallbacks
- Minimizing logging during startup
"""

import os
import time
import logging
import asyncio
from typing import Dict, Optional
import threading

logger = logging.getLogger(__name__)

class StartupOptimizer:
    """Optimizes startup performance by pre-loading essential models"""
    
    def __init__(self):
        self.essential_models_loaded = False
        self.background_loading = False
        self.startup_time = 0
        
    def fast_startup(self) -> Dict[str, bool]:
        """Perform fast startup with essential models only"""
        start_time = time.time()
        
        try:
            from .fast_model_loader import get_fast_loader
            
            # Load only essential models
            loader = get_fast_loader()
            essential_models = loader.get_essential_models()
            
            self.essential_models_loaded = True
            self.startup_time = time.time() - start_time
            
            logger.info(f"🚀 Fast startup completed in {self.startup_time:.2f}s with {len(essential_models)} models")
            
            # Start background loading for other models
            self._start_background_loading()
            
            return {
                "fast_startup": True,
                "essential_models": len(essential_models),
                "startup_time": self.startup_time,
                "background_loading": True
            }
            
        except Exception as e:
            logger.error(f"Fast startup failed: {e}")
            return {
                "fast_startup": False,
                "error": str(e),
                "fallback_needed": True
            }
    
    def _start_background_loading(self):
        """Start background loading of non-essential models"""
        def background_load():
            try:
                logger.info("🔄 Starting background model loading...")
                from .fast_model_loader import get_fast_loader
                
                loader = get_fast_loader()
                
                # Load additional models in background
                additional_models = ["resnet50", "resnet101"]
                for model_name in additional_models:
                    try:
                        model = loader.load_model_fast(model_name)
                        if model:
                            logger.debug(f"✅ Background loaded: {model_name}")
                    except Exception as e:
                        logger.debug(f"⚠️ Background loading failed for {model_name}: {e}")
                
                logger.info("✅ Background model loading completed")
                self.background_loading = True
                
            except Exception as e:
                logger.warning(f"Background loading failed: {e}")
        
        # Start background thread
        thread = threading.Thread(target=background_load, daemon=True)
        thread.start()
    
    def get_startup_status(self) -> Dict[str, any]:
        """Get current startup status"""
        return {
            "essential_models_loaded": self.essential_models_loaded,
            "background_loading": self.background_loading,
            "startup_time": self.startup_time,
            "ready_for_detection": self.essential_models_loaded
        }

# Global startup optimizer
_startup_optimizer = None

def get_startup_optimizer() -> StartupOptimizer:
    """Get global startup optimizer instance"""
    global _startup_optimizer
    if _startup_optimizer is None:
        _startup_optimizer = StartupOptimizer()
    return _startup_optimizer

def fast_startup() -> Dict[str, bool]:
    """Perform fast startup"""
    optimizer = get_startup_optimizer()
    return optimizer.fast_startup()

def get_startup_status() -> Dict[str, any]:
    """Get startup status"""
    optimizer = get_startup_optimizer()
    return optimizer.get_startup_status()

# Environment variable optimizations
def apply_startup_optimizations():
    """Apply environment variable optimizations for faster startup"""
    
    # Reduce logging during startup
    os.environ["MODEL_LOADING_VERBOSE"] = "false"
    
    # Enable minimal startup if requested
    if os.getenv("FAST_STARTUP", "false").lower() == "true":
        os.environ["MINIMAL_STARTUP"] = "1"
        os.environ["DISABLE_ENSEMBLE_LOADING"] = "1"
        
    # Optimize PyTorch for faster loading
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
    
    logger.info("🚀 Startup optimizations applied")
