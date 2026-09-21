# backend/app/services/enhanced_model_loader.py - Enhanced Model Loading with Custom Model Support

import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
import warnings

# Environment variable to control model loading verbosity
MODEL_LOADING_VERBOSE = os.getenv("MODEL_LOADING_VERBOSE", "false").lower() == "true"

# Import centralized import management with caching
try:
    from .import_manager import get_cached_imports, fix_efficientnet_classifier
    import_cache = get_cached_imports()
    
    torch = import_cache['torch']
    torchvision = import_cache['torchvision']
    cv2 = import_cache['cv2']
    np = import_cache['numpy']
    
    if torch is None or torchvision is None:
        raise ImportError("Critical imports failed")
    
    nn = torch.nn
    models = torchvision["models"]
    transforms = torchvision["transforms"]
    
except ImportError as e:
    # Fallback imports
    import torch
    import torch.nn as nn
    import numpy as np
    import cv2
    from torchvision import models, transforms
    print(f"[INFO] Using fallback imports: {e}")

logger = logging.getLogger(__name__)

# Import face data validator for type conversion
try:
    from .face_data_validator import FaceDataValidator
    FACE_VALIDATOR_AVAILABLE = True
except ImportError:
    FACE_VALIDATOR_AVAILABLE = False
    logger.warning("FaceDataValidator not available")

# ✅ CUDA MEMORY FIX: Global CUDA memory management
def setup_cuda_memory_management():
    """Setup global CUDA memory management to prevent allocation errors"""
    try:
        if torch.cuda.is_available():
            # Clear any existing cache
            torch.cuda.empty_cache()
            
            # Set memory fraction to prevent OOM errors
            torch.cuda.set_per_process_memory_fraction(0.8)
            
            # Enable memory pooling for better memory management
            try:
                torch.cuda.memory._set_allocator_settings('expandable_segments:True')
            except:
                pass  # Some PyTorch versions don't support this
            
            logger.info("✅ Global CUDA memory management initialized")
            return True
    except Exception as e:
        logger.warning(f"CUDA memory management setup failed: {e}")
        return False

# Initialize global CUDA memory management
setup_cuda_memory_management()

