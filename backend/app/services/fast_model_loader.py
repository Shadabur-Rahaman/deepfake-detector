"""
Fast Model Loader - Optimized Model Loading System
=================================================

This module provides optimized model loading with:
- Lazy loading (models loaded only when needed)
- Model caching to avoid reloading
- Parallel loading for multiple models
- GPU-direct loading when possible
- Minimal logging for faster startup
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from functools import lru_cache

try:
    import torch
    import torch.nn as nn
    from torchvision import models
except ImportError:
    torch = None
    models = None

logger = logging.getLogger(__name__)

class FastModelLoader:
    """Optimized model loader with caching and lazy loading"""
    
    def __init__(self, device: str = "auto", max_workers: int = 2):
        self.device = self._get_device(device)
        self.max_workers = max_workers
        self.model_cache = {}
        self.loading_locks = {}
        self.model_configs = self._setup_fast_configs()
        
    def _get_device(self, device: str):
        """Get optimal device for loading with CUDA safety"""
        if device == "auto":
            if torch and torch.cuda.is_available():
                try:
                    # Test CUDA with a simple operation to avoid driver errors - create on CPU first
                    test_tensor = torch.tensor([1.0])  # Create on CPU first
                    test_tensor = test_tensor.to("cuda")  # Move to CUDA safely
                    del test_tensor
                    torch.cuda.empty_cache()
                    return torch.device("cuda")
                except Exception as e:
                    error_str = str(e)
                    if "INTERNAL ASSERT FAILED" in error_str:
                        logger.warning(f"CUDA driver error detected, forcing CPU: {e}")
                    else:
                        logger.warning(f"CUDA test failed, falling back to CPU: {e}")
                    return torch.device("cpu")
            return torch.device("cpu")
        return torch.device(device)
    
    def _setup_fast_configs(self):
        """Setup minimal model configurations for fast loading"""
        ml_artifacts = self._find_ml_artifacts()
        
        return {
            # Essential models only
            "efficientnet_b0": {
                "path": os.path.join(ml_artifacts, "efficientnet_b0.pth"),
                "architecture": "efficientnet_b0",
                "weight": 0.8,
                "priority": 1  # High priority
            },
            "custom_finetuned": {
                "path": os.path.join(ml_artifacts, "deepfake_detector_finetuned1.pth"),
                "architecture": "efficientnet_b0",
                "weight": 1.0,
                "priority": 1  # Highest priority
            },
            "resnet50": {
                "path": os.path.join(ml_artifacts, "resnet50.pth"),
                "architecture": "resnet50", 
                "weight": 0.3,
                "priority": 2
            },
            "resnet101": {
                "path": os.path.join(ml_artifacts, "resnet101.pth"),
                "architecture": "resnet101",
                "weight": 0.2,
                "priority": 3
            }
        }
    
    def _find_ml_artifacts(self):
        """Find ml_artifacts directory quickly"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, '../../../ml_artifacts'),
            os.path.join(current_dir, '../../ml_artifacts'),
            os.path.abspath('ml_artifacts')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return os.path.join(current_dir, '../../../ml_artifacts')
    
    @lru_cache(maxsize=1)
    def get_model_lock(self, model_name: str):
        """Get thread lock for model loading"""
        return threading.Lock()
    
    def load_model_fast(self, model_name: str) -> Optional[torch.nn.Module]:
        """Load model with caching and fast loading"""
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        if model_name not in self.model_configs:
            logger.warning(f"Model {model_name} not in configurations")
            return None
        
        # Use thread lock to prevent duplicate loading
        with self.get_model_lock(model_name):
            # Check cache again after acquiring lock
            if model_name in self.model_cache:
                return self.model_cache[model_name]
            
            config = self.model_configs[model_name]
            model_path = config["path"]
            
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found: {model_path}")
                # Try to find alternative paths
                current_dir = os.path.dirname(os.path.abspath(__file__))
                alternative_paths = [
                    os.path.join(current_dir, f'../../../ml_artifacts/{os.path.basename(model_path)}'),
                    os.path.join(current_dir, f'../../ml_artifacts/{os.path.basename(model_path)}'),
                    os.path.join(current_dir, f'../ml_artifacts/{os.path.basename(model_path)}'),
                ]
                
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        logger.info(f"Found model at alternative path: {alt_path}")
                        model_path = alt_path
                        break
                else:
                    logger.error(f"Model file not found in any path: {model_path}")
                    return None
            
            try:
                start_time = time.time()
                logger.info(f"🚀 Fast loading {model_name}...")
                
                # Enhanced loading with CUDA safety
                try:
                    # Always load to CPU first to avoid CUDA driver issues
                    loaded_data = torch.load(model_path, map_location="cpu")
                    
                    if isinstance(loaded_data, torch.nn.Module):
                        model = loaded_data
                    else:
                        # If it's a state dict, create model first
                        model = self._create_model_from_config(config)
                        model.load_state_dict(loaded_data, strict=False)
                    
                    # Only move to device if it's safe and not CUDA
                    if str(self.device) == "cpu":
                        model = model.to(self.device)
                    else:
                        # Test CUDA device before moving model
                        try:
                            test_tensor = torch.tensor([1.0]).to(self.device)
                            del test_tensor
                            model = model.to(self.device)
                        except Exception as device_error:
                            logger.warning(f"CUDA device failed, using CPU: {device_error}")
                            model = model.to("cpu")
                            self.device = torch.device("cpu")
                            
                except Exception as load_error:
                    logger.error(f"Model loading failed: {load_error}")
                    raise load_error
                
                model.eval()
                load_time = time.time() - start_time
                
                # Cache the model
                self.model_cache[model_name] = model
                
                logger.info(f"✅ {model_name} loaded in {load_time:.2f}s")
                return model
                
            except Exception as e:
                logger.error(f"❌ Failed to load {model_name}: {e}")
                logger.debug(f"Model path: {model_path}")
                logger.debug(f"Model config: {config}")
                return None
    
    def _create_model_from_config(self, config: Dict) -> torch.nn.Module:
        """Create model architecture from config"""
        architecture = config["architecture"]
        
        if architecture == "efficientnet_b0":
            model = models.efficientnet_b0(weights=None)
            # Fix classifier for binary classification (1 output for probability)
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(model.classifier[1].in_features, 1)
            )
        elif architecture == "resnet50":
            model = models.resnet50(weights=None)
            model.fc = nn.Linear(model.fc.in_features, 2)
        elif architecture == "resnet101":
            model = models.resnet101(weights=None)
            model.fc = nn.Linear(model.fc.in_features, 2)
        else:
            # Default to EfficientNet-B0
            model = models.efficientnet_b0(weights=None)
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(model.classifier[1].in_features, 1)
            )
        
        return model
    
    async def load_models_parallel(self, model_names: List[str]) -> Dict[str, torch.nn.Module]:
        """Load multiple models in parallel"""
        results = {}
        
        def load_single_model(model_name):
            return model_name, self.load_model_fast(model_name)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all loading tasks
            future_to_model = {
                executor.submit(load_single_model, model_name): model_name 
                for model_name in model_names
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    name, model = future.result()
                    results[name] = model
                except Exception as e:
                    logger.error(f"Failed to load {model_name}: {e}")
                    results[model_name] = None
        
        return results
    
    def get_essential_models(self) -> Dict[str, torch.nn.Module]:
        """Get only essential models for fast startup"""
        essential_models = {}
        
        # Load only high priority models
        for model_name, config in self.model_configs.items():
            if config.get("priority", 999) <= 1:  # Only priority 1 models
                model = self.load_model_fast(model_name)
                if model:
                    essential_models[model_name] = model
        
        return essential_models
    
    def warmup_model(self, model_name: str):
        """Warm up model with dummy inference"""
        model = self.load_model_fast(model_name)
        if model and torch:
            try:
                dummy_input = torch.randn(1, 3, 224, 224).to(self.device)
                with torch.no_grad():
                    _ = model(dummy_input)
                logger.debug(f"🔥 {model_name} warmed up")
            except Exception as e:
                logger.warning(f"Warmup failed for {model_name}: {e}")
    
    def clear_cache(self):
        """Clear model cache to free memory"""
        self.model_cache.clear()
        logger.info("🧹 Model cache cleared")

# Global fast loader instance
_fast_loader = None

def get_fast_loader() -> FastModelLoader:
    """Get global fast loader instance"""
    global _fast_loader
    if _fast_loader is None:
        _fast_loader = FastModelLoader()
    return _fast_loader

def load_essential_models_fast() -> Dict[str, torch.nn.Module]:
    """Load only essential models for fast startup"""
    loader = get_fast_loader()
    return loader.get_essential_models()

def load_model_fast(model_name: str) -> Optional[torch.nn.Module]:
    """Load single model quickly"""
    loader = get_fast_loader()
    return loader.load_model_fast(model_name)
