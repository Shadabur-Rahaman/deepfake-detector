"""
Enhanced Mode-Based Detection Service

This module provides a production-grade detection service that integrates
with the mode system to provide dynamic switching between different inference modes.

Design Principles:
- Service Layer: Clean separation of concerns
- Mode Integration: Seamless integration with mode registry and factory
- Error Handling: Comprehensive error handling and fallbacks
- Performance: Optimized for production use
- Logging: Detailed logging for monitoring and debugging

Author: Senior ML Engineer
Date: 2024
"""

import logging
import asyncio
from typing import Dict, Optional, Any, Union, List
from pathlib import Path
import uuid
import time

from .mode_registry import DetectionMode, get_mode_registry
from .mode_factory import ModeFactory, get_mode_factory, DetectionResult
from .model_loader import get_model_loader

logger = logging.getLogger(__name__)

class EnhancedModeDetector:
    """
    Enhanced detection service with mode-based inference switching.
    
    This service provides a high-level interface for deepfake detection
    with support for multiple inference modes and comprehensive error handling.
    """
    
    def __init__(self):
        self.mode_registry = get_mode_registry()
        self.mode_factory = get_mode_factory()
        self.model_loader = get_model_loader()
        self._detection_cache: Dict[str, DetectionResult] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
    async def detect_video(
        self, 
        video_data: Union[str, bytes, Any], 
        mode: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Detect deepfake in video using specified mode or auto-selection
        
        Args:
            video_data: Video file path, bytes, or file-like object
            mode: Detection mode ('traditional' or 'modern_ai'). If None, uses auto-selection
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing detection results
        """
        try:
            detection_id = str(uuid.uuid4())
            start_time = time.time()
            
            logger.info(f"Starting video detection (ID: {detection_id})")
            
            # Determine detection mode
            selected_mode = await self._select_detection_mode(mode, video_data)
            if not selected_mode:
                return self._create_error_response("Failed to select detection mode")
            
            logger.info(f"Using detection mode: {selected_mode.value}")
            
            # Check cache first
            cache_key = self._generate_cache_key(video_data, selected_mode)
            if cache_key in self._detection_cache:
                cached_result = self._detection_cache[cache_key]
                if time.time() - cached_result.processing_time_ms < self._cache_ttl:
                    logger.info("Returning cached result")
                    return self._format_detection_response(cached_result, detection_id)
            
            # Perform detection
            result = await self.mode_factory.detect_with_mode(selected_mode, video_data, **kwargs)
            
            # Cache result
            self._detection_cache[cache_key] = result
            
            # Calculate total processing time
            total_time = (time.time() - start_time) * 1000
            
            logger.info(f"Detection completed in {total_time:.2f}ms (ID: {detection_id})")
            
            return self._format_detection_response(result, detection_id, total_time)
            
        except Exception as e:
            logger.error(f"Video detection failed: {e}")
            return self._create_error_response(f"Detection failed: {str(e)}")
    
    async def detect_video_file(
        self, 
        file_path: str, 
        mode: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Detect deepfake in video file"""
        try:
            if not Path(file_path).exists():
                return self._create_error_response(f"Video file not found: {file_path}")
            
            return await self.detect_video(file_path, mode, **kwargs)
            
        except Exception as e:
            logger.error(f"File detection failed: {e}")
            return self._create_error_response(f"File detection failed: {str(e)}")
    
    async def detect_video_bytes(
        self, 
        video_bytes: bytes, 
        mode: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Detect deepfake in video bytes"""
        try:
            return await self.detect_video(video_bytes, mode, **kwargs)
            
        except Exception as e:
            logger.error(f"Bytes detection failed: {e}")
            return self._create_error_response(f"Bytes detection failed: {str(e)}")
    
    async def _select_detection_mode(self, requested_mode: Optional[str], video_data: Any) -> Optional[DetectionMode]:
        """Select the appropriate detection mode"""
        try:
            # If mode is explicitly requested, validate and use it
            if requested_mode:
                is_valid, mode_enum, error_msg = self.mode_registry.validate_mode_request(requested_mode)
                if is_valid and mode_enum:
                    logger.info(f"Using requested mode: {mode_enum.value}")
                    return mode_enum
                else:
                    logger.warning(f"Invalid mode request '{requested_mode}': {error_msg}")
                    # Fall back to auto-selection
            
            # Auto-selection logic
            return await self._auto_select_mode(video_data)
            
        except Exception as e:
            logger.error(f"Mode selection failed: {e}")
            # Emergency fallback to traditional mode
            if self.mode_registry.is_mode_available(DetectionMode.TRADITIONAL):
                logger.warning("Using emergency fallback to traditional mode")
                return DetectionMode.TRADITIONAL
            return None
    
    async def _auto_select_mode(self, video_data: Any) -> Optional[DetectionMode]:
        """Automatically select the best detection mode based on video characteristics"""
        try:
            # Get available modes
            available_modes = self.mode_registry.get_enabled_modes()
            if not available_modes:
                logger.error("No detection modes available")
                return None
            
            # Simple auto-selection logic (can be enhanced based on video characteristics)
            # For now, prefer modern AI mode if available, otherwise traditional
            if DetectionMode.MODERN_AI in available_modes:
                logger.info("Auto-selected modern AI mode")
                return DetectionMode.MODERN_AI
            elif DetectionMode.TRADITIONAL in available_modes:
                logger.info("Auto-selected traditional mode")
                return DetectionMode.TRADITIONAL
            else:
                # Use the first available mode
                first_mode = next(iter(available_modes.keys()))
                logger.info(f"Auto-selected first available mode: {first_mode.value}")
                return first_mode
                
        except Exception as e:
            logger.error(f"Auto-selection failed: {e}")
            return None
    
    def _generate_cache_key(self, video_data: Any, mode: DetectionMode) -> str:
        """Generate cache key for video data and mode"""
        try:
            if isinstance(video_data, str):
                # File path
                return f"{Path(video_data).name}_{mode.value}"
            elif isinstance(video_data, bytes):
                # Video bytes - use hash
                import hashlib
                data_hash = hashlib.md5(video_data[:1024]).hexdigest()  # Use first 1KB for hash
                return f"{data_hash}_{mode.value}"
            else:
                # File-like object - use object id
                return f"{id(video_data)}_{mode.value}"
        except Exception as e:
            logger.warning(f"Cache key generation failed: {e}")
            return f"unknown_{mode.value}_{int(time.time())}"
    
    def _format_detection_response(self, result: DetectionResult, detection_id: str, total_time: Optional[float] = None) -> Dict[str, Any]:
        """Format detection result into API response"""
        try:
            response = {
                "detection_id": detection_id,
                "status": "completed" if not result.error_message else "failed",
                "prediction": result.prediction,
                "confidence": result.confidence,
                "processing_time": result.processing_time_ms / 1000.0,  # Convert to seconds
                "model_used": result.model_used,
                "mode_used": result.mode_used,
                "faces_detected": result.faces_detected,
                "timestamp": time.time()
            }
            
            if total_time:
                response["total_processing_time"] = total_time / 1000.0
            
            if result.error_message:
                response["error"] = result.error_message
                response["status"] = "failed"
            
            return response
            
        except Exception as e:
            logger.error(f"Response formatting failed: {e}")
            return self._create_error_response(f"Response formatting failed: {str(e)}")
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "detection_id": str(uuid.uuid4()),
            "status": "failed",
            "prediction": "Error",
            "confidence": 0.0,
            "processing_time": 0.0,
            "model_used": "Unknown",
            "mode_used": "Unknown",
            "faces_detected": 0,
            "error": error_message,
            "timestamp": time.time()
        }
    
    async def get_available_modes(self) -> Dict[str, Any]:
        """Get information about available detection modes"""
        try:
            modes_info = {}
            available_modes = self.mode_registry.get_enabled_modes()
            
            for mode, config in available_modes.items():
                modes_info[mode.value] = self.mode_registry.get_mode_info(mode)
            
            return {
                "available_modes": list(modes_info.keys()),
                "mode_details": modes_info,
                "active_modes": self.mode_factory.get_active_modes()
            }
            
        except Exception as e:
            logger.error(f"Failed to get available modes: {e}")
            return {"error": f"Failed to get available modes: {str(e)}"}
    
    async def get_mode_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all modes"""
        try:
            return self.mode_factory.get_mode_status()
        except Exception as e:
            logger.error(f"Failed to get mode status: {e}")
            return {"error": f"Failed to get mode status: {str(e)}"}
    
    async def preload_mode(self, mode: str) -> Dict[str, Any]:
        """Preload a specific mode for faster subsequent detection"""
        try:
            is_valid, mode_enum, error_msg = self.mode_registry.validate_mode_request(mode)
            if not is_valid or not mode_enum:
                return {"success": False, "error": error_msg}
            
            # Create mode instance
            mode_instance = self.mode_factory.create_mode(mode_enum)
            if mode_instance:
                return {
                    "success": True,
                    "mode": mode_enum.value,
                    "message": f"Mode {mode_enum.value} preloaded successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to preload mode {mode_enum.value}"
                }
                
        except Exception as e:
            logger.error(f"Mode preloading failed: {e}")
            return {"success": False, "error": f"Mode preloading failed: {str(e)}"}
    
    async def cleanup_mode(self, mode: str) -> Dict[str, Any]:
        """Cleanup a specific mode to free resources"""
        try:
            is_valid, mode_enum, error_msg = self.mode_registry.validate_mode_request(mode)
            if not is_valid or not mode_enum:
                return {"success": False, "error": error_msg}
            
            success = self.mode_factory.cleanup_mode(mode_enum)
            if success:
                return {
                    "success": True,
                    "mode": mode_enum.value,
                    "message": f"Mode {mode_enum.value} cleaned up successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to cleanup mode {mode_enum.value}"
                }
                
        except Exception as e:
            logger.error(f"Mode cleanup failed: {e}")
            return {"success": False, "error": f"Mode cleanup failed: {str(e)}"}
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear detection cache"""
        try:
            cache_size = len(self._detection_cache)
            self._detection_cache.clear()
            return {
                "success": True,
                "message": f"Cleared {cache_size} cached results"
            }
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return {"success": False, "error": f"Cache clearing failed: {str(e)}"}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            return {
                "cache_size": len(self._detection_cache),
                "cache_ttl": self._cache_ttl,
                "cache_keys": list(self._detection_cache.keys())
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": f"Failed to get cache stats: {str(e)}"}

# Global enhanced detector instance
_enhanced_detector: Optional[EnhancedModeDetector] = None

def get_enhanced_detector() -> EnhancedModeDetector:
    """Get the global enhanced detector instance (singleton pattern)"""
    global _enhanced_detector
    if _enhanced_detector is None:
        _enhanced_detector = EnhancedModeDetector()
    return _enhanced_detector

def reset_enhanced_detector():
    """Reset the global enhanced detector (useful for testing)"""
    global _enhanced_detector
    _enhanced_detector = None
