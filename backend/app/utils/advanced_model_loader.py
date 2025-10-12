# backend/app/utils/advanced_model_loader.py
"""
Centralized advanced model loader with graceful fallbacks
Handles imports from multiple locations: advanced_models/, backend/app/models/, app/models/
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Setup paths for advanced models
def setup_advanced_models_paths():
    """Add all possible advanced model directories to Python path"""
    paths_added = []
    
    # Get project root (deepfake-detector/)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    
    # Possible locations for advanced models
    possible_paths = [
        project_root / "advanced_models",
        project_root / "backend" / "app" / "models",
        project_root / "app" / "models",
    ]
    
    for path in possible_paths:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))
            paths_added.append(str(path))
            logger.info(f"✅ Added to path: {path}")
    
    return paths_added

# Initialize paths on module import
ADVANCED_MODEL_PATHS = setup_advanced_models_paths()

# Model availability tracking
MODEL_AVAILABILITY = {
    'lstm_detector': False,
    'vivit_detector': False,
    'vision_transformer': False,
    'resnet50_detector': False,
    'yolov8_face': False,
    'mesonet_detector': False,
    'ensemble_detector': False,
    'hybrid_detector': False,
    'unite_detector': False,
    'divid_detector': False,
}

# Model instances cache
MODEL_CACHE = {}


def try_import_lstm_detector():
    """Try to import LSTM detector from multiple locations"""
    try:
        # Try advanced_models first
        try:
            from advanced_models.lstm_detector import AdvancedLSTMDetector
            logger.info("✅ Imported AdvancedLSTMDetector from advanced_models")
            return AdvancedLSTMDetector
        except ImportError:
            pass
        
        # Try backend.app.models
        try:
            from backend.app.models.temporal_analysis.lstm_detector import LSTMDetector
            logger.info("✅ Imported LSTMDetector from backend.app.models")
            return LSTMDetector
        except ImportError:
            pass
        
        # Try app.models
        try:
            from app.models.temporal_analysis.lstm_detector import LSTMDetector
            logger.info("✅ Imported LSTMDetector from app.models")
            return LSTMDetector
        except ImportError:
            pass
        
        logger.warning("⚠️ LSTM detector not found in any location")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error importing LSTM detector: {e}")
        return None


def try_import_vivit_detector():
    """Try to import ViViT detector from multiple locations"""
    try:
        # Try advanced_models first
        try:
            from advanced_models.vivit_detector import AdvancedViViTDetector
            logger.info("✅ Imported AdvancedViViTDetector from advanced_models")
            return AdvancedViViTDetector
        except ImportError:
            pass
        
        # Try backend.app.models
        try:
            from backend.app.models.temporal_analysis.vivit_detector import ViViTDetector
            logger.info("✅ Imported ViViTDetector from backend.app.models")
            return ViViTDetector
        except ImportError:
            pass
        
        # Try app.models
        try:
            from app.models.temporal_analysis.vivit_detector import ViViTDetector
            logger.info("✅ Imported ViViTDetector from app.models")
            return ViViTDetector
        except ImportError:
            pass
        
        logger.warning("⚠️ ViViT detector not found in any location")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error importing ViViT detector: {e}")
        return None


def try_import_vision_transformer():
    """Try to import Vision Transformer from multiple locations"""
    try:
        # Try advanced_models first
        try:
            from advanced_models.vision_transformer import AdvancedVisionTransformerDetector
            logger.info("✅ Imported AdvancedVisionTransformerDetector from advanced_models")
            return AdvancedVisionTransformerDetector
        except ImportError:
            pass
        
        # Try backend.app.models
        try:
            from backend.app.models.spatial_analysis.vision_transformer import VisionTransformerDetector
            logger.info("✅ Imported VisionTransformerDetector from backend.app.models")
            return VisionTransformerDetector
        except ImportError:
            pass
        
        # Try app.models
        try:
            from app.models.spatial_analysis.vision_transformer import VisionTransformerDetector
            logger.info("✅ Imported VisionTransformerDetector from app.models")
            return VisionTransformerDetector
        except ImportError:
            pass
        
        logger.warning("⚠️ Vision Transformer not found in any location")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error importing Vision Transformer: {e}")
        return None


def try_import_hybrid_detector():
    """Try to import Hybrid CNN-LSTM detector from multiple locations"""
    try:
        # Try advanced_models first
        try:
            from advanced_models.hybrid_detector import HybridCNNLSTMDetector
            logger.info("✅ Imported HybridCNNLSTMDetector from advanced_models")
            return HybridCNNLSTMDetector
        except ImportError:
            pass
        
        # Try backend.app.services
        try:
            from backend.app.services.hybrid_detector import HybridCNNLSTMDetector
            logger.info("✅ Imported HybridCNNLSTMDetector from backend.app.services")
            return HybridCNNLSTMDetector
        except ImportError:
            pass
        
        logger.warning("⚠️ Hybrid detector not found in any location")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error importing Hybrid detector: {e}")
        return None


def get_advanced_model(model_name: str) -> Optional[Any]:
    """
    Get an advanced model class by name
    
    Args:
        model_name: Name of the model (e.g., 'lstm_detector', 'vivit_detector')
    
    Returns:
        Model class or None if not available
    """
    # Check cache first
    if model_name in MODEL_CACHE:
        return MODEL_CACHE[model_name]
    
    # Import mapping
    import_functions = {
        'lstm_detector': try_import_lstm_detector,
        'vivit_detector': try_import_vivit_detector,
        'vision_transformer': try_import_vision_transformer,
        'hybrid_detector': try_import_hybrid_detector,
    }
    
    if model_name in import_functions:
        model_class = import_functions[model_name]()
        if model_class:
            MODEL_CACHE[model_name] = model_class
            MODEL_AVAILABILITY[model_name] = True
        return model_class
    else:
        logger.warning(f"⚠️ Unknown model name: {model_name}")
        return None


def get_model_availability() -> Dict[str, bool]:
    """Get availability status of all advanced models"""
    return MODEL_AVAILABILITY.copy()


def initialize_all_models():
    """
    Attempt to initialize all advanced models
    Returns dict with availability status
    """
    logger.info("🔄 Initializing all advanced models...")
    
    for model_name in MODEL_AVAILABILITY.keys():
        try:
            model_class = get_advanced_model(model_name)
            if model_class:
                logger.info(f"✅ {model_name} is available")
            else:
                logger.warning(f"⚠️ {model_name} is not available")
        except Exception as e:
            logger.error(f"❌ Error initializing {model_name}: {e}")
    
    available_count = sum(MODEL_AVAILABILITY.values())
    total_count = len(MODEL_AVAILABILITY)
    
    logger.info(f"📊 Advanced models initialized: {available_count}/{total_count} available")
    
    return get_model_availability()


# Auto-initialize on import
if __name__ != "__main__":
    logger.info("🚀 Advanced model loader initialized")
    logger.info(f"📁 Paths added: {len(ADVANCED_MODEL_PATHS)}")

