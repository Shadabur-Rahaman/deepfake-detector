#!/usr/bin/env python3
"""
Installation Verification Script
Checks that all dependencies are properly installed and compatible
"""

import sys
import importlib
import subprocess

def check_package(package_name, expected_version=None, min_version=None):
    """Check if a package is installed and optionally verify version"""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, '__version__', 'Unknown')
        
        if expected_version:
            if version == expected_version:
                print(f"✅ {package_name}: {version} (Expected: {expected_version})")
                return True
            else:
                print(f"❌ {package_name}: {version} (Expected: {expected_version})")
                return False
        elif min_version:
            # Simple version comparison (works for most cases)
            if version >= min_version:
                print(f"✅ {package_name}: {version} (Min: {min_version})")
                return True
            else:
                print(f"❌ {package_name}: {version} (Min: {min_version})")
                return False
        else:
            print(f"✅ {package_name}: {version}")
            return True
            
    except ImportError:
        print(f"❌ {package_name}: NOT INSTALLED")
        return False

def check_cuda_availability():
    """Check if CUDA is available in PyTorch"""
    try:
        import torch
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            device_name = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "Unknown"
            print(f"✅ CUDA: Available (Version: {cuda_version}, Device: {device_name})")
            return True
        else:
            print("❌ CUDA: Not available")
            return False
    except ImportError:
        print("❌ CUDA: PyTorch not installed")
        return False

def check_opencv_functionality():
    """Check if OpenCV is working correctly"""
    try:
        import cv2
        import numpy as np
        
        # Test basic functionality
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        resized = cv2.resize(test_img, (50, 50))
        
        if resized.shape == (50, 50, 3):
            print("✅ OpenCV: Basic functionality working")
            return True
        else:
            print("❌ OpenCV: Basic functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ OpenCV: Error - {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 VERIFYING DEPENDENCY INSTALLATION")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 0
    
    # Check core packages
    print("\n📦 Core Packages:")
    print("-" * 30)
    
    total_checks += 1
    if check_package("numpy", "1.26.4"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("cv2"):
        checks_passed += 1
    
    # Check PyTorch stack
    print("\n🔥 PyTorch Stack:")
    print("-" * 30)
    
    total_checks += 1
    if check_package("torch", "2.1.2+cu121"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("torchvision", "0.16.2+cu121"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("torchaudio", "2.1.2+cu121"):
        checks_passed += 1
    
    # Check ML packages
    print("\n🤖 ML Packages:")
    print("-" * 30)
    
    total_checks += 1
    if check_package("sklearn", "1.3.2"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("scipy", "1.11.4"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("matplotlib", "3.8.2"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("PIL"):
        checks_passed += 1
    
    # Check face detection packages
    print("\n👤 Face Detection:")
    print("-" * 30)
    
    total_checks += 1
    if check_package("ultralytics", "8.0.196"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("mtcnn", "0.1.1"):
        checks_passed += 1
    
    # Check additional packages
    print("\n🔧 Additional Packages:")
    print("-" * 30)
    
    total_checks += 1
    if check_package("albumentations", "2.0.8"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("imgaug", "0.4.0"):
        checks_passed += 1
    
    total_checks += 1
    if check_package("torchmetrics", "1.8.1"):
        checks_passed += 1
    
    # Check functionality
    print("\n⚡ Functionality Tests:")
    print("-" * 30)
    
    total_checks += 1
    if check_cuda_availability():
        checks_passed += 1
    
    total_checks += 1
    if check_opencv_functionality():
        checks_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION SUMMARY: {checks_passed}/{total_checks} checks passed")
    print("=" * 50)
    
    if checks_passed == total_checks:
        print("🎉 ALL DEPENDENCIES ARE PROPERLY INSTALLED!")
        print("\n✅ Your deepfake detector should now work without errors.")
        print("✅ You can run the test scripts:")
        print("   python test_simple_opencv.py")
        print("   python test_opencv_fixes.py")
        return True
    else:
        print(f"⚠️ {total_checks - checks_passed} checks failed.")
        print("\n🔧 To fix the issues:")
        print("1. Run: fix_all_dependencies.bat")
        print("2. Or follow the manual steps in: MANUAL_FIX_STEPS.md")
        print("3. Then run this verification script again")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n🚨 TROUBLESHOOTING:")
        print("• Check that you're in the correct virtual environment")
        print("• Ensure you have administrator privileges")
        print("• Try clearing pip cache: pip cache purge")
        print("• Check your Python version (should be 3.10)")
    
    input("\nPress Enter to continue...")
