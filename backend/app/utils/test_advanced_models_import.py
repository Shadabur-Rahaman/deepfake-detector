#!/usr/bin/env python3
"""
Test script to verify advanced models can be imported correctly
Run this to diagnose import issues
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "app"))
sys.path.insert(0, str(project_root / "advanced_models"))

print("="*80)
print("ADVANCED MODELS IMPORT DIAGNOSTIC")
print("="*80)
print(f"\n📁 Project root: {project_root}")
print(f"📁 Python paths added:")
for p in sys.path[:5]:
    print(f"   - {p}")

print("\n" + "="*80)
print("TESTING IMPORTS")
print("="*80)

# Test 1: Advanced model loader
print("\n1. Testing advanced_model_loader...")
try:
    from backend.app.utils.advanced_model_loader import (
        setup_advanced_models_paths,
        get_model_availability,
        get_advanced_model,
        initialize_all_models
    )
    paths = setup_advanced_models_paths()
    print(f"   ✅ Advanced model loader imported successfully")
    print(f"   ✅ {len(paths)} paths added")
except Exception as e:
    print(f"   ❌ Failed to import advanced_model_loader: {e}")

# Test 2: LSTM Detector
print("\n2. Testing LSTM Detector...")
try:
    # Try from advanced_models
    try:
        from advanced_models.lstm_detector import AdvancedLSTMDetector
        print(f"   ✅ AdvancedLSTMDetector imported from advanced_models")
        detector = AdvancedLSTMDetector()
        print(f"   ✅ AdvancedLSTMDetector instantiated successfully")
    except ImportError:
        # Try from backend.app.models
        from backend.app.models.temporal_analysis.lstm_detector import LSTMDetector
        print(f"   ✅ LSTMDetector imported from backend.app.models")
        detector = LSTMDetector()
        print(f"   ✅ LSTMDetector instantiated successfully")
except Exception as e:
    print(f"   ❌ LSTM Detector failed: {e}")

# Test 3: ViViT Detector
print("\n3. Testing ViViT Detector...")
try:
    # Try from advanced_models
    try:
        from advanced_models.vivit_detector import AdvancedViViTDetector
        print(f"   ✅ AdvancedViViTDetector imported from advanced_models")
        detector = AdvancedViViTDetector()
        print(f"   ✅ AdvancedViViTDetector instantiated successfully")
    except ImportError:
        # Try from backend.app.models
        from backend.app.models.temporal_analysis.vivit_detector import ViViTDetector
        print(f"   ✅ ViViTDetector imported from backend.app.models")
        detector = ViViTDetector()
        print(f"   ✅ ViViTDetector instantiated successfully")
except Exception as e:
    print(f"   ❌ ViViT Detector failed: {e}")

# Test 4: Advanced models package
print("\n4. Testing advanced_models package...")
try:
    import advanced_models
    print(f"   ✅ advanced_models package imported")
    available = advanced_models.get_available_models()
    print(f"   ✅ Available models: {list(available.keys())}")
    print(f"   ✅ Model count: {advanced_models.get_model_count()}/{len(advanced_models.AVAILABLE_MODELS)}")
except Exception as e:
    print(f"   ❌ advanced_models package failed: {e}")

# Test 5: Using centralized loader
print("\n5. Testing centralized model loader...")
try:
    from backend.app.utils.advanced_model_loader import get_advanced_model
    
    lstm_class = get_advanced_model('lstm_detector')
    if lstm_class:
        print(f"   ✅ LSTM detector class loaded via centralized loader")
    else:
        print(f"   ⚠️  LSTM detector not available via centralized loader")
    
    vivit_class = get_advanced_model('vivit_detector')
    if vivit_class:
        print(f"   ✅ ViViT detector class loaded via centralized loader")
    else:
        print(f"   ⚠️  ViViT detector not available via centralized loader")
        
except Exception as e:
    print(f"   ❌ Centralized loader failed: {e}")

# Test 6: Initialize all models
print("\n6. Testing model initialization...")
try:
    from backend.app.utils.advanced_model_loader import initialize_all_models
    availability = initialize_all_models()
    print(f"   ✅ Model initialization completed")
    print(f"   📊 Availability status:")
    for model_name, available in availability.items():
        status = "✅" if available else "❌"
        print(f"      {status} {model_name}: {'Available' if available else 'Not available'}")
except Exception as e:
    print(f"   ❌ Model initialization failed: {e}")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80)
print("\n✅ If you see green checkmarks above, the imports are working correctly")
print("⚠️  Yellow warnings indicate optional features that aren't available")
print("❌ Red X marks indicate errors that need to be fixed\n")

