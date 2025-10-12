# backend/app/services/model_availability.py - Centralized Model Availability Detection

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Initialize all availability flags to False at module level
TIMM_AVAILABLE = False
YOLO_AVAILABLE = False
TORCHVISION_AVAILABLE = False
VIT_AVAILABLE = False
LSTM_AVAILABLE = False
RESNET_AVAILABLE = False

# Safe import detection with proper error handling
def _safe_import_timm():
    """Safely import timm and set global flag"""
    global TIMM_AVAILABLE
    try:
        import timm  # type: ignore
        TIMM_AVAILABLE = True
        logger.info("[OK] timm imported successfully")
        return True
    except ImportError as e:
        logger.info(f"ℹ️ timm not available: {e}")
        TIMM_AVAILABLE = False
        return False
    except Exception as e:
        logger.warning(f"[WARNING] timm import error: {e}")
        TIMM_AVAILABLE = False
        return False

def _safe_import_yolo():
    """Safely import YOLO and set global flag"""
    global YOLO_AVAILABLE
    try:
        from ultralytics import YOLO  # type: ignore
        YOLO_AVAILABLE = True
        logger.info("[OK] ultralytics (YOLO) imported successfully")
        return True
    except ImportError as e:
        logger.info(f"ℹ️ ultralytics not available: {e}")
        YOLO_AVAILABLE = False
        return False
    except Exception as e:
        logger.warning(f"[WARNING] ultralytics import error: {e}")
        YOLO_AVAILABLE = False
        return False

def _safe_import_torchvision():
    """Safely import torchvision and set global flag"""
    global TORCHVISION_AVAILABLE
    try:
        import torchvision  # type: ignore
        TORCHVISION_AVAILABLE = True
        logger.info("[OK] torchvision imported successfully")
        return True
    except ImportError as e:
        logger.info(f"ℹ️ torchvision not available: {e}")
        TORCHVISION_AVAILABLE = False
        return False
    except Exception as e:
        logger.warning(f"[WARNING] torchvision import error: {e}")
        TORCHVISION_AVAILABLE = False
        return False

def _safe_import_vit():
    """Safely import Vision Transformer and set global flag"""
    global VIT_AVAILABLE
    try:
        import vit_pytorch  # type: ignore
        VIT_AVAILABLE = True
        logger.info("[OK] vit-pytorch imported successfully")
        return True
    except ImportError as e:
        logger.info(f"ℹ️ vit-pytorch not available: {e}")
        VIT_AVAILABLE = False
        return False
    except Exception as e:
        logger.warning(f"[WARNING] vit-pytorch import error: {e}")
        VIT_AVAILABLE = False
        return False

def _safe_import_lstm():
    """Safely import LSTM dependencies and set global flag"""
    global LSTM_AVAILABLE
    try:
        import torch.nn as nn
        # Check if we have the required modules for LSTM
        if hasattr(nn, 'LSTM'):
            LSTM_AVAILABLE = True
            logger.info("[OK] LSTM modules available")
            return True
        else:
            LSTM_AVAILABLE = False
            return False
    except Exception as e:
        logger.warning(f"[WARNING] LSTM import error: {e}")
        LSTM_AVAILABLE = False
        return False

def _safe_import_resnet():
    """Safely import ResNet dependencies and set global flag"""
    global RESNET_AVAILABLE
    try:
        import torchvision.models as models
        if hasattr(models, 'resnet50'):
            RESNET_AVAILABLE = True
            logger.info("[OK] ResNet50 available via torchvision")
            return True
        else:
            RESNET_AVAILABLE = False
            return False
    except Exception as e:
        logger.warning(f"[WARNING] ResNet import error: {e}")
        RESNET_AVAILABLE = False
        return False

def initialize_model_availability():
    """Initialize all model availability flags"""
    logger.info("🔍 Checking model availability...")
    
    # Import all modules safely
    _safe_import_timm()
    _safe_import_yolo()
    _safe_import_torchvision()
    _safe_import_vit()
    _safe_import_lstm()
    _safe_import_resnet()
    
    # Log summary
    available_models = []
    unavailable_models = []
    
    if TIMM_AVAILABLE:
        available_models.append("timm")
    else:
        unavailable_models.append("timm")
    
    if YOLO_AVAILABLE:
        available_models.append("yolo")
    else:
        unavailable_models.append("yolo")
    
    if TORCHVISION_AVAILABLE:
        available_models.append("torchvision")
    else:
        unavailable_models.append("torchvision")
    
    if VIT_AVAILABLE:
        available_models.append("vit")
    else:
        unavailable_models.append("vit")
    
    if LSTM_AVAILABLE:
        available_models.append("lstm")
    else:
        unavailable_models.append("lstm")
    
    if RESNET_AVAILABLE:
        available_models.append("resnet")
    else:
        unavailable_models.append("resnet")
    
    logger.info(f"[OK] Available modules: {', '.join(available_models)}")
    if unavailable_models:
        logger.info(f"ℹ️ Unavailable modules: {', '.join(unavailable_models)}")
    
    return {
        'timm': TIMM_AVAILABLE,
        'yolo': YOLO_AVAILABLE,
        'torchvision': TORCHVISION_AVAILABLE,
        'vit': VIT_AVAILABLE,
        'lstm': LSTM_AVAILABLE,
        'resnet': RESNET_AVAILABLE
    }

def get_availability_status() -> Dict[str, bool]:
    """Get current availability status of all models"""
    return {
        'timm': TIMM_AVAILABLE,
        'yolo': YOLO_AVAILABLE,
        'torchvision': TORCHVISION_AVAILABLE,
        'vit': VIT_AVAILABLE,
        'lstm': LSTM_AVAILABLE,
        'resnet': RESNET_AVAILABLE
    }

def get_installation_hints() -> Dict[str, str]:
    """Get installation hints for unavailable models"""
    hints = {}
    
    if not TIMM_AVAILABLE:
        hints['timm'] = "pip install timm"
    
    if not YOLO_AVAILABLE:
        hints['yolo'] = "pip install ultralytics"
    
    if not TORCHVISION_AVAILABLE:
        hints['torchvision'] = "pip install torchvision"
    
    if not VIT_AVAILABLE:
        hints['vit'] = "pip install vit-pytorch"
    
    if not LSTM_AVAILABLE:
        hints['lstm'] = "LSTM is part of PyTorch core - check PyTorch installation"
    
    if not RESNET_AVAILABLE:
        hints['resnet'] = "pip install torchvision"
    
    return hints

# Initialize on module import
initialize_model_availability()