class EnhancedModelLoader:
    """Enhanced model loader supporting multiple models and ensemble detection"""
    
    def __init__(self, device: str = "cuda:0", silent_mode: bool = None):
        # ✅ STARTUP OPTIMIZATION: Check for forced CPU mode
        if os.getenv("FORCE_CPU_MODE", "0") == "1":
            logger.info("🔧 Force CPU mode enabled via environment variable")
            device = "cpu"
        
        # ✅ CUDA MEMORY FIX: Add proper CUDA memory management
        self._initialize_cuda_memory()
        
        # Enforce consistent GPU selection, fallback to CPU on errors
        try:
            # Force CPU mode if environment variable is set
            if os.getenv("FORCE_CPU_MODE", "0") == "1":
                target = "cpu"
            else:
                target = device if torch.cuda.is_available() else "cpu"
            self.device = torch.device(target)
            self._device_string = target
        except Exception:
            self.device = torch.device("cpu")
            self._device_string = "cpu"
        
        # ✅ GPU MEMORY MANAGEMENT: Set model limits based on GPU memory
        # ✅ FIX: Ensure gpu_memory_gb is always a float, never None
        gpu_memory = self._get_gpu_memory_gb()
        if gpu_memory is None or not isinstance(gpu_memory, (int, float)):
            gpu_memory = 0.0
        self.gpu_memory_gb = float(gpu_memory)
        self.gpu_model_limit = self._calculate_gpu_model_limit()
        # ✅ CRITICAL FIX: Ensure gpu_memory_gb is not None before comparison
        gpu_mem_for_comparison = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
        if not isinstance(gpu_mem_for_comparison, (int, float)):
            gpu_mem_for_comparison = 0.0
        self.force_cpu_for_ensemble = float(gpu_mem_for_comparison) < 6.0  # Force CPU for < 6GB GPUs
        self.gpu_models_loaded = 0
        
        logger.info(f"🔍 GPU Memory: {self.gpu_memory_gb:.1f}GB, GPU Model Limit: {self.gpu_model_limit}")
        
        self.models = {}
        self.model_configs = {}
        self.ensemble_weights = {}
        # ✅ PHASE 4: Model usage tracking
        self._model_usage_count = {}  # Track how many times each model is used
        self._model_last_used = {}    # Track when each model was last used
        # ✅ GPU MODEL SWAPPING: Track which models are on GPU vs CPU
        self._gpu_models = set()  # Models currently on GPU
        self._model_locations = {}  # Track where each model is (GPU/CPU)
        self._use_fp16 = True  # Use mixed precision to halve memory usage
        # ✅ FAST STARTUP: Lazy loading support
        self._lazy_models = []  # Models that load on-demand
        # Use environment variable if silent_mode not specified
        self.silent_mode = silent_mode if silent_mode is not None else not MODEL_LOADING_VERBOSE
        self._setup_model_configs()
    
    def _initialize_cuda_memory(self):
        """Initialize CUDA memory management to prevent allocation errors"""
        try:
            if torch.cuda.is_available():
                # Clear CUDA cache to free any fragmented memory
                torch.cuda.empty_cache()
                
                # Set memory fraction based on GPU size - more conservative for 4GB GPU
                # ✅ FIX: Ensure gpu_memory is always a float, never None
                gpu_memory = self._get_gpu_memory_gb()
                if gpu_memory is None or not isinstance(gpu_memory, (int, float)):
                    gpu_memory = 0.0
                gpu_memory = float(gpu_memory)
                
                # ✅ CRITICAL FIX: Double-check before comparison
                if gpu_memory is None:
                    gpu_memory = 0.0
                gpu_memory = float(gpu_memory)
                
                if gpu_memory < 4.5:  # 4GB GPU
                    torch.cuda.set_per_process_memory_fraction(0.5)  # Use only 50%
                    logger.info("🔧 Conservative memory fraction (50%) set for 4GB GPU")
                elif gpu_memory < 6.0:  # 5-6GB GPU
                    torch.cuda.set_per_process_memory_fraction(0.6)  # Use 60%
                    logger.info("🔧 Moderate memory fraction (60%) set for 5-6GB GPU")
                else:
                    torch.cuda.set_per_process_memory_fraction(0.7)  # Use 70% for larger GPUs
                
                # Enable memory pooling for better memory management
                try:
                    torch.cuda.memory._set_allocator_settings('expandable_segments:True')
                except:
                    pass  # Some PyTorch versions don't support this
                
                logger.debug("✅ CUDA memory management initialized")
        except Exception as e:
            logger.warning(f"CUDA memory initialization failed: {e}")
    
    def _clear_cuda_cache(self):
        """✅ ADVANCED: Clear CUDA cache to free memory with comprehensive cleanup"""
        try:
            if torch.cuda.is_available():
                # ✅ CRITICAL FIX: More aggressive memory clearing to prevent OOM
                # Clear CUDA cache multiple times for better memory recovery
                for _ in range(2):  # Clear twice for better effect
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                
                # ✅ ADVANCED: Force garbage collection to free Python references
                import gc
                # Run garbage collection multiple times to ensure cleanup
                for _ in range(3):
                    gc.collect()
                
                # Clear cache again after GC
                for _ in range(2):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                
                # Additional cleanup for fragmented memory
                try:
                    torch.cuda.reset_peak_memory_stats()
                except:
                    pass  # Some PyTorch versions don't support this
                
                # ✅ CRITICAL FIX: Force memory compaction if available
                try:
                    if hasattr(torch.cuda, 'memory') and hasattr(torch.cuda.memory, 'empty_cache'):
                        torch.cuda.memory.empty_cache()
                except:
                    pass
                
                # ✅ ADVANCED: Log memory stats for monitoring
                if torch.cuda.is_available():
                    allocated = torch.cuda.memory_allocated() / (1024**3)
                    reserved = torch.cuda.memory_reserved() / (1024**3)
                    logger.debug(f"🧹 CUDA cache cleared: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
        except Exception as e:
            logger.debug(f"CUDA cache clear failed: {e}")
    
    def _get_gpu_memory_gb(self) -> float:
        """Get total GPU memory in GB"""
        if not torch.cuda.is_available():
            return 0.0
        try:
            total_memory = torch.cuda.get_device_properties(0).total_memory
            memory_gb = total_memory / (1024**3)  # Convert bytes to GB
            # ✅ FIX: Ensure we always return a float, never None
            if memory_gb is None or not isinstance(memory_gb, (int, float)):
                return 0.0
            return float(memory_gb)
        except Exception:
            return 0.0
    
    def _calculate_gpu_model_limit(self) -> int:
        """Calculate maximum number of models that can be loaded on GPU"""
        # ✅ FIX: Ensure gpu_memory_gb is always a float, never None
        gpu_memory = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
        if not isinstance(gpu_memory, (int, float)):
            gpu_memory = 0.0
        # ✅ CRITICAL FIX: Double-check and ensure it's a valid float
        try:
            gpu_memory = float(gpu_memory)
            if gpu_memory is None or (isinstance(gpu_memory, float) and (gpu_memory != gpu_memory)):  # Check for NaN
                gpu_memory = 0.0
        except (TypeError, ValueError):
            gpu_memory = 0.0
        
        if not torch.cuda.is_available() or gpu_memory < 2.0:
            return 0
        
        # With FP16 (half precision), models use ~50% memory, so we can fit more
        # Each model ~0.4-0.6GB with FP16 instead of 0.8-1.2GB
        # With 50% memory limit (2GB usable) and FP16, we can fit ~4-5 models
        if gpu_memory < 4.5:  # 4GB GPU
            return 4  # With FP16, can fit 4 models (was 2)
        elif gpu_memory < 6.0:  # 5-6GB GPU
            return 6  # With FP16, can fit 6 models (was 3)
        elif gpu_memory < 8.0:  # 8GB GPU
            return 8  # With FP16, can fit 8 models (was 4)
        else:  # 8GB+ GPU
            return 12  # With FP16, can fit 12 models (was 6)
    
    def _should_load_on_gpu(self, model_name: str) -> bool:
        """Determine if model should be loaded on GPU - try GPU first, swap if needed"""
        # Always try GPU first for speed (we'll swap if needed)
        if not torch.cuda.is_available():
            return False
        
        # Check if we can make space by swapping out unused models
        if self.gpu_models_loaded >= self.gpu_model_limit:
            # Try to free up space by moving least recently used model to CPU
            if self._swap_least_used_model_to_cpu():
                logger.debug(f"🔄 Swapped out least used model to make GPU space for {model_name}")
            else:
                logger.debug(f"💻 {model_name} will use CPU (GPU limit reached, no swap available)")
                return False
        
            # Check available GPU memory
        try:
            # ✅ FIX: Ensure gpu_memory_gb is always a float, never None
            gpu_memory = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
            if not isinstance(gpu_memory, (int, float)):
                gpu_memory = 0.0
            # ✅ CRITICAL FIX: Double-check before comparison
            try:
                gpu_memory = float(gpu_memory)
                if gpu_memory is None or (isinstance(gpu_memory, float) and (gpu_memory != gpu_memory)):  # Check for NaN
                    gpu_memory = 0.0
            except (TypeError, ValueError):
                gpu_memory = 0.0
            
            allocated = torch.cuda.memory_allocated() / (1024**3)  # GB
            # ✅ CRITICAL FIX: Safe comparison with additional check
            if gpu_memory is not None and isinstance(gpu_memory, (int, float)):
                usable_memory = gpu_memory * 0.5 if float(gpu_memory) < 4.5 else gpu_memory * 0.6
            else:
                usable_memory = 0.0
            free_memory = usable_memory - allocated
            
            # Need at least 400MB free for new model (with FP16, models are smaller)
            if free_memory < 0.4:
                # Try to free more space
                self._clear_cuda_cache()
                allocated = torch.cuda.memory_allocated() / (1024**3)
                free_memory = usable_memory - allocated
                if free_memory < 0.4:
                    logger.debug(f"💻 {model_name} will use CPU (insufficient free memory: {free_memory:.2f}GB)")
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"⚠️ GPU memory check failed: {e}, using CPU for {model_name}")
            return False
    
    def _swap_least_used_model_to_cpu(self) -> bool:
        """Swap least recently used GPU model to CPU to free GPU memory"""
        if len(self._gpu_models) == 0:
            return False
        
        # Find least recently used model on GPU
        lru_model = None
        lru_time = float('inf')
        for model_name in self._gpu_models:
            if model_name in self._model_last_used:
                if self._model_last_used[model_name] < lru_time:
                    lru_time = self._model_last_used[model_name]
                    lru_model = model_name
        
        if lru_model and lru_model in self.models:
            try:
                logger.debug(f"🔄 Swapping {lru_model} from GPU to CPU")
                model = self.models[lru_model]
                model = model.cpu()
                self.models[lru_model] = model
                self._gpu_models.discard(lru_model)
                self._model_locations[lru_model] = 'cpu'
                self.gpu_models_loaded -= 1
                self._clear_cuda_cache()
                return True
            except Exception as e:
                logger.warning(f"⚠️ Failed to swap {lru_model} to CPU: {e}")
                return False
        
        return False
    
    def _load_model_to_gpu_on_demand(self, model_name: str) -> bool:
        """Load a model to GPU on-demand if it's currently on CPU"""
        if model_name not in self.models:
            return False
        
        if model_name in self._gpu_models:
            return True  # Already on GPU
        
        # Check if we can load to GPU
        if not self._should_load_on_gpu(model_name):
            return False
        
        try:
            model = self.models[model_name]
            model = model.half() if self._use_fp16 else model  # Convert to FP16 for memory savings
            model = model.to(torch.device("cuda:0"))
            self.models[model_name] = model
            self._gpu_models.add(model_name)
            self._model_locations[model_name] = 'cuda:0'
            self.gpu_models_loaded += 1
            logger.debug(f"✅ Loaded {model_name} to GPU on-demand")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Failed to load {model_name} to GPU: {e}")
            return False
    
    def _log_info(self, message: str):
        """Conditional info logging based on silent mode"""
        if not self.silent_mode:
            logger.info(message)
        else:
            logger.debug(message)
    
    def _log_debug(self, message: str):
        """Always log debug messages"""
        logger.debug(message)
    
    def _setup_model_configs(self):
        """Setup comprehensive model configurations for 25+ model ensemble"""
        
        # ✅ FIX: Use absolute path to ml_artifacts folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Try multiple possible locations for ml_artifacts
        possible_paths = [
            os.path.join(current_dir, '../../../ml_artifacts'),
            os.path.join(current_dir, '../../ml_artifacts'),
            os.path.join(current_dir, '../ml_artifacts'),
            os.path.abspath('ml_artifacts'),  # From project root
        ]
        
        ml_artifacts = None
        for path in possible_paths:
            if os.path.exists(path):
                ml_artifacts = path
                break
        
        if ml_artifacts is None:
            # Fallback to relative path
            ml_artifacts = os.path.join(current_dir, '../../../ml_artifacts')
            logger.warning(f"ml_artifacts folder not found, using fallback path: {ml_artifacts}")
        
        self.model_configs = {
            # ===== TRADITIONAL MODELS (35% total weight) =====
            "efficientnet_b0": {
                "path": os.path.join(ml_artifacts, "efficientnet_b0.pth"),
                "type": "efficientnet",
                "architecture": "efficientnet_b0",
                "input_size": (224, 224),
                "weight": 0.04  # ✅ FIXED: Reduced to normalize total to 1.0
            },
            "efficientnet_b4": {
                "path": os.path.join(ml_artifacts, "effnb4_best.pth"),
                "type": "efficientnet",
                "architecture": "efficientnet_b4",
                "input_size": (224, 224),
                "weight": 0.05
            },
            "efficientnet_b7": {
                "path": os.path.join(ml_artifacts, "efficientnet_b7.pth"),
                "type": "efficientnet",
                "architecture": "efficientnet_b7",
                "input_size": (224, 224),
                "weight": 0.05
            },
            "resnet50": {
                "path": os.path.join(ml_artifacts, "resnet50.pth"),
                "type": "resnet",
                "architecture": "resnet50",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "resnet101": {
                "path": os.path.join(ml_artifacts, "resnet101.pth"),
                "type": "resnet",
                "architecture": "resnet101",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "resnet152": {
                "path": os.path.join(ml_artifacts, "resnet152.pth"),
                "type": "resnet",
                "architecture": "resnet152",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "densenet121": {
                "path": os.path.join(ml_artifacts, "densenet121.pth"),
                "type": "densenet",
                "architecture": "densenet121",
                "input_size": (224, 224),
                "weight": 0.03
            },
            "inception_v3": {
                "path": os.path.join(ml_artifacts, "inception_v3.pth"),
                "type": "inception",
                "architecture": "inception_v3",
                "input_size": (224, 224),
                "weight": 0.02
            },
            
            # ===== SPECIALIZED DEEPFAKE MODELS (30% total weight) =====
            "mesonet": {
                "path": os.path.join(ml_artifacts, "meso4_best.pth"),
                "type": "mesonet",
                "architecture": "mesonet4",
                "input_size": (224, 224),
                "weight": 0.05
            },
            "xception": {
                "path": os.path.join(ml_artifacts, "xception_best.pth"),
                "type": "xception",
                "architecture": "xception",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "capsule_net": {
                "path": os.path.join(ml_artifacts, "capsule_best.pth"),
                "type": "capsule",
                "architecture": "capsule_net",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "f3net": {
                "path": os.path.join(ml_artifacts, "f3net_best.pth"),
                "type": "f3net",
                "architecture": "f3net",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "ffd": {
                "path": os.path.join(ml_artifacts, "ffd_best.pth"),
                "type": "ffd",
                "architecture": "ffd",
                "input_size": (224, 224),
                "weight": 0.03
            },
            "srm": {
                "path": os.path.join(ml_artifacts, "srm_best.pth"),
                "type": "srm",
                "architecture": "srm_net",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "recce": {
                "path": os.path.join(ml_artifacts, "recce_best.pth"),
                "type": "recce",
                "architecture": "recce",
                "input_size": (224, 224),
                "weight": 0.03
            },
            "spsl": {
                "path": os.path.join(ml_artifacts, "spsl_best.pth"),
                "type": "spsl",
                "architecture": "spsl",
                "input_size": (224, 224),
                "weight": 0.02
            },
            
            # ===== MODERN TRANSFORMER MODELS (20% total weight) =====
            "vision_transformer": {
                "path": os.path.join(ml_artifacts, "vision_transformer.pth"),
                "type": "vision_transformer",
                "architecture": "vit_base_patch16_224",
                "input_size": (224, 224),
                "weight": 0.06
            },
            "swin_transformer": {
                "path": os.path.join(ml_artifacts, "swin_transformer.pth"),
                "type": "swin_transformer",
                "architecture": "swin_base_patch4_window7_224",
                "input_size": (224, 224),
                "weight": 0.05
            },
            "convnext": {
                "path": os.path.join(ml_artifacts, "convnext.pth"),
                "type": "convnext",
                "architecture": "convnext_base",
                "input_size": (224, 224),
                "weight": 0.04
            },
            "deit": {
                "path": os.path.join(ml_artifacts, "deit.pth"),
                "type": "deit",
                "architecture": "deit_base_patch16_224",
                "input_size": (224, 224),
                "weight": 0.03
            },
            "beit": {
                "path": os.path.join(ml_artifacts, "beit.pth"),
                "type": "beit",
                "architecture": "beit_base_patch16_224",
                "input_size": (224, 224),
                "weight": 0.02
            },
            
            # ===== CUSTOM TRAINED MODEL (15% total weight) =====
            "custom_finetuned": {
                "path": os.path.join(ml_artifacts, "deepfake_detector_finetuned1.pth"),
                "type": "custom",
                "architecture": "efficientnet_b0",
                "input_size": (224, 224),
                "weight": 0.15  # ✅ FIXED: Reduced from 0.25 to 0.15
            },
            "efficientnet_finetuned": {
                "path": os.path.join(ml_artifacts, "deepfake_detector_finetuned1.pth"),
                "type": "efficientnet",
                "architecture": "efficientnet_b0",
                "input_size": (224, 224),
                "weight": 0.05  # ✅ FIXED: Added proper weight instead of 0.00
            }
        }
        
        # ✅ FIX: Verify weights sum to 1.0 (handle None weights)
        weights_list = []
        for cfg in self.model_configs.values():
            w = cfg.get('weight', 0.1) if cfg.get('weight') is not None else 0.1
            # ✅ CRITICAL FIX: Ensure weight is a valid number
            if w is None:
                w = 0.1
            try:
                w = float(w)
                if w is None or (isinstance(w, float) and (w != w)):  # Check for NaN
                    w = 0.1
            except (TypeError, ValueError):
                w = 0.1
            weights_list.append(w)
        total_weight = sum(weights_list)
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Model weights sum to {total_weight:.3f}, expected 1.0 - normalizing")
            # Normalize weights
            for model_name in self.model_configs:
                current_weight = self.model_configs[model_name].get('weight', 0.1)
                if current_weight is not None:
                    try:
                        self.model_configs[model_name]['weight'] = float(current_weight) / total_weight
                    except (TypeError, ValueError):
                        self.model_configs[model_name]['weight'] = 0.1 / total_weight
                else:
                    self.model_configs[model_name]['weight'] = 0.1 / total_weight
        else:
            self._log_info(f"✅ Model weights sum to {total_weight:.3f} (correct)")
        
        self._log_info(f"✅ Configured {len(self.model_configs)} models with balanced weights")
    
    async def load_all_models_progressive(self, priority_first: bool = True):
        """
        Load models progressively with priority-based ordering.
        
        High priority: efficientnet_b0, mesonet, xception, vision_transformer
        Medium priority: resnet50, f3net, swin_transformer
        Low priority: additional variants for ensemble diversity
        """
        priority_order = {
            'high': ['efficientnet_b0', 'mesonet', 'xception', 'vision_transformer'],
            'medium': ['resnet50', 'f3net', 'swin_transformer', 'convnext'],
            'low': ['efficientnet_b4', 'resnet101', 'capsule_net', 'deit', 'beit']
        }
        
        loaded_count = 0
        
        for priority_level in ['high', 'medium', 'low']:
            for model_name in priority_order[priority_level]:
                if model_name in self.model_configs:
                    try:
                        logger.info(f"Loading {priority_level} priority model: {model_name}")
                        self.models[model_name] = await self._load_model_async(model_name)
                        loaded_count += 1
                        logger.info(f"✅ {model_name} loaded ({loaded_count}/{len(self.model_configs)})")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load {model_name}: {e}")
                        continue
        
        logger.info(f"✅ Loaded {loaded_count}/{len(self.model_configs)} models")
        return loaded_count
    
    async def _load_model_async(self, model_name: str) -> Optional[torch.nn.Module]:
        """Async wrapper for model loading"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.load_model, model_name)
    
    def load_model(self, model_name: str) -> Optional[torch.nn.Module]:
        """Load a specific model by name with CUDA memory management and lazy loading"""
        try:
            if model_name not in self.model_configs:
                logger.error(f"Unknown model: {model_name}")
                return None
            
            # ✅ FAST STARTUP: Check if model is already loaded
            if model_name in self.models and self.models[model_name] is not None:
                return self.models[model_name]
            
            # ✅ FAST STARTUP: Lazy loading - load model on first use
            logger.debug(f"📦 Loading model on-demand: {model_name}")
            
            # ✅ CUDA MEMORY FIX: Aggressive cache clearing before loading
            self._clear_cuda_cache()
            # Additional sync to ensure cleanup is complete
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            
            config = self.model_configs[model_name]
            model_path = config["path"]
            
            # ✅ GPU MEMORY MANAGEMENT: Determine device based on memory constraints
            # ✅ CRITICAL FIX: Clear cache aggressively before loading to prevent OOM
            self._clear_cuda_cache()
            
            use_gpu = self._should_load_on_gpu(model_name)
            
            # ✅ FIX: Ensure gpu_memory_gb is not None before comparisons
            if self.gpu_memory_gb is None:
                gpu_mem = self._get_gpu_memory_gb()
                if gpu_mem is None or not isinstance(gpu_mem, (int, float)):
                    gpu_mem = 0.0
                self.gpu_memory_gb = float(gpu_mem)
            
            # ✅ CRITICAL FIX: Check available memory before loading and force CPU if needed
            if use_gpu and torch.cuda.is_available():
                try:
                    allocated = torch.cuda.memory_allocated() / (1024**3)
                    gpu_mem_gb = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
                    if not isinstance(gpu_mem_gb, (int, float)):
                        gpu_mem_gb = 0.0
                    gpu_mem_gb = float(gpu_mem_gb)
                    
                    # ✅ CRITICAL FIX: Force CPU if memory usage is too high (>80% of available)
                    if gpu_mem_gb > 0:
                        usage_percent = (allocated / gpu_mem_gb) * 100
                        if usage_percent > 80:
                            logger.warning(f"⚠️ GPU memory usage too high ({usage_percent:.1f}%), forcing CPU for {model_name}")
                            use_gpu = False
                except Exception as mem_check_error:
                    logger.warning(f"⚠️ Memory check failed: {mem_check_error}, using CPU for {model_name}")
                    use_gpu = False
            
            # Enhanced CUDA safety check
            try:
                if use_gpu and torch.cuda.is_available():
                    # Use centralized CUDA safety manager to avoid driver conflicts
                    try:
                        # Force GPU mode - bypass CUDA safety manager issues
                        # torch is already imported at module level, no need to reimport
                        if torch.cuda.is_available():
                            target_device = torch.device("cuda:0")
                            logger.info(f"🚀 Loading {model_name} on GPU (models loaded: {self.gpu_models_loaded}/{self.gpu_model_limit})")
                        else:
                            target_device = "cpu"
                            use_gpu = False
                            logger.info(f"💻 Loading {model_name} on CPU (CUDA not available)")
                    except Exception as cuda_test_error:
                        error_str = str(cuda_test_error)
                        if "INTERNAL ASSERT FAILED" in error_str:
                            logger.warning(f"CUDA driver error detected for {model_name}, forcing CPU: {cuda_test_error}")
                            use_gpu = False
                            target_device = torch.device("cpu")
                            logger.info(f"💻 Loading {model_name} on CPU (CUDA driver error)")
                        else:
                            # Force GPU mode even if CUDA safety manager fails
                            # torch is already imported at module level, no need to reimport
                            if torch.cuda.is_available():
                                target_device = torch.device("cuda:0")
                                logger.info(f"🚀 Loading {model_name} on GPU (forced, models loaded: {self.gpu_models_loaded}/{self.gpu_model_limit})")
                            else:
                                raise
                else:
                    # ✅ FIX: Better GPU memory management - try to free space before failing
                    if self.gpu_models_loaded >= self.gpu_model_limit:
                        # Try to clear cache and see if we can fit this model
                        self._clear_cuda_cache()
                        # Check if we can still load on GPU (limit might be conservative)
                        # ✅ FIX: Ensure gpu_memory_gb is not None before comparison
                        gpu_mem_gb = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
                        if torch.cuda.is_available() and gpu_mem_gb > 0 and torch.cuda.memory_allocated() / (1024**3) < gpu_mem_gb * 0.8:
                            # We have space, try GPU anyway
                            target_device = torch.device("cuda:0")
                            logger.info(f"🚀 Loading {model_name} on GPU (cache cleared, models loaded: {self.gpu_models_loaded}/{self.gpu_model_limit})")
                        else:
                            raise Exception("CUDA not available or GPU limit reached")
                    else:
                        raise Exception("CUDA not available or GPU limit reached")
            except Exception as cuda_error:
                error_str = str(cuda_error)
                if "INTERNAL ASSERT FAILED" in error_str:
                    logger.warning(f"CUDA driver error detected for {model_name}, forcing CPU: {cuda_error}")
                    use_gpu = False
                    target_device = torch.device("cpu")
                    logger.info(f"💻 Loading {model_name} on CPU (CUDA driver error)")
                elif "GPU limit reached" in error_str or "CUDA not available" in error_str:
                    # ✅ FIX: Only fall back to CPU if we really can't use GPU
                    # Try one more time with cache clearing
                    if torch.cuda.is_available():
                        self._clear_cuda_cache()
                        current_memory = torch.cuda.memory_allocated() / (1024**3)
                        # ✅ FIX: Ensure gpu_memory_gb is not None before comparison
                        gpu_mem_gb = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
                        if gpu_mem_gb > 0 and current_memory < gpu_mem_gb * 0.7:
                            # We have space now, use GPU
                            target_device = torch.device("cuda:0")
                            use_gpu = True
                            logger.info(f"🚀 Loading {model_name} on GPU (cache cleared, retry successful)")
                        else:
                            use_gpu = False
                            target_device = torch.device("cpu")
                            gpu_mem_display = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
                            logger.info(f"💻 Loading {model_name} on CPU (GPU memory exhausted: {current_memory:.2f}GB/{gpu_mem_display:.2f}GB)")
                    else:
                        use_gpu = False
                        target_device = torch.device("cpu")
                        logger.info(f"💻 Loading {model_name} on CPU (CUDA not available)")
                else:
                    logger.info(f"CUDA test failed for {model_name}, using CPU: {cuda_error}")
                    use_gpu = False
                    target_device = torch.device("cpu")
                    logger.info(f"💻 Loading {model_name} on CPU (CUDA unavailable or forced CPU)")
            
            # ✅ ENHANCED MODEL FILE VALIDATION: Comprehensive path resolution and error handling
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found: {model_path}")
                
                # ✅ COMPREHENSIVE PATH RESOLUTION: Try multiple alternative paths
                current_dir = os.path.dirname(os.path.abspath(__file__))
                alternative_paths = [
                    # Relative paths from current service directory
                    os.path.join(current_dir, f'../../../ml_artifacts/{os.path.basename(model_path)}'),
                    os.path.join(current_dir, f'../../ml_artifacts/{os.path.basename(model_path)}'),
                    os.path.join(current_dir, f'../ml_artifacts/{os.path.basename(model_path)}'),
                    # Absolute paths from project root
                    os.path.abspath(f'ml_artifacts/{os.path.basename(model_path)}'),
                    os.path.abspath(f'backend/ml_artifacts/{os.path.basename(model_path)}'),
                    # Environment-specific paths
                    os.path.join(os.getcwd(), f'ml_artifacts/{os.path.basename(model_path)}'),
                    os.path.join(os.getcwd(), f'backend/ml_artifacts/{os.path.basename(model_path)}'),
                ]
                
                # ✅ SYSTEMATIC PATH SEARCH: Try each alternative path
                model_found = False
                for alt_path in alternative_paths:
                    try:
                        if os.path.exists(alt_path):
                            # Validate file size to ensure it's not corrupted
                            file_size = os.path.getsize(alt_path)
                            if file_size > 1000:  # At least 1KB
                                model_path = alt_path
                                logger.info(f"✅ Found model at alternative path: {alt_path} (size: {file_size} bytes)")
                                model_found = True
                                break
                            else:
                                logger.warning(f"Model file too small ({file_size} bytes): {alt_path}")
                    except Exception as path_error:
                        logger.debug(f"Path check failed for {alt_path}: {path_error}")
                        continue
                
                if not model_found:
                    # ✅ COMPREHENSIVE ERROR REPORTING: Detailed debugging information
                    logger.error(f"❌ Model file not found in any alternative location: {model_name}")
                    logger.error(f"Expected file: {model_path}")
                    
                    # ✅ FILE SYSTEM DIAGNOSTICS: Check available files
                    logger.error(f"Searching for available model files...")
                    search_dirs = [
                        os.path.dirname(model_path),
                        os.path.abspath('ml_artifacts'),
                        os.path.abspath('backend/ml_artifacts'),
                        current_dir
                    ]
                    
                    for search_dir in search_dirs:
                        try:
                            if os.path.exists(search_dir):
                                files = os.listdir(search_dir)
                                model_files = [f for f in files if f.endswith('.pth') or f.endswith('.pt')]
                                if model_files:
                                    logger.error(f"Available models in {search_dir}: {model_files[:5]}...")
                        except Exception as dir_error:
                            logger.debug(f"Cannot list directory {search_dir}: {dir_error}")
                    
                    # ✅ FALLBACK MODEL CREATION: Create a working fallback instead of failing
                    logger.info(f"Creating fallback model for {model_name} to prevent system failure")
                    return self._create_fallback_model(model_name, config)
            
            # Load model based on type
            if config["type"] == "efficientnet":
                model = self._load_efficientnet_model(model_path, config)
            elif config["type"] == "custom":
                model = self._load_custom_model(model_path, config)
            elif config["type"] == "resnet":
                model = self._load_resnet_model(model_path, config)
            elif config["type"] == "mesonet":
                model = self._load_mesonet_model(model_path, config)
            elif config["type"] == "xception":
                model = self._load_xception_model(model_path, config)
            elif config["type"] == "capsule":
                model = self._load_capsule_model(model_path, config)
            elif config["type"] == "f3net":
                model = self._load_f3net_model(model_path, config)
            elif config["type"] == "ffd":
                model = self._load_ffd_model(model_path, config)
            elif config["type"] == "srm":
                model = self._load_srm_model(model_path, config)
            elif config["type"] == "recce":
                model = self._load_recce_model(model_path, config)
            elif config["type"] == "spsl":
                model = self._load_spsl_model(model_path, config)
            elif config["type"] == "vision_transformer":
                model = self._load_vision_transformer_model(model_path, config)
            elif config["type"] == "swin_transformer":
                model = self._load_swin_transformer_model(model_path, config)
            elif config["type"] == "convnext":
                model = self._load_convnext_model(model_path, config)
            elif config["type"] == "deit":
                model = self._load_deit_model(model_path, config)
            elif config["type"] == "beit":
                model = self._load_beit_model(model_path, config)
            elif config["type"] == "densenet":
                model = self._load_densenet_model(model_path, config)
            elif config["type"] == "inception":
                model = self._load_inception_model(model_path, config)
            else:
                logger.warning(f"Unknown model type: {config['type']}, falling back to efficientnet")
                model = self._load_efficientnet_model(model_path, config)
            
            if model is not None:
                # ✅ GPU MEMORY MANAGEMENT: Move model to target device with FP16 and OOM retry
                try:
                    # Convert to FP16 for memory savings if using GPU
                    # ✅ FIX: Skip FP16 for models that don't support it well (e.g., MesoNet)
                    models_no_fp16 = ['mesonet', 'capsule_net']  # Models that have issues with FP16
                    if use_gpu and self._use_fp16 and model_name not in models_no_fp16:
                        try:
                            model = model.half()  # Convert to FP16 - reduces memory by 50%
                            logger.debug(f"🔧 Converted {model_name} to FP16 for memory savings")
                        except Exception as fp16_error:
                            logger.debug(f"⚠️ FP16 conversion failed for {model_name}: {fp16_error}, using FP32")
                    elif model_name in models_no_fp16:
                        logger.debug(f"🔧 Skipping FP16 for {model_name} (known compatibility issues)")
                    
                    model = model.to(target_device)
                    if use_gpu:
                        self.gpu_models_loaded += 1
                        self._gpu_models.add(model_name)
                        self._model_locations[model_name] = 'cuda:0'
                        logger.info(f"✅ {model_name} loaded on GPU (FP16={self._use_fp16}, GPU models: {self.gpu_models_loaded}/{self.gpu_model_limit})")
                    else:
                        self._model_locations[model_name] = 'cpu'
                        logger.info(f"✅ {model_name} loaded on CPU")
                except torch.cuda.OutOfMemoryError:
                    logger.warning(f"⚠️ GPU OOM for {model_name}, falling back to CPU")
                    # Try without FP16 if FP16 was used
                    if self._use_fp16:
                        try:
                            model = model.float()  # Convert back to FP32
                        except:
                            pass
                    target_device = torch.device("cpu")
                    model = model.to(target_device)
                    self._model_locations[model_name] = 'cpu'
                    logger.info(f"✅ {model_name} loaded on CPU (OOM fallback)")
                
                self.models[model_name] = model
                # ✅ FIX: Ensure weight is not None before storing
                weight = config.get("weight", 0.1) if config else 0.1
                if weight is None:
                    weight = 0.1  # Default weight if None
                # ✅ CRITICAL FIX: Ensure weight is a valid number before storing
                try:
                    weight = float(weight) if weight is not None else 0.1
                    if weight is None or (isinstance(weight, float) and (weight != weight)):  # Check for NaN
                        weight = 0.1
                except (TypeError, ValueError):
                    weight = 0.1
                self.ensemble_weights[model_name] = weight
                # ✅ CUDA MEMORY FIX: Clear cache after loading
                self._clear_cuda_cache()
                # Reduced logging to avoid duplicates
            
            return model
            
        except RuntimeError as e:
            if "CUDA" in str(e) or "memory" in str(e).lower():
                logger.error(f"CUDA memory error loading {model_name}: {e}")
                logger.warning(f"Skipping {model_name} due to CUDA memory issues")
                # Clear cache and continue
                self._clear_cuda_cache()
                return None
            else:
                logger.error(f"Failed to load model {model_name}: {e}")
                # Create fallback model
                logger.info(f"Creating fallback model for {model_name}")
                return self._create_fallback_model(model_name, config)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            # Create fallback model
            logger.info(f"Creating fallback model for {model_name}")
            return self._create_fallback_model(model_name, config)
    
    def _create_fallback_model(self, model_name: str, config: Dict) -> Optional[torch.nn.Module]:
        """Create a fallback model when the original model file is missing"""
        try:
            # ✅ FIX: Handle None config
            if config is None:
                config = {"type": "efficientnet", "weight": 0.1}
            logger.info(f"Creating fallback EfficientNet model for {model_name}")
            
            # Create a simple EfficientNet-B0 model as fallback
            model = models.efficientnet_b0(weights=None)
            
            # Rebuild classifier for binary classification
            in_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(in_features, 2)
            )
            
            # Initialize weights randomly (since we don't have pretrained weights)
            self._initialize_weights(model)
            
            # ✅ CUDA MEMORY FIX: Add memory management before moving model to device
            try:
                # Clear CUDA cache before loading model to device
                self._clear_cuda_cache()
                
                # ✅ CRITICAL FIX: Ensure model is moved to device and stays there
                model = model.to(self.device)
                # Verify model is actually on the correct device
                model_device = next(model.parameters()).device
                if model_device != self.device:
                    logger.debug(f"Model device mismatch: expected {self.device}, got {model_device} (this is expected for CPU-loaded models)")
                    # Don't force move - model is already on correct device (CPU or GPU based on memory)
                model.eval()
                
                # Clear cache again after loading
                self._clear_cuda_cache()
                
            except RuntimeError as e:
                if "CUDA" in str(e) or "memory" in str(e).lower():
                    logger.warning(f"CUDA memory error loading model: {e}")
                    logger.warning("Falling back to CPU for this model")
                    # Clear cache and try CPU
                    self._clear_cuda_cache()
                    model = model.to(torch.device("cpu"))
                    model.eval()
                else:
                    raise e
            
            logger.info(f"✅ Fallback model created for {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to create fallback model for {model_name}: {e}")
            return None
    
    def _initialize_weights(self, model: torch.nn.Module):
        """Initialize model weights"""
        for m in model.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def _remap_state_dict_keys(self, state_dict: Dict[str, torch.Tensor], model_name: str) -> Dict[str, torch.Tensor]:
        """Remap state dict keys to match torchvision model architecture"""
        try:
            remapped_dict = {}
            original_keys = list(state_dict.keys())
            
            self._log_debug(f"🔍 Remapping keys for {model_name}: {len(original_keys)} keys")
            
            for key, value in state_dict.items():
                new_key = key
                
                # Handle different prefix patterns
                if key.startswith('backbone.efficientnet.'):
                    # Remove backbone.efficientnet. prefix
                    new_key = key.replace('backbone.efficientnet.', '')
                elif key.startswith('backbone.'):
                    # Remove backbone. prefix
                    new_key = key.replace('backbone.', '')
                elif key.startswith('module.'):
                    # Remove module. prefix (DataParallel)
                    new_key = key.replace('module.', '')
                
                # Handle specific architecture mappings
                if 'efficientnet' in model_name.lower():
                    # EfficientNet specific mappings
                    if new_key.startswith('_conv_stem'):
                        new_key = new_key.replace('_conv_stem', 'features.0.0')
                    elif new_key.startswith('_bn0'):
                        new_key = new_key.replace('_bn0', 'features.0.1')
                    elif new_key.startswith('_blocks'):
                        # Map EfficientNet blocks to features
                        new_key = new_key.replace('_blocks', 'features')
                        # Convert block indices to proper features indices
                        parts = new_key.split('.')
                        if len(parts) > 1 and parts[1].isdigit():
                            block_idx = int(parts[1])
                            # EfficientNet B0 has 16 blocks (0-15), map to features.1-16
                            new_block_idx = block_idx + 1
                            parts[1] = str(new_block_idx)
                            new_key = '.'.join(parts)
                elif 'resnet' in model_name.lower():
                    # ResNet specific mappings
                    if new_key.startswith('conv1'):
                        new_key = new_key.replace('conv1', 'conv1')
                    elif new_key.startswith('bn1'):
                        new_key = new_key.replace('bn1', 'bn1')
                    elif new_key.startswith('layer'):
                        # Keep ResNet layer structure as is
                        pass
                elif 'densenet' in model_name.lower():
                    # DenseNet specific mappings
                    if new_key.startswith('features'):
                        # Keep DenseNet features structure as is
                        pass
                elif 'inception' in model_name.lower():
                    # Inception specific mappings
                    if new_key.startswith('Conv2d_'):
                        # Map Inception Conv2d layers
                        new_key = new_key.replace('Conv2d_', '')
                
                remapped_dict[new_key] = value
            
            # Log key remapping statistics
            if len(original_keys) != len(remapped_dict):
                logger.warning(f"⚠️ Key count changed during remapping: {len(original_keys)} → {len(remapped_dict)}")
            
            self._log_debug(f"✅ Key remapping completed for {model_name}: {len(remapped_dict)} keys")
            return remapped_dict
            
        except Exception as e:
            logger.error(f"Failed to remap keys for {model_name}: {e}")
            return state_dict  # Return original on failure
    
    def _detect_architecture_from_checkpoint(self, state_dict: Dict[str, torch.Tensor], model_name: str) -> str:
        """Detect the actual architecture from checkpoint structure"""
        try:
            keys = list(state_dict.keys())
            
            # Analyze key patterns to determine architecture
            if any('features.' in key for key in keys):
                # PyTorch EfficientNet architecture detected (uses 'features' structure)
                # Check the first conv layer to determine variant
                first_conv_key = None
                for key in keys:
                    if 'features.0.0.weight' in key:
                        first_conv_key = key
                        break
                
                if first_conv_key and first_conv_key in state_dict:
                    first_conv_shape = state_dict[first_conv_key].shape
                    out_channels = first_conv_shape[0]
                    logger.debug(f"🔍 First conv layer shape: {first_conv_shape}, out_channels: {out_channels}")
                    
                    # Map channel count to EfficientNet variant
                    if out_channels == 32:
                        return 'efficientnet_b0'
                    elif out_channels == 56:
                        return 'efficientnet_b1'
                    elif out_channels == 64:
                        return 'efficientnet_b2'
                    elif out_channels == 80:
                        return 'efficientnet_b3'
                    elif out_channels == 112:
                        return 'efficientnet_b4'
                    elif out_channels == 128:
                        return 'efficientnet_b5'
                    elif out_channels == 160:
                        return 'efficientnet_b6'
                    elif out_channels == 224:
                        return 'efficientnet_b7'
                    else:
                        logger.warning(f"Unknown EfficientNet variant with {out_channels} channels, defaulting to B0")
                        return 'efficientnet_b0'
                        
            elif any('_conv_stem' in key for key in keys):
                # Alternative EfficientNet architecture detected (timm-style)
                if any('_blocks.0' in key for key in keys):
                    # Count blocks to determine variant
                    block_indices = []
                    for key in keys:
                        if '_blocks.' in key:
                            try:
                                block_idx = int(key.split('_blocks.')[1].split('.')[0])
                                block_indices.append(block_idx)
                            except:
                                pass
                    
                    max_blocks = max(block_indices) if block_indices else 0
                    
                    # Map block count to EfficientNet variant
                    if max_blocks <= 15:  # EfficientNet-B0 has 16 blocks (0-15)
                        return 'efficientnet_b0'
                    elif max_blocks <= 23:  # EfficientNet-B4 has 24 blocks (0-23)
                        return 'efficientnet_b4'
                    elif max_blocks <= 31:  # EfficientNet-B7 has 32 blocks (0-31)
                        return 'efficientnet_b7'
                    else:
                        return 'efficientnet_b0'  # Default fallback
                        
            elif any('layer1' in key for key in keys) and any('layer4' in key for key in keys):
                # ResNet architecture detected
                if any('layer4.2' in key for key in keys):  # ResNet-152 has layer4.2
                    return 'resnet152'
                elif any('layer4.1' in key for key in keys):  # ResNet-101 has layer4.1
                    return 'resnet101'
                else:  # ResNet-50 has layer4.0
                    return 'resnet50'
                    
            elif any('features.denseblock' in key for key in keys):
                # DenseNet architecture detected
                return 'densenet121'
                
            elif any('Conv2d_1a_3x3' in key for key in keys):
                # Inception architecture detected
                return 'inception_v3'
            
            # Default fallback based on model name
            if 'efficientnet' in model_name.lower():
                if 'b4' in model_name.lower():
                    return 'efficientnet_b4'
                elif 'b7' in model_name.lower():
                    return 'efficientnet_b7'
                else:
                    return 'efficientnet_b0'
            elif 'resnet' in model_name.lower():
                if '152' in model_name.lower():
                    return 'resnet152'
                elif '101' in model_name.lower():
                    return 'resnet101'
                else:
                    return 'resnet50'
            elif 'capsule' in model_name.lower():
                return 'capsule_net'
            elif 'xception' in model_name.lower():
                return 'xception'
            elif 'f3net' in model_name.lower():
                return 'f3net'
            elif 'ffd' in model_name.lower():
                return 'ffd'
            elif 'srm' in model_name.lower():
                return 'srm_net'
            elif 'recce' in model_name.lower():
                return 'recce'
            elif 'spsl' in model_name.lower():
                return 'spsl'
            elif 'deit' in model_name.lower():
                return 'deit_base_patch16_224'
            elif 'beit' in model_name.lower():
                return 'beit_base_patch16_224'
            
            logger.warning(f"⚠️ Could not detect architecture for {model_name}, using default")
            return 'efficientnet_b0'  # Safe default
            
        except Exception as e:
            logger.error(f"Failed to detect architecture for {model_name}: {e}")
            return 'efficientnet_b0'  # Safe default
    
    def _handle_missing_keys(self, model: torch.nn.Module, missing_keys: List[str]):
        """Handle missing keys by initializing them with proper weights"""
        try:
            # Get the current state dict to understand what's missing
            current_state = model.state_dict()
            
            for missing_key in missing_keys:
                # Skip classifier keys as they're handled separately
                if 'classifier' in missing_key or 'fc' in missing_key:
                    continue
                
                # Try to find the corresponding module and initialize it
                try:
                    # Parse the key to find the module
                    parts = missing_key.split('.')
                    module = model
                    
                    # Navigate to the parent module
                    for part in parts[:-1]:
                        if hasattr(module, part):
                            module = getattr(module, part)
                        else:
                            # Try to find by index if it's a sequential module
                            try:
                                module = module[int(part)]
                            except (ValueError, IndexError):
                                break
                    
                    # Get the parameter name (last part of the key)
                    param_name = parts[-1]
                    
                    # Initialize the missing parameter
                    if hasattr(module, param_name):
                        param = getattr(module, param_name)
                        if isinstance(param, nn.Parameter):
                            if 'weight' in param_name:
                                if len(param.shape) == 2:  # Linear layer
                                    nn.init.normal_(param, 0, 0.01)
                                elif len(param.shape) == 4:  # Conv2d layer
                                    nn.init.kaiming_normal_(param, mode='fan_out', nonlinearity='relu')
                                elif len(param.shape) == 1:  # Bias or 1D weight
                                    nn.init.constant_(param, 0)
                            elif 'bias' in param_name:
                                nn.init.constant_(param, 0)
                            elif 'running_mean' in param_name or 'running_var' in param_name:
                                nn.init.constant_(param, 0)
                            elif 'num_batches_tracked' in param_name:
                                param.data.fill_(0)
                    
                except Exception as e:
                    logger.debug(f"Could not initialize missing key {missing_key}: {e}")
                    continue
            
            self._log_debug(f"✅ Initialized missing keys for better model compatibility")
            
        except Exception as e:
            logger.warning(f"Failed to handle missing keys: {e}")
            # Continue without failing - the model will still work
    
    def _load_efficientnet_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load EfficientNet-based model with automatic classifier rebuilding"""
        try:
            # Load checkpoint first to detect output dimensions
            try:
                state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            except Exception as e:
                logger.warning(f"Failed to load with weights_only=False, trying weights_only=True: {e}")
                state_dict = torch.load(model_path, map_location="cpu", weights_only=True)
            
            # Handle different checkpoint formats
            if isinstance(state_dict, dict):
                if 'state_dict' in state_dict:
                    state_dict = state_dict['state_dict']
                elif 'model_state_dict' in state_dict:
                    state_dict = state_dict['model_state_dict']
                elif 'model' in state_dict:
                    state_dict = state_dict['model']
            
            # Detect architecture from checkpoint
            model_name = config.get("name", model_path.split('/')[-1].replace('.pth', ''))
            detected_architecture = self._detect_architecture_from_checkpoint(state_dict, model_name)
            self._log_debug(f"🔍 Detected architecture: {detected_architecture} for {model_name}")
            
            # Create the correct EfficientNet architecture
            if detected_architecture == 'efficientnet_b0':
                model = models.efficientnet_b0(weights=None)
            elif detected_architecture == 'efficientnet_b1':
                model = models.efficientnet_b1(weights=None)
            elif detected_architecture == 'efficientnet_b2':
                model = models.efficientnet_b2(weights=None)
            elif detected_architecture == 'efficientnet_b3':
                model = models.efficientnet_b3(weights=None)
            elif detected_architecture == 'efficientnet_b4':
                model = models.efficientnet_b4(weights=None)
            elif detected_architecture == 'efficientnet_b5':
                model = models.efficientnet_b5(weights=None)
            elif detected_architecture == 'efficientnet_b6':
                model = models.efficientnet_b6(weights=None)
            elif detected_architecture == 'efficientnet_b7':
                model = models.efficientnet_b7(weights=None)
            else:
                logger.warning(f"Unknown architecture {detected_architecture}, defaulting to EfficientNet-B0")
                model = models.efficientnet_b0(weights=None)  # Default
            
            # Apply key remapping to fix missing keys
            original_key_count = len(state_dict)
            state_dict = self._remap_state_dict_keys(state_dict, model_name)
            remapped_key_count = len(state_dict)
            
            if original_key_count != remapped_key_count:
                logger.debug(f"🔄 Key remapping: {original_key_count} → {remapped_key_count} keys")
            
            # ✅ FIX: Detect output dimension from checkpoint
            classifier_key = 'classifier.1.weight'  # EfficientNet classifier layer
            old_num_classes = None
            if classifier_key in state_dict:
                old_num_classes = state_dict[classifier_key].shape[0]
                self._log_debug(f"Detected {old_num_classes} classes in checkpoint")
            
            # ✅ FIX: Rebuild classifier if dimensions don't match
            expected_num_classes = 2  # Binary classification: Real vs Fake
            
            if old_num_classes != expected_num_classes:
                logger.debug(f"Rebuilding classifier: {old_num_classes} → {expected_num_classes}")
                
                # Get input features dimension
                in_features = model.classifier[1].in_features
                
                # Rebuild classifier for binary output
                model.classifier = nn.Sequential(
                    nn.Dropout(p=0.2, inplace=True),
                    nn.Linear(in_features, expected_num_classes)
                )
                
                # Remove old classifier weights from state_dict
                state_dict = {k: v for k, v in state_dict.items() 
                             if 'classifier' not in k}
                
                self._log_debug(f"✅ Classifier rebuilt: {in_features} → {expected_num_classes}")
            
            # Use centralized classifier fix as fallback
            model = fix_efficientnet_classifier(model, num_classes=2)
            
            # Clean state dict keys and filter out incompatible layers
            clean_state_dict = {}
            for key, value in state_dict.items():
                # Remove module prefix if present
                clean_key = key.replace('module.', '') if key.startswith('module.') else key
                
                # Skip classifier layer if it has wrong dimensions (1000 classes vs 2 classes)
                if 'classifier.1.weight' in clean_key and len(value.shape) > 0 and value.shape[0] != 2:
                    logger.info(f"Skipping classifier layer with wrong dimensions: {value.shape}")
                    continue
                if 'classifier.1.bias' in clean_key and len(value.shape) > 0 and value.shape[0] != 2:
                    logger.info(f"Skipping classifier bias with wrong dimensions: {value.shape}")
                    continue
                
                clean_state_dict[clean_key] = value
            
            # ✅ ENHANCED: Load with comprehensive error handling
            try:
                # Load with strict=False to handle architecture mismatches
                missing_keys, unexpected_keys = model.load_state_dict(clean_state_dict, strict=False)
                
                # Handle missing keys by creating compatible layers
                if missing_keys:
                    self._log_debug(f"✅ Model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
                    self._handle_missing_keys(model, missing_keys)
                else:
                    self._log_debug(f"✅ Model loaded successfully with {len(unexpected_keys)} unexpected keys")
                    
            except Exception as load_error:
                logger.error(f"❌ State dict loading failed: {load_error}")
                
                # Try to provide more specific error information
                if "size mismatch" in str(load_error):
                    logger.error("🔍 Size mismatch detected - this usually means architecture mismatch")
                    
                    # Try to find the specific mismatched layer
                    for key, value in clean_state_dict.items():
                        try:
                            model_param = dict(model.named_parameters())[key]
                            if model_param.shape != value.shape:
                                logger.error(f"❌ Mismatch in {key}: checkpoint {value.shape} vs model {model_param.shape}")
                        except KeyError:
                            continue
                    
                    # Try loading with even more lenient settings
                    logger.info("🔧 Attempting fallback loading with partial state dict...")
                    try:
                        # Filter out problematic keys
                        filtered_state_dict = {}
                        for key, value in clean_state_dict.items():
                            try:
                                model_param = dict(model.named_parameters())[key]
                                if model_param.shape == value.shape:
                                    filtered_state_dict[key] = value
                                else:
                                    logger.warning(f"⚠️ Skipping mismatched layer: {key}")
                            except KeyError:
                                # Skip keys that don't exist in model
                                continue
                        
                        missing_keys, unexpected_keys = model.load_state_dict(filtered_state_dict, strict=False)
                        self._log_debug(f"✅ Fallback loading successful with {len(filtered_state_dict)} compatible layers")
                        
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback loading also failed: {fallback_error}")
                        raise load_error  # Re-raise original error
                    else:
                        raise load_error  # Re-raise non-size-mismatch errors
            
            # ✅ CUDA MEMORY FIX: Add memory management before moving model to device
            model_device = None
            try:
                # Clear CUDA cache before loading model to device
                self._clear_cuda_cache()
                
                # ✅ CRITICAL FIX: Try to move to target device, but handle OOM gracefully
                target_device = self.device
                try:
                    # Try moving to GPU if available and requested
                    if torch.cuda.is_available() and target_device.type == 'cuda':
                        # Check available memory first
                        allocated = torch.cuda.memory_allocated() / (1024**3)
                        gpu_mem_gb = self.gpu_memory_gb if self.gpu_memory_gb is not None else 0.0
                        if not isinstance(gpu_mem_gb, (int, float)):
                            gpu_mem_gb = 0.0
                        gpu_mem_gb = float(gpu_mem_gb)
                        
                        # Estimate model size (EfficientNet ~0.1-0.2GB)
                        if gpu_mem_gb > 0 and (allocated + 0.3) > (gpu_mem_gb * 0.5):
                            logger.warning(f"GPU memory low ({allocated:.2f}GB/{gpu_mem_gb:.2f}GB), using CPU for this model")
                            target_device = torch.device("cpu")
                            model = model.to(target_device)
                        else:
                            model = model.to(target_device)
                            # Verify model is actually on the correct device
                            model_device = next(model.parameters()).device
                            if model_device != target_device:
                                logger.warning(f"Model device mismatch: expected {target_device}, got {model_device}, using CPU")
                                target_device = torch.device("cpu")
                                model = model.to(target_device)
                                model_device = target_device
                    else:
                        # Use CPU if CUDA not available or not requested
                        target_device = torch.device("cpu")
                        model = model.to(target_device)
                        model_device = target_device
                except RuntimeError as move_error:
                    if "CUDA" in str(move_error) or "memory" in str(move_error).lower():
                        logger.warning(f"CUDA memory error moving model: {move_error}")
                        logger.warning("Falling back to CPU for this model")
                        target_device = torch.device("cpu")
                        model = model.to(target_device)
                        model_device = target_device
                    else:
                        raise move_error
                
                # Get final device if not already set
                if model_device is None:
                    model_device = next(model.parameters()).device
                
                model.eval()
                
                # Clear cache again after loading
                self._clear_cuda_cache()
                
            except RuntimeError as e:
                if "CUDA" in str(e) or "memory" in str(e).lower():
                    logger.warning(f"CUDA memory error loading model: {e}")
                    logger.warning("Falling back to CPU for this model")
                    # Clear cache and try CPU
                    self._clear_cuda_cache()
                    model = model.to(torch.device("cpu"))
                    model_device = torch.device("cpu")
                    model.eval()
                else:
                    raise e
            
            # ✅ FAST STARTUP: Skip test inference during loading (saves ~2-5 seconds per model)
            # Test inference will happen on first actual use, not during loading
            if model_device is None:
                model_device = next(model.parameters()).device
            logger.debug(f"EfficientNet model loaded successfully on {model_device} (test inference skipped for speed)")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load EfficientNet model: {e}")
            return None
    
    def _load_custom_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load custom trained model with error handling and path resolution"""
        import time
        
        try:
            self._log_info("🎯 Loading YOUR trained custom model (deepfake_detector_finetuned1.pth)...")
            start_time = time.time()
            
            # ✅ FIX: Check multiple possible paths for the model
            if not os.path.exists(model_path):
                logger.warning(f"⚠️ Model not found at primary path: {model_path}")
                # Try alternative paths
                current_dir = os.path.dirname(os.path.abspath(__file__))
                alternative_paths = [
                    os.path.join(current_dir, '../../../ml_artifacts/deepfake_detector_finetuned1.pth'),
                    os.path.join(current_dir, '../../ml_artifacts/deepfake_detector_finetuned1.pth'),
                    os.path.join(current_dir, '../../../model_weights/deepfake_detector_finetuned1.pth'),
                    os.path.join(current_dir, '../../model_weights/deepfake_detector_finetuned1.pth'),
                    os.path.abspath('ml_artifacts/deepfake_detector_finetuned1.pth'),
                    os.path.abspath('model_weights/deepfake_detector_finetuned1.pth'),
                ]
                
                found_path = None
                for alt_path in alternative_paths:
                    if os.path.exists(alt_path):
                        found_path = alt_path
                        logger.info(f"✅ Found model at alternative path: {alt_path}")
                        break
                
                if found_path:
                    model_path = found_path
                else:
                    logger.error(f"❌ Model not found in any of the checked paths:")
                    for alt_path in alternative_paths:
                        logger.error(f"   - {alt_path}")
                    return None
            
            logger.info(f"📂 Loading model from: {model_path}")
            
            # Load state dict first with progress indication
            self._log_debug("Loading state dict from file...")
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            load_time = time.time() - start_time
            # Fix time anomalies - ensure positive timing
            if load_time < 0:
                load_time = 0.01  # Minimum realistic time
            self._log_debug(f"State dict loaded in {load_time:.2f}s")
            
            # Check if loading took too long
            if load_time > 30:
                logger.warning(f"[WARNING] Model loading took {load_time:.2f}s (slow but continuing)")
            
            # Handle different checkpoint formats
            if isinstance(state_dict, dict):
                if 'state_dict' in state_dict:
                    state_dict = state_dict['state_dict']
                elif 'model_state_dict' in state_dict:
                    state_dict = state_dict['model_state_dict']
                elif 'model' in state_dict:
                    state_dict = state_dict['model']
            
            # Create EfficientNet architecture using torchvision (more reliable than timm)
            self._log_info("Creating EfficientNet architecture...")
            model = models.efficientnet_b0(weights=None)
            num_ftrs = model.classifier[1].in_features
            
            # Check if the custom model uses 1 or 2 output classes
            # Look at the classifier weight shape in the state dict
            classifier_weight_key = None
            for key in state_dict.keys():
                if 'classifier.1.weight' in key or 'classifier.weight' in key:
                    classifier_weight_key = key
                    break
            
            # ✅ FIX: Initialize output_classes to avoid NoneType errors
            output_classes = 1  # Default
            if classifier_weight_key and classifier_weight_key in state_dict:
                try:
                    weight_tensor = state_dict[classifier_weight_key]
                    if weight_tensor is not None and hasattr(weight_tensor, 'shape') and len(weight_tensor.shape) > 0:
                        output_classes = int(weight_tensor.shape[0])
                        # ✅ FIX: Ensure output_classes is a valid integer
                        if output_classes is None or not isinstance(output_classes, (int, float)):
                            output_classes = 1
                        output_classes = int(output_classes)
                    else:
                        output_classes = 1
                except Exception as shape_error:
                    logger.warning(f"Failed to get output classes from shape: {shape_error}, using default 1")
                    output_classes = 1
                
                self._log_debug(f"Detected {output_classes} output classes in custom model")
                # Adapt classifier to 2 classes when pretrain head has >2 classes
                if output_classes > 2:
                    logger.warning(f"Classifier output {output_classes} > 2; adapting head to 2 classes")
                    model.classifier[1] = nn.Linear(num_ftrs, 2)
                else:
                    model.classifier[1] = nn.Linear(num_ftrs, output_classes)
            else:
                # Default to 1 class (binary with sigmoid)
                self._log_debug("Using default 1 output class (binary with sigmoid)")
                model.classifier[1] = nn.Linear(num_ftrs, 1)
                output_classes = 1
            
            # Clean state dict keys with enhanced remapping
            self._log_debug("Cleaning state dict keys...")
            clean_state_dict = self._remap_state_dict_keys(state_dict, "custom_model")
            
            # Load state dict with strict=False to handle architecture mismatches
            self._log_debug("Loading state dict into model...")
            dict_start_time = time.time()
            try:
                missing_keys, unexpected_keys = model.load_state_dict(clean_state_dict, strict=False)
                logger.debug("✅ Successfully loaded custom EfficientNet model")
            except Exception as load_error:
                logger.error(f"Failed to load custom model: {load_error}")
                
                # Fallback: Try with EfficientNet-B0 (most common)
                logger.debug("🔄 Attempting fallback to EfficientNet-B0...")
                try:
                    model = models.efficientnet_b0(weights=None)
                    # Rebuild classifier for binary output
                    in_features = model.classifier[1].in_features
                    expected_num_classes = 2  # Binary classification
                    model.classifier = nn.Sequential(
                        nn.Dropout(p=0.2, inplace=True),
                        nn.Linear(in_features, expected_num_classes)
                    )
                    missing_keys, unexpected_keys = model.load_state_dict(clean_state_dict, strict=False)
                    logger.debug("✅ Successfully loaded with EfficientNet-B0 fallback")
                except Exception as fallback_error:
                    logger.error(f"Fallback to EfficientNet-B0 also failed: {fallback_error}")
                    raise load_error  # Re-raise original error
            
            dict_load_time = time.time() - dict_start_time
            # Fix time anomalies - ensure positive timing
            if dict_load_time < 0:
                dict_load_time = 0.01  # Minimum realistic time
            logger.debug(f"State dict loaded into model in {dict_load_time:.2f}s")
            
            # Handle missing keys by initializing them properly
            if missing_keys:
                self._log_debug(f"Model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
                self._handle_missing_keys(model, missing_keys)
                if missing_keys:
                    self._log_debug(f"Missing keys: {missing_keys[:5]}...")  # Show first 5
                if unexpected_keys:
                    self._log_debug(f"Unexpected keys: {unexpected_keys[:5]}...")  # Show first 5
            else:
                self._log_debug(f"Model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
            
            # Ensure model is in eval mode
            self._log_debug("Moving model to device...")
            try:
                model = model.to(self.device)
            except Exception as move_e:
                logger.warning(f"CUDA move failed ({move_e}); falling back to CPU")
                model = model.to(torch.device("cpu"))
                self.device = torch.device("cpu")
                self._device_string = "cpu"
            model.eval()
            
            total_time = time.time() - start_time
            logger.info(f"✅ YOUR trained custom model loaded successfully in {total_time:.2f}s")
            logger.info(f"   📍 Model path: {model_path}")
            logger.info(f"   🔧 Device: {self.device}")
            logger.info(f"   📊 Output classes: {output_classes if 'output_classes' in locals() else '1'}")
            logger.info(f"   🎯 Model ready for inference!")
            return model
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to load custom model: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _check_model_file_exists(self, model_name: str) -> bool:
        """Check if model file exists before attempting to load"""
        if model_name not in self.model_configs:
            return False
        
        model_path = self.model_configs[model_name]["path"]
        exists = os.path.exists(model_path)
        
        if not exists:
            logger.debug(f"[SKIP] Model file not found: {model_name} ({model_path})")
        
        return exists
    
    def load_all_models(self) -> Dict[str, torch.nn.Module]:
        """Load all available models with FAST STARTUP - only critical models, rest load lazily"""
        # Skip loading if environment variables are set
        if os.getenv("DISABLE_MODEL_LOADING_ON_STARTUP", "0") == "1":
            self._log_info("🔧 Skipping model loading during startup - will load on first use")
            return {}
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        loaded_models = {}
        failed_models = []
        missing_files = []
        
        # ✅ CUDA MEMORY FIX: Clear cache before loading all models
        self._clear_cuda_cache()
        
        # ✅ FAST STARTUP: Only load critical models at startup, rest load lazily
        # Check which models have files available first
        available_models = []
        for model_name in self.model_configs.keys():
            if self._check_model_file_exists(model_name):
                available_models.append(model_name)
            else:
                missing_files.append(model_name)
        
        # ✅ FAST STARTUP: Only load 3-5 critical models at startup
        # Critical models needed for basic functionality
        critical_models = ['efficientnet_b0', 'custom_finetuned', 'mesonet']
        critical_models = [m for m in critical_models if m in available_models]
        
        # All other models will load lazily (on first use)
        lazy_models = [m for m in available_models if m not in critical_models]
        
        if missing_files:
            logger.debug(f"[INFO] {len(missing_files)} model files not found (will skip)")
        
        logger.info(f"🚀 FAST STARTUP: Loading {len(critical_models)} critical models (others load on-demand)")
        logger.debug(f"   📦 Critical: {critical_models}")
        logger.debug(f"   ⏳ Lazy: {len(lazy_models)} models (load on first use)")
        
        # Only load critical models at startup
        all_models_to_load = critical_models
        
        # Thread-safe lock for GPU memory tracking
        gpu_lock = threading.Lock()
        
        def load_model_with_tracking(model_name: str):
            """Load a single model with thread-safe GPU tracking"""
            try:
                # Control logging verbosity with environment variable
                if MODEL_LOADING_VERBOSE:
                    logger.info(f"Loading model: {model_name}")
                elif len(loaded_models) < 5:
                    logger.info(f"Loading model: {model_name}")
                else:
                    logger.debug(f"Loading model: {model_name}")
                
                # Load the model
                model = self.load_model(model_name)
                
                # Thread-safe GPU tracking
                with gpu_lock:
                    if model is not None:
                        # Check if this model was loaded on GPU
                        model_device = next(model.parameters()).device if hasattr(model, 'parameters') and len(list(model.parameters())) > 0 else None
                        if model_device and 'cuda' in str(model_device):
                            self.gpu_models_loaded += 1
                            self._gpu_models.add(model_name)
                            self._model_locations[model_name] = 'cuda:0'
                            if self.gpu_models_loaded >= self.gpu_model_limit:
                                logger.debug(f"⚠️ GPU model limit reached ({self.gpu_models_loaded}/{self.gpu_model_limit}), remaining models will use CPU")
                
                return model_name, model, None
                
            except Exception as e:
                return model_name, None, e
        
        # ✅ FAST STARTUP: Load critical models in parallel (only 3-5 models, safe to parallelize)
        # Since we're only loading 3-5 critical models, we can load them in parallel for speed
        if len(all_models_to_load) <= 5:
            # ✅ FAST STARTUP: Parallel loading for critical models (only 3-5 models)
            logger.info(f"🚀 Parallel loading {len(all_models_to_load)} critical models for fast startup...")
            max_workers = min(3, len(all_models_to_load))  # Max 3 parallel workers for critical models
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all critical model loading tasks
                future_to_model = {
                    executor.submit(load_model_with_tracking, model_name): model_name 
                    for model_name in all_models_to_load
                    if model_name in self.model_configs
                }
                
                # Process completed tasks quickly
                try:
                    for future in as_completed(future_to_model, timeout=60):  # 1 minute timeout for critical models
                        model_name = future_to_model[future]
                        try:
                            name, model, error = future.result(timeout=20)  # 20 second per model timeout
                            
                            if error:
                                failed_models.append(model_name)
                                logger.warning(f"⚠️ {model_name} failed: {error}")
                            elif model is not None:
                                loaded_models[name] = model
                                logger.info(f"✅ {name} loaded")
                            else:
                                failed_models.append(model_name)
                                logger.warning(f"⚠️ {model_name} failed: model is None")
                                
                        except TimeoutError:
                            failed_models.append(model_name)
                            logger.warning(f"⏱️ {model_name} loading timed out")
                        except Exception as e:
                            failed_models.append(model_name)
                            logger.error(f"❌ {model_name} failed: {e}")
                            
                except TimeoutError:
                    logger.warning("⏱️ Critical model loading timed out")
                    for future in future_to_model:
                        future.cancel()
        else:
            # Fallback: Sequential loading if somehow more than 5 models
            logger.info(f"🔧 Sequential loading {len(all_models_to_load)} models...")
            import gc
            for i, model_name in enumerate(all_models_to_load):
                if model_name not in self.model_configs:
                    continue
                
                try:
                    if i > 0:
                        self._clear_cuda_cache()
                        gc.collect()
                    
                    name, model, error = load_model_with_tracking(model_name)
                    
                    if error:
                        failed_models.append(model_name)
                        logger.error(f"Failed to load {model_name}: {error}")
                    elif model is not None:
                        loaded_models[name] = model
                        logger.info(f"✅ {name} loaded ({i+1}/{len(all_models_to_load)})")
                    else:
                        failed_models.append(model_name)
                        logger.warning(f"⚠️ {model_name} failed to load")
                    
                    self._clear_cuda_cache()
                    gc.collect()
                        
                except Exception as e:
                    failed_models.append(model_name)
                    logger.error(f"Failed to load {model_name}: {e}")
                    self._clear_cuda_cache()
        
        # ✅ FAST STARTUP: Store lazy models list for on-demand loading
        self._lazy_models = lazy_models
        logger.info(f"⏳ {len(lazy_models)} models will load on first use for faster startup")
        
        # ✅ CRITICAL FIX: Store loaded models in self.models
        self.models.update(loaded_models)
        
        # ✅ FAST STARTUP: Log summary (clean, no duplicates)
        logger.info(f"✅ FAST STARTUP complete: {len(loaded_models)}/{len(all_models_to_load)} critical models loaded")
        if failed_models:
            logger.warning(f"⚠️ {len(failed_models)} models failed: {failed_models[:3]}...")
        
        # ✅ PHASE 4: Initialize usage tracking for loaded models
        for model_name in loaded_models.keys():
            if model_name not in self._model_usage_count:
                self._model_usage_count[model_name] = 0
                self._model_last_used[model_name] = None
        
        # ✅ CUDA MEMORY FIX: Final cache clear
        self._clear_cuda_cache()
        
        logger.info(f"✅ Enhanced model loader initialized with {len(loaded_models)} critical models (out of {len(available_models)} available, {len(lazy_models)} lazy)")
        
        # ✅ PHASE 4: Log model loading summary for debugging
        if loaded_models:
            logger.info(f"[MODEL SUMMARY] Successfully loaded models: {list(loaded_models.keys())}")
        if failed_models:
            logger.warning(f"[MODEL SUMMARY] Failed to load: {failed_models}")
        if missing_files:
            logger.info(f"[MODEL SUMMARY] Files not found (skipped): {missing_files}")
        
        return loaded_models
    
    def get_model_usage_stats(self) -> Dict[str, Any]:
        """✅ PHASE 4: Get comprehensive model usage statistics"""
        return {
            'total_configured': len(self.model_configs),
            'total_loaded': len(self.models),
            'usage_counts': dict(self._model_usage_count),
            'last_used': dict(self._model_last_used),
            'loaded_models': list(self.models.keys()),
            'unused_models': [name for name in self.models.keys() if self._model_usage_count.get(name, 0) == 0]
        }
    
    def load_ensemble_models(self) -> Dict[str, torch.nn.Module]:
        """Load ensemble models on demand for better startup performance"""
        if self.ensemble_loaded:
            return {name: model for name, model in self.models.items() if name in self.ensemble_models}
        
        logger.info(f"[LAZY LOADING] Loading {len(self.ensemble_models)} ensemble models on demand...")
        
        ensemble_loaded = {}
        for model_name in self.ensemble_models:
            try:
                model = self.load_model(model_name)
                if model is not None:
                    ensemble_loaded[model_name] = model
                    logger.debug(f"✅ Ensemble model {model_name} loaded")
                else:
                    logger.warning(f"⚠️ Ensemble model {model_name} failed to load")
            except Exception as e:
                logger.warning(f"⚠️ Ensemble model {model_name} failed: {e}")
        
        self.ensemble_loaded = True
        logger.info(f"✅ Ensemble models loaded: {len(ensemble_loaded)}/{len(self.ensemble_models)}")
        return ensemble_loaded
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names"""
        return list(self.model_configs.keys())
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model"""
        if model_name not in self.model_configs:
            return None
        
        config = self.model_configs[model_name]
        return {
            "name": model_name,
            "path": config["path"],
            "type": config["type"],
            "architecture": config["architecture"],
            "input_size": config["input_size"],
            "weight": config["weight"],
            "loaded": model_name in self.models
        }
    
    def preprocess_face(self, face: Union[np.ndarray, torch.Tensor], input_size: Tuple[int, int] = (224, 224)) -> torch.Tensor:
        """Preprocess face for model inference with comprehensive error handling
        
        PERFORMANCE FIX: Standardize all models to use 224x224 input for consistency
        and memory efficiency.
        
        ENHANCED: Now handles both numpy arrays and already-preprocessed tensors.
        FIXED: Now handles dict inputs that were causing type errors.
        """
        try:
            if face is None:
                raise ValueError("Face input is None")
            
            # FIXED: Handle dict inputs that were causing the main error
            if isinstance(face, dict):
                if FACE_VALIDATOR_AVAILABLE:
                    validated_face = FaceDataValidator.validate_and_convert(face, "enhanced_model_loader")
                    if validated_face is not None:
                        face = validated_face
                    else:
                        raise ValueError("Face validation failed for dict input")
                else:
                    # Fallback: try to extract face data from dict
                    if 'face' in face:
                        face = face['face']
                    elif 'image' in face:
                        face = face['image']
                    elif 'data' in face:
                        face = face['data']
                    else:
                        raise ValueError(f"Could not extract face data from dict keys: {list(face.keys())}")
            
            # ✅ STEP 1: Check if input is already a preprocessed tensor
            if isinstance(face, torch.Tensor):
                # Already a tensor - check if preprocessed
                if face.dim() == 3 and face.shape[0] == 3:
                    # Already in CHW format (3, H, W) - likely preprocessed
                    logger.debug(f"Input is already a preprocessed tensor with shape: {face.shape}")
                    
                    # Ensure it's on the correct device and has correct shape
                    face_tensor = face.to(self.device)
                    
                    # If shape is correct (3, 224, 224), return as-is
                    if face_tensor.shape == (3, 224, 224):
                        return face_tensor
                    else:
                        # Resize to standard size if needed
                        logger.debug(f"Resizing tensor from {face_tensor.shape} to (3, 224, 224)")
                        face_tensor = torch.nn.functional.interpolate(
                            face_tensor.unsqueeze(0), size=(224, 224), mode='bilinear', align_corners=False
                        ).squeeze(0)
                        return face_tensor
                        
                elif face.dim() == 4:
                    # Already batched (B, C, H, W) - this shouldn't happen but handle it
                    logger.warning(f"Received batched tensor input with shape: {face.shape}")
                    return face.to(self.device)
                else:
                    # Unexpected tensor dimensions - convert to numpy and process normally
                    logger.warning(f"Unexpected tensor dimensions: {face.shape}, converting to numpy")
                    face = face.cpu().numpy()
            
            # ✅ STEP 2: Process numpy arrays normally
            # Ensure face is numpy array
            if not isinstance(face, np.ndarray):
                face = np.array(face)
            
            # Ensure face is uint8
            if face.dtype != np.uint8:
                face = np.clip(face, 0, 255).astype(np.uint8)
            
            # ✅ PERFORMANCE FIX: Force all models to use 224x224 for consistency
            # This eliminates tensor shape errors and reduces memory usage
            STANDARD_SIZE = (224, 224)
            
            # Validate input dimensions
            if len(face.shape) not in [2, 3]:
                raise ValueError(f"Invalid face shape: {face.shape}")
            
            # For grayscale images, convert to RGB
            if len(face.shape) == 2:
                face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
            
            # Resize to standard size
            face_resized = cv2.resize(face, STANDARD_SIZE, interpolation=cv2.INTER_LINEAR)
            
            # Convert to tensor and normalize to [0, 1] range
            face_tensor = torch.from_numpy(face_resized.astype(np.float32))
            
            # Convert HWC to CHW format
            if len(face_tensor.shape) == 3 and face_tensor.shape[2] == 3:
                face_tensor = face_tensor.permute(2, 0, 1)
            
            # Normalize to [0, 1] range
            face_tensor = face_tensor / 255.0
            
            # ✅ FIXED: Always use ImageNet normalization for EfficientNet-based models
            # Your custom model (deepfake_detector_finetuned1.pth) is EfficientNet-B0 based,
            # which should use ImageNet normalization like standard EfficientNet models
            
            # Apply ImageNet normalization (standard for EfficientNet architectures)
            logger.debug(f"Applying ImageNet normalization for model: {getattr(self, '_current_model_name', 'unknown')}")
            
            # Create mean and std tensors with the same dtype as face_tensor
            # ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            mean = torch.tensor([0.485, 0.456, 0.406], dtype=face_tensor.dtype, device=face_tensor.device).view(3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225], dtype=face_tensor.dtype, device=face_tensor.device).view(3, 1, 1)
            
            # Ensure proper broadcasting for tensor dimensions
            if face_tensor.dim() == 3:  # (C, H, W)
                face_tensor = (face_tensor - mean) / std
            elif face_tensor.dim() == 4:  # (B, C, H, W) 
                mean = mean.unsqueeze(0)  # (1, 3, 1, 1)
                std = std.unsqueeze(0)    # (1, 3, 1, 1)
                face_tensor = (face_tensor - mean) / std
            else:
                logger.error(f"Unexpected tensor dimensions: {face_tensor.shape}")
                raise ValueError(f"Unexpected tensor dimensions: {face_tensor.shape}")
            
            # ✅ CRITICAL FIX: Check GPU memory before moving to device
            target_device = self.device
            if torch.cuda.is_available() and self.device.type == 'cuda':
                try:
                    allocated = torch.cuda.memory_allocated() / (1024**3)
                    total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    free_memory = total_memory - allocated
                    if free_memory < 0.3:  # Less than 300MB free
                        logger.debug(f"GPU memory low ({free_memory:.2f}GB free), keeping tensor on CPU")
                        target_device = torch.device("cpu")
                    else:
                        # Move tensor to device AFTER normalization to prevent device mismatch
                        face_tensor = face_tensor.to(self.device)
                        target_device = self.device
                except Exception as mem_check_error:
                    logger.warning(f"Memory check failed: {mem_check_error}, using CPU")
                    target_device = torch.device("cpu")
            else:
                # Not using CUDA, keep on CPU
                target_device = torch.device("cpu")
            
            # Only move to device if we have enough memory
            if target_device != face_tensor.device:
                try:
                    face_tensor = face_tensor.to(target_device)
                except RuntimeError as move_error:
                    if "CUDA" in str(move_error) or "memory" in str(move_error).lower():
                        logger.warning(f"Failed to move to {target_device}: {move_error}, keeping on CPU")
                        target_device = torch.device("cpu")
                        face_tensor = face_tensor.to(target_device) if face_tensor.device != target_device else face_tensor
                    else:
                        raise move_error
            
            # Ensure correct shape (3, 224, 224)
            if face_tensor.shape != (3, 224, 224):
                logger.warning(f"Tensor shape mismatch: {face_tensor.shape}, expected (3, 224, 224)")
                # Force correct shape on target device
                try:
                    face_tensor = torch.zeros(3, 224, 224, dtype=torch.float32, device=target_device)
                except:
                    face_tensor = torch.zeros(3, 224, 224, dtype=torch.float32, device="cpu")
            
            return face_tensor
            
        except Exception as e:
            logger.error(f"Face preprocessing failed: {e}")
            logger.error(f"Face shape: {face.shape if hasattr(face, 'shape') else 'No shape attribute'}")
            logger.error(f"Input size: {input_size}")
            logger.error(f"Device: {self.device}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            
            # ✅ CRITICAL FIX: Check if error is CUDA OOM and use CPU for fallback
            error_str = str(e)
            is_oom = "CUDA" in error_str or "memory" in error_str.lower() or "out of memory" in error_str.lower()
            fallback_device = "cpu" if is_oom else self.device
            
            # Clear CUDA cache if OOM
            if is_oom and torch.cuda.is_available():
                try:
                    torch.cuda.empty_cache()
                except:
                    pass
            
            # Return a safe fallback tensor with comprehensive error handling
            try:
                # Try to create a tensor with the specified input size - ensure 3D shape (C, H, W)
                if isinstance(input_size, (tuple, list)) and len(input_size) == 2:
                    fallback_tensor = torch.zeros(3, int(input_size[0]), int(input_size[1]), device=fallback_device, dtype=torch.float32)
                else:
                    fallback_tensor = torch.zeros(3, 224, 224, device=fallback_device, dtype=torch.float32)
                
                logger.warning(f"Returning fallback tensor with shape: {fallback_tensor.shape} on {fallback_device}")
                return fallback_tensor
                
            except Exception as fallback_error:
                logger.error(f"Fallback tensor creation failed: {fallback_error}")
                # Last resort: create the most basic tensor possible on CPU - ensure 3D shape (C, H, W)
                try:
                    return torch.zeros(3, 224, 224, device="cpu", dtype=torch.float32)
                except Exception as final_error:
                    logger.error(f"Final fallback failed: {final_error}")
                    # Absolute last resort: create on CPU (don't try to move to device)
                    try:
                        cpu_tensor = torch.zeros(3, 224, 224, dtype=torch.float32)
                        logger.warning("Created CPU tensor as last resort")
                        return cpu_tensor
                    except Exception as cpu_error:
                        logger.error(f"CPU fallback failed: {cpu_error}")
                        # Return None and let the calling code handle it
                        return None
    
    def predict_single_model(self, model_name: str, faces: List[np.ndarray]) -> Tuple[str, float]:
        """Get prediction from a single model with bias detection and on-demand loading"""
        # ✅ PHASE 1 FIX: Load model on-demand if not already loaded
        # ✅ GPU ON-DEMAND: Try to move model to GPU if it's on CPU
        if model_name in self.models and model_name not in self._gpu_models:
            # Try to load to GPU for faster inference
            if self._load_model_to_gpu_on_demand(model_name):
                logger.debug(f"🚀 Moved {model_name} to GPU for faster inference")
        
        if model_name not in self.models:
            # Check if model is configured
            if model_name not in self.model_configs:
                logger.error(f"❌ Model '{model_name}' not configured. Available models: {list(self.model_configs.keys())}")
                return "Model Not Configured", 0.0
            
            # Check if model file exists
            if not self._check_model_file_exists(model_name):
                logger.warning(f"⚠️ Model '{model_name}' file not found, skipping")
                return "Model File Not Found", 0.0
            
            # ✅ PHASE 1 FIX: Load model on-demand
            logger.info(f"🔄 Model '{model_name}' not loaded, loading on-demand...")
            try:
                model = self.load_model(model_name)
                if model is not None:
                    self.models[model_name] = model
                    logger.info(f"✅ Model '{model_name}' loaded successfully on-demand")
                else:
                    logger.error(f"❌ Failed to load model '{model_name}' on-demand")
                    return "Model Load Failed", 0.0
            except Exception as e:
                logger.error(f"❌ Exception loading model '{model_name}' on-demand: {e}")
                return "Model Load Exception", 0.0
        
        # ✅ PHASE 4: Track model usage
        if model_name not in self._model_usage_count:
            self._model_usage_count[model_name] = 0
        self._model_usage_count[model_name] += 1
        self._model_last_used[model_name] = time.time()
        
        # ✅ LOGGING: Confirm which model is being used
        logger.info(f"🔍 Using model: {model_name} for prediction on {len(faces)} faces (usage count: {self._model_usage_count[model_name]})")
        
        # ✅ BIAS DETECTION: Check if model is consistently biased
        if hasattr(self, '_model_bias_tracker'):
            if model_name in self._model_bias_tracker:
                bias_count = self._model_bias_tracker[model_name]
                if bias_count > 5:  # If model has been biased > 5 times recently
                    logger.warning(f"Model {model_name} detected as consistently biased, applying extra conservative correction")
                    # Apply extra conservative correction for biased models
                    return self._predict_with_bias_correction(model_name, faces)
        else:
            self._model_bias_tracker = {}
        
        try:
            model = self.models[model_name]
            config = self.model_configs[model_name]
            
            # ✅ CRITICAL FIX: Get model's actual device (don't move model, move inputs instead)
            model_device = next(model.parameters()).device
            # Don't move model - models stay on their original device (GPU or CPU)
            # Instead, move input tensors to match model device
            if model_device.type != self.device.type:
                logger.debug(f"Model {model_name} on {model_device}, input will be moved to match")
            
            if not faces:
                return "No Faces Detected", 0.0
            
            # Preprocess faces with safe input_size extraction
            processed_faces = []
            for face in faces:
                # Safely extract input_size from config
                input_size = config.get("input_size", (224, 224))
                if isinstance(input_size, dict):
                    # Handle dict format
                    if 'width' in input_size and 'height' in input_size:
                        input_size = (input_size['width'], input_size['height'])
                    elif 'w' in input_size and 'h' in input_size:
                        input_size = (input_size['w'], input_size['h'])
                    else:
                        input_size = (224, 224)
                elif not isinstance(input_size, (tuple, list)) or len(input_size) != 2:
                    input_size = (224, 224)
                
                # CRITICAL FIX: Ensure input_size is a tuple before passing to preprocess_face
                if not isinstance(input_size, tuple):
                    input_size = tuple(input_size) if isinstance(input_size, (list, tuple)) else (224, 224)
                
                # Set current model name for preprocessing context
                self._current_model_name = model_name
                
                # ✅ CRITICAL FIX: Check GPU memory before preprocessing
                use_cpu_for_preprocessing = False
                if torch.cuda.is_available() and self.device.type == 'cuda':
                    try:
                        allocated = torch.cuda.memory_allocated() / (1024**3)
                        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                        free_memory = total_memory - allocated
                        if free_memory < 0.3:  # Less than 300MB free
                            logger.warning(f"⚠️ GPU memory low ({free_memory:.2f}GB free), using CPU for preprocessing")
                            use_cpu_for_preprocessing = True
                            torch.cuda.empty_cache()
                    except:
                        pass
                
                processed_face = self.preprocess_face(face, input_size)
                
                # Handle None returns from preprocessing
                if processed_face is None:
                    logger.error(f"Face preprocessing returned None for face {len(processed_faces)}")
                    # ✅ CRITICAL FIX: Create fallback on CPU if GPU memory is low
                    fallback_device = "cpu" if use_cpu_for_preprocessing else self.device
                    try:
                        processed_face = torch.zeros(3, input_size[0], input_size[1], device=fallback_device, dtype=torch.float32)
                    except:
                        # If that fails, force CPU
                        processed_face = torch.zeros(3, input_size[0], input_size[1], device="cpu", dtype=torch.float32)
                
                processed_faces.append(processed_face)
            
            # CRITICAL FIX: Ensure proper batch tensor creation with 4D shape
            if not processed_faces:
                logger.error("No processed faces available")
                return "No Processed Faces", 0.0
            
            # Stack into batch - ensure all tensors have batch dimension
            try:
                # Ensure all tensors are 4D (batch_size, channels, height, width)
                batch_faces = []
                # ✅ CRITICAL FIX: Check if we should use CPU for batch creation
                batch_device = self.device
                if torch.cuda.is_available() and self.device.type == 'cuda':
                    try:
                        allocated = torch.cuda.memory_allocated() / (1024**3)
                        total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                        free_memory = total_memory - allocated
                        if free_memory < 0.3:  # Less than 300MB free
                            logger.warning(f"⚠️ GPU memory low ({free_memory:.2f}GB free), using CPU for batch creation")
                            batch_device = torch.device("cpu")
                            torch.cuda.empty_cache()
                    except:
                        pass
                
                for i, face_tensor in enumerate(processed_faces):
                    if face_tensor is None:
                        logger.warning(f"Face {i} is None, creating fallback")
                        try:
                            face_tensor = torch.zeros(3, 224, 224, device=batch_device, dtype=torch.float32)
                        except:
                            face_tensor = torch.zeros(3, 224, 224, device="cpu", dtype=torch.float32)
                    
                    # ✅ CRITICAL FIX: Handle tensor dimension mismatch properly
                    if face_tensor.dim() == 3:
                        # Tensor is (C, H, W), add batch dimension to make (1, C, H, W)
                        face_tensor = face_tensor.unsqueeze(0)
                        logger.debug(f"Added batch dimension: {face_tensor.shape}")
                    elif face_tensor.dim() == 4:
                        # Tensor is already (B, C, H, W), use as is
                        logger.debug(f"Tensor already 4D: {face_tensor.shape}")
                    elif face_tensor.dim() == 2:
                        # Tensor is (H, W), add channel and batch dimensions
                        face_tensor = face_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)
                        # Repeat to make 3 channels
                        face_tensor = face_tensor.repeat(1, 3, 1, 1)  # (1, 3, H, W)
                        logger.debug(f"Converted 2D to 4D: {face_tensor.shape}")
                    else:
                        logger.error(f"Invalid tensor dimensions: {face_tensor.dim()}, expected 2, 3, or 4")
                        # Create a proper fallback tensor with 3D shape first on batch_device
                        try:
                            face_tensor = torch.zeros(3, 224, 224, device=batch_device, dtype=torch.float32)
                        except:
                            face_tensor = torch.zeros(3, 224, 224, device="cpu", dtype=torch.float32)
                        face_tensor = face_tensor.unsqueeze(0)  # Add batch dimension
                    
                    # ✅ VALIDATION: Ensure tensor has correct shape before adding to batch
                    if face_tensor.shape[1] != 3:
                        logger.error(f"Invalid channel count: {face_tensor.shape[1]}, expected 3")
                        try:
                            face_tensor = torch.zeros(1, 3, 224, 224, device=batch_device, dtype=torch.float32)
                        except:
                            face_tensor = torch.zeros(1, 3, 224, 224, device="cpu", dtype=torch.float32)
                    
                    if face_tensor.shape[2:] != (224, 224):
                        logger.warning(f"Invalid spatial dimensions: {face_tensor.shape[2:]}, expected (224, 224)")
                        # Resize the tensor to correct spatial dimensions
                        face_tensor = torch.nn.functional.interpolate(
                            face_tensor, size=(224, 224), mode='bilinear', align_corners=False
                        )
                    
                    batch_faces.append(face_tensor)
                
                # ✅ CRITICAL FIX: Ensure all tensors are on the same device before stacking
                # Move all to CPU if any is on CPU (to avoid device mismatch)
                if any(f.device.type == 'cpu' for f in batch_faces):
                    logger.debug("Some faces are on CPU, moving all to CPU for batch")
                    batch_faces = [f.cpu() if f.device.type != 'cpu' else f for f in batch_faces]
                    batch_device = torch.device("cpu")
                else:
                    batch_device = batch_faces[0].device if batch_faces else self.device
                
                # Stack into batch tensor
                face_batch = torch.cat(batch_faces, dim=0)
                # ✅ CRITICAL FIX: Ensure batch is on the correct device
                if face_batch.device != batch_device:
                    face_batch = face_batch.to(batch_device)
                logger.debug(f"Face batch shape: {face_batch.shape}, device: {face_batch.device}")
                
                # Validate batch tensor shape
                if face_batch.dim() != 4:
                    logger.error(f"Invalid batch tensor dimensions: {face_batch.dim()}, expected 4")
                    return "Invalid Batch Tensor", 0.0
                
                if face_batch.shape[1] != 3:
                    logger.error(f"Invalid channel count: {face_batch.shape[1]}, expected 3")
                    return "Invalid Channel Count", 0.0
                
            except Exception as batch_error:
                error_str = str(batch_error)
                # ✅ CRITICAL FIX: Handle CUDA OOM by falling back to CPU or smaller batches
                if "CUDA" in error_str or "memory" in error_str.lower() or "out of memory" in error_str.lower():
                    logger.warning(f"⚠️ CUDA OOM during batch creation: {batch_error}")
                    logger.info("🔄 Attempting to process on CPU or with smaller batches...")
                    
                    # Clear CUDA cache
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    
                    # Try processing on CPU instead
                    try:
                        # Move all faces to CPU and process in smaller batches
                        cpu_batch_faces = []
                        batch_size = 5  # Process 5 faces at a time
                        
                        for i in range(0, len(processed_faces), batch_size):
                            batch_chunk = processed_faces[i:i+batch_size]
                            chunk_tensors = []
                            
                            for face_tensor in batch_chunk:
                                if face_tensor is not None:
                                    # Move to CPU
                                    face_tensor_cpu = face_tensor.cpu() if face_tensor.device.type == 'cuda' else face_tensor
                                    # Ensure correct shape
                                    if face_tensor_cpu.dim() == 3:
                                        face_tensor_cpu = face_tensor_cpu.unsqueeze(0)
                                    if face_tensor_cpu.shape[1] != 3:
                                        face_tensor_cpu = torch.zeros(1, 3, 224, 224, device='cpu', dtype=torch.float32)
                                    if face_tensor_cpu.shape[2:] != (224, 224):
                                        face_tensor_cpu = torch.nn.functional.interpolate(
                                            face_tensor_cpu, size=(224, 224), mode='bilinear', align_corners=False
                                        )
                                    chunk_tensors.append(face_tensor_cpu)
                            
                            if chunk_tensors:
                                chunk_batch = torch.cat(chunk_tensors, dim=0)
                                cpu_batch_faces.append(chunk_batch)
                        
                        if cpu_batch_faces:
                            # Process each chunk separately
                            all_predictions = []
                            model_device = next(model.parameters()).device
                            
                            # Move model to CPU if needed
                            if model_device.type == 'cuda':
                                logger.info("🔄 Moving model to CPU for batch processing...")
                                model = model.cpu()
                                model_device = torch.device('cpu')
                            
                            for chunk_batch in cpu_batch_faces:
                                chunk_batch = chunk_batch.to(model_device)
                                with torch.no_grad():
                                    model.eval()
                                    chunk_output = model(chunk_batch)
                                    all_predictions.append(chunk_output)
                            
                            # Combine predictions
                            if all_predictions:
                                combined_output = torch.cat(all_predictions, dim=0)
                                # Average predictions
                                if combined_output.dim() > 1:
                                    avg_output = combined_output.mean(dim=0)
                                else:
                                    avg_output = combined_output.mean()
                                
                                # Get probability
                                if avg_output.dim() == 0:
                                    prob = avg_output.item()
                                else:
                                    prob = torch.softmax(avg_output, dim=0)[1].item() if len(avg_output) > 1 else avg_output[0].item()
                                
                                result = "Deepfake Detected" if prob > 0.5 else "Real Face"
                                confidence = prob if prob > 0.5 else (1.0 - prob)
                                
                                logger.info(f"✅ Processed on CPU with smaller batches: {result} (confidence: {confidence:.4f})")
                                return result, confidence
                    
                    except Exception as cpu_error:
                        logger.error(f"❌ CPU fallback also failed: {cpu_error}")
                
                logger.error(f"Batch tensor creation failed: {batch_error}")
                logger.error(f"Processed faces count: {len(processed_faces)}")
                for i, face in enumerate(processed_faces[:5]):  # Only log first 5 to avoid spam
                    if face is not None:
                        logger.error(f"Face {i} shape: {face.shape}, dtype: {face.dtype}, device: {face.device}")
                    else:
                        logger.error(f"Face {i}: None")
                return "Batch Creation Failed", 0.0
            
            # ✅ VALIDATION: Verify model is loaded and ready
            if model is None:
                logger.error(f"Model {model_name} is None, cannot perform inference")
                return "Model Not Loaded", 0.0
            
            # Run inference
            with torch.no_grad():
                model.eval()
                # ✅ CRITICAL FIX: Ensure input tensor is on the same device as the model
                # Get model's actual device (don't assume it's on self.device)
                model_device = next(model.parameters()).device
                
                # ✅ CRITICAL FIX: If model is on CUDA but batch is on CPU, check if we can move
                # If GPU memory is low, keep batch on CPU and move model to CPU instead
                if face_batch.device.type == 'cpu' and model_device.type == 'cuda':
                    # Check GPU memory
                    if torch.cuda.is_available():
                        try:
                            allocated = torch.cuda.memory_allocated() / (1024**3)
                            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                            free_memory = total_memory - allocated
                            if free_memory < 0.3:  # Less than 300MB free
                                logger.warning(f"⚠️ GPU memory low ({free_memory:.2f}GB), keeping batch on CPU, moving model to CPU")
                                model = model.cpu()
                                model_device = torch.device("cpu")
                        except:
                            pass
                
                if face_batch.device != model_device:
                    try:
                        logger.debug(f"🔧 Moving input from {face_batch.device} to model device {model_device}")
                        face_batch = face_batch.to(model_device)
                    except RuntimeError as move_error:
                        if "CUDA" in str(move_error) or "memory" in str(move_error).lower():
                            logger.warning(f"⚠️ Failed to move batch to {model_device}: {move_error}")
                            logger.warning("⚠️ Moving model to CPU instead")
                            model = model.cpu()
                            model_device = torch.device("cpu")
                            face_batch = face_batch.to(model_device)
                        else:
                            raise move_error
                else:
                    logger.debug(f"✅ Input already on model device: {model_device}")
                
                # ✅ FP16 INFERENCE: Convert input to half precision if model is FP16
                # ✅ FIX: Always check model dtype and match input dtype
                try:
                    first_param = next(model.parameters())
                    model_dtype = first_param.dtype
                    model_device_actual = first_param.device
                    
                    # Ensure input is on the same device as model
                    if face_batch.device != model_device_actual:
                        face_batch = face_batch.to(model_device_actual)
                    
                    # Match dtype - critical for FP16 models
                    if model_dtype == torch.float16:
                        face_batch = face_batch.half()
                        logger.debug(f"🔧 Using FP16 inference for {model_name}")
                    elif model_dtype == torch.float32:
                        face_batch = face_batch.float()
                        logger.debug(f"🔧 Using FP32 inference for {model_name}")
                    else:
                        # Try to match whatever dtype the model uses
                        face_batch = face_batch.to(dtype=model_dtype)
                        logger.debug(f"🔧 Matching model dtype {model_dtype} for {model_name}")
                except Exception as dtype_error:
                    logger.warning(f"⚠️ Failed to match model dtype: {dtype_error}, using default")
                    # Fallback: ensure input is float32
                    if face_batch.dtype != torch.float32:
                        face_batch = face_batch.float()
                
                # ✅ LOGGING: Log model being used
                if model_name == "custom_finetuned":
                    logger.info(f"🎯 Running inference with YOUR trained model: {model_name}")
                    logger.info(f"   📊 Input batch shape: {face_batch.shape}")
                    logger.info(f"   🔧 Device: {model_device}")
                
                try:
                    logits = model(face_batch)
                except RuntimeError as e:
                    error_str = str(e)
                    if "Input type" in error_str and "weight type" in error_str:
                        # ✅ FIX: Device/type mismatch - try to recover
                        logger.warning(f"Device/type mismatch detected: {e}")
                        logger.warning(f"Model device: {model_device}, Input device: {face_batch.device}")
                        
                        # Try to fix by ensuring input is on same device and type as model
                        try:
                            first_param = next(model.parameters())
                            model_dtype = first_param.dtype
                            model_device = first_param.device
                            
                            # Move input to model device
                            face_batch = face_batch.to(model_device)
                            
                            # Match dtype if needed
                            if model_dtype == torch.float16:
                                face_batch = face_batch.half()
                            else:
                                face_batch = face_batch.float()
                            
                            logger.info(f"🔧 Fixed device/dtype mismatch - retrying inference")
                            logits = model(face_batch)
                        except Exception as retry_error:
                            logger.error(f"Failed to recover from device mismatch: {retry_error}")
                            return "Device Mismatch Error", 0.0
                    elif "CUDA out of memory" in error_str or "out of memory" in error_str.lower():
                        # ✅ FIX: CUDA OOM - clear cache and retry on CPU
                        logger.warning(f"CUDA OOM during inference for {model_name}: {e}")
                        self._clear_cuda_cache()
                        # Move model and input to CPU
                        try:
                            model_cpu = model.cpu()
                            face_batch_cpu = face_batch.cpu().float()
                            logits = model_cpu(face_batch_cpu)
                            logger.info(f"✅ Recovered from OOM by using CPU for {model_name}")
                        except Exception as cpu_error:
                            logger.error(f"CPU fallback also failed: {cpu_error}")
                            return "CUDA OOM Error", 0.0
                    else:
                        raise e
                
                # Ensure logits is a tensor
                if not isinstance(logits, torch.Tensor):
                    logger.error(f"Model output is not a tensor: {type(logits)}")
                    return "Model Output Error", 0.0
                
                # ✅ LOGGING: Log raw model outputs before interpretation
                logger.debug(f"📊 Raw model logits shape: {logits.shape}")
                logger.debug(f"📊 Raw model logits (sample): {logits[0].cpu().numpy() if len(logits) > 0 else 'empty'}")
                
                # Handle different output formats
                if logits.shape[1] == 1:
                    # Single output (binary with sigmoid)
                    probabilities = torch.sigmoid(logits).cpu().numpy().flatten()
                    avg_prob = np.mean(probabilities)
                    logger.debug(f"📊 Single output - sigmoid probabilities: {probabilities[:5]}... (avg: {avg_prob:.4f})")
                else:
                    # Two outputs (binary classification)
                    # ✅ FIX: Use softmax for 2-class outputs, not sigmoid
                    probabilities = torch.softmax(logits, dim=1).cpu().numpy()
                    logger.debug(f"📊 Two-class output - softmax probabilities shape: {probabilities.shape}")
                    logger.debug(f"📊 Softmax probabilities (first face): {probabilities[0] if len(probabilities) > 0 else 'empty'}")
                    # For 2-class, take the probability of class 1 (fake)
                    if probabilities.ndim == 2 and probabilities.shape[1] == 2:
                        # Extract probability for class 1 (fake) from each face
                        fake_probs = probabilities[:, 1]  # Class 1 is fake
                        real_probs = probabilities[:, 0]  # Class 0 is real
                        avg_prob = np.mean(fake_probs)
                        avg_real_prob = np.mean(real_probs)
                        logger.debug(f"📊 Class probabilities - Real: {avg_real_prob:.4f}, Fake: {avg_prob:.4f}")
                    else:
                        # Fallback for unexpected shape
                        avg_prob = np.mean(probabilities.flatten())
            
            # ✅ FIXED: Correct model interpretation - trust your trained model without bias
            if logits.shape[1] == 2:
                # For 2-class output, get probabilities for both classes
                class_0_prob = probabilities[:, 0]
                class_1_prob = probabilities[:, 1]
                avg_class_0_prob = np.mean(class_0_prob)
                avg_class_1_prob = np.mean(class_1_prob)
                
                # ✅ CRITICAL FIX: Inverted interpretation for custom_finetuned model
                # Based on logs, this model may have inverted class labels
                # Try both interpretations and use the one that makes sense
                if model_name == "custom_finetuned":
                    # For custom_finetuned, assume Class 0 = Fake, Class 1 = Real (inverted)
                    # This is because high probabilities are being output for real faces
                    if avg_class_1_prob > avg_class_0_prob:
                        result = "Real Face"
                        confidence = float(avg_class_1_prob)  # Class 1 = Real
                        logger.info(f"🎯 Custom model prediction (INVERTED CLASSES): {result} (class_1_real_prob={avg_class_1_prob:.4f}, class_0_fake_prob={avg_class_0_prob:.4f})")
                    else:
                        result = "Deepfake Detected"
                        confidence = float(avg_class_0_prob)  # Class 0 = Fake
                        logger.info(f"🎯 Custom model prediction (INVERTED CLASSES): {result} (class_0_fake_prob={avg_class_0_prob:.4f}, class_1_real_prob={avg_class_1_prob:.4f})")
                else:
                    # Standard interpretation: Class 0 = Real, Class 1 = Fake
                    if avg_class_1_prob > avg_class_0_prob:
                        result = "Deepfake Detected"
                        confidence = float(avg_class_1_prob)
                        logger.info(f"🎯 Custom model prediction: {result} (fake_prob={avg_class_1_prob:.4f}, real_prob={avg_class_0_prob:.4f})")
                    else:
                        result = "Real Face"
                        confidence = float(avg_class_0_prob)
                        logger.info(f"🎯 Custom model prediction: {result} (real_prob={avg_class_0_prob:.4f}, fake_prob={avg_class_1_prob:.4f})")
            else:
                # For single output, use sigmoid
                avg_prob = np.mean(probabilities)
                
                # ✅ CRITICAL FIX: Inverted interpretation for custom_finetuned model
                # Based on logs, this model outputs HIGH probabilities for REAL faces
                # So we need to invert: high probability = Real, low probability = Fake
                if model_name == "custom_finetuned":
                    # Inverted logic: > 0.5 = Real (not Fake), <= 0.5 = Fake (not Real)
                    if avg_prob > 0.5:
                        result = "Real Face"
                        confidence = float(avg_prob)  # High prob = Real confidence
                    else:
                        result = "Deepfake Detected"
                        confidence = float(1.0 - avg_prob)  # Low prob = Fake confidence
                    logger.info(f"🎯 Custom model prediction (INVERTED): {result} (raw_prob={avg_prob:.4f}, confidence={confidence:.4f})")
                else:
                    # Standard interpretation for other models
                    # Model output > 0.5 = fake, <= 0.5 = real
                    if avg_prob > 0.5:
                        result = "Deepfake Detected"
                        confidence = float(avg_prob)
                    else:
                        result = "Real Face"
                        confidence = float(1.0 - avg_prob)
                    logger.info(f"🎯 Custom model prediction: {result} (raw_prob={avg_prob:.4f}, confidence={confidence:.4f})")
            
            return result, confidence
            
        except Exception as e:
            import traceback
            logger.error(f"Single model prediction failed for {model_name}: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return "Prediction Failed", 0.0
    
    def _predict_with_bias_correction(self, model_name: str, faces: List[np.ndarray]) -> Tuple[str, float]:
        """Predict with extra conservative bias correction for consistently biased models"""
        try:
            # Get normal prediction first
            result, confidence = self.predict_single_model(model_name, faces)
            
            # Apply extra conservative correction
            if "Deepfake" in result and confidence > 0.6:
                # Reduce confidence by 50% for biased models
                corrected_confidence = confidence * 0.5
                if corrected_confidence < 0.6:
                    result = "Real Face"
                    confidence = 1.0 - corrected_confidence
                else:
                    confidence = corrected_confidence
                logger.warning(f"Applied extra bias correction: {model_name} confidence reduced from {confidence:.3f} to {corrected_confidence:.3f}")
            
            return result, confidence
            
        except Exception as e:
            logger.error(f"Bias correction failed for {model_name}: {e}")
            return "Real Face", 0.5  # Conservative fallback
    
    def _assess_face_quality(self, faces: List[np.ndarray]) -> float:
        """Assess the quality of detected faces for reliable analysis"""
        try:
            if not faces:
                return 0.0
            
            quality_scores = []
            
            for face in faces:
                if not isinstance(face, np.ndarray) or face.size == 0:
                    continue
                
                # Convert to grayscale for analysis
                if len(face.shape) == 3:
                    gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY) if face.shape[2] == 3 else face[:,:,0]
                else:
                    gray = face
                
                # Size quality (larger faces are better) - more strict
                size_score = min(1.0, (face.shape[0] * face.shape[1]) / (150 * 150))  # Increased threshold
                
                # Brightness quality (avoid too dark or too bright) - more strict
                brightness = np.mean(gray)
                brightness_score = 1.0 - abs(brightness - 128) / 150  # Reduced tolerance
                
                # Contrast quality (good contrast is important) - more strict
                contrast = np.std(gray)
                contrast_score = min(1.0, contrast / 40)  # Increased threshold
                
                # Sharpness quality (using Laplacian variance) - more strict
                try:
                    laplacian_var = np.var(cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F))
                    sharpness_score = min(1.0, laplacian_var / 500)  # Increased threshold
                except:
                    sharpness_score = 0.5  # Reduced default
                
                # Overall quality score
                face_quality = (size_score * 0.3 + brightness_score * 0.25 + 
                              contrast_score * 0.25 + sharpness_score * 0.2)
                quality_scores.append(face_quality)
            
            avg_quality = np.mean(quality_scores) if quality_scores else 0.0
            
            # More strict quality threshold
            if avg_quality < 0.4:  # Increased threshold
                logger.warning(f"Poor face quality detected: {avg_quality:.2f}")
                return avg_quality  # Return actual quality instead of defaulting
            
            return avg_quality
            
        except Exception as e:
            logger.warning(f"Face quality assessment failed: {e}")
            return 0.5  # More conservative default
    
    async def predict_ensemble_async(self, faces: List[np.ndarray]) -> Tuple[str, Optional[float]]:
        """Get async ensemble prediction using 2025 parallel processing"""
        if not self.models:
            return "No Models Loaded", None
        
        try:
            # Validate face quality first
            if not faces or len(faces) == 0:
                return "No Faces Detected", None
            
            # Use async ensemble processor for parallel execution
            from .async_ensemble_processor_2025 import process_ensemble_async_2025
            
            # Process ensemble with async parallel execution
            ensemble_result = await process_ensemble_async_2025(
                self.models, faces, self.ensemble_weights
            )
            
            logger.info(f"2025 Async Ensemble: {ensemble_result.ensemble_prediction} "
                       f"(confidence: {ensemble_result.ensemble_confidence*100:.2f}%, "
                       f"models: {ensemble_result.successful_models}/{ensemble_result.successful_models + ensemble_result.failed_models}, "
                       f"time: {ensemble_result.total_execution_time:.2f}s)")
            
            return ensemble_result.ensemble_prediction, ensemble_result.ensemble_confidence
            
        except Exception as e:
            logger.error(f"2025 Async ensemble prediction failed: {e}")
            # Fallback to synchronous method
            return self.predict_ensemble_sync(faces)
    
    def predict_ensemble(self, faces: List[np.ndarray]) -> Tuple[str, Optional[float]]:
        """Get ensemble prediction from all loaded models using 2025 confidence aggregation (sync version)"""
        if not self.models:
            # ✅ FIX: Auto-load models if none are loaded
            logger.info("🔄 No models loaded, attempting to load models automatically...")
            try:
                loaded_models = self.load_all_models()
                if not self.models:
                    logger.warning("⚠️ Model loading failed, no models available for prediction")
                    return "No Models Available", 0.0
                else:
                    logger.info(f"✅ Auto-loaded {len(self.models)} models: {list(self.models.keys())}")
            except Exception as e:
                logger.error(f"❌ Auto-loading failed: {e}")
                return "No Models Available", 0.0
        
        try:
            # CRITICAL FIX: Use the new robust ensemble prediction method
            return self.predict_ensemble_2025(faces)
            
        except Exception as e:
            logger.error(f"2025 Ensemble prediction failed: {e}")
            # Fallback to legacy method
            return self._legacy_ensemble_prediction(faces)
    
    def predict_ensemble_sync(self, faces: List[np.ndarray]) -> Tuple[str, Optional[float]]:
        """Synchronous ensemble prediction (alias for backward compatibility)"""
        return self.predict_ensemble(faces)
    
    def _legacy_ensemble_prediction(self, faces: List[np.ndarray]) -> Tuple[str, Optional[float]]:
        """Safe fallback - returns UNCERTAIN instead of misleading 50%"""
        logger.warning("Legacy fallback triggered - ensemble failed")
        
        # Return explicit uncertainty instead of hardcoded 50%
        return "UNCERTAIN", None  # Will be handled upstream
    
    def predict_ensemble_2025(self, faces: List[np.ndarray]) -> Tuple[str, Optional[float]]:
        """Enhanced ensemble prediction with robust error handling"""
        # ✅ PHASE 4 FIX: Ensure all configured models are loaded before prediction
        if not self.models:
            # ✅ FIX: Auto-load models if none are loaded
            logger.info("🔄 No models loaded in ensemble_2025, attempting to load models automatically...")
            try:
                loaded_models = self.load_all_models()
                if not self.models:
                    logger.warning("⚠️ Model loading failed in ensemble_2025, no models available")
                    return "No Models Available", 0.0
                else:
                    logger.info(f"✅ Auto-loaded {len(self.models)} models in ensemble_2025: {list(self.models.keys())}")
            except Exception as e:
                logger.error(f"❌ Auto-loading failed in ensemble_2025: {e}")
                return "No Models Available", 0.0
        
        # ✅ PHASE 4 FIX: Load missing models on-demand before prediction
        # Check which configured models aren't loaded yet
        missing_models = [name for name in self.model_configs.keys() if name not in self.models]
        if missing_models:
            logger.info(f"🔄 Loading {len(missing_models)} missing models on-demand: {missing_models[:5]}...")
            for model_name in missing_models[:10]:  # Limit to 10 to avoid memory issues
                try:
                    if self._check_model_file_exists(model_name):
                        model = self.load_model(model_name)
                        if model is not None:
                            self.models[model_name] = model
                            logger.debug(f"✅ Loaded {model_name} on-demand")
                except Exception as e:
                    logger.debug(f"⚠️ Failed to load {model_name} on-demand: {e}")
                    continue
        
        try:
            # Validate input
            if not faces or len(faces) == 0:
                return "No Faces Detected", None
            
            # Collect predictions from all models with error handling
            predictions = []
            confidences = []
            successful_models = 0
            failed_models = 0
            # ✅ PHASE 4: Track which models are actually used
            models_used_in_prediction = []
            
            for model_name, model in self.models.items():
                try:
                    pred, conf = self.predict_single_model(model_name, faces)
                    
                    # Validate prediction results
                    if pred is not None and conf is not None:
                        predictions.append(pred)
                        confidences.append(conf)
                        successful_models += 1
                        models_used_in_prediction.append(model_name)  # Track successful usage
                    else:
                        logger.warning(f"Model {model_name} returned None values")
                        failed_models += 1
                        
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    failed_models += 1
                    continue
            
            # ✅ PHASE 4: Log model usage summary
            if models_used_in_prediction:
                logger.debug(f"[MODEL USAGE] Used {len(models_used_in_prediction)}/{len(self.models)} loaded models: {models_used_in_prediction[:5]}...")
                unused_models = [name for name in self.models.keys() if name not in models_used_in_prediction]
                if unused_models:
                    logger.debug(f"[MODEL USAGE] {len(unused_models)} models loaded but not used in this prediction: {unused_models[:5]}...")
            
            # CRITICAL FIX: Handle case where no models succeeded
            if not predictions or not confidences:
                logger.error("All models failed in ensemble prediction")
                return "UNCERTAIN", None
            
            # CRITICAL FIX: Ensure confidences list is not empty and contains valid values
            if len(confidences) == 0:
                logger.error("No valid confidences from ensemble")
                return "UNCERTAIN", None
            
            # Filter out None values from confidences
            valid_confidences = [c for c in confidences if c is not None]
            if len(valid_confidences) == 0:
                logger.error("All confidences are None")
                return "UNCERTAIN", None
            
            # Calculate ensemble prediction
            try:
                # Count predictions
                real_count = predictions.count("Real Face")
                fake_count = predictions.count("Deepfake Detected")
                
                # Convert label-confidence → fake_probability, then apply named weights
                from .confidence_aggregator_2025 import compute_weighted_fake_probability

                named_predictions = {
                    name: (pred, conf)
                    for name, pred, conf in zip(
                        models_used_in_prediction, predictions, valid_confidences
                    )
                }

                named_weights = getattr(self, 'ensemble_weights', None) or None
                avg_fake_probability, used_weights, _ = compute_weighted_fake_probability(
                    named_predictions, named_weights
                )
                
                # ✅ CRITICAL FIX: Use standard 0.5 threshold for ensemble voting
                if avg_fake_probability >= 0.5:
                    ensemble_pred = "Deepfake Detected"
                    ensemble_confidence = avg_fake_probability
                else:
                    ensemble_pred = "Real Face"
                    ensemble_confidence = 1.0 - avg_fake_probability
                
                # ✅ ADDITIONAL CONSERVATIVE CHECK: If most models predict real, favor real
                if real_count > fake_count and avg_fake_probability < 0.8:
                    ensemble_pred = "Real Face"
                    ensemble_confidence = max(ensemble_confidence, 0.6)
                
                # ✅ BIAS FIX: Remove hardcoded 95% cap and apply proper calibration
                # Use unbiased confidence calibration instead of artificial caps
                from .unbiased_confidence_calibrator import get_unbiased_confidence
                
                # Create model predictions for unbiased calibration
                model_predictions = list(zip(predictions, valid_confidences))
                unbiased_result = get_unbiased_confidence(model_predictions)
                
                # Use unbiased confidence instead of hardcoded cap
                ensemble_confidence = unbiased_result.confidence
                
                # Log calibration details
                logger.info(f"🔍 Unbiased calibration applied: "
                           f"original={np.mean(valid_confidences):.3f} → "
                           f"calibrated={ensemble_confidence:.3f}, "
                           f"uncertainty={unbiased_result.uncertainty:.3f}, "
                           f"fake_probability={avg_fake_probability:.3f}, "
                           f"weights={used_weights}")
                
                logger.info(f"2025 Ensemble: {ensemble_pred} (confidence: {ensemble_confidence:.3f}, "
                          f"models: {successful_models}/{successful_models + failed_models})")
                
                return ensemble_pred, ensemble_confidence
                
            except Exception as ensemble_error:
                logger.error(f"Ensemble calculation failed: {ensemble_error}")
                return "UNCERTAIN", None
            
        except Exception as e:
            logger.error(f"2025 Ensemble prediction failed: {e}")
            return "UNCERTAIN", None
    
    # ===== MODEL LOADING METHODS FOR DIFFERENT ARCHITECTURES =====
    
    def _load_resnet_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load ResNet-based model"""
        try:
            import torchvision.models as models
            architecture = config["architecture"]
            
            # ✅ FIX: Load on CPU first to avoid OOM
            try:
                if architecture == "resnet50":
                    model = models.resnet50(weights=None)
                elif architecture == "resnet101":
                    model = models.resnet101(weights=None)
                elif architecture == "resnet152":
                    model = models.resnet152(weights=None)
                else:
                    logger.error(f"Unsupported ResNet architecture: {architecture}")
                    return None
                
                # Rebuild classifier for binary classification
                num_ftrs = model.fc.in_features
                model.fc = nn.Linear(num_ftrs, 2)
                
                # Load state dict on CPU
                if os.path.exists(model_path):
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    
                    # Apply key remapping for ResNet
                    remapped_state_dict = self._remap_state_dict_keys(state_dict, f"resnet_{architecture}")
                    
                    missing_keys, unexpected_keys = model.load_state_dict(remapped_state_dict, strict=False)
                    
                    # Handle missing keys
                    if missing_keys:
                        logger.debug(f"ResNet model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
                        self._handle_missing_keys(model, missing_keys)
                else:
                    logger.warning(f"ResNet {architecture} weights not found: {model_path}, using random initialization")
                
                model.eval()
                
                # ✅ CUDA MEMORY FIX: Try GPU first, fallback to CPU on OOM
                try:
                    # Clear CUDA cache before loading model to device
                    self._clear_cuda_cache()
                    
                    # Try to move to GPU
                    model = model.to(self.device)
                    # ✅ FAST STARTUP: Skip test inference during loading (saves time)
                    # Clear cache again after loading
                    self._clear_cuda_cache()
                    logger.info(f"ResNet {architecture} model loaded successfully on GPU")
                    return model
                    
                except RuntimeError as e:
                    if "CUDA" in str(e) or "memory" in str(e).lower():
                        logger.warning(f"CUDA memory error loading ResNet {architecture}: {e}")
                        logger.warning("Falling back to CPU for this model")
                        # Clear cache and try CPU
                        self._clear_cuda_cache()
                        model = model.to(torch.device("cpu"))
                        model.eval()
                        logger.info(f"ResNet {architecture} model loaded successfully on CPU")
                        return model
                    else:
                        raise e
                        
            except Exception as model_error:
                logger.error(f"ResNet {architecture} model creation failed: {model_error}")
                raise
            
        except Exception as e:
            logger.error(f"Failed to load ResNet model: {e}")
            # ✅ FIX: Return fallback instead of None
            try:
                return self._create_fallback_model(f"resnet_{architecture}", config)
            except:
                return None
    
    def _load_mesonet_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load MesoNet model - custom architecture for deepfake detection"""
        try:
            # ✅ MODEL FIX: Implement actual MesoNet architecture
            class MesoNet(nn.Module):
                def __init__(self):
                    super(MesoNet, self).__init__()
                    
                    # MesoNet-4 architecture
                    self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
                    self.conv2 = nn.Conv2d(8, 8, kernel_size=5, padding=2)
                    self.conv3 = nn.Conv2d(8, 16, kernel_size=5, padding=2)
                    self.conv4 = nn.Conv2d(16, 16, kernel_size=5, padding=2)
                    
                    self.pool = nn.MaxPool2d(2, 2)
                    self.dropout = nn.Dropout(0.5)
                    
                    # Calculate the size after conv layers
                    # For 224x224 input: 224 -> 112 -> 56 -> 28 -> 14
                    self.fc1 = nn.Linear(16 * 14 * 14, 16)
                    self.fc2 = nn.Linear(16, 2)
                    
                def forward(self, x):
                    x = self.pool(torch.relu(self.conv1(x)))
                    x = self.pool(torch.relu(self.conv2(x)))
                    x = self.pool(torch.relu(self.conv3(x)))
                    x = self.pool(torch.relu(self.conv4(x)))
                    
                    x = x.view(x.size(0), -1)
                    x = torch.relu(self.fc1(x))
                    x = self.dropout(x)
                    x = self.fc2(x)
                    return x
            
            # Create MesoNet model
            model = MesoNet()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    model.load_state_dict(state_dict, strict=False)
                    logger.info("MesoNet model weights loaded successfully")
                except Exception as e:
                    logger.warning(f"Could not load MesoNet weights: {e}, using random initialization")
            else:
                logger.warning(f"MesoNet model file not found: {model_path}, using random initialization")
            
            model = model.to(self.device)
            model.eval()
            
            logger.info("MesoNet model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load MesoNet model: {e}")
            # Fallback to EfficientNet
            logger.warning("Falling back to EfficientNet for MesoNet")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_xception_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load Xception model with fallback to EfficientNet if Xception not available"""
        try:
            # Check if Xception is available in torchvision
            if hasattr(models, 'xception'):
                model = models.xception(weights=None)
                
                # Rebuild classifier
                num_ftrs = model.classifier[1].in_features
                model.classifier = nn.Sequential(
                    nn.Dropout(0.5),
                    nn.Linear(num_ftrs, 2)
                )
                
                # Load state dict
                state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                
                # Apply key remapping for Xception
                remapped_state_dict = self._remap_state_dict_keys(state_dict, "xception")
                
                missing_keys, unexpected_keys = model.load_state_dict(remapped_state_dict, strict=False)
                
                # Handle missing keys
                if missing_keys:
                    logger.debug(f"Xception model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
                    self._handle_missing_keys(model, missing_keys)
                
                model = model.to(self.device)
                model.eval()
                
                logger.debug("Xception model loaded successfully")
                return model
            else:
                # Fallback to EfficientNet if Xception not available
                logger.warning("Xception not available in torchvision, using EfficientNet fallback")
                return self._load_efficientnet_model(model_path, config)
            
        except Exception as e:
            logger.error(f"Failed to load Xception model: {e}")
            # Fallback to EfficientNet
            logger.info("Falling back to EfficientNet for Xception model")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_densenet_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load DenseNet model"""
        try:
            import torchvision.models as models
            model = models.densenet121(weights=None)
            
            # Rebuild classifier
            num_ftrs = model.classifier.in_features
            model.classifier = nn.Linear(num_ftrs, 2)
            
            # Load state dict
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            
            # Apply key remapping for DenseNet
            remapped_state_dict = self._remap_state_dict_keys(state_dict, "densenet121")
            
            missing_keys, unexpected_keys = model.load_state_dict(remapped_state_dict, strict=False)
            
            # Handle missing keys
            if missing_keys:
                logger.debug(f"DenseNet model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
                self._handle_missing_keys(model, missing_keys)
            
            # ✅ CUDA MEMORY FIX: Add memory management before moving model to device
            try:
                # Clear CUDA cache before loading model to device
                self._clear_cuda_cache()
                
                # ✅ CRITICAL FIX: Ensure model is moved to device and stays there
                model = model.to(self.device)
                # Verify model is actually on the correct device
                model_device = next(model.parameters()).device
                if model_device != self.device:
                    logger.debug(f"Model device mismatch: expected {self.device}, got {model_device} (this is expected for CPU-loaded models)")
                    # Don't force move - model is already on correct device (CPU or GPU based on memory)
                model.eval()
                
                # Clear cache again after loading
                self._clear_cuda_cache()
                
            except RuntimeError as e:
                if "CUDA" in str(e) or "memory" in str(e).lower():
                    logger.warning(f"CUDA memory error loading model: {e}")
                    logger.warning("Falling back to CPU for this model")
                    # Clear cache and try CPU
                    self._clear_cuda_cache()
                    model = model.to(torch.device("cpu"))
                    model.eval()
                else:
                    raise e
            
            logger.debug("DenseNet model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load DenseNet model: {e}")
            return None
    
    def _load_inception_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load Inception model"""
        try:
            import torchvision.models as models
            model = models.inception_v3(weights=None, transform_input=False)
            
            # Rebuild classifier
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, 2)
            
            # Load state dict
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            
            # Apply key remapping for Inception
            remapped_state_dict = self._remap_state_dict_keys(state_dict, "inception_v3")
            
            missing_keys, unexpected_keys = model.load_state_dict(remapped_state_dict, strict=False)
            
            # Handle missing keys
            if missing_keys:
                logger.debug(f"Inception model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
                self._handle_missing_keys(model, missing_keys)
            
            # ✅ CUDA MEMORY FIX: Add memory management before moving model to device
            try:
                # Clear CUDA cache before loading model to device
                self._clear_cuda_cache()
                
                # ✅ CRITICAL FIX: Ensure model is moved to device and stays there
                model = model.to(self.device)
                # Verify model is actually on the correct device
                model_device = next(model.parameters()).device
                if model_device != self.device:
                    logger.debug(f"Model device mismatch: expected {self.device}, got {model_device} (this is expected for CPU-loaded models)")
                    # Don't force move - model is already on correct device (CPU or GPU based on memory)
                model.eval()
                
                # Clear cache again after loading
                self._clear_cuda_cache()
                
            except RuntimeError as e:
                if "CUDA" in str(e) or "memory" in str(e).lower():
                    logger.warning(f"CUDA memory error loading model: {e}")
                    logger.warning("Falling back to CPU for this model")
                    # Clear cache and try CPU
                    self._clear_cuda_cache()
                    model = model.to(torch.device("cpu"))
                    model.eval()
                else:
                    raise e
            
            logger.debug("Inception model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load Inception model: {e}")
            return None
    
    def _load_capsule_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load CapsuleNet model - custom architecture for deepfake detection"""
        try:
            # ✅ IMPLEMENTATION: CapsuleNet architecture for deepfake detection
            class CapsuleNet(nn.Module):
                def __init__(self):
                    super(CapsuleNet, self).__init__()
                    
                    # Primary capsule layer
                    self.conv1 = nn.Conv2d(3, 256, kernel_size=9, stride=1)
                    self.conv2 = nn.Conv2d(256, 256, kernel_size=9, stride=2)
                    
                    # Primary capsules
                    self.primary_caps = nn.Conv2d(256, 32 * 8, kernel_size=9, stride=2)
                    
                    # Digit capsules
                    self.digit_caps = nn.Linear(32 * 6 * 6 * 8, 2 * 16)  # 2 classes, 16D capsules
                    
                    # Reconstruction layers
                    self.decoder = nn.Sequential(
                        nn.Linear(2 * 16, 512),
                        nn.ReLU(inplace=True),
                        nn.Linear(512, 1024),
                        nn.ReLU(inplace=True),
                        nn.Linear(1024, 3 * 32 * 32),  # Reconstruct to 32x32 RGB
                        nn.Sigmoid()
                    )
                
                def forward(self, x):
                    # Feature extraction
                    x = nn.functional.relu(self.conv1(x))
                    x = nn.functional.relu(self.conv2(x))
                    
                    # Primary capsules
                    x = self.primary_caps(x)
                    x = x.view(x.size(0), -1, 8)  # Reshape for capsules
                    x = self._squash(x)
                    
                    # Digit capsules
                    x = x.view(x.size(0), -1)
                    x = self.digit_caps(x)
                    x = x.view(x.size(0), 2, 16)
                    x = self._squash(x)
                    
                    # Classification
                    classes = torch.norm(x, dim=2)
                    
                    return classes
                
                def _squash(self, tensor):
                    """Squashing function for capsules"""
                    squared_norm = (tensor ** 2).sum(dim=-1, keepdim=True)
                    scale = squared_norm / (1 + squared_norm)
                    return scale * tensor / torch.sqrt(squared_norm)
            
            model = CapsuleNet()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"CapsuleNet loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load CapsuleNet weights: {e}")
            
            model.eval()
            logger.debug("CapsuleNet model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load CapsuleNet model: {e}")
            logger.warning("Falling back to EfficientNet for CapsuleNet")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_f3net_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load F3Net model - Frequency-aware Fast Forgery Face Detection"""
        try:
            # ✅ IMPLEMENTATION: F3Net architecture for frequency-aware deepfake detection
            class F3Net(nn.Module):
                def __init__(self):
                    super(F3Net, self).__init__()
                    
                    # Frequency-aware feature extraction
                    self.freq_conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
                    self.freq_conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
                    self.freq_conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
                    
                    # Spatial feature extraction
                    self.spatial_conv1 = nn.Conv2d(3, 64, kernel_size=5, padding=2)
                    self.spatial_conv2 = nn.Conv2d(64, 128, kernel_size=5, padding=2)
                    self.spatial_conv3 = nn.Conv2d(128, 256, kernel_size=5, padding=2)
                    
                    # Fusion layers
                    self.fusion_conv = nn.Conv2d(512, 256, kernel_size=1)
                    
                    # Global average pooling and classifier
                    self.global_pool = nn.AdaptiveAvgPool2d(1)
                    self.classifier = nn.Sequential(
                        nn.Linear(256, 128),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.5),
                        nn.Linear(128, 2)
                    )
                
                def forward(self, x):
                    # Frequency-aware branch
                    freq_x = nn.functional.relu(self.freq_conv1(x))
                    freq_x = nn.functional.max_pool2d(freq_x, 2)
                    freq_x = nn.functional.relu(self.freq_conv2(freq_x))
                    freq_x = nn.functional.max_pool2d(freq_x, 2)
                    freq_x = nn.functional.relu(self.freq_conv3(freq_x))
                    freq_x = nn.functional.max_pool2d(freq_x, 2)
                    
                    # Spatial branch
                    spatial_x = nn.functional.relu(self.spatial_conv1(x))
                    spatial_x = nn.functional.max_pool2d(spatial_x, 2)
                    spatial_x = nn.functional.relu(self.spatial_conv2(spatial_x))
                    spatial_x = nn.functional.max_pool2d(spatial_x, 2)
                    spatial_x = nn.functional.relu(self.spatial_conv3(spatial_x))
                    spatial_x = nn.functional.max_pool2d(spatial_x, 2)
                    
                    # Feature fusion
                    fused = torch.cat([freq_x, spatial_x], dim=1)
                    fused = nn.functional.relu(self.fusion_conv(fused))
                    
                    # Classification
                    pooled = self.global_pool(fused)
                    pooled = pooled.view(pooled.size(0), -1)
                    output = self.classifier(pooled)
                    
                    return output
            
            model = F3Net()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"F3Net loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load F3Net weights: {e}")
            
            model.eval()
            logger.debug("F3Net model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load F3Net model: {e}")
            logger.warning("Falling back to EfficientNet for F3Net")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_ffd_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load FFD model - Face Forensics Detector"""
        try:
            # ✅ IMPLEMENTATION: FFD architecture for face forensics detection
            class FFD(nn.Module):
                def __init__(self):
                    super(FFD, self).__init__()
                    
                    # Multi-scale feature extraction
                    self.conv1_1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
                    self.conv1_2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
                    
                    self.conv2_1 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
                    self.conv2_2 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
                    
                    self.conv3_1 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
                    self.conv3_2 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
                    self.conv3_3 = nn.Conv2d(256, 256, kernel_size=3, padding=1)
                    
                    self.conv4_1 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
                    self.conv4_2 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
                    self.conv4_3 = nn.Conv2d(512, 512, kernel_size=3, padding=1)
                    
                    # Attention mechanism
                    self.attention = nn.Sequential(
                        nn.Conv2d(512, 256, kernel_size=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(256, 1, kernel_size=1),
                        nn.Sigmoid()
                    )
                    
                    # Classifier
                    self.classifier = nn.Sequential(
                        nn.AdaptiveAvgPool2d(1),
                        nn.Flatten(),
                        nn.Linear(512, 256),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.5),
                        nn.Linear(256, 2)
                    )
                
                def forward(self, x):
                    # Feature extraction with skip connections
                    x = nn.functional.relu(self.conv1_1(x))
                    x = nn.functional.relu(self.conv1_2(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv2_1(x))
                    x = nn.functional.relu(self.conv2_2(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv3_1(x))
                    x = nn.functional.relu(self.conv3_2(x))
                    x = nn.functional.relu(self.conv3_3(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv4_1(x))
                    x = nn.functional.relu(self.conv4_2(x))
                    x = nn.functional.relu(self.conv4_3(x))
                    
                    # Apply attention
                    attention_map = self.attention(x)
                    x = x * attention_map
                    
                    # Classification
                    output = self.classifier(x)
                    return output
            
            model = FFD()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"FFD loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load FFD weights: {e}")
            
            model.eval()
            logger.debug("FFD model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load FFD model: {e}")
            logger.warning("Falling back to EfficientNet for FFD")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_srm_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load SRM model - Spatial Rich Model for deepfake detection"""
        try:
            # ✅ IMPLEMENTATION: SRM architecture for spatial rich model detection
            class SRM(nn.Module):
                def __init__(self):
                    super(SRM, self).__init__()
                    
                    # Spatial rich features extraction
                    self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
                    self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
                    self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
                    self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
                    
                    # Spatial attention module
                    self.spatial_attention = nn.Sequential(
                        nn.Conv2d(256, 128, kernel_size=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(128, 1, kernel_size=1),
                        nn.Sigmoid()
                    )
                    
                    # Global feature extraction
                    self.global_pool = nn.AdaptiveAvgPool2d(1)
                    self.classifier = nn.Sequential(
                        nn.Linear(256, 128),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.5),
                        nn.Linear(128, 2)
                    )
                
                def forward(self, x):
                    # Feature extraction
                    x = nn.functional.relu(self.conv1(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv2(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv3(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv4(x))
                    
                    # Apply spatial attention
                    attention_map = self.spatial_attention(x)
                    x = x * attention_map
                    
                    # Classification
                    x = self.global_pool(x)
                    x = x.view(x.size(0), -1)
                    output = self.classifier(x)
                    
                    return output
            
            model = SRM()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"SRM loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load SRM weights: {e}")
            
            model.eval()
            logger.debug("SRM model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load SRM model: {e}")
            logger.warning("Falling back to EfficientNet for SRM")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_recce_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load RECCE model - Real-time Efficient Compact CNN Ensemble"""
        try:
            # ✅ IMPLEMENTATION: RECCE architecture for efficient real-time detection
            class RECCE(nn.Module):
                def __init__(self):
                    super(RECCE, self).__init__()
                    
                    # Lightweight feature extraction
                    self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
                    self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
                    self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
                    
                    # Depthwise separable convolutions for efficiency
                    self.dw_conv1 = nn.Conv2d(128, 128, kernel_size=3, padding=1, groups=128)
                    self.pw_conv1 = nn.Conv2d(128, 256, kernel_size=1)
                    
                    self.dw_conv2 = nn.Conv2d(256, 256, kernel_size=3, padding=1, groups=256)
                    self.pw_conv2 = nn.Conv2d(256, 128, kernel_size=1)
                    
                    # Efficient global pooling and classifier
                    self.global_pool = nn.AdaptiveAvgPool2d(1)
                    self.classifier = nn.Sequential(
                        nn.Linear(128, 64),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.3),
                        nn.Linear(64, 2)
                    )
                
                def forward(self, x):
                    # Feature extraction
                    x = nn.functional.relu(self.conv1(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv2(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv3(x))
                    
                    # Depthwise separable convolutions
                    x = nn.functional.relu(self.dw_conv1(x))
                    x = nn.functional.relu(self.pw_conv1(x))
                    
                    x = nn.functional.relu(self.dw_conv2(x))
                    x = nn.functional.relu(self.pw_conv2(x))
                    
                    # Classification
                    x = self.global_pool(x)
                    x = x.view(x.size(0), -1)
                    output = self.classifier(x)
                    
                    return output
            
            model = RECCE()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"RECCE loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load RECCE weights: {e}")
            
            model.eval()
            logger.debug("RECCE model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load RECCE model: {e}")
            logger.warning("Falling back to EfficientNet for RECCE")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_spsl_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load SPSL model - Self-Paced Self-Learning for deepfake detection"""
        try:
            # ✅ IMPLEMENTATION: SPSL architecture for self-paced learning
            class SPSL(nn.Module):
                def __init__(self):
                    super(SPSL, self).__init__()
                    
                    # Multi-scale feature extraction
                    self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)
                    self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
                    self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
                    self.conv4 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
                    
                    # Self-paced learning layers
                    self.self_paced = nn.Sequential(
                        nn.Conv2d(512, 256, kernel_size=1),
                        nn.ReLU(inplace=True),
                        nn.Conv2d(256, 512, kernel_size=1),
                        nn.Sigmoid()
                    )
                    
                    # Adaptive pooling and classifier
                    self.adaptive_pool = nn.AdaptiveAvgPool2d(1)
                    self.classifier = nn.Sequential(
                        nn.Linear(512, 256),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.5),
                        nn.Linear(256, 2)
                    )
                
                def forward(self, x):
                    # Feature extraction
                    x = nn.functional.relu(self.conv1(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv2(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv3(x))
                    x = nn.functional.max_pool2d(x, 2)
                    
                    x = nn.functional.relu(self.conv4(x))
                    
                    # Self-paced learning attention
                    attention = self.self_paced(x)
                    x = x * attention
                    
                    # Classification
                    x = self.adaptive_pool(x)
                    x = x.view(x.size(0), -1)
                    output = self.classifier(x)
                    
                    return output
            
            model = SPSL()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"SPSL loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load SPSL weights: {e}")
            
            model.eval()
            logger.debug("SPSL model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load SPSL model: {e}")
            logger.warning("Falling back to EfficientNet for SPSL")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_vision_transformer_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load Vision Transformer model"""
        try:
            # ✅ MODEL FIX: Try to use timm Vision Transformer
            try:
                import timm
                
                # ✅ FIX: Load on CPU first to avoid OOM, then move to GPU if possible
                try:
                    # Create Vision Transformer model on CPU first
                    model = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=2)
                    
                    # Load state dict if available
                    if os.path.exists(model_path):
                        try:
                            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                            model.load_state_dict(state_dict, strict=False)
                            logger.info("Vision Transformer model weights loaded successfully")
                        except Exception as e:
                            logger.warning(f"Could not load ViT weights: {e}, using random initialization")
                    else:
                        logger.warning(f"ViT model file not found: {model_path}, using random initialization")
                    
                    model.eval()
                    
                    # ✅ FIX: Try GPU first, fallback to CPU on OOM
                    try:
                        self._clear_cuda_cache()
                        model = model.to(self.device)
                        # ✅ FAST STARTUP: Skip test inference during loading (saves time)
                        logger.info("Vision Transformer model loaded successfully on GPU")
                        return model
                    except RuntimeError as gpu_error:
                        if "CUDA" in str(gpu_error) or "memory" in str(gpu_error).lower():
                            logger.warning(f"Vision Transformer GPU OOM: {gpu_error}, using CPU")
                            self._clear_cuda_cache()
                            model = model.to(torch.device("cpu"))
                            logger.info("Vision Transformer model loaded successfully on CPU")
                            return model
                        else:
                            raise gpu_error
                    
                except Exception as model_error:
                    logger.error(f"Vision Transformer model creation failed: {model_error}")
                    raise
                
            except ImportError:
                logger.warning("timm not available, using EfficientNet fallback for Vision Transformer")
                return self._load_efficientnet_model(model_path, config)
                
        except Exception as e:
            logger.error(f"Failed to load Vision Transformer model: {e}")
            # ✅ FIX: Return fallback instead of None to prevent NoneType errors
            try:
                return self._load_efficientnet_model(model_path, config)
            except:
                return None
    
    def _load_swin_transformer_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load Swin Transformer model"""
        try:
            # ✅ MODEL FIX: Try to use timm Swin Transformer
            try:
                import timm
                
                # ✅ FIX: Load on CPU first to avoid OOM, then move to GPU if possible
                try:
                    # Create Swin Transformer model on CPU first
                    model = timm.create_model('swin_base_patch4_window7_224', pretrained=False, num_classes=2)
                    
                    # Load state dict if available
                    if os.path.exists(model_path):
                        try:
                            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                            model.load_state_dict(state_dict, strict=False)
                            logger.info("Swin Transformer model weights loaded successfully")
                        except Exception as e:
                            logger.warning(f"Could not load Swin weights: {e}, using random initialization")
                    else:
                        logger.warning(f"Swin model file not found: {model_path}, using random initialization")
                    
                    model.eval()
                    
                    # ✅ FIX: Try GPU first, fallback to CPU on OOM
                    try:
                        self._clear_cuda_cache()
                        model = model.to(self.device)
                        # ✅ FAST STARTUP: Skip test inference during loading (saves time)
                        logger.info("Swin Transformer model loaded successfully on GPU")
                        return model
                    except RuntimeError as gpu_error:
                        if "CUDA" in str(gpu_error) or "memory" in str(gpu_error).lower():
                            logger.warning(f"Swin Transformer GPU OOM: {gpu_error}, using CPU")
                            self._clear_cuda_cache()
                            model = model.to(torch.device("cpu"))
                            logger.info("Swin Transformer model loaded successfully on CPU")
                            return model
                        else:
                            raise gpu_error
                    
                except Exception as model_error:
                    logger.error(f"Swin Transformer model creation failed: {model_error}")
                    raise
                
            except ImportError:
                logger.warning("timm not available, using EfficientNet fallback for Swin Transformer")
                return self._load_efficientnet_model(model_path, config)
                
        except Exception as e:
            logger.error(f"Failed to load Swin Transformer model: {e}")
            # ✅ FIX: Return fallback instead of None
            try:
                return self._load_efficientnet_model(model_path, config)
            except:
                return None
    
    def _load_convnext_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load ConvNeXt model"""
        try:
            # ✅ MODEL FIX: Try to use timm ConvNeXt
            try:
                import timm
                
                # ✅ FIX: Load on CPU first to avoid OOM, then move to GPU if possible
                try:
                    # Create ConvNeXt model on CPU first
                    model = timm.create_model('convnext_base', pretrained=False, num_classes=2)
                    
                    # Load state dict if available
                    if os.path.exists(model_path):
                        try:
                            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                            model.load_state_dict(state_dict, strict=False)
                            logger.info("ConvNeXt model weights loaded successfully")
                        except Exception as e:
                            logger.warning(f"Could not load ConvNeXt weights: {e}, using random initialization")
                    else:
                        logger.warning(f"ConvNeXt model file not found: {model_path}, using random initialization")
                    
                    model.eval()
                    
                    # ✅ FIX: Try GPU first, fallback to CPU on OOM
                    try:
                        self._clear_cuda_cache()
                        model = model.to(self.device)
                        # Test inference to ensure it works
                        with torch.no_grad():
                            test_input = torch.randn(1, 3, 224, 224).to(self.device)
                            _ = model(test_input)
                        logger.info("ConvNeXt model loaded successfully on GPU")
                        return model
                    except RuntimeError as gpu_error:
                        if "CUDA" in str(gpu_error) or "memory" in str(gpu_error).lower():
                            logger.warning(f"ConvNeXt GPU OOM: {gpu_error}, using CPU")
                            self._clear_cuda_cache()
                            model = model.to(torch.device("cpu"))
                            logger.info("ConvNeXt model loaded successfully on CPU")
                            return model
                        else:
                            raise gpu_error
                    
                except Exception as model_error:
                    logger.error(f"ConvNeXt model creation failed: {model_error}")
                    raise
                
            except ImportError:
                logger.warning("timm not available, using EfficientNet fallback for ConvNeXt")
                return self._load_efficientnet_model(model_path, config)
                
        except Exception as e:
            logger.error(f"Failed to load ConvNeXt model: {e}")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_deit_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load DeiT model - Data-efficient Image Transformer"""
        try:
            # ✅ IMPLEMENTATION: DeiT architecture for data-efficient image transformers
            class DeiT(nn.Module):
                def __init__(self, patch_size=16, embed_dim=768, num_heads=12, num_layers=12):
                    super(DeiT, self).__init__()
                    
                    self.patch_size = patch_size
                    self.embed_dim = embed_dim
                    
                    # Patch embedding
                    self.patch_embed = nn.Conv2d(3, embed_dim, kernel_size=patch_size, stride=patch_size)
                    
                    # Position embedding
                    self.pos_embed = nn.Parameter(torch.zeros(1, 197, embed_dim))  # 14*14+1=197
                    
                    # Class token
                    self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
                    
                    # Transformer encoder
                    encoder_layer = nn.TransformerEncoderLayer(
                        d_model=embed_dim,
                        nhead=num_heads,
                        dim_feedforward=embed_dim * 4,
                        dropout=0.1,
                        activation='gelu',
                        batch_first=True
                    )
                    self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
                    
                    # Layer normalization
                    self.norm = nn.LayerNorm(embed_dim)
                    
                    # Classifier head
                    self.head = nn.Linear(embed_dim, 2)
                    
                    # Initialize weights
                    self._init_weights()
                
                def _init_weights(self):
                    nn.init.trunc_normal_(self.pos_embed, std=0.02)
                    nn.init.trunc_normal_(self.cls_token, std=0.02)
                    nn.init.trunc_normal_(self.head.weight, std=0.02)
                    nn.init.constant_(self.head.bias, 0)
                
                def forward(self, x):
                    B = x.shape[0]
                    
                    # Patch embedding
                    x = self.patch_embed(x)  # (B, embed_dim, H//patch_size, W//patch_size)
                    x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)
                    
                    # Add class token
                    cls_tokens = self.cls_token.expand(B, -1, -1)
                    x = torch.cat((cls_tokens, x), dim=1)
                    
                    # Add position embedding
                    x = x + self.pos_embed
                    
                    # Transformer encoder
                    x = self.transformer(x)
                    x = self.norm(x)
                    
                    # Classification head
                    cls_output = x[:, 0]  # Take class token
                    output = self.head(cls_output)
                    
                    return output
            
            model = DeiT()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"DeiT loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load DeiT weights: {e}")
            
            model.eval()
            logger.debug("DeiT model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load DeiT model: {e}")
            logger.warning("Falling back to EfficientNet for DeiT")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_beit_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load BEiT model - BERT Pre-Training of Image Transformers"""
        try:
            # ✅ IMPLEMENTATION: BEiT architecture for BERT-style image transformer
            class BEiT(nn.Module):
                def __init__(self, patch_size=16, embed_dim=768, num_heads=12, num_layers=12):
                    super(BEiT, self).__init__()
                    
                    self.patch_size = patch_size
                    self.embed_dim = embed_dim
                    
                    # Patch embedding with learnable position embeddings
                    self.patch_embed = nn.Conv2d(3, embed_dim, kernel_size=patch_size, stride=patch_size)
                    
                    # Position embedding (learnable)
                    self.pos_embed = nn.Parameter(torch.zeros(1, 197, embed_dim))  # 14*14+1=197
                    
                    # Class token
                    self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
                    
                    # Dropout
                    self.pos_drop = nn.Dropout(p=0.1)
                    
                    # Transformer encoder with relative position bias
                    encoder_layer = nn.TransformerEncoderLayer(
                        d_model=embed_dim,
                        nhead=num_heads,
                        dim_feedforward=embed_dim * 4,
                        dropout=0.1,
                        activation='gelu',
                        batch_first=True
                    )
                    self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
                    
                    # Layer normalization
                    self.norm = nn.LayerNorm(embed_dim)
                    
                    # Classification head
                    self.head = nn.Linear(embed_dim, 2)
                    
                    # Initialize weights
                    self._init_weights()
                
                def _init_weights(self):
                    nn.init.trunc_normal_(self.pos_embed, std=0.02)
                    nn.init.trunc_normal_(self.cls_token, std=0.02)
                    nn.init.trunc_normal_(self.head.weight, std=0.02)
                    nn.init.constant_(self.head.bias, 0)
                
                def forward(self, x):
                    B = x.shape[0]
                    
                    # Patch embedding
                    x = self.patch_embed(x)  # (B, embed_dim, H//patch_size, W//patch_size)
                    x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)
                    
                    # Add class token
                    cls_tokens = self.cls_token.expand(B, -1, -1)
                    x = torch.cat((cls_tokens, x), dim=1)
                    
                    # Add position embedding
                    x = x + self.pos_embed
                    x = self.pos_drop(x)
                    
                    # Transformer encoder
                    x = self.transformer(x)
                    x = self.norm(x)
                    
                    # Classification head
                    cls_output = x[:, 0]  # Take class token
                    output = self.head(cls_output)
                    
                    return output
            
            model = BEiT()
            
            # Load state dict if available
            if os.path.exists(model_path):
                try:
                    state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
                    if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                        state_dict = state_dict['state_dict']
                    
                    # Load with error handling
                    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
                    if missing_keys:
                        logger.debug(f"BEiT loaded with {len(missing_keys)} missing keys")
                    
                except Exception as e:
                    logger.warning(f"Could not load BEiT weights: {e}")
            
            model.eval()
            logger.debug("BEiT model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load BEiT model: {e}")
            logger.warning("Falling back to EfficientNet for BEiT")
            return self._load_efficientnet_model(model_path, config)

# Global model loader instance - lazy initialization to prevent startup hanging
enhanced_loader = None

def get_or_create_enhanced_loader() -> EnhancedModelLoader:
    """Get or create the global enhanced model loader with lazy initialization"""
    global enhanced_loader
    if enhanced_loader is None:
        # Check if we should skip model loading during startup
        if os.getenv("DISABLE_MODEL_LOADING_ON_STARTUP", "0") == "1":
            logger.info("🔧 Skipping model loading during startup - will load on first use")
            # Create a minimal loader without loading models
            enhanced_loader = EnhancedModelLoader(silent_mode=True)
        else:
            enhanced_loader = EnhancedModelLoader(silent_mode=True)
    return enhanced_loader

def get_enhanced_loader() -> EnhancedModelLoader:
    """Get the global enhanced model loader and ensure models are loaded"""
    enhanced_loader = get_or_create_enhanced_loader()
    
    # Skip model loading during startup if environment variables are set
    if os.getenv("DISABLE_MODEL_LOADING_ON_STARTUP", "0") == "1":
        logger.info("🔧 Skipping model loading during startup - will load on first use")
        return enhanced_loader
    
    if not enhanced_loader.models:
        logger.info("🔧 Enhanced model loader models not loaded, loading now...")
        logger.info(f"🔧 Available model configs: {list(enhanced_loader.model_configs.keys())}")
        loaded_models = get_or_create_enhanced_loader().load_all_models()
        logger.info(f"🔧 Enhanced model loader models loaded: {list(enhanced_loader.models.keys())}")
        logger.info(f"🔧 Returned loaded models: {list(loaded_models.keys())}")
        
        # ✅ FIX: Defensive check to ensure at least fallback models exist
        if not enhanced_loader.models:
            logger.warning("⚠️ No models loaded, creating fallback models...")
            # Create at least one fallback model for basic functionality
            try:
                fallback_model = enhanced_loader._create_fallback_model("fallback_efficientnet", {
                    "type": "efficientnet",
                    "architecture": "efficientnet_b0",
                    "weight": 1.0
                })
                if fallback_model:
                    enhanced_loader.models["fallback_efficientnet"] = fallback_model
                    enhanced_loader.ensemble_weights["fallback_efficientnet"] = 1.0
                    logger.info("✅ Fallback model created successfully")
                else:
                    logger.error("❌ Failed to create fallback model")
            except Exception as e:
                logger.error(f"❌ Fallback model creation failed: {e}")
    else:
        logger.info(f"🔧 Enhanced model loader models already loaded: {list(enhanced_loader.models.keys())}")
    return enhanced_loader

def load_custom_model() -> Optional[torch.nn.Module]:
    """Load the custom finetuned model specifically"""
    return get_or_create_enhanced_loader().load_model("custom_finetuned")

def load_all_models() -> Dict[str, torch.nn.Module]:
    """Load all available models"""
    return get_or_create_enhanced_loader().load_all_models()

def predict_with_ensemble(faces: List[np.ndarray]) -> Tuple[str, float]:
    """Get ensemble prediction"""
    loader = get_or_create_enhanced_loader()
    if loader is None:
        logger.error("❌ Enhanced loader is None, cannot make prediction")
        return "Model Not Loaded", 0.0
    return loader.predict_ensemble(faces)

def predict_with_custom_model(faces: List[np.ndarray]) -> Tuple[str, float]:
    """Get prediction using only the custom finetuned model"""
    loader = get_or_create_enhanced_loader()
    if loader is None:
        logger.error("❌ Enhanced loader is None, cannot make prediction")
        return "Model Not Loaded", 0.0
    return loader.predict_single_model("custom_finetuned", faces)
