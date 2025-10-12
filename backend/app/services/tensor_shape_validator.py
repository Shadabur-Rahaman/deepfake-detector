"""
Tensor Shape Validation Utility
==============================

This module provides comprehensive tensor shape validation and debugging
for PyTorch tensors used in deepfake detection.

Author: Senior ML Engineer
Date: 2024
"""

import torch
import numpy as np
import logging
from typing import Tuple, Optional, Union

logger = logging.getLogger(__name__)

class TensorShapeValidator:
    """Comprehensive tensor shape validation and debugging"""
    
    def __init__(self):
        self.validation_count = 0
        self.error_count = 0
    
    def validate_tensor_shape(self, tensor: torch.Tensor, expected_shape: Optional[Tuple] = None, 
                            name: str = "tensor") -> bool:
        """
        Validate tensor shape and log detailed information
        
        Args:
            tensor: PyTorch tensor to validate
            expected_shape: Expected shape tuple (optional)
            name: Name for logging purposes
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.validation_count += 1
            
            # Basic tensor info
            shape = tensor.shape
            device = tensor.device
            dtype = tensor.dtype
            dims = tensor.dim()
            
            logger.debug(f"🔍 {name} validation #{self.validation_count}:")
            logger.debug(f"   Shape: {shape}")
            logger.debug(f"   Device: {device}")
            logger.debug(f"   Dtype: {dtype}")
            logger.debug(f"   Dimensions: {dims}")
            
            # Check if tensor is empty
            if tensor.numel() == 0:
                logger.error(f"❌ {name} is empty!")
                self.error_count += 1
                return False
            
            # Check for NaN or Inf values
            if torch.isnan(tensor).any():
                logger.warning(f"⚠️ {name} contains NaN values")
            if torch.isinf(tensor).any():
                logger.warning(f"⚠️ {name} contains Inf values")
            
            # Check value range
            min_val = tensor.min().item()
            max_val = tensor.max().item()
            logger.debug(f"   Value range: [{min_val:.4f}, {max_val:.4f}]")
            
            # Validate against expected shape
            if expected_shape is not None:
                if shape != expected_shape:
                    logger.error(f"❌ {name} shape mismatch!")
                    logger.error(f"   Expected: {expected_shape}")
                    logger.error(f"   Actual: {shape}")
                    self.error_count += 1
                    return False
                else:
                    logger.debug(f"✅ {name} shape matches expected")
            
            # Check for common issues
            if dims < 2:
                logger.warning(f"⚠️ {name} has {dims} dimensions (expected >= 2)")
            
            if dims == 3 and shape[0] not in [1, 3]:
                logger.warning(f"⚠️ {name} has unusual channel count: {shape[0]}")
            
            if dims == 4 and shape[1] not in [1, 3]:
                logger.warning(f"⚠️ {name} has unusual channel count: {shape[1]}")
            
            logger.debug(f"✅ {name} validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ {name} validation failed: {e}")
            self.error_count += 1
            return False
    
    def validate_imagenet_normalization(self, tensor: torch.Tensor, mean: torch.Tensor, 
                                      std: torch.Tensor, name: str = "tensor") -> bool:
        """
        Validate ImageNet normalization compatibility
        
        Args:
            tensor: Input tensor
            mean: Mean tensor
            std: Std tensor
            name: Name for logging
            
        Returns:
            bool: True if compatible, False otherwise
        """
        try:
            logger.debug(f"🔍 ImageNet normalization validation for {name}:")
            
            # Validate input tensor
            if not self.validate_tensor_shape(tensor, name=f"{name}_input"):
                return False
            
            # Validate mean tensor
            if not self.validate_tensor_shape(mean, name=f"{name}_mean"):
                return False
            
            # Validate std tensor
            if not self.validate_tensor_shape(std, name=f"{name}_std"):
                return False
            
            # Check device compatibility
            if tensor.device != mean.device or tensor.device != std.device:
                logger.error(f"❌ Device mismatch in {name} normalization:")
                logger.error(f"   Tensor device: {tensor.device}")
                logger.error(f"   Mean device: {mean.device}")
                logger.error(f"   Std device: {std.device}")
                return False
            
            # Check dtype compatibility
            if tensor.dtype != mean.dtype or tensor.dtype != std.dtype:
                logger.error(f"❌ Dtype mismatch in {name} normalization:")
                logger.error(f"   Tensor dtype: {tensor.dtype}")
                logger.error(f"   Mean dtype: {mean.dtype}")
                logger.error(f"   Std dtype: {std.dtype}")
                return False
            
            # Check broadcasting compatibility
            try:
                # Test broadcasting without actually computing
                torch.broadcast_shapes(tensor.shape, mean.shape, std.shape)
                logger.debug(f"✅ {name} normalization broadcasting compatible")
            except Exception as e:
                logger.error(f"❌ Broadcasting incompatible for {name}: {e}")
                return False
            
            logger.debug(f"✅ {name} ImageNet normalization validation passed")
            return True
            
        except Exception as e:
            logger.error(f"❌ {name} ImageNet normalization validation failed: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get validation statistics"""
        return {
            "total_validations": self.validation_count,
            "error_count": self.error_count,
            "success_rate": (self.validation_count - self.error_count) / max(self.validation_count, 1)
        }
    
    def reset_statistics(self):
        """Reset validation statistics"""
        self.validation_count = 0
        self.error_count = 0
        logger.info("Tensor validation statistics reset")

