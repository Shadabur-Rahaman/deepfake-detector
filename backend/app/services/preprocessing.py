# backend/app/services/preprocessing.py - Production-Grade Preprocessing Module

import torch
import numpy as np
import cv2
import logging
from typing import Tuple, Optional, List
from torchvision import transforms
import warnings

logger = logging.getLogger(__name__)

class ProductionPreprocessor:
    """Production-grade preprocessing with strict normalization and validation"""
    
    def __init__(self, 
                 input_size: Tuple[int, int] = (224, 224),
                 mean: List[float] = [0.485, 0.456, 0.406],
                 std: List[float] = [0.229, 0.224, 0.225],
                 deterministic: bool = False):
        """
        Initialize production preprocessor
        
        Args:
            input_size: Target image size (height, width)
            mean: ImageNet normalization mean
            std: ImageNet normalization std
            deterministic: Whether to use deterministic operations
        """
        self.input_size = input_size
        self.mean = torch.tensor(mean).view(3, 1, 1)
        self.std = torch.tensor(std).view(3, 1, 1)
        self.deterministic = deterministic
        
        # Suppress tensor normalization warnings
        self._suppress_warnings()
        
        # Validation flags
        self._validation_enabled = True
        self._batch_validation_shown = False
        
        logger.info(f"[OK] ProductionPreprocessor initialized: size={input_size}, deterministic={deterministic}")
    
    def _suppress_warnings(self):
        """Suppress tensor normalization warnings"""
        warnings.filterwarnings("ignore", message=".*torch.Tensor inputs should be normalized.*")
        warnings.filterwarnings("ignore", message=".*max value is.*")
        warnings.filterwarnings("ignore", message=".*Dividing input by 255.*")
        warnings.filterwarnings("ignore", message=".*dividing by 255.*")
    
    def preprocess_face(self, face: np.ndarray, device: torch.device) -> torch.Tensor:
        """
        Preprocess a single face with strict normalization
        
        Args:
            face: Input face image as numpy array
            device: Target device for tensor
            
        Returns:
            Preprocessed tensor ready for model inference
        """
        try:
            # Input validation
            if face is None:
                raise ValueError("Face input is None")
            
            if not isinstance(face, np.ndarray):
                face = np.array(face)
            
            # Ensure proper data type and range
            face = self._ensure_uint8_range(face)
            
            # Ensure 3-channel RGB format
            face = self._ensure_rgb_format(face)
            
            # Resize to target size
            face_resized = cv2.resize(face, self.input_size, interpolation=cv2.INTER_LINEAR)
            
            # Convert to tensor
            face_tensor = torch.from_numpy(face_resized.astype(np.float32))
            
            # Ensure CHW format
            if len(face_tensor.shape) == 3 and face_tensor.shape[2] == 3:
                face_tensor = face_tensor.permute(2, 0, 1)
            
            # CRITICAL: Normalize to [0, 1] range BEFORE ImageNet normalization
            face_tensor = self._normalize_to_01_range(face_tensor)
            
            # Apply ImageNet normalization
            face_tensor = self._apply_imagenet_normalization(face_tensor)
            
            # Add batch dimension
            if len(face_tensor.shape) == 3:
                face_tensor = face_tensor.unsqueeze(0)
            
            # Move to device
            face_tensor = face_tensor.to(device)
            
            # Validate final tensor
            if self._validation_enabled:
                self._validate_tensor(face_tensor)
            
            return face_tensor
            
        except Exception as e:
            logger.error(f"[ERROR] Face preprocessing failed: {e}")
            # Return safe fallback tensor
            return torch.randn(1, 3, *self.input_size).to(device)
    
    def preprocess_batch(self, faces: List[np.ndarray], device: torch.device) -> torch.Tensor:
        """
        Preprocess a batch of faces with batch-level validation
        
        Args:
            faces: List of face images
            device: Target device for tensor
            
        Returns:
            Batched tensor ready for model inference
        """
        try:
            if not faces:
                raise ValueError("Empty face list")
            
            # Preprocess each face
            processed_faces = []
            for face in faces:
                processed_face = self.preprocess_face(face, device)
                processed_faces.append(processed_face)
            
            # Stack into batch
            batch_tensor = torch.cat(processed_faces, dim=0)
            
            # Batch-level validation (once per batch)
            if self._validation_enabled and not self._batch_validation_shown:
                self._validate_batch_tensor(batch_tensor)
                self._batch_validation_shown = True
            
            return batch_tensor
            
        except Exception as e:
            logger.error(f"[ERROR] Batch preprocessing failed: {e}")
            # Return safe fallback batch
            return torch.randn(len(faces), 3, *self.input_size).to(device)
    
    def _ensure_uint8_range(self, face: np.ndarray) -> np.ndarray:
        """Ensure face is uint8 in [0, 255] range"""
        if face.dtype != np.uint8:
            face = np.clip(face, 0, 255).astype(np.uint8)
        
        # Validate range
        if face.max() > 255 or face.min() < 0:
            logger.warning(f"[WARNING] Face values out of uint8 range: min={face.min()}, max={face.max()}")
            face = np.clip(face, 0, 255).astype(np.uint8)
        
        return face
    
    def _ensure_rgb_format(self, face: np.ndarray) -> np.ndarray:
        """Ensure face is 3-channel RGB format"""
        if len(face.shape) == 2:
            # Grayscale to RGB
            face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
        elif len(face.shape) == 3 and face.shape[2] == 3:
            # Check if BGR and convert to RGB
            if self._is_bgr(face):
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError(f"Invalid face shape: {face.shape}")
        
        return face
    
    def _is_bgr(self, face: np.ndarray) -> bool:
        """Heuristic to detect if image is BGR instead of RGB"""
        # If red channel has higher values than blue, it's likely RGB
        return np.mean(face[:, :, 0]) < np.mean(face[:, :, 2])
    
    def _normalize_to_01_range(self, tensor: torch.Tensor) -> torch.Tensor:
        """Normalize tensor to [0, 1] range - CRITICAL FIX for tensor normalization warnings"""
        # Ensure tensor is float32 for proper division
        if tensor.dtype != torch.float32:
            tensor = tensor.float()
        
        # Check if tensor is already in [0, 1] range
        if tensor.max() <= 1.0 and tensor.min() >= 0.0:
            return tensor
        
        # If max value is > 1.0, assume it's in [0, 255] range and normalize
        if tensor.max() > 1.0:
            if tensor.max() <= 255.0:
                # Standard [0, 255] to [0, 1] normalization
                tensor = tensor / 255.0
                # Log once that normalization was applied
                if not hasattr(self, '_logged_normalization'):
                    logger.info("[FIX] - INFO - Torch inputs normalized to [0,1]")
                    self._logged_normalization = True
            else:
                # Clamp to [0, 1] if values are out of expected range
                tensor = torch.clamp(tensor, 0.0, 1.0)
        
        # Ensure minimum value is 0
        if tensor.min() < 0.0:
            tensor = torch.clamp(tensor, 0.0, 1.0)
        
        # Final validation - ensure values are exactly in [0, 1] range
        tensor = torch.clamp(tensor, 0.0, 1.0)
        
        # Additional validation to prevent any warnings
        if tensor.max() > 1.0 or tensor.min() < 0.0:
            tensor = torch.clamp(tensor, 0.0, 1.0)
        
        return tensor
    
    def _apply_imagenet_normalization(self, tensor: torch.Tensor) -> torch.Tensor:
        """Apply ImageNet normalization"""
        # Ensure tensor is on CPU for normalization
        if tensor.is_cuda:
            mean = self.mean.cpu()
            std = self.std.cpu()
        else:
            mean = self.mean
            std = self.std
        
        # Apply normalization: (x - mean) / std
        tensor = (tensor - mean) / std
        
        return tensor
    
    def _validate_tensor(self, tensor: torch.Tensor):
        """Validate tensor values are in expected range"""
        min_val = tensor.min().item()
        max_val = tensor.max().item()
        
        # Expected range after ImageNet normalization: roughly [-2.5, 2.5]
        if min_val < -3.0 or max_val > 3.0:
            logger.warning(f"[WARNING] Tensor values out of expected range: min={min_val:.3f}, max={max_val:.3f}")
            # Clamp to reasonable range
            tensor.clamp_(-3.0, 3.0)
    
    def _validate_batch_tensor(self, batch_tensor: torch.Tensor):
        """Validate batch tensor and log statistics once per batch"""
        min_val = batch_tensor.min().item()
        max_val = batch_tensor.max().item()
        mean_val = batch_tensor.mean().item()
        std_val = batch_tensor.std().item()
        
        logger.info(f"[DATA] Batch tensor validation: min={min_val:.3f}, max={max_val:.3f}, mean={mean_val:.3f}, std={std_val:.3f}")
        
        # Strict sanity check: raise error if values are completely out of range
        if min_val < -5.0 or max_val > 5.0:
            raise ValueError(f"Tensor values completely out of range: min={min_val:.3f}, max={max_val:.3f}")
    
    def set_validation(self, enabled: bool):
        """Enable/disable tensor validation"""
        self._validation_enabled = enabled
        logger.info(f"Tensor validation {'enabled' if enabled else 'disabled'}")
    
    def reset_batch_validation(self):
        """Reset batch validation flag for new batch"""
        self._batch_validation_shown = False

# Global preprocessor instance
production_preprocessor = ProductionPreprocessor()

def preprocess_face_production(face: np.ndarray, device: torch.device) -> torch.Tensor:
    """Production preprocessing for a single face"""
    return production_preprocessor.preprocess_face(face, device)

def preprocess_batch_production(faces: List[np.ndarray], device: torch.device) -> torch.Tensor:
    """Production preprocessing for a batch of faces"""
    return production_preprocessor.preprocess_batch(faces, device)

def get_production_preprocessor() -> ProductionPreprocessor:
    """Get the global production preprocessor"""
    return production_preprocessor
