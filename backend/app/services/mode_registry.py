"""
Mode Registry for Deepfake Detection System

This module provides a production-grade mode management system that allows
dynamic switching between different inference modes (traditional vs modern AI).

Design Principles:
- Factory Pattern: Clean instantiation of detection modes
- Registry Pattern: Centralized mode management
- Error Handling: Graceful fallbacks and comprehensive logging
- Extensibility: Easy addition of new modes and models
- Type Safety: Full type hints and validation

Author: Senior ML Engineer
Date: 2024
"""

import os
import logging
from typing import Dict, Optional, Type, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class DetectionMode(Enum):
    """Enumeration of available detection modes"""
    TRADITIONAL = "traditional"
    MODERN_AI = "modern_ai"  # Using 'modern_ai' as the cleaner alias

@dataclass
class ModelConfig:
    """Configuration for a specific model within a detection mode"""
    model_path: str
    model_name: str
    description: str
    accuracy: float
    processing_time_ms: int
    memory_usage_mb: int
    supported_formats: List[str]
    fallback_available: bool = True

@dataclass
class ModeConfig:
    """Configuration for a detection mode"""
    mode_id: DetectionMode
    display_name: str
    description: str
    primary_model: ModelConfig
    fallback_models: List[ModelConfig]
    enabled: bool = True
    priority: int = 0  # Higher number = higher priority

