# app/utils/model_importer.py
import sys
import os
from pathlib import Path

def setup_advanced_models_path():
    """Add advanced_models directory to Python path"""
    # Get the root directory of your project
    root_dir = Path(__file__).parent.parent.parent  # Goes up to deepfake-detector/
    advanced_models_path = root_dir / "advanced_models"
    
    if str(advanced_models_path) not in sys.path:
        sys.path.insert(0, str(advanced_models_path))
        print(f"✅ Advanced models path added: {advanced_models_path}")
    
    return advanced_models_path

# Call this once when the module is imported
ADVANCED_MODELS_PATH = setup_advanced_models_path()

def get_model_availability():
    """Check which advanced models are available"""
    available_models = {}
    
    try:
        from yolov8_face import YOLOv8Face
        available_models['yolov8'] = True
    except ImportError:
        available_models['yolov8'] = False
    
    try:
        from mesonet_detector import mesonet_detector
        available_models['mesonet'] = True
    except ImportError:
        available_models['mesonet'] = False
    
    try:
        from ensemble_detector import UltraEnsembleDetector
        available_models['ultra_ensemble'] = True
    except ImportError:
        available_models['ultra_ensemble'] = False
        
    return available_models

# Global availability check
MODEL_AVAILABILITY = get_model_availability()
print(f"🔍 Available advanced models: {MODEL_AVAILABILITY}")