# Global validator instance
tensor_validator = TensorShapeValidator()

def validate_tensor_for_imagenet(tensor: torch.Tensor, name: str = "tensor") -> bool:
    """
    Validate tensor for ImageNet normalization
    
    Args:
        tensor: Input tensor
        name: Name for logging
        
    Returns:
        bool: True if valid for ImageNet normalization
    """
    # Basic shape validation
    if not tensor_validator.validate_tensor_shape(tensor, name=name):
        return False
    
    # Check if tensor is in [0, 1] range (required for ImageNet)
    min_val = tensor.min().item()
    max_val = tensor.max().item()
    
    if min_val < 0.0 or max_val > 1.0:
        logger.warning(f"⚠️ {name} not in [0, 1] range: [{min_val:.4f}, {max_val:.4f}]")
        logger.warning(f"   Consider normalizing to [0, 1] range before ImageNet normalization")
    
    # Check tensor dimensions
    if tensor.dim() not in [3, 4]:
        logger.error(f"❌ {name} has {tensor.dim()} dimensions, expected 3 or 4")
        return False
    
    # Check channel count
    if tensor.dim() == 3:
        if tensor.shape[0] != 3:
            logger.error(f"❌ {name} has {tensor.shape[0]} channels, expected 3")
            logger.error(f"   Tensor shape: {tensor.shape}")
            logger.error(f"   This suggests the tensor might be in HWC format instead of CHW format")
            logger.error(f"   Try: tensor.permute(2, 0, 1) to convert from HWC to CHW")
            return False
    elif tensor.dim() == 4:
        if tensor.shape[1] != 3:
            logger.error(f"❌ {name} has {tensor.shape[1]} channels, expected 3")
            logger.error(f"   Tensor shape: {tensor.shape}")
            logger.error(f"   This suggests the tensor might be in BHWC format instead of BCHW format")
            logger.error(f"   Try: tensor.permute(0, 3, 1, 2) to convert from BHWC to BCHW")
            return False
    
    logger.debug(f"✅ {name} is valid for ImageNet normalization")
    return True

def safe_imagenet_normalization(tensor: torch.Tensor, mean: list = [0.485, 0.456, 0.406], 
                               std: list = [0.229, 0.224, 0.225], name: str = "tensor") -> torch.Tensor:
    """
    Safe ImageNet normalization with comprehensive validation
    
    Args:
        tensor: Input tensor
        mean: Mean values
        std: Std values
        name: Name for logging
        
    Returns:
        torch.Tensor: Normalized tensor
    """
    try:
        # Validate input tensor
        if not validate_tensor_for_imagenet(tensor, name):
            raise ValueError(f"Invalid tensor for ImageNet normalization: {name}")
        
        # Create mean and std tensors with proper device and dtype
        mean_tensor = torch.tensor(mean, device=tensor.device, dtype=tensor.dtype).view(3, 1, 1)
        std_tensor = torch.tensor(std, device=tensor.device, dtype=tensor.dtype).view(3, 1, 1)
        
        # Validate normalization compatibility
        if not tensor_validator.validate_imagenet_normalization(tensor, mean_tensor, std_tensor, name):
            raise ValueError(f"ImageNet normalization incompatible: {name}")
        
        # Apply normalization with proper broadcasting
        if tensor.dim() == 3:  # (C, H, W)
            normalized = (tensor - mean_tensor) / std_tensor
        elif tensor.dim() == 4:  # (B, C, H, W)
            mean_tensor = mean_tensor.unsqueeze(0)  # (1, 3, 1, 1)
            std_tensor = std_tensor.unsqueeze(0)    # (1, 3, 1, 1)
            normalized = (tensor - mean_tensor) / std_tensor
        else:
            raise ValueError(f"Unexpected tensor dimensions: {tensor.shape}")
        
        logger.debug(f"✅ {name} ImageNet normalization completed successfully")
        return normalized
        
    except Exception as e:
        logger.error(f"❌ {name} ImageNet normalization failed: {e}")
        raise

if __name__ == "__main__":
    # Test the validator
    test_tensor = torch.randn(3, 224, 224)
    validate_tensor_for_imagenet(test_tensor, "test_tensor")
    
    normalized = safe_imagenet_normalization(test_tensor, name="test_tensor")
    print(f"Normalized tensor shape: {normalized.shape}")
