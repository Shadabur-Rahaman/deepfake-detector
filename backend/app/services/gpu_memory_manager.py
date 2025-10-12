"""
GPU Memory Manager - CUDA Memory Optimization
============================================

This module provides GPU memory management utilities to prevent CUDA out of memory
errors and optimize memory usage for the deepfake detection ensemble.

Key features:
- Memory monitoring and cleanup
- Model loading/unloading management
- Batch size optimization based on available memory
- Automatic fallback to CPU when GPU memory is insufficient
"""

import logging
import torch
import gc
import time
from typing import Dict, Optional, Tuple
import psutil

logger = logging.getLogger(__name__)

class GPUMemoryManager:
    """Enhanced GPU memory management for deepfake detection with smart allocation"""
    
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.memory_threshold = 0.85  # 85% memory usage threshold
        self.min_free_memory = 1024 * 1024 * 1024  # 1GB minimum free memory
        
        # Model priority system for 23 models
        self.model_priorities = {
            'yolo_face': 1,  # Critical - face detection
            'efficientnet_b0': 2,  # Critical - primary detector
            'efficientnet_b7': 3,  # Critical - ensemble
            'resnet50': 4,  # Critical - ensemble
            'densenet121': 5,  # Critical - ensemble
            'inception_v3': 6,  # Important - ensemble
            'vgg16': 7,  # Important - ensemble
            'mesonet': 8,  # Important - specialized
            'capsule_net': 9,  # Optional - specialized
            'f3net': 10,  # Optional - specialized
            'ffd': 11,  # Optional - specialized
            'srm': 12,  # Optional - specialized
            'recce': 13,  # Optional - specialized
            'spsl': 14,  # Optional - specialized
            'vision_transformer': 15,  # Optional - transformer
            'swin_transformer': 16,  # Optional - transformer
            'beit': 17,  # Optional - transformer
            'convnext': 18,  # Optional - modern
            'efficientnetv2': 19,  # Optional - modern
            'regnet': 20,  # Optional - modern
            'resnext': 21,  # Optional - ensemble
            'wide_resnet': 22,  # Optional - ensemble
            'densenet201': 23,  # Optional - ensemble
        }
        
        # Model memory profiling
        self.model_memory_profiles = {}
        self.loaded_models = {}
        self.cpu_fallback_models = set()
        
    def get_memory_info(self) -> Dict[str, float]:
        """Get current GPU memory information"""
        if not torch.cuda.is_available():
            return {
                'total': 0.0,
                'allocated': 0.0,
                'free': 0.0,
                'usage_percent': 0.0,
                'available': False
            }
        
        try:
            total_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated(0)
            free_memory = total_memory - allocated_memory
            usage_percent = (allocated_memory / total_memory) * 100
            
            return {
                'total': total_memory / (1024**3),  # Convert to GB
                'allocated': allocated_memory / (1024**3),
                'free': free_memory / (1024**3),
                'usage_percent': usage_percent,
                'available': True
            }
        except Exception as e:
            logger.error(f"Failed to get GPU memory info: {e}")
            return {
                'total': 0.0,
                'allocated': 0.0,
                'free': 0.0,
                'usage_percent': 0.0,
                'available': False
            }
    
    def is_memory_available(self, required_memory_gb: float = 1.0) -> bool:
        """Check if enough GPU memory is available"""
        if not torch.cuda.is_available():
            return False
        
        memory_info = self.get_memory_info()
        if not memory_info['available']:
            return False
        
        free_memory_gb = memory_info['free']
        usage_percent = memory_info['usage_percent']
        
        # Check if we have enough free memory and are under threshold
        return (free_memory_gb >= required_memory_gb and 
                usage_percent < (self.memory_threshold * 100))
    
    def cleanup_memory(self):
        """Clean up GPU memory"""
        if torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                gc.collect()
                logger.debug("✅ GPU memory cleaned up")
            except Exception as e:
                logger.warning(f"GPU memory cleanup failed: {e}")
    
    def get_optimal_batch_size(self, base_batch_size: int = 4) -> int:
        """Calculate optimal batch size based on available memory"""
        if not torch.cuda.is_available():
            return base_batch_size
        
        memory_info = self.get_memory_info()
        if not memory_info['available']:
            return base_batch_size
        
        free_memory_gb = memory_info['free']
        usage_percent = memory_info['usage_percent']
        
        # Adjust batch size based on available memory
        if usage_percent > 80:  # High memory usage
            return max(1, base_batch_size // 4)
        elif usage_percent > 60:  # Medium memory usage
            return max(1, base_batch_size // 2)
        elif free_memory_gb < 2.0:  # Low free memory
            return max(1, base_batch_size // 2)
        else:
            return base_batch_size
    
    def should_use_cpu_fallback(self) -> bool:
        """Determine if we should fallback to CPU processing"""
        if not torch.cuda.is_available():
            return True
        
        memory_info = self.get_memory_info()
        if not memory_info['available']:
            return True
        
        # Fallback to CPU if memory usage is too high
        return memory_info['usage_percent'] > (self.memory_threshold * 100)
    
    def log_memory_status(self, context: str = ""):
        """Log current memory status"""
        memory_info = self.get_memory_info()
        if memory_info['available']:
            logger.info(f"🔍 GPU Memory Status {context}:")
            logger.info(f"   📊 Total: {memory_info['total']:.1f} GB")
            logger.info(f"   💾 Allocated: {memory_info['allocated']:.1f} GB")
            logger.info(f"   🆓 Free: {memory_info['free']:.1f} GB")
            logger.info(f"   📈 Usage: {memory_info['usage_percent']:.1f}%")
        else:
            logger.info(f"🔍 GPU Memory: Not available {context}")

    def get_model_priority(self, model_name: str) -> int:
        """Get priority of a model (lower number = higher priority)"""
        return self.model_priorities.get(model_name, 99)  # Default to low priority

    def should_load_on_gpu(self, model_name: str, estimated_memory_gb: float = 0.5) -> bool:
        """Determine if a model should be loaded on GPU based on priority and memory"""
        if not torch.cuda.is_available():
            return False
        
        priority = self.get_model_priority(model_name)
        memory_info = self.get_memory_info()
        
        if not memory_info['available']:
            return False
        
        # Critical models (priority 1-5) always try GPU first
        if priority <= 5:
            return True
        
        # Important models (priority 6-10) try GPU if memory available
        if priority <= 10:
            return memory_info['usage_percent'] < 70 and memory_info['free'] > estimated_memory_gb
        
        # Optional models (priority 11+) use GPU only if plenty of memory
        return memory_info['usage_percent'] < 50 and memory_info['free'] > estimated_memory_gb * 2

    def register_model_memory_usage(self, model_name: str, memory_usage_gb: float, device: str):
        """Register memory usage for a model"""
        self.model_memory_profiles[model_name] = {
            'memory_gb': memory_usage_gb,
            'device': device,
            'timestamp': time.time()
        }
        
        if device == 'cuda':
            self.loaded_models[model_name] = True
        else:
            self.cpu_fallback_models.add(model_name)
        
        logger.info(f"📊 Model {model_name}: {memory_usage_gb:.2f}GB on {device}")

    def get_optimal_device_for_model(self, model_name: str, estimated_memory_gb: float = 0.5) -> str:
        """Get optimal device (cuda/cpu) for a model based on priority and memory"""
        if self.should_load_on_gpu(model_name, estimated_memory_gb):
            return "cuda:0"
        else:
            return "cpu"

    def unload_low_priority_models(self, required_memory_gb: float) -> int:
        """Unload low priority models to free memory"""
        if not torch.cuda.is_available():
            return 0
        
        unloaded_count = 0
        memory_freed = 0
        
        # Sort models by priority (highest priority numbers = lowest priority)
        sorted_models = sorted(self.model_memory_profiles.items(), 
                             key=lambda x: self.get_model_priority(x[0]), reverse=True)
        
        for model_name, profile in sorted_models:
            if model_name in self.loaded_models and memory_freed < required_memory_gb:
                # Unload the model
                memory_freed += profile['memory_gb']
                unloaded_count += 1
                
                # Move to CPU fallback
                self.cpu_fallback_models.add(model_name)
                if model_name in self.loaded_models:
                    del self.loaded_models[model_name]
                
                logger.info(f"🔄 Unloaded {model_name} to free {profile['memory_gb']:.2f}GB")
        
        if unloaded_count > 0:
            torch.cuda.empty_cache()
            gc.collect()
            logger.info(f"✅ Unloaded {unloaded_count} models, freed {memory_freed:.2f}GB")
        
        return unloaded_count

    def get_loading_strategy(self) -> Dict[str, str]:
        """Get loading strategy for all 23 models based on current memory"""
        memory_info = self.get_memory_info()
        strategy = {}
        
        # Sort models by priority
        sorted_models = sorted(self.model_priorities.items(), key=lambda x: x[1])
        
        for model_name, priority in sorted_models:
            if priority <= 5:  # Critical models
                strategy[model_name] = "gpu"
            elif priority <= 10:  # Important models
                strategy[model_name] = "gpu" if memory_info['usage_percent'] < 70 else "cpu"
            else:  # Optional models
                strategy[model_name] = "cpu"  # Load on CPU by default, can be moved to GPU later
        
        return strategy

    def get_memory_usage_summary(self) -> Dict[str, any]:
        """Get comprehensive memory usage summary"""
        memory_info = self.get_memory_info()
        
        gpu_models = len(self.loaded_models)
        cpu_models = len(self.cpu_fallback_models)
        total_memory_used = sum(profile['memory_gb'] for profile in self.model_memory_profiles.values())
        
        return {
            'gpu_available': memory_info['available'],
            'gpu_usage_percent': memory_info['usage_percent'],
            'gpu_free_gb': memory_info['free'],
            'models_on_gpu': gpu_models,
            'models_on_cpu': cpu_models,
            'total_models': gpu_models + cpu_models,
            'total_memory_used_gb': total_memory_used,
            'loading_strategy': self.get_loading_strategy()
        }


# Global instance
gpu_memory_manager = GPUMemoryManager()

def get_memory_manager() -> GPUMemoryManager:
    """Get the global GPU memory manager instance"""
    return gpu_memory_manager

def cleanup_gpu_memory():
    """Convenience function to clean up GPU memory"""
    gpu_memory_manager.cleanup_memory()

def is_gpu_memory_available(required_memory_gb: float = 1.0) -> bool:
    """Convenience function to check GPU memory availability"""
    return gpu_memory_manager.is_memory_available(required_memory_gb)

def get_optimal_batch_size(base_batch_size: int = 4) -> int:
    """Convenience function to get optimal batch size"""
    return gpu_memory_manager.get_optimal_batch_size(base_batch_size)

def get_optimal_device_for_model(model_name: str, estimated_memory_gb: float = 0.5) -> str:
    """Convenience function to get optimal device for a model"""
    return gpu_memory_manager.get_optimal_device_for_model(model_name, estimated_memory_gb)

def register_model_memory_usage(model_name: str, memory_usage_gb: float, device: str):
    """Convenience function to register model memory usage"""
    gpu_memory_manager.register_model_memory_usage(model_name, memory_usage_gb, device)

def get_loading_strategy() -> Dict[str, str]:
    """Convenience function to get loading strategy for all models"""
    return gpu_memory_manager.get_loading_strategy()

def get_memory_usage_summary() -> Dict[str, any]:
    """Convenience function to get memory usage summary"""
    return gpu_memory_manager.get_memory_usage_summary()

def unload_low_priority_models(required_memory_gb: float) -> int:
    """Convenience function to unload low priority models"""
    return gpu_memory_manager.unload_low_priority_models(required_memory_gb)
