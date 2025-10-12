"""
Mode Factory for Deepfake Detection System

This module provides a factory pattern implementation for creating and managing
detection mode instances with proper error handling and resource management.

Design Principles:
- Factory Pattern: Clean instantiation of detection modes
- Error Handling: Graceful fallbacks and comprehensive logging
- Resource Management: Proper cleanup and memory management
- Type Safety: Full type hints and validation
- Extensibility: Easy addition of new detection modes

Author: Senior ML Engineer
Date: 2024
"""

import logging
from typing import Dict, Optional, Any, Type, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .mode_registry import DetectionMode, ModeConfig, get_mode_registry
from .model_loader import ModelLoader, get_model_loader, ModelLoadResult

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Result of a detection operation"""
    prediction: str
    confidence: float
    processing_time_ms: float
    model_used: str
    mode_used: str
    faces_detected: int = 0
    error_message: Optional[str] = None

class BaseDetectionMode(ABC):
    """Abstract base class for all detection modes"""
    
    def __init__(self, mode_config: ModeConfig, model: Any):
        self.mode_config = mode_config
        self.model = model
        self.model_loader = get_model_loader()
    
    @abstractmethod
    async def detect(self, input_data: Any, **kwargs) -> DetectionResult:
        """Perform detection on input data"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        pass

