"""
Memory Optimized Loader - GPU Memory Management
==============================================

This module optimizes GPU memory usage by:
- Loading models one at a time
- Using CPU fallback for large models
- Implementing memory cleanup
- Prioritizing essential models
"""

import os
import gc
import time
import logging
import torch
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class MemoryOptimizedLoader:
    """Memory-optimized model loader for limited GPU memory"""
    
    def __init__(self, device: str = "auto", max_gpu_memory_gb: float = 3.0):
        self.device = self._get_device(device)
        self.max_gpu_memory_gb = max_gpu_memory_gb
        self.gpu_memory_threshold = max_gpu_memory_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.loaded_models = {}
        self.model_memory_usage = {}
        
    def _get_device(self, device: str):
        """Get optimal device with memory awareness"""
        if device == "auto":
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory
                if gpu_memory > self.gpu_memory_threshold:
                    return torch.device("cuda")
                else:
                    logger.warning(f"GPU memory ({gpu_memory/1024**3:.1f}GB) below threshold, using CPU")
                    return torch.device("cpu")
            return torch.device("cpu")
        return torch.device(device)
    
    def get_gpu_memory_usage(self) -> Dict[str, float]:
        """Get current GPU memory usage"""
        if not torch.cuda.is_available():
            return {"allocated": 0, "reserved": 0, "free": 0}
        
        allocated = torch.cuda.memory_allocated() / 1024**3  # GB
        reserved = torch.cuda.memory_reserved() / 1024**3    # GB
        total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        free = total - allocated
        
        return {
            "allocated": allocated,
            "reserved": reserved,
            "free": free,
            "total": total
        }
    
    def should_use_cpu(self, model_size_estimate: float = 0.5) -> bool:
        """Check if model should be loaded on CPU due to memory constraints"""
        if not torch.cuda.is_available():
            return True
        
        memory_usage = self.get_gpu_memory_usage()
        estimated_usage = model_size_estimate + memory_usage["allocated"]
        
        return estimated_usage > self.max_gpu_memory_gb
    
    @contextmanager
    def memory_cleanup(self):
        """Context manager for memory cleanup"""
        try:
            yield
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
    
    def load_model_with_memory_management(self, model_name: str, model_path: str, 
                                        model_size_estimate: float = 0.5) -> Optional[torch.nn.Module]:
        """Load model with memory management"""
        
        # Check if already loaded
        if model_name in self.loaded_models:
            return self.loaded_models[model_name]
        
        # Determine device based on memory
        use_cpu = self.should_use_cpu(model_size_estimate)
        device = torch.device("cpu") if use_cpu else self.device
        
        logger.info(f"🔄 Loading {model_name} on {device} (size estimate: {model_size_estimate:.1f}GB)")
        
        with self.memory_cleanup():
            try:
                start_time = time.time()
                
                # Load model
                if use_cpu:
                    model = torch.load(model_path, map_location="cpu", weights_only=True)
                else:
                    try:
                        model = torch.load(model_path, map_location=self.device, weights_only=True)
                    except torch.cuda.OutOfMemoryError:
                        logger.warning(f"⚠️ GPU OOM for {model_name}, falling back to CPU")
                        model = torch.load(model_path, map_location="cpu", weights_only=True)
                        device = torch.device("cpu")
                
                # Handle different model formats
                if isinstance(model, dict):
                    # It's a state dict, create model architecture
                    model = self._create_model_architecture(model_name)
                    model.load_state_dict(model)
                
                model = model.to(device)
                model.eval()
                
                load_time = time.time() - start_time
                
                # Track memory usage
                if torch.cuda.is_available() and device.type == "cuda":
                    memory_usage = self.get_gpu_memory_usage()
                    self.model_memory_usage[model_name] = memory_usage["allocated"]
                
                self.loaded_models[model_name] = model
                
                logger.info(f"✅ {model_name} loaded on {device} in {load_time:.2f}s")
                return model
                
            except Exception as e:
                logger.error(f"❌ Failed to load {model_name}: {e}")
                return None
    
    def _create_model_architecture(self, model_name: str) -> torch.nn.Module:
        """Create model architecture based on name"""
        from torchvision import models
        import torch.nn as nn
        
        if "efficientnet" in model_name.lower():
            model = models.efficientnet_b0(weights=None)
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(model.classifier[1].in_features, 2)
            )
        elif "resnet" in model_name.lower():
            if "101" in model_name:
                model = models.resnet101(weights=None)
            else:
                model = models.resnet50(weights=None)
            model.fc = nn.Linear(model.fc.in_features, 2)
        else:
            # Default to EfficientNet
            model = models.efficientnet_b0(weights=None)
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(model.classifier[1].in_features, 2)
            )
        
        return model
    
    def unload_model(self, model_name: str):
        """Unload model to free memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            if model_name in self.model_memory_usage:
                del self.model_memory_usage[model_name]
            
            with self.memory_cleanup():
                logger.info(f"🗑️ Unloaded {model_name}")
    
    def load_essential_models_only(self) -> Dict[str, torch.nn.Module]:
        """Load only essential models to avoid memory issues"""
        essential_models = {}
        
        # Essential model configurations
        ml_artifacts = self._find_ml_artifacts()
        essential_configs = {
            "custom_finetuned": {
                "path": os.path.join(ml_artifacts, "deepfake_detector_finetuned1.pth"),
                "size": 0.3,  # GB
                "priority": 1
            },
            "efficientnet_b0": {
                "path": os.path.join(ml_artifacts, "efficientnet_b0.pth"),
                "size": 0.2,  # GB
                "priority": 2
            }
        }
        
        # Sort by priority
        sorted_configs = sorted(essential_configs.items(), key=lambda x: x[1]["priority"])
        
        for model_name, config in sorted_configs:
            if os.path.exists(config["path"]):
                model = self.load_model_with_memory_management(
                    model_name, 
                    config["path"], 
                    config["size"]
                )
                if model:
                    essential_models[model_name] = model
                    
                    # Check if we should stop loading more models
                    memory_usage = self.get_gpu_memory_usage()
                    if memory_usage["allocated"] > self.max_gpu_memory_gb * 0.8:  # 80% threshold
                        logger.warning(f"⚠️ Memory usage at {memory_usage['allocated']:.1f}GB, stopping model loading")
                        break
            else:
                logger.warning(f"⚠️ Model file not found: {config['path']}")
        
        logger.info(f"🎯 Loaded {len(essential_models)} essential models")
        return essential_models
    
    def _find_ml_artifacts(self):
        """Find ml_artifacts directory"""
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
    
    def get_memory_report(self) -> Dict:
        """Get detailed memory usage report"""
        memory_usage = self.get_gpu_memory_usage()
        
        return {
            "gpu_memory": memory_usage,
            "loaded_models": list(self.loaded_models.keys()),
            "model_count": len(self.loaded_models),
            "memory_optimized": True,
            "device": str(self.device)
        }

# Global memory-optimized loader
_memory_loader = None

def get_memory_loader() -> MemoryOptimizedLoader:
    """Get global memory-optimized loader"""
    global _memory_loader
    if _memory_loader is None:
        _memory_loader = MemoryOptimizedLoader()
    return _memory_loader

def load_essential_models_memory_optimized() -> Dict[str, torch.nn.Module]:
    """Load only essential models with memory optimization"""
    loader = get_memory_loader()
    return loader.load_essential_models_only()

def get_memory_report() -> Dict:
    """Get memory usage report"""
    loader = get_memory_loader()
    return loader.get_memory_report()
