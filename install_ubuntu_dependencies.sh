#!/bin/bash

# Install Ubuntu Dependencies for Modern AI Deepfake Detection System
# This script installs all required dependencies for the modern AI detection mode

set -e  # Exit on any error

echo "🚀 Installing Ubuntu Dependencies for Modern AI Deepfake Detection System"
echo "=================================================================="

# Update package lists
echo "📦 Updating package lists..."
sudo apt update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    wget \
    curl \
    git \
    unzip \
    sqlite3 \
    libsqlite3-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgthread-2.0-0 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0

# Install CUDA dependencies (if NVIDIA GPU is available)
echo "🎮 Checking for NVIDIA GPU and installing CUDA dependencies..."
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Installing CUDA dependencies..."
    
    # Install CUDA toolkit
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt update
    sudo apt install -y cuda-toolkit-12-4
    
    # Install cuDNN
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cudnn-local-repo-ubuntu2404-9.11.0_1.0-1_amd64.deb
    sudo dpkg -i cudnn-local-repo-ubuntu2404-9.11.0_1.0-1_amd64.deb
    sudo apt update
    sudo apt install -y libcudnn9 libcudnn9-dev
    
    echo "✅ CUDA dependencies installed"
else
    echo "ℹ️ No NVIDIA GPU detected. Skipping CUDA installation."
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv deepfake-env
source deepfake-env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."

# Core ML dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Computer Vision
pip install opencv-python==4.8.1.78
pip install opencv-contrib-python==4.8.1.78
pip install Pillow==10.0.1
pip install scikit-image==0.21.0

# Deep Learning frameworks
pip install tensorflow==2.13.0
pip install transformers==4.35.0
pip install timm==0.9.12
pip install efficientnet-pytorch==0.7.1

# Data processing
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scipy==1.11.3

# Web framework
pip install fastapi==0.104.0
pip install uvicorn==0.24.0
pip install python-multipart==0.0.6
pip install websockets==12.0

# Database
pip install sqlalchemy==2.0.23
pip install alembic==1.12.0

# Utilities
pip install python-dotenv==1.0.0
pip install pydantic==2.5.0
pip install httpx==0.25.0
pip install aiofiles==23.2.1
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4

# Face detection and processing
pip install mtcnn==0.1.1
pip install facenet-pytorch==2.5.3
pip install insightface==0.7.3

# YOLO and object detection
pip install ultralytics==8.0.0
pip install yolov8==1.0.0

# Audio processing (for video analysis)
pip install librosa==0.10.1
pip install soundfile==0.12.1

# Additional ML libraries
pip install scikit-learn==1.3.0
pip install xgboost==2.0.0
pip install lightgbm==4.0.0

# Visualization
pip install matplotlib==3.7.2
pip install seaborn==0.12.2
pip install plotly==5.17.0

# Progress bars and logging
pip install tqdm==4.66.1
pip install rich==13.7.0

# Image processing
pip install imageio==2.31.5
pip install imageio-ffmpeg==0.4.9

# Video processing
pip install moviepy==1.0.3
pip install opencv-python-headless==4.8.1.78

# Additional utilities
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3

# Install project-specific requirements if they exist
if [ -f "requirements.txt" ]; then
    echo "📋 Installing project-specific requirements..."
    pip install -r requirements.txt
fi

if [ -f "requirements_production.txt" ]; then
    echo "📋 Installing production requirements..."
    pip install -r requirements_production.txt
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/sample_videos
mkdir -p data/processed_faces
mkdir -p data/processed_faces_optimized
mkdir -p uploads
mkdir -p downloaded_videos
mkdir -p results
mkdir -p storage
mkdir -p ml_artifacts
mkdir -p model_weights
mkdir -p free_models

# Set permissions
echo "🔐 Setting permissions..."
chmod +x test_modern_ai_detection.py
chmod +x start_app.py
chmod +x start_production_detection.py

# Verify installation
echo "✅ Verifying installation..."
python3 -c "
import torch
import cv2
import numpy as np
import fastapi
import sqlalchemy
print('✅ Core dependencies imported successfully')
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
"

echo ""
echo "🎉 Installation completed successfully!"
echo "=================================================================="
echo "Next steps:"
echo "1. Activate the virtual environment: source deepfake-env/bin/activate"
echo "2. Run the test script: python test_modern_ai_detection.py"
echo "3. Start the application: python start_app.py"
echo ""
echo "For CUDA support, make sure your NVIDIA drivers are installed:"
echo "sudo apt install nvidia-driver-535"
echo "=================================================================="
