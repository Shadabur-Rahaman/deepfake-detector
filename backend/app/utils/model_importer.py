# app/utils/model_importer.py
import sys
import os
import traceback
from pathlib import Path

def setup_advanced_models_path():
    """Add advanced_models directory to Python path"""
    # Get the root directory of your project
    root_dir = Path(__file__).parent.parent.parent.parent  # Goes up to deepfake-detector/
    advanced_models_path = root_dir / "advanced_models"
    
    # Check if the path exists before adding it
    if advanced_models_path.exists():
        if str(advanced_models_path) not in sys.path:
            sys.path.insert(0, str(advanced_models_path))
            print(f"✅ Advanced models path added: {advanced_models_path}")
    else:
        # Create the directory if it doesn't exist
        advanced_models_path.mkdir(exist_ok=True)
        if str(advanced_models_path) not in sys.path:
            sys.path.insert(0, str(advanced_models_path))
            print(f"✅ Advanced models path created and added: {advanced_models_path}")
    
    return advanced_models_path

# Call this once when the module is imported
ADVANCED_MODELS_PATH = setup_advanced_models_path()

def get_model_availability():
    """Check which advanced models are available"""
    available_models = {}
    
    # Check YOLOv8 face detector
    try:
        from yolov8_face import AdvancedYOLOv8FaceDetector
        # Test instantiation to ensure it's functional
        detector = AdvancedYOLOv8FaceDetector()
        available_models['yolov8'] = True
        print(f"[OK] YOLOv8 AdvancedYOLOv8FaceDetector imported and instantiated successfully")
    except Exception as e:
        try:
            # Try alternative import using importlib
            import importlib
            yolov8_module = importlib.import_module('yolov8_face')
            if hasattr(yolov8_module, 'AdvancedYOLOv8FaceDetector'):
                available_models['yolov8'] = True
                print(f"[OK] YOLOv8 face detector imported successfully (alternative)")
            else:
                available_models['yolov8'] = False
                print(f"[INFO] YOLOv8 AdvancedYOLOv8FaceDetector class not found")
        except Exception as e2:
            available_models['yolov8'] = False
            print(f"[INFO] YOLOv8 advanced model not available: {type(e).__name__}: {str(e)[:100]}")
    
    # Check MesoNet detector
    try:
        from mesonet_detector import MesoNet
        # Test instantiation to ensure it's functional
        model = MesoNet()
        available_models['mesonet'] = True
        print(f"[OK] MesoNet imported and instantiated successfully")
    except Exception as e:
        try:
            # Try alternative import using importlib
            import importlib
            mesonet_module = importlib.import_module('mesonet_detector')
            if hasattr(mesonet_module, 'MesoNet'):
                available_models['mesonet'] = True
                print(f"[OK] MesoNet imported successfully (alternative)")
            else:
                available_models['mesonet'] = False
                print(f"[INFO] MesoNet class not found")
        except Exception as e2:
            available_models['mesonet'] = False
            print(f"[INFO] MesoNet advanced model not available: {type(e).__name__}: {str(e)[:100]}")
    
    # Check Ultra Ensemble detector
    try:
        from ensemble_detector import AdvancedEnsembleDetector
        # Test instantiation to ensure it's functional
        ensemble = AdvancedEnsembleDetector()
        available_models['ultra_ensemble'] = True
        print(f"[OK] Ultra Ensemble AdvancedEnsembleDetector imported and instantiated successfully")
    except Exception as e:
        try:
            # Try alternative import using importlib
            import importlib
            ensemble_module = importlib.import_module('ensemble_detector')
            if hasattr(ensemble_module, 'AdvancedEnsembleDetector'):
                available_models['ultra_ensemble'] = True
                print(f"[OK] Ultra Ensemble imported successfully (alternative)")
            else:
                available_models['ultra_ensemble'] = False
                print(f"[INFO] AdvancedEnsembleDetector class not found")
        except Exception as e2:
            available_models['ultra_ensemble'] = False
            print(f"[INFO] Ultra Ensemble advanced model not available: {type(e).__name__}: {str(e)[:100]}")
        
    return available_models

# Global availability check
MODEL_AVAILABILITY = get_model_availability()
print(f"🔍 Available advanced models: {MODEL_AVAILABILITY}")
