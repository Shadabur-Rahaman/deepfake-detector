#!/usr/bin/env python3
# backend/app/tools/test_startup_graceful_degradation.py - Test Graceful Degradation

import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_missing_modules():
    """Test that missing modules don't crash the system"""
    print("[TEST] Testing graceful degradation with missing modules...")
    
    try:
        # Test model availability
        from services.model_availability import initialize_model_availability, get_availability_status
        print("[OK] Model availability module imported successfully")
        
        # Test model loader
        from services.model_loader import load_all_models, get_startup_summary
        print("[OK] Model loader module imported successfully")
        
        # Test spatial analysis
        from services.spatial_analysis import get_resnet50_detector, get_vit_analyzer, get_availability_status as spatial_status
        print("[OK] Spatial analysis module imported successfully")
        
        # Test temporal analysis
        from services.temporal_analysis import get_vivit_detector, get_lstm_detector, get_availability_status as temporal_status
        print("[OK] Temporal analysis module imported successfully")
        
        # Initialize availability
        print("\n🔍 Checking model availability...")
        availability = initialize_model_availability()
        print(f"Availability status: {availability}")
        
        # Load models
        print("\n[LOADING] Loading all models...")
        model_results = load_all_models()
        
        # Get startup summary
        print("\n[DATA] Getting startup summary...")
        summary = get_startup_summary()
        
        print(f"\n[OK] Successfully loaded models: {summary['successful_models']}")
        print(f"[WARNING] Failed to load models: {summary['failed_models']}")
        print(f"[FIX] Missing dependencies: {summary['missing_dependencies']}")
        print(f"🎯 Ensemble ready: {summary['ensemble_models']}")
        
        # Test individual model availability
        print("\n🔍 Testing individual model availability...")
        
        # Test ResNet50
        resnet50 = get_resnet50_detector()
        if resnet50:
            print("[OK] ResNet50 detector available")
        else:
            print("[WARNING] ResNet50 detector not available (expected if torchvision missing)")
        
        # Test ViT
        vit = get_vit_analyzer()
        if vit:
            print("[OK] ViT analyzer available")
        else:
            print("[WARNING] ViT analyzer not available (expected if vit-pytorch missing)")
        
        # Test ViViT
        vivit = get_vivit_detector()
        if vivit:
            print("[OK] ViViT detector available")
        else:
            print("[WARNING] ViViT detector not available (expected if vit-pytorch missing)")
        
        # Test LSTM
        lstm = get_lstm_detector()
        if lstm:
            print("[OK] LSTM detector available")
        else:
            print("[WARNING] LSTM detector not available (unexpected - LSTM should be available)")
        
        print("\n[OK] All tests completed successfully - no crashes!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ensemble_initialization():
    """Test that ensemble initializes with available models only"""
    print("\n[TEST] Testing ensemble initialization...")
    
    try:
        from services.deterministic_ensemble_detector import DeterministicEnsembleDetector
        from services.model_loader import load_all_models
        
        # Load models first
        load_all_models()
        
        # Initialize ensemble
        detector = DeterministicEnsembleDetector()
        
        # Test model initialization
        import asyncio
        async def test_init():
            success = await detector.initialize_models()
            if success:
                print(f"[OK] Ensemble initialized with {len(detector.models)} models: {list(detector.models.keys())}")
                return True
            else:
                print("[ERROR] Ensemble initialization failed")
                return False
        
        result = asyncio.run(test_init())
        return result
        
    except Exception as e:
        print(f"[ERROR] Ensemble test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("[START] Testing Graceful Degradation for Model Loading")
    print("=" * 60)
    
    # Test 1: Missing modules don't crash
    test1_passed = test_missing_modules()
    
    # Test 2: Ensemble initializes with available models
    test2_passed = test_ensemble_initialization()
    
    # Summary
    print("\n" + "=" * 60)
    print("[DATA] TEST SUMMARY")
    print("=" * 60)
    
    if test1_passed:
        print("[OK] Test 1: Missing modules handled gracefully - PASSED")
    else:
        print("[ERROR] Test 1: Missing modules handled gracefully - FAILED")
    
    if test2_passed:
        print("[OK] Test 2: Ensemble initialization - PASSED")
    else:
        print("[ERROR] Test 2: Ensemble initialization - FAILED")
    
    if test1_passed and test2_passed:
        print("\n[COMPLETE] All tests passed! System handles missing modules gracefully.")
        return 0
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