class TraditionalDetectionMode(BaseDetectionMode):
    """Traditional deepfake detection mode using EfficientNet-B0"""
    
    def __init__(self, mode_config: ModeConfig, model: Any):
        super().__init__(mode_config, model)
        self.model_name = "EfficientNet-B0 Fine-tuned"
    
    async def detect(self, input_data: Any, **kwargs) -> DetectionResult:
        """Perform traditional deepfake detection"""
        try:
            import time
            start_time = time.time()
            
            # Import detection utilities
            from .deepfake_detector import DeepfakeDetector
            
            # Create detector instance if needed
            if not hasattr(self, '_detector'):
                self._detector = DeepfakeDetector()
                if hasattr(self._detector, 'efficientnet_model') and self._detector.efficientnet_model is None:
                    self._detector.efficientnet_model = self.model
            
            # Perform detection
            if hasattr(input_data, 'read'):  # File-like object
                result = await self._detector.detect_video_file(input_data)
            elif isinstance(input_data, str):  # File path
                result = await self._detector.detect_video_path(input_data)
            else:
                result = await self._detector.detect_video_data(input_data)
            
            processing_time = (time.time() - start_time) * 1000
            
            return DetectionResult(
                prediction=result.get('prediction', 'Unknown'),
                confidence=result.get('confidence', 0.0),
                processing_time_ms=processing_time,
                model_used=self.model_name,
                mode_used=self.mode_config.mode_id.value,
                faces_detected=result.get('faces_detected', 0)
            )
            
        except Exception as e:
            logger.error(f"Traditional detection failed: {e}")
            return DetectionResult(
                prediction="Error",
                confidence=0.0,
                processing_time_ms=0.0,
                model_used=self.model_name,
                mode_used=self.mode_config.mode_id.value,
                error_message=str(e)
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the traditional model"""
        return {
            "model_name": self.model_name,
            "model_type": "EfficientNet-B0",
            "accuracy": self.mode_config.primary_model.accuracy,
            "description": self.mode_config.primary_model.description,
            "supported_formats": self.mode_config.primary_model.supported_formats
        }

class ModernAIDetectionMode(BaseDetectionMode):
    """Modern AI deepfake detection mode using advanced models"""
    
    def __init__(self, mode_config: ModeConfig, model: Any):
        super().__init__(mode_config, model)
        self.model_name = "Advanced AI Model"
    
    async def detect(self, input_data: Any, **kwargs) -> DetectionResult:
        """Perform modern AI deepfake detection"""
        try:
            import time
            start_time = time.time()
            
            # Import advanced detection utilities
            from .enhanced_detection_engine import EnhancedDetectionEngine
            from .unified_detection_pipeline import UnifiedDetectionPipeline
            
            # Create enhanced detector
            if not hasattr(self, '_detector'):
                self._detector = EnhancedDetectionEngine()
                # Set the loaded model
                if hasattr(self._detector, 'set_primary_model'):
                    self._detector.set_primary_model(self.model)
            
            # Perform enhanced detection
            if hasattr(input_data, 'read'):  # File-like object
                result = await self._detector.detect_video_file(input_data)
            elif isinstance(input_data, str):  # File path
                result = await self._detector.detect_video_path(input_data)
            else:
                result = await self._detector.detect_video_data(input_data)
            
            processing_time = (time.time() - start_time) * 1000
            
            return DetectionResult(
                prediction=result.get('prediction', 'Unknown'),
                confidence=result.get('confidence', 0.0),
                processing_time_ms=processing_time,
                model_used=self.model_name,
                mode_used=self.mode_config.mode_id.value,
                faces_detected=result.get('faces_detected', 0)
            )
            
        except Exception as e:
            logger.error(f"Modern AI detection failed: {e}")
            # Fallback to traditional detection
            logger.info("Falling back to traditional detection")
            traditional_mode = TraditionalDetectionMode(self.mode_config, self.model)
            return await traditional_mode.detect(input_data, **kwargs)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the modern AI model"""
        return {
            "model_name": self.model_name,
            "model_type": "Advanced AI",
            "accuracy": self.mode_config.primary_model.accuracy,
            "description": self.mode_config.primary_model.description,
            "supported_formats": self.mode_config.primary_model.supported_formats,
            "enhanced_features": [
                "Advanced neural networks",
                "Multi-frame analysis",
                "Temporal consistency checking",
                "Metadata analysis"
            ]
        }

class ModeFactory:
    """
    Factory class for creating and managing detection mode instances.
    
    This class implements the Factory pattern to provide a clean interface
    for creating detection modes with proper error handling and resource management.
    """
    
    def __init__(self):
        self._mode_registry = get_mode_registry()
        self._model_loader = get_model_loader()
        self._active_modes: Dict[DetectionMode, BaseDetectionMode] = {}
        self._mode_classes: Dict[DetectionMode, Type[BaseDetectionMode]] = {
            DetectionMode.TRADITIONAL: TraditionalDetectionMode,
            DetectionMode.MODERN_AI: ModernAIDetectionMode
        }
    
    def create_mode(self, mode: DetectionMode) -> Optional[BaseDetectionMode]:
        """
        Create a detection mode instance
        
        Args:
            mode: The detection mode to create
            
        Returns:
            Detection mode instance or None if creation fails
        """
        try:
            logger.info(f"Creating detection mode: {mode.value}")
            
            # Check if mode is already active
            if mode in self._active_modes:
                logger.info(f"Mode {mode.value} already active, returning existing instance")
                return self._active_modes[mode]
            
            # Get mode configuration
            mode_config = self._mode_registry.get_mode(mode)
            if not mode_config:
                logger.error(f"Mode configuration not found for {mode.value}")
                return None
            
            # Load model for the mode
            model_result = self._model_loader.load_model_for_mode(mode)
            if not model_result.success:
                logger.error(f"Failed to load model for mode {mode.value}: {model_result.error_message}")
                return None
            
            # Get mode class
            mode_class = self._mode_classes.get(mode)
            if not mode_class:
                logger.error(f"No mode class found for {mode.value}")
                return None
            
            # Create mode instance
            mode_instance = mode_class(mode_config, model_result.model)
            self._active_modes[mode] = mode_instance
            
            logger.info(f"[OK] Successfully created mode: {mode.value}")
            return mode_instance
            
        except Exception as e:
            logger.error(f"Failed to create mode {mode.value}: {e}")
            return None
    
    def get_mode(self, mode: DetectionMode) -> Optional[BaseDetectionMode]:
        """Get an existing mode instance or create a new one"""
        if mode in self._active_modes:
            return self._active_modes[mode]
        return self.create_mode(mode)
    
    def get_mode_by_alias(self, alias: str) -> Optional[BaseDetectionMode]:
        """Get mode by string alias"""
        mode_enum = self._mode_registry.get_mode_by_alias(alias)
        if mode_enum:
            return self.get_mode(mode_enum)
        return None
    
    async def detect_with_mode(self, mode: DetectionMode, input_data: Any, **kwargs) -> DetectionResult:
        """
        Perform detection using a specific mode
        
        Args:
            mode: The detection mode to use
            input_data: The input data to analyze
            **kwargs: Additional parameters
            
        Returns:
            Detection result
        """
        try:
            # Get or create mode instance
            mode_instance = self.get_mode(mode)
            if not mode_instance:
                return DetectionResult(
                    prediction="Error",
                    confidence=0.0,
                    processing_time_ms=0.0,
                    model_used="Unknown",
                    mode_used=mode.value,
                    error_message=f"Failed to create mode {mode.value}"
                )
            
            # Perform detection
            return await mode_instance.detect(input_data, **kwargs)
            
        except Exception as e:
            logger.error(f"Detection failed for mode {mode.value}: {e}")
            return DetectionResult(
                prediction="Error",
                confidence=0.0,
                processing_time_ms=0.0,
                model_used="Unknown",
                mode_used=mode.value,
                error_message=str(e)
            )
    
    def cleanup_mode(self, mode: DetectionMode) -> bool:
        """Cleanup a specific mode instance"""
        try:
            if mode in self._active_modes:
                mode_instance = self._active_modes[mode]
                mode_instance.cleanup()
                del self._active_modes[mode]
                logger.info(f"Cleaned up mode: {mode.value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup mode {mode.value}: {e}")
            return False
    
    def cleanup_all_modes(self):
        """Cleanup all active mode instances"""
        try:
            for mode in list(self._active_modes.keys()):
                self.cleanup_mode(mode)
            logger.info("Cleaned up all active modes")
        except Exception as e:
            logger.error(f"Failed to cleanup all modes: {e}")
    
    def get_active_modes(self) -> Dict[str, Any]:
        """Get information about all active modes"""
        return {
            mode.value: {
                "active": True,
                "model_info": mode_instance.get_model_info()
            }
            for mode, mode_instance in self._active_modes.items()
        }
    
    def is_mode_active(self, mode: DetectionMode) -> bool:
        """Check if a mode is currently active"""
        return mode in self._active_modes
    
    def get_mode_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all modes"""
        status = {
            "active_modes": list(self._active_modes.keys()),
            "available_modes": [],
            "mode_details": {}
        }
        
        # Get available modes from registry
        available_modes = self._mode_registry.get_enabled_modes()
        for mode, config in available_modes.items():
            status["available_modes"].append(mode.value)
            status["mode_details"][mode.value] = {
                "display_name": config.display_name,
                "description": config.description,
                "enabled": config.enabled,
                "active": mode in self._active_modes,
                "model_info": self._active_modes[mode].get_model_info() if mode in self._active_modes else None
            }
        
        return status

# Global mode factory instance
_mode_factory: Optional[ModeFactory] = None

def get_mode_factory() -> ModeFactory:
    """Get the global mode factory instance (singleton pattern)"""
    global _mode_factory
    if _mode_factory is None:
        _mode_factory = ModeFactory()
    return _mode_factory

def reset_mode_factory():
    """Reset the global mode factory (useful for testing)"""
    global _mode_factory
    if _mode_factory is not None:
        _mode_factory.cleanup_all_modes()
    _mode_factory = None
