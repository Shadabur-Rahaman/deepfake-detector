# backend/app/services/deterministic_config.py - Deterministic Configuration Module

import torch
import numpy as np
import random
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class DeterministicConfig:
    """Configuration for deterministic inference and training"""
    
    def __init__(self, 
                 enable_deterministic: bool = True,
                 seed: int = 42,
                 cuda_deterministic: bool = True):
        """
        Initialize deterministic configuration
        
        Args:
            enable_deterministic: Whether to enable deterministic mode
            seed: Random seed for reproducibility
            cuda_deterministic: Whether to enable CUDA deterministic operations
        """
        self.enable_deterministic = enable_deterministic
        self.seed = seed
        self.cuda_deterministic = cuda_deterministic
        
        # Model weights for ensemble - BALANCED to prevent EfficientNet dominance
        self.model_weights = {
            'efficientnet_b0': 0.20,  # Reduced from 0.35 to prevent dominance
            'yolov8_face': 0.15,
            'mesonet': 0.25,  # Increased from 0.20
            'resnet50': 0.20,  # Increased from 0.15
            'vit': 0.15,  # Increased from 0.10
            'vivit': 0.05
        }
        
        # Thresholds for decision making - CONSERVATIVE for real videos
        self.thresholds = {
            'deepfake_threshold': 0.6,  # Raised from 0.5 - more conservative
            'min_confidence_for_fake': 0.8,  # Raised from 0.7 - require higher confidence for fake
            'uncertainty_threshold': 0.05,  # Threshold for uncertain predictions
            'temporal_window_size': 5,  # Window size for temporal smoothing
            'temporal_smoothing_alpha': 0.3  # Alpha for exponential smoothing
        }
        
        # Preprocessing configuration
        self.preprocessing_config = {
            'input_size': [224, 224],
            'normalization_mean': [0.485, 0.456, 0.406],
            'normalization_std': [0.229, 0.224, 0.225],
            'interpolation': 'bilinear',
            'deterministic': True
        }
        
        # Probability calibration
        self.calibration_config = {
            'temperature': 1.5,
            'enable_calibration': True,
            'uncertainty_penalty': 0.1
        }
        
        # Initialize deterministic settings
        if self.enable_deterministic:
            self._setup_deterministic()
    
    def _setup_deterministic(self):
        """Setup deterministic operations"""
        try:
            # Set random seeds
            random.seed(self.seed)
            np.random.seed(self.seed)
            torch.manual_seed(self.seed)
            
            # Set CUDA deterministic operations
            if self.cuda_deterministic and torch.cuda.is_available():
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
                torch.cuda.manual_seed(self.seed)
                torch.cuda.manual_seed_all(self.seed)
                
                # Set environment variables for CUDA deterministic behavior
                os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'
                os.environ['PYTHONHASHSEED'] = str(self.seed)
            
            logger.info(f"[OK] Deterministic mode enabled with seed {self.seed}")
            logger.info(f"[OK] CUDA deterministic: {self.cuda_deterministic}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to setup deterministic mode: {e}")
            self.enable_deterministic = False
    
    def ensure_model_deterministic(self, model: torch.nn.Module):
        """Ensure model is in deterministic mode"""
        if not self.enable_deterministic:
            return
        
        try:
            # Set model to eval mode
            model.eval()
            
            # Disable dropout and batch norm training behavior
            for module in model.modules():
                if isinstance(module, (torch.nn.Dropout, torch.nn.Dropout2d, torch.nn.Dropout3d)):
                    module.eval()
                elif isinstance(module, (torch.nn.BatchNorm1d, torch.nn.BatchNorm2d, torch.nn.BatchNorm3d)):
                    module.eval()
                    module.training = False
            
            logger.debug("[OK] Model configured for deterministic inference")
            
        except Exception as e:
            logger.warning(f"[WARNING] Failed to configure model for deterministic mode: {e}")
    
    def get_model_weights(self) -> Dict[str, float]:
        """Get model weights for ensemble"""
        return self.model_weights.copy()
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get thresholds for decision making"""
        return self.thresholds.copy()
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get preprocessing configuration"""
        return self.preprocessing_config.copy()
    
    def get_calibration_config(self) -> Dict[str, Any]:
        """Get probability calibration configuration"""
        return self.calibration_config.copy()
    
    def generate_preprocessing_hash(self, face: np.ndarray) -> str:
        """Generate deterministic hash for preprocessing validation"""
        try:
            import hashlib
            
            # Create deterministic hash from face data
            face_bytes = face.tobytes()
            hash_obj = hashlib.md5(face_bytes)
            return hash_obj.hexdigest()[:8]  # First 8 characters
            
        except Exception as e:
            logger.warning(f"[WARNING] Failed to generate preprocessing hash: {e}")
            return "unknown"
    
    def set_threshold(self, threshold_name: str, value: float):
        """Update a threshold value"""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value
            logger.info(f"[OK] Threshold {threshold_name} updated to {value}")
        else:
            logger.warning(f"[WARNING] Unknown threshold: {threshold_name}")
    
    def set_model_weight(self, model_name: str, weight: float):
        """Update a model weight"""
        if model_name in self.model_weights:
            self.model_weights[model_name] = weight
            logger.info(f"[OK] Model weight {model_name} updated to {weight}")
        else:
            logger.warning(f"[WARNING] Unknown model: {model_name}")
    
    def set_calibration_temperature(self, temperature: float):
        """Update calibration temperature"""
        if temperature > 0:
            self.calibration_config['temperature'] = temperature
            logger.info(f"[OK] Calibration temperature updated to {temperature}")
        else:
            logger.warning(f"[WARNING] Invalid temperature: {temperature}")
    
    def disable_deterministic(self):
        """Disable deterministic mode"""
        self.enable_deterministic = False
        logger.info("[OK] Deterministic mode disabled")
    
    def enable_deterministic_mode(self):
        """Enable deterministic mode"""
        self.enable_deterministic = True
        self._setup_deterministic()
        logger.info("[OK] Deterministic mode enabled")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get complete configuration summary"""
        return {
            'deterministic_enabled': self.enable_deterministic,
            'seed': self.seed,
            'cuda_deterministic': self.cuda_deterministic,
            'model_weights': self.model_weights,
            'thresholds': self.thresholds,
            'preprocessing_config': self.preprocessing_config,
            'calibration_config': self.calibration_config
        }

# Global deterministic configuration
_deterministic_config = None

def get_deterministic_config() -> DeterministicConfig:
    """Get the global deterministic configuration"""
    global _deterministic_config
    if _deterministic_config is None:
        _deterministic_config = DeterministicConfig()
    return _deterministic_config

def set_deterministic_config(config: DeterministicConfig):
    """Set the global deterministic configuration"""
    global _deterministic_config
    _deterministic_config = config
    logger.info("[OK] Global deterministic configuration updated")

def reset_deterministic_config():
    """Reset the global deterministic configuration to defaults"""
    global _deterministic_config
    _deterministic_config = DeterministicConfig()
    logger.info("[OK] Global deterministic configuration reset to defaults")

def setup_deterministic_inference(seed: int = 42, cuda_deterministic: bool = True):
    """
    Setup deterministic inference with given parameters
    
    Args:
        seed: Random seed for reproducibility
        cuda_deterministic: Whether to enable CUDA deterministic operations
    """
    try:
        config = DeterministicConfig(
            enable_deterministic=True,
            seed=seed,
            cuda_deterministic=cuda_deterministic
        )
        set_deterministic_config(config)
        logger.info(f"[OK] Deterministic inference setup with seed {seed}")
        return config
    except Exception as e:
        logger.error(f"[ERROR] Failed to setup deterministic inference: {e}")
        return None

def ensure_deterministic_startup():
    """Ensure deterministic mode is properly initialized at startup"""
    try:
        config = get_deterministic_config()
        if config.enable_deterministic:
            logger.info("[OK] Deterministic mode already enabled")
        else:
            config.enable_deterministic_mode()
            logger.info("[OK] Deterministic mode enabled at startup")
        return True
    except Exception as e:
        logger.error(f"[ERROR] Failed to ensure deterministic startup: {e}")
        return False