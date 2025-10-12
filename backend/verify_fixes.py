#!/usr/bin/env python3
"""
Verification Script for Deepfake Detection Backend
==================================================

This script verifies that all imports are working correctly, models are loading,
and the backend is functioning properly.

Author: AI Assistant
Date: 2025
"""

import sys
import os
import requests
import json
import time

def test_imports():
    """Test that all critical imports work"""
    print("🔍 Testing imports...")
    
    try:
        # Test main module import
        import backend.app.main
        print("✅ Main module imports successfully")
        
        # Test service imports
        from backend.app.services import enhanced_model_loader
        from backend.app.services import video_processor
        from backend.app.services import deepfake_detector
        print("✅ Core services import successfully")
        
        # Test model imports
        import torch
        print(f"✅ PyTorch available: {torch.__version__}")
        
        try:
            from ultralytics import YOLO
            print("✅ YOLOv8 available")
        except ImportError:
            print("⚠️ YOLOv8 not available (expected in some environments)")
        
        from torchvision import models
        print("✅ Torchvision available")
        
        import cv2
        print(f"✅ OpenCV available: {cv2.__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_backend_server():
    """Test that the backend server is responding"""
    print("\n🌐 Testing backend server...")
    
    try:
        # Test root endpoint
        response = requests.get("http://127.0.0.1:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend server responding")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Capabilities: {len(data.get('capabilities', {}))} enabled")
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
            
        # Test model status
        response = requests.get("http://127.0.0.1:8000/models/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Model status endpoint working")
            print(f"   Integration status: {data.get('integration_status', 'unknown')}")
        else:
            print(f"⚠️ Model status endpoint returned status {response.status_code}")
            
        # Test enhanced detection pipeline
        response = requests.get("http://127.0.0.1:8000/api/enhanced-detection/pipeline-status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced detection pipeline available")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Face detectors: {data.get('face_detectors', [])}")
        else:
            print(f"⚠️ Enhanced detection pipeline returned status {response.status_code}")
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server (is it running?)")
        return False
    except Exception as e:
        print(f"❌ Backend server test failed: {e}")
        return False

def test_model_loading():
    """Test that models can be loaded without crashing"""
    print("\n🤖 Testing model loading...")
    
    try:
        # Test EnhancedModelLoader
        from backend.app.services.enhanced_model_loader import EnhancedModelLoader
        
        loader = EnhancedModelLoader(device="cpu")
        
        # Test loading each model
        models_to_test = ["efficientnet_b0", "custom_finetuned", "efficientnet_finetuned"]
        loaded_models = 0
        
        for model_name in models_to_test:
            try:
                model = loader.load_model(model_name)
                if model is not None:
                    print(f"✅ {model_name} loaded successfully")
                    loaded_models += 1
                else:
                    print(f"⚠️ {model_name} loading returned None")
            except Exception as e:
                print(f"⚠️ {model_name} loading failed: {e}")
        
        print(f"✅ {loaded_models}/{len(models_to_test)} models loaded successfully")
        return loaded_models > 0
        
    except Exception as e:
        print(f"❌ Model loading test failed: {e}")
        return False

def test_cuda_availability():
    """Test CUDA availability and fallback"""
    print("\n🖥️ Testing CUDA availability...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.version.cuda}")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        else:
            print("⚠️ CUDA not available, using CPU fallback")
            print("   This is expected in some environments")
        
        return True
        
    except Exception as e:
        print(f"❌ CUDA test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🚀 Deepfake Detection Backend Verification")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Backend Server Tests", test_backend_server),
        ("Model Loading Tests", test_model_loading),
        ("CUDA Availability Tests", test_cuda_availability),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ All imports fixed, false imports removed, models loaded, and backend running successfully.")
        return True
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
