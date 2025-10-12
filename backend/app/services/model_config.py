#!/usr/bin/env python3
"""
Model Loading Configuration - Control which models to load
"""

import os
from typing import Dict, List, Set

class ModelConfig:
    """Configuration for model loading"""
    
    def __init__(self):
        self.essential_models = {
            "yolo_face_detector",
            "basic_deepfake_detector",
            "efficientnet_b0",
            "haar_cascade"
        }
        
        self.optional_models = {
            "ultra_ensemble_25_models",
            "production_advanced_detector", 
            "neural_texture_analyzer",
            "vision_transformer_models",
            "clip_models",
            "openai_models",
            "google_models",
            "frequency_analyzer",
            "temporal_coherence_checker",
            "metadata_classifier",
            "deterministic_ensemble",
            "free_ai_ensemble",
            "enhanced_detection_engine",
            "modern_ai_detector"
        }
        
        self.heavy_models = {
            "ultra_ensemble_25_models",  # 27 models
            "production_advanced_detector",  # 15+ models
            "vision_transformer_models",  # Large transformers
            "neural_texture_analyzer"  # Complex neural networks
        }
    
    def get_models_to_load(self) -> Set[str]:
        """Get which models should be loaded based on environment variables"""
        models_to_load = self.essential_models.copy()
        
        # Add optional models based on environment variables
        if os.getenv("LOAD_ULTRA_ENSEMBLE", "false").lower() == "true":
            models_to_load.add("ultra_ensemble_25_models")
        
        if os.getenv("LOAD_PRODUCTION_ADVANCED", "false").lower() == "true":
            models_to_load.add("production_advanced_detector")
        
        if os.getenv("LOAD_NEURAL_TEXTURE", "false").lower() == "true":
            models_to_load.add("neural_texture_analyzer")
        
        if os.getenv("LOAD_VISION_TRANSFORMERS", "false").lower() == "true":
            models_to_load.add("vision_transformer_models")
        
        if os.getenv("LOAD_CLIP_MODELS", "false").lower() == "true":
            models_to_load.add("clip_models")
        
        if os.getenv("LOAD_AI_MODELS", "false").lower() == "true":
            models_to_load.update(["openai_models", "google_models"])
        
        return models_to_load
    
    def get_models_to_skip(self) -> Set[str]:
        """Get which models should be skipped"""
        models_to_load = self.get_models_to_load()
        return self.optional_models - models_to_load
    
    def is_fast_mode(self) -> bool:
        """Check if fast startup mode is enabled"""
        return os.getenv("FAST_STARTUP", "false").lower() == "true"
    
    def get_startup_mode(self) -> str:
        """Get the current startup mode"""
        if self.is_fast_mode():
            return "fast"
        elif len(self.get_models_to_load()) <= len(self.essential_models):
            return "minimal"
        else:
            return "full"

# Global model configuration
model_config = ModelConfig()

