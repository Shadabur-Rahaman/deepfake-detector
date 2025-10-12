"""
Tensor Conversion Fixes - Core Foundation Level
==============================================

This module provides comprehensive fixes for tensor/numpy array conversion issues
that are causing the core errors in the deepfake detection system.

FIXES APPLIED:
1. Unified tensor conversion handling
2. Proper numpy array to tensor conversion
3. Device placement and shape validation
4. Error handling for edge cases
5. Memory optimization

Author: Senior ML Engineer
Date: 2024
"""

import torch
import numpy as np
import logging
from typing import List, Union, Tuple, Optional
import cv2

logger = logging.getLogger(__name__)

class TensorConversionFixer:
    """Comprehensive tensor conversion utility with error handling"""
    
    def __init__(self, device: str = "auto"):
        # Enhanced device selection with comprehensive CUDA safety
        self.device = self._get_safe_device(device)
        self.conversion_errors = 0
        self.successful_conversions = 0
        logger.info(f"TensorConversionFixer initialized on device: {self.device}")
    
    def _get_safe_device(self, requested_device: str) -> str:
        """Get a safe device with comprehensive CUDA driver error detection"""
        try:
            # First, test if CUDA is available without triggering driver errors
            if requested_device == "cuda":
                try:
                    # Wrap CUDA availability check to catch driver errors
                    cuda_available = torch.cuda.is_available()
                    if not cuda_available:
                        logger.info("🔧 CUDA not available, using CPU for tensor conversion")
                        return "cpu"
                except Exception as cuda_check_error:
                    error_str = str(cuda_check_error)
                    if "INTERNAL ASSERT FAILED" in error_str or "driver" in error_str.lower():
                        logger.warning(f"CUDA driver error detected during availability check: {cuda_check_error}")
                        logger.info("🔧 Forcing CPU mode due to CUDA driver error")
                        return "cpu"
                    raise
                
                # Test CUDA with safe operations - create on CPU first
                try:
                    test_tensor = torch.tensor([1.0])  # Create on CPU first
                    test_tensor = test_tensor.to("cuda")  # Move to CUDA safely
                    _ = test_tensor * 2
                    del test_tensor
                    torch.cuda.empty_cache()
                    logger.info("✅ CUDA device test passed for tensor conversion")
                    return "cuda"
                except Exception as cuda_test_error:
                    error_str = str(cuda_test_error)
                    if "INTERNAL ASSERT FAILED" in error_str:
                        logger.warning(f"CUDA driver error during tensor test: {cuda_test_error}")
                        logger.info("🔧 Forcing CPU mode due to CUDA driver error")
                        return "cpu"
                    else:
                        logger.error(f"❌ CUDA device test failed for tensor conversion: {cuda_test_error}")
                        logger.info("🔧 Falling back to CPU for tensor conversion")
                        return "cpu"
            else:
                logger.info("🔧 Using CPU device for tensor conversion")
                return "cpu"
        except Exception as e:
            logger.error(f"❌ Device detection failed: {e}")
            logger.info("🔧 Falling back to CPU for tensor conversion")
            return "cpu"
    
    def _safe_move_to_device(self, tensor: torch.Tensor) -> torch.Tensor:
        """Safely move tensor to device with comprehensive CUDA driver error handling"""
        try:
            if str(tensor.device) == self.device:
                return tensor  # Already on correct device
            
            # Try to move to device with driver error detection
            moved_tensor = tensor.to(self.device)
            return moved_tensor
            
        except Exception as device_error:
            error_str = str(device_error)
            if "INTERNAL ASSERT FAILED" in error_str:
                logger.warning(f"⚠️ CUDA driver error moving tensor to {self.device}: {device_error}")
                logger.info("🔧 Falling back to CPU due to driver error")
            else:
                logger.warning(f"⚠️ Failed to move tensor to {self.device}: {device_error}")
            
            # Fallback to CPU
            try:
                return tensor.cpu()
            except Exception as cpu_error:
                logger.error(f"❌ Failed to move tensor to CPU: {cpu_error}")
                return tensor  # Return as-is if all else fails
    
    def convert_to_tensor(self, data: Union[np.ndarray, torch.Tensor, List], 
                         target_shape: Tuple[int, ...] = None,
                         normalize: bool = True) -> torch.Tensor:
        """
        Convert various data types to properly formatted PyTorch tensors
        
        Args:
            data: Input data (numpy array, tensor, or list)
            target_shape: Expected tensor shape (C, H, W)
            normalize: Whether to normalize to [0, 1] range
            
        Returns:
            Properly formatted PyTorch tensor
        """
        try:
            # Handle None input
            if data is None:
                logger.warning("Received None input, returning fallback tensor")
                return self._create_fallback_tensor()
            
            # Handle list input
            if isinstance(data, list):
                if not data:
                    logger.warning("Received empty list, returning fallback tensor")
                    return self._create_fallback_tensor()
                # Convert list to numpy array first
                data = np.array(data)
            
            # Handle numpy array conversion
            if isinstance(data, np.ndarray):
                return self._convert_numpy_to_tensor(data, target_shape, normalize)
            
            # Handle existing tensor
            elif isinstance(data, torch.Tensor):
                return self._convert_tensor_to_tensor(data, target_shape, normalize)
            
            else:
                logger.warning(f"Unexpected data type: {type(data)}, converting to numpy first")
                try:
                    data = np.array(data)
                    return self._convert_numpy_to_tensor(data, target_shape, normalize)
                except Exception as e:
                    logger.error(f"Failed to convert {type(data)} to numpy: {e}")
                    return self._create_fallback_tensor()
                    
        except Exception as e:
            logger.error(f"Tensor conversion failed: {e}")
            self.conversion_errors += 1
            return self._create_fallback_tensor()
    
    def _convert_numpy_to_tensor(self, data: np.ndarray, target_shape: Tuple[int, ...] = None, 
                               normalize: bool = True) -> torch.Tensor:
        """Convert numpy array to properly formatted tensor"""
        try:
            # Ensure proper data type
            if data.dtype != np.float32:
                if data.dtype == np.uint8:
                    data = data.astype(np.float32) / 255.0
                else:
                    data = data.astype(np.float32)
            
            # Handle different input shapes
            if len(data.shape) == 3:
                # Assume (H, W, C) format, convert to (C, H, W)
                if data.shape[2] in [1, 3]:  # RGB or grayscale
                    data = np.transpose(data, (2, 0, 1))
                else:
                    logger.warning(f"Unexpected 3D shape: {data.shape}")
                    data = data.reshape(-1, data.shape[0], data.shape[1])
            elif len(data.shape) == 2:
                # Grayscale image, add channel dimension
                data = np.expand_dims(data, axis=0)
            elif len(data.shape) == 4:
                # Batch format, take first element
                data = data[0]
            else:
                logger.warning(f"Unexpected shape: {data.shape}")
                return self._create_fallback_tensor()
            
            # Resize if target shape is specified
            if target_shape and data.shape != target_shape:
                try:
                    data = cv2.resize(data.transpose(1, 2, 0), (target_shape[2], target_shape[1]))
                    data = np.transpose(data, (2, 0, 1))
                except Exception as e:
                    logger.warning(f"Failed to resize to target shape: {e}")
            
            # Normalize if requested with additional validation
            if normalize and data.max() > 1.0:
                data = np.clip(data, 0.0, 1.0)
            
            # Additional validation to prevent warnings
            if data.max() > 1.0 or data.min() < 0.0:
                data = np.clip(data, 0.0, 1.0)
            
            # Convert to tensor
            tensor = torch.from_numpy(data)
            
            # Add batch dimension if needed
            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)
            
            # Move to device with CUDA safety
            tensor = self._safe_move_to_device(tensor)
            
            self.successful_conversions += 1
            return tensor
            
        except Exception as e:
            logger.error(f"Numpy to tensor conversion failed: {e}")
            return self._create_fallback_tensor()
    
    def _convert_tensor_to_tensor(self, data: torch.Tensor, target_shape: Tuple[int, ...] = None,
                                normalize: bool = True) -> torch.Tensor:
        """Convert existing tensor to properly formatted tensor"""
        try:
            # Ensure tensor is on correct device with CUDA safety
            if str(data.device) != self.device:
                data = self._safe_move_to_device(data)
            
            # Handle different tensor shapes
            if data.dim() == 3:
                # Add batch dimension
                data = data.unsqueeze(0)
            elif data.dim() == 4:
                # Already has batch dimension
                pass
            elif data.dim() == 2:
                # Grayscale, add channel and batch dimensions
                data = data.unsqueeze(0).unsqueeze(0)
            else:
                logger.warning(f"Unexpected tensor dimensions: {data.dim()}")
                return self._create_fallback_tensor()
            
            # Normalize if requested with additional validation
            if normalize and data.max() > 1.0:
                data = torch.clamp(data, 0.0, 1.0)
            
            # Additional validation to prevent warnings
            if data.max() > 1.0 or data.min() < 0.0:
                data = torch.clamp(data, 0.0, 1.0)
            
            self.successful_conversions += 1
            return data
            
        except Exception as e:
            logger.error(f"Tensor to tensor conversion failed: {e}")
            return self._create_fallback_tensor()
    
    def _create_fallback_tensor(self) -> torch.Tensor:
        """Create a safe fallback tensor - CPU only to avoid CUDA driver errors"""
        try:
            # Create a neutral tensor on CPU only (never move to CUDA to avoid driver errors)
            fallback = torch.zeros(1, 3, 224, 224, dtype=torch.float32)
            logger.warning("Created fallback tensor on CPU due to conversion failure")
            
            # Never attempt to move fallback tensors to CUDA to prevent driver errors
            # Keep all fallback tensors on CPU for reliability
            return fallback
            
        except Exception as e:
            logger.error(f"Failed to create fallback tensor: {e}")
            # Last resort: create on CPU only (no device movement)
            return torch.zeros(1, 3, 224, 224, dtype=torch.float32)
    
    def batch_convert_faces(self, faces: List[Union[np.ndarray, torch.Tensor]], 
                          target_shape: Tuple[int, ...] = (3, 224, 224)) -> List[torch.Tensor]:
        """
        Convert a batch of faces to properly formatted tensors
        
        Args:
            faces: List of face data (numpy arrays or tensors)
            target_shape: Expected tensor shape (C, H, W)
            
        Returns:
            List of properly formatted tensors
        """
        converted_faces = []
        
        for i, face in enumerate(faces):
            try:
                # FIXED: Ensure proper conversion with device placement
                converted_face = self.convert_to_tensor(face, target_shape)
                
                # Ensure tensor is on correct device with CUDA safety
                converted_face = self._safe_move_to_device(converted_face)
                
                # Ensure tensor is properly formatted (C, H, W)
                if converted_face.dim() == 4 and converted_face.shape[0] == 1:
                    converted_face = converted_face.squeeze(0)
                elif converted_face.dim() == 2:
                    converted_face = converted_face.unsqueeze(0)
                
                # Final validation
                if converted_face.dim() != 3:
                    logger.warning(f"Face {i} has unexpected dimensions: {converted_face.dim()}")
                    converted_face = self._create_fallback_tensor()
                
                converted_faces.append(converted_face)
                self.successful_conversions += 1
                
            except Exception as e:
                logger.error(f"Failed to convert face {i}: {e}")
                self.conversion_errors += 1
                # Add fallback tensor for this face
                converted_faces.append(self._create_fallback_tensor())
        
        return converted_faces
    
    def stack_faces_batch(self, faces: List[torch.Tensor]) -> torch.Tensor:
        """
        Stack a list of face tensors into a single batch tensor
        
        Args:
            faces: List of face tensors
            
        Returns:
            Stacked batch tensor
        """
        try:
            if not faces:
                logger.warning("No faces to stack, returning empty batch")
                return torch.empty(0, 3, 224, 224, device=self.device)
            
            # FIXED: Ensure all faces are properly shaped (C, H, W) before stacking
            normalized_faces = []
            
            for face in faces:
                # Ensure face is 3D (C, H, W)
                if face.dim() == 4:
                    # Remove batch dimension if present
                    if face.shape[0] == 1:
                        face = face.squeeze(0)
                    else:
                        logger.warning(f"Unexpected 4D tensor shape: {face.shape}")
                        continue
                elif face.dim() == 2:
                    # Add channel dimension
                    face = face.unsqueeze(0)
                elif face.dim() != 3:
                    logger.warning(f"Unexpected tensor dimension: {face.dim()}, shape: {face.shape}")
                    continue
                
                # Ensure correct shape (C, H, W)
                if face.shape[0] not in [1, 3]:
                    logger.warning(f"Unexpected channel count: {face.shape[0]}")
                    continue
                
                # Resize to standard size if needed
                if face.shape[1:] != (224, 224):
                    face = torch.nn.functional.interpolate(
                        face.unsqueeze(0),
                        size=(224, 224),
                        mode='bilinear',
                        align_corners=False
                    ).squeeze(0)
                
                normalized_faces.append(face)
            
            if not normalized_faces:
                logger.warning("No valid faces after normalization")
                return self._create_fallback_tensor()
            
            # Stack into batch - should be (N, C, H, W)
            batch = torch.stack(normalized_faces, dim=0)
            logger.info(f"Stacked batch shape: {batch.shape}")
            return batch
            
        except Exception as e:
            logger.error(f"Failed to stack faces: {e}")
            # Return single fallback tensor
            return self._create_fallback_tensor()
    
    def get_conversion_stats(self) -> dict:
        """Get conversion statistics"""
        total = self.conversion_errors + self.successful_conversions
        success_rate = (self.successful_conversions / total * 100) if total > 0 else 0
        
        return {
            "successful_conversions": self.successful_conversions,
            "conversion_errors": self.conversion_errors,
            "success_rate": success_rate,
            "total_attempts": total
        }
    
    def reset_stats(self):
        """Reset conversion statistics"""
        self.conversion_errors = 0
        self.successful_conversions = 0

# Global instance for easy access - auto device selection with CUDA safety
tensor_converter = TensorConversionFixer(device="auto")

# Convenience functions
def safe_convert_to_tensor(data: Union[np.ndarray, torch.Tensor, List], 
                          target_shape: Tuple[int, ...] = None,
                          normalize: bool = True) -> torch.Tensor:
    """Safe tensor conversion with error handling"""
    return tensor_converter.convert_to_tensor(data, target_shape, normalize)

def safe_batch_convert_faces(faces: List[Union[np.ndarray, torch.Tensor]], 
                           target_shape: Tuple[int, ...] = (3, 224, 224)) -> List[torch.Tensor]:
    """Safe batch face conversion"""
    return tensor_converter.batch_convert_faces(faces, target_shape)

def safe_stack_faces_batch(faces: List[torch.Tensor]) -> torch.Tensor:
    """Safe face batch stacking"""
    return tensor_converter.stack_faces_batch(faces)

def get_tensor_conversion_stats() -> dict:
    """Get tensor conversion statistics"""
    return tensor_converter.get_conversion_stats()

def reset_tensor_conversion_stats():
    """Reset tensor conversion statistics"""
    tensor_converter.reset_stats()
