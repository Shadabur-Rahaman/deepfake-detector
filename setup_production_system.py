#!/usr/bin/env python3
"""
Production Deepfake Detection System Setup Script

This script sets up the complete production-grade deepfake detection system with:
- All advanced models (ResNet, LSTM, YOLOv8, MesoNet, ViT)
- Deterministic detection (no randomness)
- Real video analysis with anomaly detection
- Comprehensive error handling
- Real-time processing capabilities

Usage:
    python setup_production_system.py

Author: Senior ML Engineer
Date: 2024
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def run_command(command: str, description: str = "") -> bool:
    """Run a command and return success status"""
    try:
        logger.info(f"Running: {description or command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ Success: {description or command}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description or command}")
        logger.error(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8 or higher is required")
        return False
    
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_system_requirements():
    """Check system requirements"""
    logger.info("🔍 Checking system requirements...")
    
    # Check OS
    system = platform.system()
    logger.info(f"Operating System: {system}")
    
    # Check available memory
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        logger.info(f"Available Memory: {memory_gb:.1f} GB")
        
        if memory_gb < 4:
            logger.warning("⚠️ At least 4GB RAM recommended")
    except ImportError:
        logger.warning("⚠️ psutil not available, cannot check memory")
    
    # Check disk space
    try:
        disk_usage = psutil.disk_usage('/')
        free_gb = disk_usage.free / (1024**3)
        logger.info(f"Available Disk Space: {free_gb:.1f} GB")
        
        if free_gb < 10:
            logger.warning("⚠️ At least 10GB free space recommended")
    except:
        logger.warning("⚠️ Cannot check disk space")
    
    return True

def install_system_dependencies():
    """Install system dependencies"""
    logger.info("📦 Installing system dependencies...")
    
    system = platform.system()
    
    if system == "Linux":
        # Ubuntu/Debian
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y build-essential cmake pkg-config",
            "sudo apt-get install -y libjpeg-dev libtiff5-dev libpng-dev",
            "sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev",
            "sudo apt-get install -y libv4l-dev libxvidcore-dev libx264-dev",
            "sudo apt-get install -y libgtk-3-dev libatlas-base-dev gfortran",
            "sudo apt-get install -y wget curl git unzip",
            "sudo apt-get install -y libgl1-mesa-glx libglib2.0-0",
            "sudo apt-get install -y libsm6 libxext6 libxrender-dev",
            "sudo apt-get install -y libgomp1 libgcc-s1 libc6-dev",
            "sudo apt-get install -y libffi-dev libssl-dev libsqlite3-dev",
            "sudo apt-get install -y libbz2-dev libreadline-dev",
            "sudo apt-get install -y libncurses5-dev libncursesw5-dev",
            "sudo apt-get install -y xz-utils tk-dev libxml2-dev",
            "sudo apt-get install -y libxmlsec1-dev liblzma-dev"
        ]
        
        for command in commands:
            if not run_command(command, f"Installing system dependencies"):
                logger.warning(f"⚠️ Command failed: {command}")
    
    elif system == "Darwin":  # macOS
        commands = [
            "brew install cmake pkg-config",
            "brew install jpeg libtiff libpng",
            "brew install ffmpeg",
            "brew install gtk+3",
            "brew install wget curl git"
        ]
        
        for command in commands:
            if not run_command(command, f"Installing system dependencies"):
                logger.warning(f"⚠️ Command failed: {command}")
    
    else:
        logger.warning(f"⚠️ Unsupported operating system: {system}")
        logger.warning("Please install dependencies manually")
    
    return True

def create_virtual_environment():
    """Create virtual environment"""
    logger.info("🐍 Creating virtual environment...")
    
    if not run_command("python -m venv deepfake-env", "Creating virtual environment"):
        return False
    
    # Activate virtual environment
    if platform.system() == "Windows":
        activate_script = "deepfake-env\\Scripts\\activate"
    else:
        activate_script = "source deepfake-env/bin/activate"
    
    logger.info(f"✅ Virtual environment created. Activate with: {activate_script}")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    logger.info("📦 Installing Python dependencies...")
    
    # Upgrade pip
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install PyTorch with CUDA support
    if not run_command(
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121",
        "Installing PyTorch with CUDA support"
    ):
        logger.warning("⚠️ PyTorch installation failed, trying CPU version")
        if not run_command(
            "pip install torch torchvision torchaudio",
            "Installing PyTorch CPU version"
        ):
            return False
    
    # Install other dependencies
    dependencies = [
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        "opencv-python>=4.8.0",
        "opencv-contrib-python>=4.8.0",
        "Pillow>=10.0.0",
        "timm>=0.9.0",
        "ultralytics>=8.0.0",
        "mediapipe>=0.10.0",
        "librosa>=0.10.0",
        "fastapi>=0.101.0",
        "uvicorn[standard]>=0.23.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.1.0",
        "sqlalchemy>=2.0.0",
        "redis>=4.6.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            logger.warning(f"⚠️ Failed to install {dep}")
    
    return True

def create_directories():
    """Create necessary directories"""
    logger.info("📁 Creating directories...")
    
    directories = [
        "model_weights",
        "ml_artifacts",
        "storage/uploads",
        "storage/results",
        "logs",
        "static"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")
    
    return True

def download_model_weights():
    """Download required model weights"""
    logger.info("📥 Downloading model weights...")
    
    import urllib.request
    
    models = {
        "yolov8n.pt": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
        "efficientnet_b0.pth": "https://download.pytorch.org/models/efficientnet_b0_rwightman-3dd342df.pth",
        "resnet50.pth": "https://download.pytorch.org/models/resnet50-0676ba61.pth"
    }
    
    for model_name, url in models.items():
        model_path = f"model_weights/{model_name}"
        if not Path(model_path).exists():
            try:
                logger.info(f"Downloading {model_name}...")
                urllib.request.urlretrieve(url, model_path)
                logger.info(f"✅ Downloaded {model_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to download {model_name}: {e}")
        else:
            logger.info(f"✅ {model_name} already exists")
    
    return True

def create_startup_scripts():
    """Create startup scripts"""
    logger.info("📝 Creating startup scripts...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting Production Deepfake Detection System...
call deepfake-env\\Scripts\\activate
set PYTHONHASHSEED=42
set CUBLAS_WORKSPACE_CONFIG=:4096:8
set OMP_NUM_THREADS=4
python start_production_detection.py
pause
"""
    
    with open("start_production.bat", "w") as f:
        f.write(windows_script)
    
    # Linux/Mac shell script
    unix_script = """#!/bin/bash
echo "Starting Production Deepfake Detection System..."
source deepfake-env/bin/activate
export PYTHONHASHSEED=42
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=4
python start_production_detection.py
"""
    
    with open("start_production.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable
    if platform.system() != "Windows":
        os.chmod("start_production.sh", 0o755)
    
    logger.info("✅ Startup scripts created")
    return True

def test_installation():
    """Test the installation"""
    logger.info("🧪 Testing installation...")
    
    try:
        # Test imports
        import torch
        import cv2
        import numpy as np
        import timm
        from ultralytics import YOLO
        import librosa
        import fastapi
        
        logger.info("✅ All imports successful")
        
        # Test CUDA
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("ℹ️ CUDA not available, using CPU")
        
        # Test basic functionality
        test_tensor = torch.randn(1, 3, 224, 224)
        result = torch.nn.functional.softmax(test_tensor, dim=1)
        logger.info("✅ PyTorch operations working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Setting up Production Deepfake Detection System")
    logger.info("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        return 1
    
    # Step 2: Check system requirements
    if not check_system_requirements():
        return 1
    
    # Step 3: Install system dependencies
    if not install_system_dependencies():
        logger.warning("⚠️ Some system dependencies may not have installed correctly")
    
    # Step 4: Create virtual environment
    if not create_virtual_environment():
        logger.error("❌ Failed to create virtual environment")
        return 1
    
    # Step 5: Install Python dependencies
    if not install_python_dependencies():
        logger.error("❌ Failed to install Python dependencies")
        return 1
    
    # Step 6: Create directories
    if not create_directories():
        logger.error("❌ Failed to create directories")
        return 1
    
    # Step 7: Download model weights
    if not download_model_weights():
        logger.warning("⚠️ Some model weights may not have downloaded correctly")
    
    # Step 8: Create startup scripts
    if not create_startup_scripts():
        logger.error("❌ Failed to create startup scripts")
        return 1
    
    # Step 9: Test installation
    if not test_installation():
        logger.error("❌ Installation test failed")
        return 1
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("")
    logger.info("To start the system:")
    if platform.system() == "Windows":
        logger.info("  Windows: start_production.bat")
    else:
        logger.info("  Linux/Mac: ./start_production.sh")
    logger.info("")
    logger.info("Or manually:")
    logger.info("  source deepfake-env/bin/activate  # Linux/Mac")
    logger.info("  deepfake-env\\Scripts\\activate     # Windows")
    logger.info("  python start_production_detection.py")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
