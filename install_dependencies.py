#!/usr/bin/env python3
"""
Dependency Installation Script for Deepfake Detector
Fixes missing packages and import errors
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 Installing missing dependencies for Deepfake Detector...")
    
    # Core dependencies that are likely missing
    packages = [
        "transformers",
        "google-generativeai", 
        "pillow",
        "scikit-learn",
        "tensorflow",
        "torch",
        "torchvision"
    ]
    
    print("\n📋 Installing required packages...")
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("You can now run: uvicorn backend.app.main:app --host 127.0.0.1 --port 8000")
    else:
        print("⚠️ Some packages failed to install. Check the errors above.")
        print("You may need to install them manually or check your Python environment.")

if __name__ == "__main__":
    main()
