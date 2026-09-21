"""
Fast Model Loader Module
Provides optimized model loading for deepfake detection
"""

import logging
import os
import torch
from typing import Optional, Dict, Any, Union
import time

logger = logging.getLogger(__name__)

class FastModelLoader:
    """
    Fast model loader with optimized loading strategies
    """
    
    def __init__(self, device: str = "auto"):
        """
        Initialize fast model loader
        
        Args:
            device: Device to use for model loading ("auto", "cpu", "cuda")
        """
        self.device = self._get_safe_device(device)
        self.loaded_models = {}
        self.model_cache = {}
        
        logger.info(f"🚀 FastModelLoader initialized with device: {self.device}")
    
    def _get_safe_device(self, device: str) -> str:
        """
        Get a safe device for model loading
        
        Args:
            device: Requested device
            
        Returns:
            Safe device string
        """
        if device == "auto":
            if torch.cuda.is_available():
                try:
                    # Test CUDA device
                    test_tensor = torch.tensor([1.0], device="cuda")
                    del test_tensor
                    return "cuda"
                except Exception as e:
                    logger.warning(f"CUDA test failed: {e}, using CPU")
                    return "cpu"
            else:
                return "cpu"
        elif device == "cuda" and torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    def load_model_fast(self, model_name: str, **kwargs) -> Optional[Any]:
        """
        Load a model with optimized loading strategy
        
        Args:
            model_name: Name of the model to load
            **kwargs: Additional model parameters
            
        Returns:
            Loaded model or None if failed
        """
        try:
            logger.info(f"🔄 Loading model: {model_name}")
            start_time = time.time()
            
            # Check cache first
            cache_key = f"{model_name}_{self.device}"
            if cache_key in self.model_cache:
                logger.info(f"✅ Using cached model: {model_name}")
                return self.model_cache[cache_key]
            
            # Load model based on name
            if model_name == "custom_finetuned":
                model = self._load_custom_finetuned_model(**kwargs)
            elif model_name == "efficientnet":
                model = self._load_efficientnet_model(**kwargs)
            elif model_name == "mesonet":
                model = self._load_mesonet_model(**kwargs)
            elif model_name == "yolov8":
                model = self._load_yolov8_model(**kwargs)
            else:
                logger.warning(f"Unknown model: {model_name}")
                return None
            
            if model is not None:
                # Cache the model
                self.model_cache[cache_key] = model
                self.loaded_models[model_name] = model
                
                load_time = time.time() - start_time
                logger.info(f"✅ Model {model_name} loaded in {load_time:.2f}s")
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return None
    
    def _load_custom_finetuned_model(self, **kwargs) -> Optional[Any]:
        """
        Load custom finetuned model - YOUR TRAINED MODEL
        
        Returns:
            Custom model or None
        """
        try:
            import torch.nn as nn
            from torchvision import models
            
            logger.info("Loading YOUR trained deepfake_detector_finetuned1.pth model...")
            
            # Get the path to your trained model
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, '../../ml_artifacts/deepfake_detector_finetuned1.pth')
            
            if not os.path.exists(model_path):
                logger.error(f"Your trained model not found at: {model_path}")
                return None
            
            # Load your trained EfficientNet model
            model = models.efficientnet_b0(weights=None)
            num_ftrs = model.classifier[1].in_features
            model.classifier = nn.Sequential(nn.Dropout(p=0.2, inplace=True), nn.Linear(num_ftrs, 1))
            
            # Load your trained weights
            state_dict = torch.load(model_path, map_location=self.device)
            if any(key.startswith('module.') for key in state_dict.keys()):
                state_dict = {key.replace('module.', ''): value for key, value in state_dict.items()}
            
            model.load_state_dict(state_dict)
            model.to(self.device)
            model.eval()
            
            logger.info("✅ YOUR trained model loaded successfully!")
            return model
            
        except Exception as e:
            logger.error(f"Your trained model loading failed: {e}")
            return None
    
    def _load_efficientnet_model(self, **kwargs) -> Optional[Any]:
        """
        Load EfficientNet model
        
        Returns:
            EfficientNet model or None
        """
        try:
            import torchvision.models as models
            
            logger.info("Loading EfficientNet model...")
            model = models.efficientnet_b0(pretrained=True)
            model.eval()
            model.to(self.device)
            
            return model
            
        except Exception as e:
            logger.error(f"EfficientNet loading failed: {e}")
            return None
    
    def _load_mesonet_model(self, **kwargs) -> Optional[Any]:
        """
        Load MesoNet model
        
        Returns:
            MesoNet model or None
        """
        try:
            logger.info("Loading MesoNet model...")
            
            # Simulate MesoNet model
            class MesoNetModel:
                def __init__(self):
                    self.device = self.device
                    self.is_loaded = True
                
                def predict(self, x):
                    return torch.randn(x.shape[0], 2)
            
            model = MesoNetModel()
            return model
            
        except Exception as e:
            logger.error(f"MesoNet loading failed: {e}")
            return None
    
    def _load_yolov8_model(self, **kwargs) -> Optional[Any]:
        """
        Load YOLOv8 model
        
        Returns:
            YOLOv8 model or None
        """
        try:
            from ultralytics import YOLO
            
            logger.info("Loading YOLOv8 model...")
            model = YOLO('yolov8n.pt')
            model.to(self.device)
            
            return model
            
        except Exception as e:
            logger.error(f"YOLOv8 loading failed: {e}")
            return None
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """
        Get a loaded model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model or None if not loaded
        """
        return self.loaded_models.get(model_name)
    
    def unload_model(self, model_name: str) -> bool:
        """
        Unload a model to free memory
        
        Args:
            model_name: Name of the model to unload
            
        Returns:
            True if unloaded successfully
        """
        try:
            if model_name in self.loaded_models:
                del self.loaded_models[model_name]
                
                # Remove from cache
                cache_key = f"{model_name}_{self.device}"
                if cache_key in self.model_cache:
                    del self.model_cache[cache_key]
                
                # Clear CUDA cache if using CUDA
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                
                logger.info(f"✅ Unloaded model: {model_name}")
                return True
            else:
                logger.warning(f"Model {model_name} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {e}")
            return False
    
    def get_loaded_models(self) -> Dict[str, Any]:
        """
        Get all loaded models
        
        Returns:
            Dictionary of loaded models
        """
        return self.loaded_models.copy()
    
    def clear_cache(self) -> None:
        """
        Clear model cache to free memory
        """
        try:
            self.model_cache.clear()
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("✅ Model cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

# Global instance
_fast_loader = None

def get_fast_loader(device: str = "auto") -> FastModelLoader:
    """
    Get global fast loader instance
    
    Args:
        device: Device to use
        
    Returns:
        FastModelLoader instance
    """
    global _fast_loader
    
    if _fast_loader is None:
        _fast_loader = FastModelLoader(device)
    
    return _fast_loader
