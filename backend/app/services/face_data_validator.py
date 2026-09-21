"""
Face Data Validator - Centralized face data type validation and conversion
Fixes the core pipeline issues with dict vs numpy array type mismatches
"""

import numpy as np
import cv2
import torch
import logging
from typing import List, Union, Optional, Dict, Any
from PIL import Image
import io

logger = logging.getLogger(__name__)

class FaceDataValidator:
    """
    Centralized validator for face data to ensure consistent numpy array format
    throughout the detection pipeline. Fixes the core type mismatch errors.
    """
    
    @staticmethod
    def validate_and_convert(face: Any, source: str = "unknown") -> Optional[np.ndarray]:
        """
        Convert any face data format to standardized numpy array (H, W, 3), dtype=uint8
        
        Args:
            face: Face data in any format (dict, tensor, numpy array, PIL Image, bytes)
            source: Source identifier for logging
            
        Returns:
            Standardized numpy array (H, W, 3) with dtype=uint8, or None if invalid
        """
        try:
            if face is None:
                logger.warning(f"[FaceValidator] {source}: Face is None")
                return None
                
            # Handle numpy arrays
            if isinstance(face, np.ndarray):
                return FaceDataValidator._convert_numpy_array(face, source)
            
            # Handle PyTorch tensors
            elif isinstance(face, torch.Tensor):
                return FaceDataValidator._convert_torch_tensor(face, source)
            
            # Handle PIL Images
            elif hasattr(face, 'mode') and hasattr(face, 'size'):  # PIL Image
                return FaceDataValidator._convert_pil_image(face, source)
            
            # Handle dictionaries (common source of errors)
            elif isinstance(face, dict):
                return FaceDataValidator._convert_dict(face, source)
            
            # Handle bytes/encoded images
            elif isinstance(face, (bytes, bytearray)):
                return FaceDataValidator._convert_bytes(face, source)
            
            # Handle lists (sometimes faces are passed as lists)
            elif isinstance(face, (list, tuple)):
                return FaceDataValidator._convert_list(face, source)
            
            else:
                logger.error(f"[FaceValidator] {source}: Unsupported face type: {type(face)}")
                return None
                
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: Conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def _convert_numpy_array(face: np.ndarray, source: str) -> Optional[np.ndarray]:
        """Convert numpy array to standard format"""
        try:
            # Ensure it's 3D (H, W, C)
            if face.ndim == 2:
                face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
            elif face.ndim == 3 and face.shape[2] == 1:
                face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
            elif face.ndim == 3 and face.shape[2] == 4:
                face = cv2.cvtColor(face, cv2.COLOR_RGBA2RGB)
            
            # Ensure correct shape (H, W, 3)
            if face.ndim != 3 or face.shape[2] != 3:
                logger.warning(f"[FaceValidator] {source}: Invalid numpy array shape: {face.shape}")
                return None
            
            # Convert to uint8 if needed
            if face.dtype != np.uint8:
                if face.dtype in [np.float32, np.float64]:
                    face = (face * 255).astype(np.uint8)
                else:
                    face = face.astype(np.uint8)
            
            # Ensure valid range
            face = np.clip(face, 0, 255)
            
            logger.debug(f"[FaceValidator] {source}: Converted numpy array {face.shape} {face.dtype}")
            return face
            
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: Numpy conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def _convert_torch_tensor(face: torch.Tensor, source: str) -> Optional[np.ndarray]:
        """Convert PyTorch tensor to numpy array"""
        try:
            # Move to CPU and detach
            if face.is_cuda:
                face = face.cpu()
            face = face.detach()
            
            # Convert to numpy
            face_np = face.numpy()
            
            # Handle different tensor formats
            if face_np.ndim == 4:  # (B, C, H, W) -> (H, W, C)
                face_np = face_np.squeeze(0).transpose(1, 2, 0)
            elif face_np.ndim == 3 and face_np.shape[0] in [1, 3, 4]:  # (C, H, W) -> (H, W, C)
                face_np = face_np.transpose(1, 2, 0)
            
            return FaceDataValidator._convert_numpy_array(face_np, f"{source}_tensor")
            
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: Tensor conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def _convert_pil_image(face: Image.Image, source: str) -> Optional[np.ndarray]:
        """Convert PIL Image to numpy array"""
        try:
            # Convert to RGB if needed
            if face.mode != 'RGB':
                face = face.convert('RGB')
            
            # Convert to numpy array
            face_np = np.array(face)
            
            return FaceDataValidator._convert_numpy_array(face_np, f"{source}_pil")
            
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: PIL conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def _convert_dict(face: Dict[str, Any], source: str) -> Optional[np.ndarray]:
        """Convert dictionary to numpy array - fixes the main error source"""
        try:
            # Common dictionary keys that might contain face data
            possible_keys = ['face', 'image', 'data', 'array', 'tensor', 'face_data', 'face_array']
            
            face_data = None
            for key in possible_keys:
                if key in face:
                    face_data = face[key]
                    break
            
            # If no standard key found, try to find any array-like data
            if face_data is None:
                for key, value in face.items():
                    if isinstance(value, (np.ndarray, torch.Tensor)) or hasattr(value, 'shape'):
                        face_data = value
                        break
            
            if face_data is None:
                logger.warning(f"[FaceValidator] {source}: No face data found in dict keys: {list(face.keys())}")
                return None
            
            # Recursively convert the found data
            return FaceDataValidator.validate_and_convert(face_data, f"{source}_dict")
            
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: Dict conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def _convert_bytes(face: Union[bytes, bytearray], source: str) -> Optional[np.ndarray]:
        """Convert bytes to numpy array"""
        try:
            # Try to decode as image
            nparr = np.frombuffer(face, np.uint8)
            face_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if face_np is None:
                logger.warning(f"[FaceValidator] {source}: Failed to decode bytes as image")
                return None
            
            # Convert BGR to RGB
            face_np = cv2.cvtColor(face_np, cv2.COLOR_BGR2RGB)
            
            return FaceDataValidator._convert_numpy_array(face_np, f"{source}_bytes")
            
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: Bytes conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def _convert_list(face: Union[List, tuple], source: str) -> Optional[np.ndarray]:
        """Convert list/tuple to numpy array"""
        try:
            # Convert to numpy array
            face_np = np.array(face)
            
            return FaceDataValidator._convert_numpy_array(face_np, f"{source}_list")
            
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: List conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def validate_face_list(faces: List[Any], source: str = "unknown") -> List[np.ndarray]:
        """
        Validate and convert a list of faces
        
        Args:
            faces: List of face data in any format
            source: Source identifier for logging
            
        Returns:
            List of valid numpy arrays (H, W, 3), dtype=uint8
        """
        if not isinstance(faces, (list, tuple)):
            logger.warning(f"[FaceValidator] {source}: Expected list, got {type(faces)}")
            return []
        
        valid_faces = []
        for i, face in enumerate(faces):
            converted_face = FaceDataValidator.validate_and_convert(face, f"{source}_face_{i}")
            if converted_face is not None:
                valid_faces.append(converted_face)
            else:
                logger.warning(f"[FaceValidator] {source}: Skipped invalid face {i}")
        
        logger.info(f"[FaceValidator] {source}: Converted {len(valid_faces)}/{len(faces)} faces")
        return valid_faces
    
    @staticmethod
    def validate_face_for_opencv(face: Any, source: str = "unknown") -> Optional[np.ndarray]:
        """
        Special validation for OpenCV operations - ensures BGR format
        
        Args:
            face: Face data in any format
            source: Source identifier for logging
            
        Returns:
            BGR numpy array (H, W, 3), dtype=uint8, or None if invalid
        """
        face_rgb = FaceDataValidator.validate_and_convert(face, source)
        if face_rgb is None:
            return None
        
        try:
            # Convert RGB to BGR for OpenCV
            face_bgr = cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR)
            logger.debug(f"[FaceValidator] {source}: Converted to BGR for OpenCV {face_bgr.shape}")
            return face_bgr
        except Exception as e:
            logger.error(f"[FaceValidator] {source}: RGB to BGR conversion failed: {str(e)}")
            return None
    
    @staticmethod
    def get_face_info(face: Any, source: str = "unknown") -> Dict[str, Any]:
        """
        Get information about face data for debugging
        
        Args:
            face: Face data in any format
            source: Source identifier for logging
            
        Returns:
            Dictionary with face information
        """
        info = {
            "source": source,
            "type": str(type(face)),
            "valid": False,
            "shape": None,
            "dtype": None,
            "min_val": None,
            "max_val": None
        }
        
        try:
            converted_face = FaceDataValidator.validate_and_convert(face, source)
            if converted_face is not None:
                info.update({
                    "valid": True,
                    "shape": converted_face.shape,
                    "dtype": str(converted_face.dtype),
                    "min_val": float(converted_face.min()),
                    "max_val": float(converted_face.max())
                })
        except Exception as e:
            info["error"] = str(e)
        
        return info

# Convenience functions for easy integration
def validate_face(face: Any, source: str = "unknown") -> Optional[np.ndarray]:
    """Convenience function for single face validation"""
    return FaceDataValidator.validate_and_convert(face, source)

def validate_faces(faces: List[Any], source: str = "unknown") -> List[np.ndarray]:
    """Convenience function for face list validation"""
    return FaceDataValidator.validate_face_list(faces, source)

def validate_face_for_opencv(face: Any, source: str = "unknown") -> Optional[np.ndarray]:
    """Convenience function for OpenCV face validation"""
    return FaceDataValidator.validate_face_for_opencv(face, source)




