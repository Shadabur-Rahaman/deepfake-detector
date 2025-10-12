"""
AI Standards Configuration 2025 - Deepfake Detection Backend
===========================================================

This module defines the configuration and standards for the 2025 AI deepfake detection system,
including calibration parameters, model weights, and performance thresholds.

Features:
- 2025 AI benchmark alignment
- Dynamic model weighting
- Calibration parameters
- Performance thresholds
- Quality assessment criteria
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class ModelArchitecture(Enum):
    """Supported model architectures for 2025 standards"""
    EFFICIENTNET = "efficientnet"
    RESNET = "resnet"
    VISION_TRANSFORMER = "vision_transformer"
    CONVNEXT = "convnext"
    SWIN_TRANSFORMER = "swin_transformer"
    MOBILE_NET = "mobile_net"
    CUSTOM = "custom"

class ConfidenceThreshold(Enum):
    """Confidence thresholds for 2025 standards"""
    VERY_LOW = (0, 40)      # Deepfake Likely
    UNCERTAIN = (41, 59)    # Needs Review
    HIGH = (60, 100)        # Authentic Likely

class QualityLevel(Enum):
    """Face quality levels for 2025 standards"""
    EXCELLENT = (0.9, 1.0)
    GOOD = (0.7, 0.89)
    FAIR = (0.5, 0.69)
    POOR = (0.0, 0.49)

@dataclass
class ModelCalibrationParams:
    """Calibration parameters for model temperature scaling"""
    temperature: float
    bias: float
    reliability_score: float
    calibration_error: float

@dataclass
class BenchmarkConfig:
    """Configuration for 2025 AI benchmarks"""
    name: str
    calibration_params: ModelCalibrationParams
    dataset_size: int
    validation_accuracy: float
    test_accuracy: float

class AIStandards2025:
    """Configuration class for 2025 AI standards"""
    
    # Model architecture weights based on 2025 performance
    MODEL_WEIGHTS = {
        ModelArchitecture.VISION_TRANSFORMER: 0.30,
        ModelArchitecture.EFFICIENTNET: 0.25,
        ModelArchitecture.CONVNEXT: 0.20,
        ModelArchitecture.RESNET: 0.15,
        ModelArchitecture.SWIN_TRANSFORMER: 0.05,
        ModelArchitecture.MOBILE_NET: 0.03,
        ModelArchitecture.CUSTOM: 0.02
    }
    
    # 2025 AI benchmark configurations
    BENCHMARK_CONFIGS = {
        "dfdc_plus_plus": BenchmarkConfig(
            name="DFDC++",
            calibration_params=ModelCalibrationParams(
                temperature=1.8,
                bias=0.1,
                reliability_score=0.92,
                calibration_error=0.05
            ),
            dataset_size=50000,
            validation_accuracy=0.89,
            test_accuracy=0.87
        ),
        "celebdf_v3": BenchmarkConfig(
            name="CelebDF-v3",
            calibration_params=ModelCalibrationParams(
                temperature=2.1,
                bias=-0.05,
                reliability_score=0.94,
                calibration_error=0.04
            ),
            dataset_size=25000,
            validation_accuracy=0.91,
            test_accuracy=0.89
        ),
        "deeperforensics_2": BenchmarkConfig(
            name="DeeperForensics-2.0",
            calibration_params=ModelCalibrationParams(
                temperature=1.9,
                bias=0.02,
                reliability_score=0.93,
                calibration_error=0.03
            ),
            dataset_size=35000,
            validation_accuracy=0.90,
            test_accuracy=0.88
        )
    }
    
    # Face quality assessment weights
    FACE_QUALITY_WEIGHTS = {
        'sharpness': 0.25,
        'brightness': 0.20,
        'contrast': 0.20,
        'size_quality': 0.20,
        'yolo_confidence': 0.15
    }
    
    # Temporal consistency weights
    TEMPORAL_WEIGHTS = {
        'frame_consistency': 0.4,
        'transition_smoothness': 0.3,
        'motion_consistency': 0.3
    }
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        'min_face_quality': 0.4,
        'min_yolo_confidence': 0.7,
        'min_model_agreement': 0.6,
        'max_uncertainty': 0.8,
        'min_processing_fps': 10.0,
        'max_processing_time': 30.0
    }
    
    # CUDA optimization settings
    CUDA_OPTIMIZATIONS = {
        'enable_mixed_precision': True,
        'enable_tensor_cores': True,
        'memory_fraction': 0.8,
        'allow_growth': True,
        'enable_cudnn_benchmark': True
    }
    
    # Async processing configuration
    ASYNC_CONFIG = {
        'max_workers': 4,
        'timeout_per_model': 30.0,
        'enable_parallel_execution': True,
        'enable_progress_tracking': True,
        'max_concurrent_requests': 10
    }
    
    # Logging configuration
    LOGGING_CONFIG = {
        'enable_interpretable_output': True,
        'enable_calibration_summary': True,
        'enable_softmax_distributions': False,
        'log_level': 'INFO',
        'enable_emoji_output': True
    }
    
    @classmethod
    def get_model_weight(cls, architecture: ModelArchitecture) -> float:
        """Get weight for a specific model architecture"""
        return cls.MODEL_WEIGHTS.get(architecture, 0.02)
    
    @classmethod
    def get_benchmark_config(cls, benchmark_name: str) -> Optional[BenchmarkConfig]:
        """Get configuration for a specific benchmark"""
        return cls.BENCHMARK_CONFIGS.get(benchmark_name)
    
    @classmethod
    def get_calibration_params(cls, benchmark_name: str) -> Optional[ModelCalibrationParams]:
        """Get calibration parameters for a specific benchmark"""
        config = cls.get_benchmark_config(benchmark_name)
        return config.calibration_params if config else None
    
    @classmethod
    def is_confidence_high(cls, confidence: float) -> bool:
        """Check if confidence meets high threshold"""
        return confidence >= ConfidenceThreshold.HIGH.value[0]
    
    @classmethod
    def is_confidence_uncertain(cls, confidence: float) -> bool:
        """Check if confidence is in uncertain range"""
        return ConfidenceThreshold.UNCERTAIN.value[0] <= confidence <= ConfidenceThreshold.UNCERTAIN.value[1]
    
    @classmethod
    def is_confidence_low(cls, confidence: float) -> bool:
        """Check if confidence is very low"""
        return confidence <= ConfidenceThreshold.VERY_LOW.value[1]
    
    @classmethod
    def get_confidence_level(cls, confidence: float) -> ConfidenceThreshold:
        """Get confidence level for a given confidence score"""
        if cls.is_confidence_low(confidence):
            return ConfidenceThreshold.VERY_LOW
        elif cls.is_confidence_uncertain(confidence):
            return ConfidenceThreshold.UNCERTAIN
        else:
            return ConfidenceThreshold.HIGH
    
    @classmethod
    def get_quality_level(cls, quality_score: float) -> QualityLevel:
        """Get quality level for a given quality score"""
        for level in QualityLevel:
            if level.value[0] <= quality_score <= level.value[1]:
                return level
        return QualityLevel.POOR
    
    @classmethod
    def should_use_ensemble(cls, num_models: int, face_quality: float) -> bool:
        """Determine if ensemble should be used based on conditions"""
        return (num_models >= 2 and 
                face_quality >= cls.PERFORMANCE_THRESHOLDS['min_face_quality'])
    
    @classmethod
    def should_use_async_processing(cls, num_models: int, num_faces: int) -> bool:
        """Determine if async processing should be used"""
        return (cls.ASYNC_CONFIG['enable_parallel_execution'] and 
                num_models >= 2 and 
                num_faces >= 3)
    
    @classmethod
    def get_optimal_workers(cls, num_models: int) -> int:
        """Get optimal number of workers for async processing"""
        return min(cls.ASYNC_CONFIG['max_workers'], num_models)
    
    @classmethod
    def format_interpretable_output(cls, prediction: str, confidence: float, 
                                  model_agreement: float, uncertainty: float) -> Dict[str, Any]:
        """Format output according to 2025 interpretable standards"""
        confidence_level = cls.get_confidence_level(confidence)
        
        # Determine emoji based on prediction and confidence
        if "authentic" in prediction.lower() or "real" in prediction.lower():
            status_emoji = "✅"
        elif "deepfake" in prediction.lower():
            status_emoji = "🤖"
        else:
            status_emoji = "❓"
        
        return {
            "prediction": prediction,
            "confidence_percentage": round(confidence, 1),
            "confidence_level": confidence_level.name,
            "status_emoji": status_emoji,
            "interpretation": f"{status_emoji} {prediction} (Confidence: {confidence:.1f}%)",
            "model_agreement": f"{model_agreement * 100:.1f}%",
            "uncertainty_estimate": f"{uncertainty:.3f}",
            "2025_standards": True,
            "quality_indicators": {
                "high_confidence": cls.is_confidence_high(confidence),
                "model_consensus": model_agreement >= 0.8,
                "low_uncertainty": uncertainty <= 0.3
            }
        }

# Global instance for easy access
ai_standards_2025 = AIStandards2025()

# Convenience functions
def get_2025_model_weight(architecture: str) -> float:
    """Get weight for model architecture by string name"""
    try:
        arch_enum = ModelArchitecture(architecture.lower())
        return ai_standards_2025.get_model_weight(arch_enum)
    except ValueError:
        return ai_standards_2025.get_model_weight(ModelArchitecture.CUSTOM)

def get_2025_calibration_params(benchmark: str) -> Optional[ModelCalibrationParams]:
    """Get calibration parameters for benchmark by name"""
    return ai_standards_2025.get_calibration_params(benchmark)

def is_2025_high_confidence(confidence: float) -> bool:
    """Check if confidence meets 2025 high threshold"""
    return ai_standards_2025.is_confidence_high(confidence)

def format_2025_output(prediction: str, confidence: float, 
                      model_agreement: float = 0.8, uncertainty: float = 0.2) -> Dict[str, Any]:
    """Format output according to 2025 standards"""
    return ai_standards_2025.format_interpretable_output(
        prediction, confidence, model_agreement, uncertainty
    )
