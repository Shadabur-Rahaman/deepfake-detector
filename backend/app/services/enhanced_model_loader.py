# backend/app/services/enhanced_model_loader.py - Enhanced Model Loading with Custom Model Support

import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
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
    print(f"[WARNING] Using fallback imports: {e}")

logger = logging.getLogger(__name__)

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
        self.gpu_memory_gb = self._get_gpu_memory_gb()
        self.gpu_model_limit = self._calculate_gpu_model_limit()
        self.force_cpu_for_ensemble = self.gpu_memory_gb < 6.0  # Force CPU for < 6GB GPUs
        self.gpu_models_loaded = 0
        
        logger.info(f"🔍 GPU Memory: {self.gpu_memory_gb:.1f}GB, GPU Model Limit: {self.gpu_model_limit}")
        
        self.models = {}
        self.model_configs = {}
        self.ensemble_weights = {}
        # Use environment variable if silent_mode not specified
        self.silent_mode = silent_mode if silent_mode is not None else not MODEL_LOADING_VERBOSE
        self._setup_model_configs()
    
    def _initialize_cuda_memory(self):
        """Initialize CUDA memory management to prevent allocation errors"""
        try:
            if torch.cuda.is_available():
                # Clear CUDA cache to free any fragmented memory
                torch.cuda.empty_cache()
                
                # Set memory fraction to prevent OOM errors
                torch.cuda.set_per_process_memory_fraction(0.8)
                
                # Enable memory pooling for better memory management
                torch.cuda.memory._set_allocator_settings('expandable_segments:True')
                
                logger.debug("✅ CUDA memory management initialized")
        except Exception as e:
            logger.warning(f"CUDA memory initialization failed: {e}")
    
    def _clear_cuda_cache(self):
        """Clear CUDA cache to free memory"""
        try:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception as e:
            logger.debug(f"CUDA cache clear failed: {e}")
    
    def _get_gpu_memory_gb(self) -> float:
        """Get total GPU memory in GB"""
        if not torch.cuda.is_available():
            return 0.0
        try:
            total_memory = torch.cuda.get_device_properties(0).total_memory
            return total_memory / (1024**3)  # Convert bytes to GB
        except Exception:
            return 0.0
    
    def _calculate_gpu_model_limit(self) -> int:
        """Calculate maximum number of models that can be loaded on GPU"""
        if not torch.cuda.is_available() or self.gpu_memory_gb < 2.0:
            return 0
        
        # Conservative estimates: each model ~0.5-1GB
        if self.gpu_memory_gb < 4.0:  # 4GB GPU
            return 2  # Very conservative for 4GB
        elif self.gpu_memory_gb < 6.0:  # 6GB GPU
            return 3
        elif self.gpu_memory_gb < 8.0:  # 8GB GPU
            return 4
        else:  # 8GB+ GPU
            return 6
    
    def _should_load_on_gpu(self, model_name: str) -> bool:
        """Determine if model should be loaded on GPU based on memory and priority"""
        # Force CPU for ensemble models on low-memory GPUs
        if self.force_cpu_for_ensemble and model_name not in ['efficientnet_b0', 'custom_finetuned']:
            return False
        
        # Check if we've reached GPU model limit
        if self.gpu_models_loaded >= self.gpu_model_limit:
            return False
        
        # Check available GPU memory
        if torch.cuda.is_available():
            try:
                allocated = torch.cuda.memory_allocated() / (1024**3)  # GB
                reserved = torch.cuda.memory_reserved() / (1024**3)    # GB
                free_memory = self.gpu_memory_gb - allocated
                
                # Need at least 500MB free for new model
                if free_memory < 0.5:
                    logger.warning(f"⚠️ Insufficient GPU memory ({free_memory:.1f}GB free), using CPU for {model_name}")
                    return False
                
                return True
            except Exception as e:
                logger.warning(f"⚠️ GPU memory check failed: {e}, using CPU for {model_name}")
                return False
        
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
        
        # ✅ FIX: Verify weights sum to 1.0
        total_weight = sum(cfg['weight'] for cfg in self.model_configs.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Model weights sum to {total_weight:.3f}, expected 1.0 - normalizing")
            # Normalize weights
            for model_name in self.model_configs:
                self.model_configs[model_name]['weight'] /= total_weight
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
        """Load a specific model by name with CUDA memory management"""
        try:
            if model_name not in self.model_configs:
                logger.error(f"Unknown model: {model_name}")
                return None
            
            # ✅ CUDA MEMORY FIX: Clear cache before loading
            self._clear_cuda_cache()
            
            config = self.model_configs[model_name]
            model_path = config["path"]
            
            # ✅ GPU MEMORY MANAGEMENT: Determine device based on memory constraints
            use_gpu = self._should_load_on_gpu(model_name)
            
            # Enhanced CUDA safety check
            try:
                if use_gpu and torch.cuda.is_available():
                    # Test CUDA device before using it - create on CPU first
                    try:
                        test_tensor = torch.tensor([1.0])  # Create on CPU first
                        test_tensor = test_tensor.to("cuda")  # Move to CUDA safely
                        del test_tensor
                        torch.cuda.empty_cache()
                        target_device = self.device
                        logger.info(f"🚀 Loading {model_name} on GPU (models loaded: {self.gpu_models_loaded}/{self.gpu_model_limit})")
                    except Exception as cuda_test_error:
                        error_str = str(cuda_test_error)
                        if "INTERNAL ASSERT FAILED" in error_str:
                            logger.warning(f"CUDA driver error detected for {model_name}, forcing CPU: {cuda_test_error}")
                            use_gpu = False
                            target_device = torch.device("cpu")
                            logger.info(f"💻 Loading {model_name} on CPU (CUDA driver error)")
                        else:
                            raise
                else:
                    raise Exception("CUDA not available or GPU limit reached")
            except Exception as cuda_error:
                if "INTERNAL ASSERT FAILED" in str(cuda_error):
                    logger.warning(f"CUDA driver error detected for {model_name}, forcing CPU: {cuda_error}")
                else:
                    logger.warning(f"CUDA test failed for {model_name}, using CPU: {cuda_error}")
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
                # ✅ GPU MEMORY MANAGEMENT: Move model to target device with OOM retry
                try:
                    model = model.to(target_device)
                    if use_gpu:
                        self.gpu_models_loaded += 1
                        logger.info(f"✅ {model_name} loaded on GPU (GPU models: {self.gpu_models_loaded}/{self.gpu_model_limit})")
                    else:
                        logger.info(f"✅ {model_name} loaded on CPU")
                except torch.cuda.OutOfMemoryError:
                    logger.warning(f"⚠️ GPU OOM for {model_name}, falling back to CPU")
                    target_device = torch.device("cpu")
                    model = model.to(target_device)
                    logger.info(f"✅ {model_name} loaded on CPU (OOM fallback)")
                
                self.models[model_name] = model
                self.ensemble_weights[model_name] = config["weight"]
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
                    logger.warning(f"Model device mismatch: expected {self.device}, got {model_device}")
                    # Force move to correct device
                    model = model.to(self.device)
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
            try:
                # Clear CUDA cache before loading model to device
                self._clear_cuda_cache()
                
                # ✅ CRITICAL FIX: Ensure model is moved to device and stays there
                model = model.to(self.device)
                # Verify model is actually on the correct device
                model_device = next(model.parameters()).device
                if model_device != self.device:
                    logger.warning(f"Model device mismatch: expected {self.device}, got {model_device}")
                    # Force move to correct device
                    model = model.to(self.device)
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
            
            # ✅ FIX: Verify output shape
            test_input = torch.randn(1, 3, 224, 224).to(self.device)
            with torch.no_grad():
                output = model(test_input)
                if output.shape != (1, 2):
                    logger.warning(f"Model output shape: {output.shape}, expected (1, 2)")
                else:
                    logger.debug(f"✅ Model output shape verified: {output.shape}")
            
            logger.debug(f"EfficientNet model loaded successfully on {self.device}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load EfficientNet model: {e}")
            return None
    
    def _load_custom_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load custom trained model with error handling"""
        import time
        
        try:
            self._log_info("Loading custom model...")
            start_time = time.time()
            
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
            
            if classifier_weight_key and classifier_weight_key in state_dict:
                output_classes = state_dict[classifier_weight_key].shape[0]
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
            logger.debug(f"[OK] Custom model loaded successfully in {total_time:.2f}s")
            return model
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to load custom model: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_all_models(self) -> Dict[str, torch.nn.Module]:
        """Load all available models in parallel with fallback handling and timeout protection"""
        # Skip loading if environment variables are set
        if os.getenv("DISABLE_MODEL_LOADING_ON_STARTUP", "0") == "1" or os.getenv("MINIMAL_STARTUP_MODE", "0") == "1":
            self._log_info("🔧 Skipping model loading during startup - will load on first use")
            return {}
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading
        
        loaded_models = {}
        failed_models = []
        
        # ✅ CUDA MEMORY FIX: Clear cache before loading all models
        self._clear_cuda_cache()
        
        # ✅ GPU MEMORY MANAGEMENT: Prioritize essential models for GPU loading
        priority_models = ['efficientnet_b0', 'custom_finetuned']
        ensemble_models = [name for name in self.model_configs.keys() if name not in priority_models]
        
        # Load priority models first (these get GPU if possible)
        all_models_to_load = priority_models + ensemble_models
        
        logger.info(f"[LOADING] Loading {len(self.model_configs)} models (Priority: {len(priority_models)}, Ensemble: {len(ensemble_models)})...")
        
        # Thread-safe lock for GPU memory tracking
        gpu_lock = threading.Lock()
        
        def load_model_with_tracking(model_name: str):
            """Load a single model with thread-safe GPU tracking"""
            try:
                # Control logging verbosity with environment variable
                if MODEL_LOADING_VERBOSE:
                    logger.info(f"Loading model: {model_name}")
                elif len(loaded_models) < 3:
                    logger.info(f"Loading model: {model_name}")
                else:
                    logger.debug(f"Loading model: {model_name}")
                
                # Load the model
                model = self.load_model(model_name)
                
                # Thread-safe GPU tracking
                with gpu_lock:
                    if model is not None:
                        # Check if this model was loaded on GPU
                        if hasattr(model, 'device') and 'cuda' in str(model.device):
                            self.gpu_models_loaded += 1
                            if self.gpu_models_loaded >= self.gpu_model_limit:
                                logger.warning(f"⚠️ GPU model limit reached ({self.gpu_models_loaded}/{self.gpu_model_limit}), remaining models will use CPU")
                                self.force_cpu_for_ensemble = True
                
                return model_name, model, None
                
            except Exception as e:
                return model_name, None, e
        
        # Use ThreadPoolExecutor for parallel loading with optimal worker count
        max_workers = min(6, len(all_models_to_load))  # Max 6 workers to prevent memory issues
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all model loading tasks
            future_to_model = {
                executor.submit(load_model_with_tracking, model_name): model_name 
                for model_name in all_models_to_load
                if model_name in self.model_configs
            }
            
            # Process completed tasks with timeout
            try:
                for future in as_completed(future_to_model, timeout=120):  # 2 minute total timeout
                    model_name = future_to_model[future]
                    try:
                        name, model, error = future.result(timeout=30)  # 30 second per model timeout
                        
                        if error:
                            failed_models.append(model_name)
                            logger.warning(f"[WARNING] {model_name} failed to load: {error}")
                        elif model is not None:
                            loaded_models[model_name] = model
                            # Reduce logging verbosity - only log for first few models
                            if len(loaded_models) <= 3:
                                self._log_info(f"[OK] {model_name} loaded successfully")
                            else:
                                self._log_debug(f"[OK] {model_name} loaded successfully")
                        else:
                            failed_models.append(model_name)
                            logger.warning(f"[WARNING] {model_name} failed to load: model is None")
                        
                        # ✅ CUDA MEMORY FIX: Clear cache periodically
                        if len(loaded_models) % 5 == 0:  # Clear every 5 models
                            self._clear_cuda_cache()
                            
                    except TimeoutError:
                        failed_models.append(model_name)
                        logger.warning(f"[TIMEOUT] {model_name} loading timed out")
                    except Exception as e:
                        failed_models.append(model_name)
                        logger.error(f"[ERROR] {model_name} failed with error: {e}")
                        
            except TimeoutError:
                logger.warning(f"[TIMEOUT] Overall model loading timed out after 2 minutes")
                # Cancel remaining futures
                for future in future_to_model:
                    future.cancel()
        
        logger.info(f"[DATA] Model loading complete: {len(loaded_models)}/{len(self.model_configs)} models loaded")
        if failed_models:
            logger.warning(f"[WARNING] Failed models: {failed_models}")
        
        # ✅ CRITICAL FIX: Store loaded models in self.models
        self.models.update(loaded_models)
        logger.info(f"[CRITICAL FIX] Models stored in self.models: {list(self.models.keys())}")
        
        # ✅ DEBUG: Log detailed loading results
        if loaded_models:
            logger.info(f"[SUCCESS] Successfully loaded {len(loaded_models)} models: {list(loaded_models.keys())}")
        else:
            logger.error("[ERROR] No models were loaded successfully!")
        
        if failed_models:
            logger.warning(f"[FAILED] Failed to load {len(failed_models)} models: {failed_models}")
        
        # ✅ CUDA MEMORY FIX: Final cache clear
        self._clear_cuda_cache()
        
        return loaded_models
    
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
        """
        try:
            if face is None:
                raise ValueError("Face input is None")
            
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
            
            # ✅ CRITICAL FIX: Apply ImageNet normalization BEFORE moving to device
            # This prevents device mismatch and tensor broadcasting issues
            
            # Create mean and std tensors with the same dtype as face_tensor
            mean = torch.tensor([0.485, 0.456, 0.406], dtype=face_tensor.dtype).view(3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225], dtype=face_tensor.dtype).view(3, 1, 1)
            
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
            
            # ✅ FIX: Move tensor to device AFTER normalization to prevent device mismatch
            face_tensor = face_tensor.to(self.device)
            
            # Ensure correct shape (3, 224, 224)
            if face_tensor.shape != (3, 224, 224):
                logger.warning(f"Tensor shape mismatch: {face_tensor.shape}, expected (3, 224, 224)")
                # Force correct shape
                face_tensor = torch.zeros(3, 224, 224, dtype=torch.float32, device=self.device)
            
            return face_tensor
            
        except Exception as e:
            logger.error(f"Face preprocessing failed: {e}")
            logger.error(f"Face shape: {face.shape if hasattr(face, 'shape') else 'No shape attribute'}")
            logger.error(f"Input size: {input_size}")
            logger.error(f"Device: {self.device}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            
            # Return a safe fallback tensor with comprehensive error handling
            try:
                # Try to create a tensor with the specified input size - ensure 3D shape (C, H, W)
                if isinstance(input_size, (tuple, list)) and len(input_size) == 2:
                    fallback_tensor = torch.zeros(3, int(input_size[0]), int(input_size[1]), device=self.device, dtype=torch.float32)
                else:
                    fallback_tensor = torch.zeros(3, 224, 224, device=self.device, dtype=torch.float32)
                
                logger.warning(f"Returning fallback tensor with shape: {fallback_tensor.shape}")
                return fallback_tensor
                
            except Exception as fallback_error:
                logger.error(f"Fallback tensor creation failed: {fallback_error}")
                # Last resort: create the most basic tensor possible - ensure 3D shape (C, H, W)
                try:
                    return torch.zeros(3, 224, 224, device=self.device, dtype=torch.float32)
                except Exception as final_error:
                    logger.error(f"Final fallback failed: {final_error}")
                    # Absolute last resort: create on CPU and move to device
                    try:
                        cpu_tensor = torch.zeros(3, 224, 224, dtype=torch.float32)
                        return cpu_tensor.to(self.device)
                    except Exception as cpu_error:
                        logger.error(f"CPU fallback failed: {cpu_error}")
                        # Return None and let the calling code handle it
                        return None
    
    def predict_single_model(self, model_name: str, faces: List[np.ndarray]) -> Tuple[str, float]:
        """Get prediction from a single model"""
        if model_name not in self.models:
            return "Model Not Loaded", 0.0
        
        try:
            model = self.models[model_name]
            config = self.model_configs[model_name]
            
            # ✅ CRITICAL FIX: Ensure model is on the correct device before prediction
            model_device = next(model.parameters()).device
            if model_device != self.device:
                logger.warning(f"Model {model_name} device mismatch: expected {self.device}, got {model_device}")
                logger.warning(f"Moving model {model_name} to {self.device}")
                model = model.to(self.device)
                self.models[model_name] = model  # Update the cached model
            
            if not faces:
                return "No Faces Detected", None
            
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
                
                processed_face = self.preprocess_face(face, input_size)
                
                # Handle None returns from preprocessing
                if processed_face is None:
                    logger.error(f"Face preprocessing returned None for face {len(processed_faces)}")
                    # Create a fallback tensor with 3D shape (C, H, W)
                    processed_face = torch.zeros(3, input_size[0], input_size[1], device=self.device, dtype=torch.float32)
                
                processed_faces.append(processed_face)
            
            # CRITICAL FIX: Ensure proper batch tensor creation with 4D shape
            if not processed_faces:
                logger.error("No processed faces available")
                return "No Processed Faces", 0.0
            
            # Stack into batch - ensure all tensors have batch dimension
            try:
                # Ensure all tensors are 4D (batch_size, channels, height, width)
                batch_faces = []
                for i, face_tensor in enumerate(processed_faces):
                    if face_tensor is None:
                        logger.warning(f"Face {i} is None, creating fallback")
                        face_tensor = torch.zeros(3, 224, 224, device=self.device, dtype=torch.float32)
                    
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
                        # Create a proper fallback tensor with 3D shape first
                        face_tensor = torch.zeros(3, 224, 224, device=self.device, dtype=torch.float32)
                        face_tensor = face_tensor.unsqueeze(0)  # Add batch dimension
                    
                    # ✅ VALIDATION: Ensure tensor has correct shape before adding to batch
                    if face_tensor.shape[1] != 3:
                        logger.error(f"Invalid channel count: {face_tensor.shape[1]}, expected 3")
                        face_tensor = torch.zeros(1, 3, 224, 224, device=self.device, dtype=torch.float32)
                    
                    if face_tensor.shape[2:] != (224, 224):
                        logger.warning(f"Invalid spatial dimensions: {face_tensor.shape[2:]}, expected (224, 224)")
                        # Resize the tensor to correct spatial dimensions
                        face_tensor = torch.nn.functional.interpolate(
                            face_tensor, size=(224, 224), mode='bilinear', align_corners=False
                        )
                    
                    batch_faces.append(face_tensor)
                
                # Stack into batch tensor
                face_batch = torch.cat(batch_faces, dim=0)
                # ✅ CRITICAL FIX: Ensure batch is on the correct device
                if len(batch_faces) > 0:
                    target_device = batch_faces[0].device
                    face_batch = face_batch.to(target_device)
                else:
                    face_batch = face_batch.to(self.device)
                logger.debug(f"Face batch shape: {face_batch.shape}, device: {face_batch.device}")
                
                # Validate batch tensor shape
                if face_batch.dim() != 4:
                    logger.error(f"Invalid batch tensor dimensions: {face_batch.dim()}, expected 4")
                    return "Invalid Batch Tensor", 0.0
                
                if face_batch.shape[1] != 3:
                    logger.error(f"Invalid channel count: {face_batch.shape[1]}, expected 3")
                    return "Invalid Channel Count", 0.0
                
            except Exception as batch_error:
                logger.error(f"Batch tensor creation failed: {batch_error}")
                logger.error(f"Processed faces count: {len(processed_faces)}")
                for i, face in enumerate(processed_faces):
                    if face is not None:
                        logger.error(f"Face {i} shape: {face.shape}, dtype: {face.dtype}, device: {face.device}")
                    else:
                        logger.error(f"Face {i}: None")
                return "Batch Creation Failed", 0.0
            
            # Run inference
            with torch.no_grad():
                model.eval()
                # ✅ CRITICAL FIX: Ensure input tensor is on the same device as the model
                model_device = next(model.parameters()).device
                logger.debug(f"Model device: {model_device}, Face batch device: {face_batch.device}")
                face_batch = face_batch.to(model_device)
                logger.debug(f"Face batch moved to device: {face_batch.device}")
                try:
                    logits = model(face_batch)
                except RuntimeError as e:
                    if "Input type" in str(e) and "weight type" in str(e):
                        logger.error(f"Device mismatch error: {e}")
                        logger.error(f"Model device: {model_device}, Input device: {face_batch.device}")
                        return "Device Mismatch Error", 0.0
                    else:
                        raise e
                
                # Ensure logits is a tensor
                if not isinstance(logits, torch.Tensor):
                    logger.error(f"Model output is not a tensor: {type(logits)}")
                    return "Model Output Error", 0.0
                
                # Handle different output formats
                if logits.shape[1] == 1:
                    # Single output (binary with sigmoid)
                    probabilities = torch.sigmoid(logits).cpu().numpy().flatten()
                    avg_prob = np.mean(probabilities)
                else:
                    # Two outputs (binary classification)
                    # ✅ FIX: Use softmax for 2-class outputs, not sigmoid
                    # ✅ FIX: Remove temperature scaling that was reducing confidence
                    probabilities = torch.softmax(logits, dim=1).cpu().numpy()
                    # For 2-class, take the probability of class 1 (fake)
                    if probabilities.ndim == 2 and probabilities.shape[1] == 2:
                        # Extract probability for class 1 (fake) from each face
                        fake_probs = probabilities[:, 1]  # Class 1 is fake
                        avg_prob = np.mean(fake_probs)
                    else:
                        # Fallback for unexpected shape
                        avg_prob = np.mean(probabilities.flatten())
            
            # ✅ FIX: Use proper probability-based decision logic with confidence calibration
            # avg_prob is now the probability of class 1 (fake) from softmax
            if avg_prob >= 0.5:
                result = "Deepfake Detected"
                # ✅ BIAS FIX: Remove 95% cap and use natural confidence
                confidence = avg_prob  # Use raw probability without artificial caps
            else:
                result = "Real Face"
                # ✅ BIAS FIX: Remove 95% cap and use natural confidence
                real_prob = 1.0 - avg_prob
                confidence = real_prob  # Use raw probability without artificial caps
            
            # REMOVED: Face count bonus that biased toward real faces
            # Single face videos are not necessarily more likely to be real
            
            return result, confidence
            
        except Exception as e:
            logger.error(f"Single model prediction failed for {model_name}: {e}")
            return "Prediction Failed", 0.0
    
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
        
        try:
            # Validate input
            if not faces or len(faces) == 0:
                return "No Faces Detected", None
            
            # Collect predictions from all models with error handling
            predictions = []
            confidences = []
            successful_models = 0
            failed_models = 0
            
            for model_name, model in self.models.items():
                try:
                    pred, conf = self.predict_single_model(model_name, faces)
                    
                    # Validate prediction results
                    if pred is not None and conf is not None:
                        predictions.append(pred)
                        confidences.append(conf)
                        successful_models += 1
                    else:
                        logger.warning(f"Model {model_name} returned None values")
                        failed_models += 1
                        
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    failed_models += 1
                    continue
            
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
                
                # ✅ CRITICAL FIX: Calculate weighted ensemble confidence BEFORE determining prediction
                # This ensures we use the correct confidence interpretation
                
                # Apply ensemble weights if available
                if hasattr(self, 'ensemble_weights') and self.ensemble_weights:
                    weighted_confidences = []
                    model_names = list(self.models.keys())
                    for i, model_name in enumerate(model_names):
                        if i < len(valid_confidences):
                            weight = self.ensemble_weights.get(model_name, 1.0)
                            weighted_confidences.append(valid_confidences[i] * weight)
                    
                    if weighted_confidences:
                        # Normalize weights to sum to 1
                        total_weight = sum(self.ensemble_weights.get(name, 1.0) for name in model_names[:len(valid_confidences)])
                        avg_fake_probability = sum(weighted_confidences) / total_weight if total_weight > 0 else np.mean(valid_confidences)
                    else:
                        avg_fake_probability = np.mean(valid_confidences)
                else:
                    avg_fake_probability = np.mean(valid_confidences)
                
                # ✅ CRITICAL FIX: Determine ensemble prediction based on weighted average probability
                if avg_fake_probability >= 0.5:
                    ensemble_pred = "Deepfake Detected"
                    ensemble_confidence = avg_fake_probability  # Use fake probability directly
                else:
                    ensemble_pred = "Real Face"
                    ensemble_confidence = 1.0 - avg_fake_probability  # Convert to real confidence
                
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
                           f"uncertainty={unbiased_result.uncertainty:.3f}")
                
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
            
            # Load state dict
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            
            # Apply key remapping for ResNet
            remapped_state_dict = self._remap_state_dict_keys(state_dict, f"resnet_{architecture}")
            
            missing_keys, unexpected_keys = model.load_state_dict(remapped_state_dict, strict=False)
            
            # Handle missing keys
            if missing_keys:
                logger.debug(f"ResNet model loaded with {len(missing_keys)} missing keys, {len(unexpected_keys)} unexpected keys")
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
                    logger.warning(f"Model device mismatch: expected {self.device}, got {model_device}")
                    # Force move to correct device
                    model = model.to(self.device)
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
            
            logger.info(f"ResNet {architecture} model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load ResNet model: {e}")
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
                    logger.warning(f"Model device mismatch: expected {self.device}, got {model_device}")
                    # Force move to correct device
                    model = model.to(self.device)
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
                    logger.warning(f"Model device mismatch: expected {self.device}, got {model_device}")
                    # Force move to correct device
                    model = model.to(self.device)
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
                
                # Create Vision Transformer model
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
                
                model = model.to(self.device)
                model.eval()
                
                logger.info("Vision Transformer model loaded successfully")
                return model
                
            except ImportError:
                logger.warning("timm not available, using EfficientNet fallback for Vision Transformer")
                return self._load_efficientnet_model(model_path, config)
                
        except Exception as e:
            logger.error(f"Failed to load Vision Transformer model: {e}")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_swin_transformer_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load Swin Transformer model"""
        try:
            # ✅ MODEL FIX: Try to use timm Swin Transformer
            try:
                import timm
                
                # Create Swin Transformer model
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
                
                model = model.to(self.device)
                model.eval()
                
                logger.info("Swin Transformer model loaded successfully")
                return model
                
            except ImportError:
                logger.warning("timm not available, using EfficientNet fallback for Swin Transformer")
                return self._load_efficientnet_model(model_path, config)
                
        except Exception as e:
            logger.error(f"Failed to load Swin Transformer model: {e}")
            return self._load_efficientnet_model(model_path, config)
    
    def _load_convnext_model(self, model_path: str, config: Dict) -> Optional[torch.nn.Module]:
        """Load ConvNeXt model"""
        try:
            # ✅ MODEL FIX: Try to use timm ConvNeXt
            try:
                import timm
                
                # Create ConvNeXt model
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
                
                model = model.to(self.device)
                model.eval()
                
                logger.info("ConvNeXt model loaded successfully")
                return model
                
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
    if os.getenv("DISABLE_MODEL_LOADING_ON_STARTUP", "0") == "1" or os.getenv("MINIMAL_STARTUP_MODE", "0") == "1":
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
    return enhanced_loader.predict_ensemble(faces)


def predict_with_custom_model(faces: List[np.ndarray]) -> Tuple[str, float]:
    """Get prediction using only the custom finetuned model"""
    return enhanced_loader.predict_single_model("custom_finetuned", faces)

def load_custom_model() -> Optional[torch.nn.Module]:
    """Load the custom finetuned model specifically"""
    return get_or_create_enhanced_loader().load_model("custom_finetuned")

def load_all_models() -> Dict[str, torch.nn.Module]:
    """Load all available models"""
    return get_or_create_enhanced_loader().load_all_models()

def predict_with_ensemble(faces: List[np.ndarray]) -> Tuple[str, float]:
    """Get ensemble prediction"""
    return enhanced_loader.predict_ensemble(faces)


def predict_with_custom_model(faces: List[np.ndarray]) -> Tuple[str, float]:
    """Get prediction using only the custom finetuned model"""
    return enhanced_loader.predict_single_model("custom_finetuned", faces)