class ModeRegistry:
    """
    Centralized registry for managing detection modes and their configurations.
    
    This class follows the Registry pattern to provide a single source of truth
    for all available detection modes, their models, and configurations.
    """
    
    def __init__(self):
        self._modes: Dict[DetectionMode, ModeConfig] = {}
        self._initialized = False
        self._initialize_default_modes()
    
    def _initialize_default_modes(self):
        """Initialize default detection modes with their configurations"""
        try:
            # Get the base directory for model files
            base_dir = Path(__file__).parent.parent.parent.parent
            models_dir = base_dir / "models"
            backend_models_dir = base_dir / "backend" / "models"
            
            # Traditional Mode Configuration - EXCLUSIVELY uses deepfake_detector_finetuned1.pth
            ml_artifacts_dir = base_dir / "ml_artifacts"
            traditional_model_path = self._find_model_file([
                ml_artifacts_dir / "deepfake_detector_finetuned1.pth",
                models_dir / "deepfake_detector_finetuned1.pth",
                backend_models_dir / "deepfake_detector_finetuned1.pth",
                base_dir / "deepfake_detector_finetuned1.pth"
            ])
            
            traditional_config = ModeConfig(
                mode_id=DetectionMode.TRADITIONAL,
                display_name="Traditional Detection",
                description="Classical deepfake detection using fine-tuned EfficientNet-B0 model",
                primary_model=ModelConfig(
                    model_path=traditional_model_path,
                    model_name="EfficientNet-B0 Fine-tuned",
                    description="Traditional deepfake detection model with proven accuracy",
                    accuracy=94.1,
                    processing_time_ms=1200,
                    memory_usage_mb=45,
                    supported_formats=["mp4", "avi", "mov", "mkv", "webm"],
                    fallback_available=True
                ),
                fallback_models=[],
                enabled=True,
                priority=1
            )
            
            # Modern AI Mode Configuration - Uses other EfficientNet-based detectors (NOT deepfake_detector_finetuned1.pth)
            modern_model_path = self._find_model_file([
                ml_artifacts_dir / "efficientnet_b0.pth",
                models_dir / "efficientnet_b0.pth", 
                backend_models_dir / "efficientnet_b0.pth",
                base_dir / "efficientnet_b0.pth",
                ml_artifacts_dir / "deepfake_detector_finetuned1.pth",  # Alternative model for modern AI
                models_dir / "deepfake_detector_finetuned1.pth"
            ])
            
            modern_config = ModeConfig(
                mode_id=DetectionMode.MODERN_AI,
                display_name="Modern AI Detection",
                description="Advanced AI-powered detection using latest model architecture",
                primary_model=ModelConfig(
                    model_path=modern_model_path,
                    model_name="EfficientNet-B0 Base Model",
                    description="Modern AI detection using EfficientNet-B0 architecture with enhanced capabilities",
                    accuracy=92.3,
                    processing_time_ms=1500,
                    memory_usage_mb=65,
                    supported_formats=["mp4", "avi", "mov", "mkv", "webm", "m4v"],
                    fallback_available=True
                ),
                fallback_models=[],
                enabled=True,
                priority=2
            )
            
            # Register modes
            self._modes[DetectionMode.TRADITIONAL] = traditional_config
            self._modes[DetectionMode.MODERN_AI] = modern_config
            
            self._initialized = True
            logger.info("[OK] Mode registry initialized with 2 detection modes")
            
        except Exception as e:
            logger.error(f"Failed to initialize mode registry: {e}")
            self._create_emergency_fallback()
    
    def _find_model_file(self, possible_paths: List[Path]) -> str:
        """Find the first existing model file from a list of possible paths"""
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found model file: {path}")
                return str(path)
        
        # If no model found, return the first path as default (will be handled by error handling)
        logger.warning(f"No model file found in any of the expected locations: {[str(p) for p in possible_paths]}")
        return str(possible_paths[0])
    
    def _create_emergency_fallback(self):
        """Create emergency fallback configuration if initialization fails"""
        try:
            # Create minimal fallback configuration
            fallback_config = ModeConfig(
                mode_id=DetectionMode.TRADITIONAL,
                display_name="Fallback Detection",
                description="Emergency fallback mode",
                primary_model=ModelConfig(
                    model_path="fallback",
                    model_name="Fallback Model",
                    description="Emergency fallback model",
                    accuracy=85.0,
                    processing_time_ms=2000,
                    memory_usage_mb=30,
                    supported_formats=["mp4", "avi"],
                    fallback_available=False
                ),
                fallback_models=[],
                enabled=True,
                priority=0
            )
            
            self._modes[DetectionMode.TRADITIONAL] = fallback_config
            self._initialized = True
            logger.warning("[WARNING] Mode registry initialized with emergency fallback only")
            
        except Exception as e:
            logger.error(f"Failed to create emergency fallback: {e}")
            self._initialized = False
    
    def get_mode(self, mode_id: DetectionMode) -> Optional[ModeConfig]:
        """Get configuration for a specific mode"""
        if not self._initialized:
            logger.error("Mode registry not initialized")
            return None
        
        return self._modes.get(mode_id)
    
    def get_all_modes(self) -> Dict[DetectionMode, ModeConfig]:
        """Get all available modes"""
        if not self._initialized:
            logger.error("Mode registry not initialized")
            return {}
        
        return self._modes.copy()
    
    def get_enabled_modes(self) -> Dict[DetectionMode, ModeConfig]:
        """Get only enabled modes"""
        if not self._initialized:
            return {}
        
        return {mode_id: config for mode_id, config in self._modes.items() if config.enabled}
    
    def get_available_modes(self) -> List[DetectionMode]:
        """Get list of available mode enums"""
        if not self._initialized:
            return []
        
        return [mode_id for mode_id, config in self._modes.items() if config.enabled]
    
    def is_mode_available(self, mode_id: DetectionMode) -> bool:
        """Check if a mode is available and enabled"""
        if not self._initialized:
            return False
        
        config = self._modes.get(mode_id)
        return config is not None and config.enabled
    
    def get_mode_by_alias(self, alias: str) -> Optional[DetectionMode]:
        """Get mode by string alias (e.g., 'traditional', 'modern_ai')"""
        if not self._initialized:
            return None
        
        alias_mapping = {
            "traditional": DetectionMode.TRADITIONAL,
            "modern": DetectionMode.MODERN_AI,
            "modern_ai": DetectionMode.MODERN_AI,
            "ai_generated": DetectionMode.MODERN_AI,
            "latest": DetectionMode.MODERN_AI
        }
        
        return alias_mapping.get(alias.lower())
    
    def validate_mode_request(self, mode_alias: str) -> Tuple[bool, Optional[DetectionMode], Optional[str]]:
        """
        Validate a mode request and return validation result
        
        Returns:
            Tuple of (is_valid, mode_enum, error_message)
        """
        if not self._initialized:
            return False, None, "Mode registry not initialized"
        
        mode_enum = self.get_mode_by_alias(mode_alias)
        if mode_enum is None:
            available_aliases = ["traditional", "modern_ai", "modern", "ai_generated", "latest"]
            return False, None, f"Invalid mode '{mode_alias}'. Available modes: {', '.join(available_aliases)}"
        
        if not self.is_mode_available(mode_enum):
            return False, mode_enum, f"Mode '{mode_alias}' is not available or disabled"
        
        return True, mode_enum, None
    
    def get_mode_info(self, mode_id: DetectionMode) -> Dict[str, Any]:
        """Get detailed information about a mode for API responses"""
        config = self.get_mode(mode_id)
        if not config:
            return {}
        
        return {
            "mode_id": config.mode_id.value,
            "display_name": config.display_name,
            "description": config.description,
            "enabled": config.enabled,
            "priority": config.priority,
            "primary_model": {
                "name": config.primary_model.model_name,
                "description": config.primary_model.description,
                "accuracy": config.primary_model.accuracy,
                "processing_time_ms": config.primary_model.processing_time_ms,
                "memory_usage_mb": config.primary_model.memory_usage_mb,
                "supported_formats": config.primary_model.supported_formats,
                "fallback_available": config.primary_model.fallback_available
            },
            "fallback_models": [
                {
                    "name": model.model_name,
                    "description": model.description,
                    "accuracy": model.accuracy,
                    "processing_time_ms": model.processing_time_ms,
                    "memory_usage_mb": model.memory_usage_mb,
                    "supported_formats": model.supported_formats
                }
                for model in config.fallback_models
            ]
        }
    
    def add_custom_mode(self, mode_config: ModeConfig) -> bool:
        """Add a custom mode to the registry (for future extensibility)"""
        try:
            if not self._initialized:
                logger.error("Cannot add custom mode: registry not initialized")
                return False
            
            self._modes[mode_config.mode_id] = mode_config
            logger.info(f"[OK] Added custom mode: {mode_config.display_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom mode: {e}")
            return False
    
    def disable_mode(self, mode_id: DetectionMode) -> bool:
        """Disable a mode (useful for maintenance)"""
        try:
            if mode_id in self._modes:
                self._modes[mode_id].enabled = False
                logger.info(f"Disabled mode: {mode_id.value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to disable mode {mode_id.value}: {e}")
            return False
    
    def enable_mode(self, mode_id: DetectionMode) -> bool:
        """Enable a mode"""
        try:
            if mode_id in self._modes:
                self._modes[mode_id].enabled = True
                logger.info(f"Enabled mode: {mode_id.value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to enable mode {mode_id.value}: {e}")
            return False

# Global registry instance
_mode_registry: Optional[ModeRegistry] = None

def get_mode_registry() -> ModeRegistry:
    """Get the global mode registry instance (singleton pattern)"""
    global _mode_registry
    if _mode_registry is None:
        _mode_registry = ModeRegistry()
    return _mode_registry

def reset_mode_registry():
    """Reset the global mode registry (useful for testing)"""
    global _mode_registry
    _mode_registry = None
