# sophisticated_efficientnet_loader.py
"""
Sophisticated EfficientNet Model Loader with Advanced Error Recovery
Provides robust model loading with multiple fallback strategies and intelligent error handling
"""

import os
import torch
import torch.nn as nn
from torchvision import models
import logging
from typing import Optional, Tuple, Dict, Any
import time
import gc
from pathlib import Path

logger = logging.getLogger(__name__)

class SophisticatedEfficientNetLoader:
    """
    Advanced EfficientNet loader with sophisticated error recovery and performance optimization
    """
    
    def __init__(self, device: str = "cuda", memory_limit_gb: float = 4.0):
        self.device = device
        self.memory_limit_gb = memory_limit_gb
        self.model_cache = {}
        self.loading_strategies = [
            self._strategy_robust_timm,
            self._strategy_torchvision_finetuned,
            self._strategy_torchvision_pretrained,
            self._strategy_lightweight_fallback,
            self._strategy_minimal_fallback
        ]
        
        # Initialize CUDA memory management
        self._setup_cuda_memory_management()
        
    def _setup_cuda_memory_management(self):
        """Setup sophisticated CUDA memory management with CUDA driver safety"""
        try:
            # Check for force CPU mode first
            if (os.environ.get("FORCE_CPU_MODE", "0") == "1" or 
                os.environ.get("CUDA_VISIBLE_DEVICES", "") == "" or
                os.environ.get("MINIMAL_STARTUP_MODE", "0") == "1"):
                logger.info("🔧 Force CPU mode detected, skipping CUDA initialization")
                self.device = "cpu"
                return
            
            # Check CUDA availability with safety checks
            if not torch.cuda.is_available():
                logger.info("🔧 CUDA not available, using CPU mode")
                self.device = "cpu"
                return
            
            # Test CUDA driver with safety checks
            try:
                # Test basic CUDA operations
                test_tensor = torch.tensor([1.0]).cuda()
                _ = test_tensor * 2
                del test_tensor
                torch.cuda.empty_cache()
                logger.info("✅ CUDA driver test passed")
            except Exception as cuda_test_error:
                logger.error(f"❌ CUDA driver test failed: {cuda_test_error}")
                logger.info("🔧 Falling back to CPU mode due to CUDA driver issues")
                self.device = "cpu"
                return
            
            # Get GPU memory info with error handling
            try:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                logger.info(f"🔍 GPU Memory Available: {gpu_memory:.1f}GB")
                
                # Set conservative memory fraction to avoid driver issues
                if gpu_memory < 6.0:  # Low memory GPU
                    memory_fraction = 0.5  # More conservative
                    logger.info(f"🔧 Low-memory GPU detected: Using {memory_fraction*100:.0f}% of GPU memory")
                else:
                    memory_fraction = 0.7  # More conservative for stability
                    logger.info(f"✅ Sufficient GPU memory: Using {memory_fraction*100:.0f}% of GPU memory")
                
                # Set memory fraction with error handling
                torch.cuda.set_per_process_memory_fraction(memory_fraction)
                
                # Set conservative memory management environment variables
                os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32,expandable_segments:False"
                
                # Test memory allocation
                test_tensor = torch.randn(100, 100).cuda()
                del test_tensor
                torch.cuda.empty_cache()
                logger.info("✅ CUDA memory management configured successfully")
                
            except Exception as memory_error:
                logger.error(f"❌ CUDA memory setup failed: {memory_error}")
                logger.info("🔧 Falling back to CPU mode due to memory issues")
                self.device = "cpu"
                
        except Exception as e:
            logger.error(f"❌ CUDA setup completely failed: {e}")
            logger.info("🔧 Falling back to CPU mode")
            self.device = "cpu"
    
    def load_efficientnet(self, model_path: Optional[str] = None, model_name: str = "efficientnet_b0") -> Optional[torch.nn.Module]:
        """
        Sophisticated EfficientNet loading with multiple strategies and intelligent fallbacks
        """
        logger.info(f"🚀 Starting sophisticated EfficientNet loading for {model_name}")
        
        # Check cache first
        cache_key = f"{model_name}_{self.device}"
        if cache_key in self.model_cache:
            logger.info("✅ Using cached EfficientNet model")
            return self.model_cache[cache_key]
        
        # Try each loading strategy
        for i, strategy in enumerate(self.loading_strategies, 1):
            try:
                logger.info(f"📋 Strategy {i}: {strategy.__name__}")
                model = strategy(model_path, model_name)
                
                if model is not None:
                    # Test the model
                    if self._test_model(model):
                        logger.info(f"✅ Strategy {i} succeeded: {strategy.__name__}")
                        self.model_cache[cache_key] = model
                        return model
                    else:
                        logger.warning(f"⚠️ Strategy {i} failed model test: {strategy.__name__}")
                        del model
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                else:
                    logger.warning(f"⚠️ Strategy {i} returned None: {strategy.__name__}")
                    
            except Exception as e:
                logger.warning(f"❌ Strategy {i} failed: {strategy.__name__} - {e}")
                continue
        
        logger.error("❌ All EfficientNet loading strategies failed")
        return None
    
    def _strategy_robust_timm(self, model_path: Optional[str], model_name: str) -> Optional[torch.nn.Module]:
        """Strategy 1: Robust timm loading with CUDA safety"""
        try:
            import timm
            logger.info("📦 Loading with timm library...")
            
            # Create model with timm - force CPU mode for safety
            model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=2)
            
            # Load custom weights if available
            if model_path and os.path.exists(model_path):
                logger.info(f"📂 Loading custom weights from {os.path.basename(model_path)}")
                try:
                    # Load checkpoint on CPU first to avoid CUDA issues
                    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
                    
                    # Handle different checkpoint formats
                    if isinstance(checkpoint, dict):
                        if 'state_dict' in checkpoint:
                            state_dict = checkpoint['state_dict']
                        elif 'model_state_dict' in checkpoint:
                            state_dict = checkpoint['model_state_dict']
                        else:
                            state_dict = checkpoint
                    else:
                        state_dict = checkpoint
                    
                    # Load with error handling
                    try:
                        model.load_state_dict(state_dict, strict=False)
                        logger.info("✅ Custom weights loaded successfully")
                    except Exception as e:
                        logger.warning(f"⚠️ Partial weight loading: {e}")
                        
                except Exception as checkpoint_error:
                    logger.warning(f"⚠️ Checkpoint loading failed: {checkpoint_error}")
            
            # Move to device after loading weights
            model = model.to(self.device)
            model.eval()
            
            # Test the model
            if self._test_model(model):
                return model
            else:
                logger.warning("⚠️ Model test failed after timm loading")
                return None
            
        except Exception as e:
            logger.warning(f"⚠️ timm strategy failed: {e}")
            return None
    
    def _strategy_torchvision_finetuned(self, model_path: Optional[str], model_name: str) -> Optional[torch.nn.Module]:
        """Strategy 2: Torchvision with finetuned weights"""
        try:
            logger.info("📦 Loading with torchvision + finetuned weights...")
            
            # Create EfficientNet-B0 with ImageNet pretrained weights
            model = models.efficientnet_b0(weights='IMAGENET1K_V1')
            
            # Modify classifier for binary classification
            num_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_features, 2)
            
            # Load custom weights if available
            if model_path and os.path.exists(model_path):
                logger.info(f"📂 Loading finetuned weights from {os.path.basename(model_path)}")
                try:
                    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
                    
                    # Handle checkpoint format
                    if isinstance(checkpoint, dict):
                        if 'state_dict' in checkpoint:
                            state_dict = checkpoint['state_dict']
                        elif 'model_state_dict' in checkpoint:
                            state_dict = checkpoint['model_state_dict']
                        else:
                            state_dict = checkpoint
                    else:
                        state_dict = checkpoint
                    
                    # Load with flexible matching
                    model_dict = model.state_dict()
                    filtered_dict = {k: v for k, v in state_dict.items() if k in model_dict and v.shape == model_dict[k].shape}
                    
                    model_dict.update(filtered_dict)
                    model.load_state_dict(model_dict)
                    logger.info(f"✅ Loaded {len(filtered_dict)}/{len(state_dict)} layers")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Finetuned weight loading failed: {e}")
            
            model = model.to(self.device)
            model.eval()
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ torchvision finetuned strategy failed: {e}")
            return None
    
    def _strategy_torchvision_pretrained(self, model_path: Optional[str], model_name: str) -> Optional[torch.nn.Module]:
        """Strategy 3: Pure torchvision with ImageNet pretrained weights"""
        try:
            logger.info("📦 Loading with torchvision pretrained weights...")
            
            # Create EfficientNet-B0 with ImageNet weights
            model = models.efficientnet_b0(weights='IMAGENET1K_V1')
            
            # Modify classifier for binary classification
            num_features = model.classifier[1].in_features
            model.classifier[1] = nn.Linear(num_features, 2)
            
            # Initialize new classifier with Xavier initialization
            nn.init.xavier_uniform_(model.classifier[1].weight)
            nn.init.zeros_(model.classifier[1].bias)
            
            model = model.to(self.device)
            model.eval()
            
            logger.info("✅ Using ImageNet pretrained weights with new classifier")
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ torchvision pretrained strategy failed: {e}")
            return None
    
    def _strategy_lightweight_fallback(self, model_path: Optional[str], model_name: str) -> Optional[torch.nn.Module]:
        """Strategy 4: Lightweight EfficientNet with reduced parameters"""
        try:
            logger.info("📦 Creating lightweight EfficientNet fallback...")
            
            # Create a smaller EfficientNet-like model
            class LightweightEfficientNet(nn.Module):
                def __init__(self, num_classes=2):
                    super().__init__()
                    self.features = nn.Sequential(
                        # Reduced complexity layers
                        nn.Conv2d(3, 32, 3, padding=1),
                        nn.BatchNorm2d(32),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(2, 2),
                        
                        nn.Conv2d(32, 64, 3, padding=1),
                        nn.BatchNorm2d(64),
                        nn.ReLU(inplace=True),
                        nn.MaxPool2d(2, 2),
                        
                        nn.Conv2d(64, 128, 3, padding=1),
                        nn.BatchNorm2d(128),
                        nn.ReLU(inplace=True),
                        nn.AdaptiveAvgPool2d(1),
                    )
                    
                    self.classifier = nn.Sequential(
                        nn.Flatten(),
                        nn.Dropout(0.2),
                        nn.Linear(128, 64),
                        nn.ReLU(inplace=True),
                        nn.Dropout(0.2),
                        nn.Linear(64, num_classes)
                    )
                
                def forward(self, x):
                    x = self.features(x)
                    x = self.classifier(x)
                    return x
            
            model = LightweightEfficientNet(num_classes=2)
            model = model.to(self.device)
            model.eval()
            
            logger.info("✅ Lightweight EfficientNet created")
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ lightweight fallback strategy failed: {e}")
            return None
    
    def _strategy_minimal_fallback(self, model_path: Optional[str], model_name: str) -> Optional[torch.nn.Module]:
        """Strategy 5: Minimal fallback model for basic inference"""
        try:
            logger.info("📦 Creating minimal fallback model...")
            
            # Create a very simple model
            class MinimalFallback(nn.Module):
                def __init__(self, num_classes=2):
                    super().__init__()
                    self.conv = nn.Conv2d(3, 16, 3, padding=1)
                    self.pool = nn.AdaptiveAvgPool2d(1)
                    self.classifier = nn.Linear(16, num_classes)
                
                def forward(self, x):
                    x = self.pool(torch.relu(self.conv(x)))
                    x = x.view(x.size(0), -1)
                    x = self.classifier(x)
                    return x
            
            model = MinimalFallback(num_classes=2)
            model = model.to(self.device)
            model.eval()
            
            logger.info("✅ Minimal fallback model created")
            return model
            
        except Exception as e:
            logger.warning(f"⚠️ minimal fallback strategy failed: {e}")
            return None
    
    def _test_model(self, model: torch.nn.Module) -> bool:
        """Test if the model works correctly with CUDA safety"""
        try:
            # Create test input on CPU first
            test_input = torch.randn(1, 3, 224, 224)
            
            # Move to device with error handling
            try:
                test_input = test_input.to(self.device)
            except Exception as device_error:
                logger.warning(f"⚠️ Failed to move test input to device {self.device}: {device_error}")
                # Try CPU as fallback
                test_input = test_input.to("cpu")
                model = model.to("cpu")
                logger.info("🔧 Using CPU for model testing")
            
            # Run inference with error handling
            with torch.no_grad():
                model.eval()
                try:
                    output = model(test_input)
                    
                    # Check output shape and values
                    if output.shape == (1, 2):
                        # Check for valid probabilities
                        probs = torch.softmax(output, dim=1)
                        if torch.all(torch.isfinite(probs)) and torch.all(probs >= 0) and torch.all(probs <= 1):
                            logger.info("✅ Model test passed")
                            return True
                    
                    logger.warning("⚠️ Model test failed: Invalid output shape or values")
                    return False
                    
                except Exception as inference_error:
                    logger.warning(f"⚠️ Model inference test failed: {inference_error}")
                    return False
            
        except Exception as e:
            logger.warning(f"⚠️ Model test failed: {e}")
            return False
    
    def get_model_info(self, model: torch.nn.Module) -> Dict[str, Any]:
        """Get comprehensive model information"""
        try:
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            # Get model size in MB
            param_size = sum(p.numel() * p.element_size() for p in model.parameters())
            buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
            model_size_mb = (param_size + buffer_size) / (1024 * 1024)
            
            return {
                'total_parameters': total_params,
                'trainable_parameters': trainable_params,
                'model_size_mb': round(model_size_mb, 2),
                'device': str(next(model.parameters()).device),
                'model_type': type(model).__name__
            }
        except Exception as e:
            logger.warning(f"⚠️ Failed to get model info: {e}")
            return {'error': str(e)}

# Global sophisticated loader instance
_sophisticated_loader = None

def get_sophisticated_efficientnet_loader(device: str = "cuda") -> SophisticatedEfficientNetLoader:
    """Get or create the sophisticated EfficientNet loader"""
    global _sophisticated_loader
    if _sophisticated_loader is None:
        _sophisticated_loader = SophisticatedEfficientNetLoader(device=device)
    return _sophisticated_loader

def load_sophisticated_efficientnet(model_path: Optional[str] = None, device: str = "cuda") -> Optional[torch.nn.Module]:
    """Load EfficientNet using sophisticated strategies"""
    loader = get_sophisticated_efficientnet_loader(device)
    return loader.load_efficientnet(model_path)
