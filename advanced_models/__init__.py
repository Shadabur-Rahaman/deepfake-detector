# advanced_models/__init__.py
"""
Advanced Models Package
Contains sophisticated deepfake detection models including:
- LSTM Detector (temporal analysis)
- ViViT Detector (video vision transformer)
- Vision Transformer
- Hybrid CNN-LSTM Detector
- UNITE Detector
- DIVID Detector
- and more...
"""

__version__ = "1.0.0"

# Graceful imports with fallbacks
import logging

logger = logging.getLogger(__name__)

# Try to import advanced models, but don't fail if they're not available
__all__ = [
    'AdvancedLSTMDetector',
    'AdvancedViViTDetector',
    'AdvancedVisionTransformerDetector',
    'HybridCNNLSTMDetector',
    'UNITEDetector',
    'DIVIDDetector',
    'AdvancedEnsembleDetector',
    'AdvancedMesoNetDetector',
    'AdvancedYOLOv8FaceDetector',
]

# Track which models are available
AVAILABLE_MODELS = {}

# LSTM Detector
try:
    from .lstm_detector import AdvancedLSTMDetector
    AVAILABLE_MODELS['AdvancedLSTMDetector'] = True
except ImportError as e:
    logger.debug(f"LSTM detector not available: {e}")
    AVAILABLE_MODELS['AdvancedLSTMDetector'] = False
    AdvancedLSTMDetector = None

# ViViT Detector
try:
    from .vivit_detector import AdvancedViViTDetector
    AVAILABLE_MODELS['AdvancedViViTDetector'] = True
except ImportError as e:
    logger.debug(f"ViViT detector not available: {e}")
    AVAILABLE_MODELS['AdvancedViViTDetector'] = False
    AdvancedViViTDetector = None

# Vision Transformer
try:
    from .vision_transformer import AdvancedVisionTransformerDetector
    AVAILABLE_MODELS['AdvancedVisionTransformerDetector'] = True
except ImportError as e:
    logger.debug(f"Vision Transformer not available: {e}")
    AVAILABLE_MODELS['AdvancedVisionTransformerDetector'] = False
    AdvancedVisionTransformerDetector = None

# Hybrid CNN-LSTM Detector
try:
    from .hybrid_detector import HybridCNNLSTMDetector
    AVAILABLE_MODELS['HybridCNNLSTMDetector'] = True
except ImportError as e:
    logger.debug(f"Hybrid detector not available: {e}")
    AVAILABLE_MODELS['HybridCNNLSTMDetector'] = False
    HybridCNNLSTMDetector = None

# UNITE Detector
try:
    from .unite_detector import UNITEDetector
    AVAILABLE_MODELS['UNITEDetector'] = True
except ImportError as e:
    logger.debug(f"UNITE detector not available: {e}")
    AVAILABLE_MODELS['UNITEDetector'] = False
    UNITEDetector = None

# DIVID Detector
try:
    from .divid_detector import DIVIDDetector
    AVAILABLE_MODELS['DIVIDDetector'] = True
except ImportError as e:
    logger.debug(f"DIVID detector not available: {e}")
    AVAILABLE_MODELS['DIVIDDetector'] = False
    DIVIDDetector = None

# Ensemble Detector
try:
    from .ensemble_detector import AdvancedEnsembleDetector
    AVAILABLE_MODELS['AdvancedEnsembleDetector'] = True
except ImportError as e:
    logger.debug(f"Ensemble detector not available: {e}")
    AVAILABLE_MODELS['AdvancedEnsembleDetector'] = False
    AdvancedEnsembleDetector = None

# MesoNet Detector
try:
    from .mesonet_detector import AdvancedMesoNetDetector
    AVAILABLE_MODELS['AdvancedMesoNetDetector'] = True
except ImportError as e:
    logger.debug(f"MesoNet detector not available: {e}")
    AVAILABLE_MODELS['AdvancedMesoNetDetector'] = False
    AdvancedMesoNetDetector = None

# YOLOv8 Face Detector
try:
    from .yolov8_face import AdvancedYOLOv8FaceDetector
    AVAILABLE_MODELS['AdvancedYOLOv8FaceDetector'] = True
except ImportError as e:
    logger.debug(f"YOLOv8 Face detector not available: {e}")
    AVAILABLE_MODELS['AdvancedYOLOv8FaceDetector'] = False
    AdvancedYOLOv8FaceDetector = None


def get_available_models():
    """Get a dictionary of available models"""
    return {k: v for k, v in AVAILABLE_MODELS.items() if v}


def get_model_count():
    """Get count of available models"""
    return sum(AVAILABLE_MODELS.values())


# Log available models on import
available_count = get_model_count()
total_count = len(AVAILABLE_MODELS)
logger.info(f"📦 Advanced models package loaded: {available_count}/{total_count} models available")

