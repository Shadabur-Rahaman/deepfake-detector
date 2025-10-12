#!/bin/bash

# Fix CUDA Installation for Ubuntu 24.04
# This script fixes the CUDA installation issue in the main script

set -e  # Exit on any error

echo "🔧 Fixing CUDA Installation for Ubuntu 24.04"
echo "============================================="

# Check if NVIDIA GPU is available
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected. Installing CUDA dependencies..."
    
    # Update package lists
    echo "📦 Updating package lists..."
    sudo apt update
    
    # Install CUDA toolkit using the correct package name
    echo "🎮 Installing CUDA toolkit..."
    sudo apt install -y nvidia-cuda-toolkit
    
    # Install cuDNN (if the repository is available)
    echo "🧠 Installing cuDNN..."
    if [ -f "cudnn-local-repo-ubuntu2404-9.11.0_1.0-1_amd64.deb" ]; then
        sudo dpkg -i cudnn-local-repo-ubuntu2404-9.11.0_1.0-1_amd64.deb
        sudo apt update
        sudo apt install -y libcudnn9 libcudnn9-dev
    else
        echo "ℹ️ cuDNN package not found. Installing from repository..."
        # Try to install cuDNN from the repository
        sudo apt install -y libcudnn9 libcudnn9-dev || echo "⚠️ cuDNN installation failed, continuing without it"
    fi
    
    # Verify CUDA installation
    echo "✅ Verifying CUDA installation..."
    if command -v nvcc &> /dev/null; then
        nvcc --version
        echo "✅ CUDA toolkit installed successfully"
    else
        echo "⚠️ CUDA toolkit installation may have failed"
    fi
    
    # Check NVIDIA driver
    echo "🔍 Checking NVIDIA driver..."
    nvidia-smi
    
else
    echo "ℹ️ No NVIDIA GPU detected. Skipping CUDA installation."
fi

echo ""
echo "🎉 CUDA installation fix completed!"
echo "============================================="
echo "Next steps:"
echo "1. Activate your virtual environment: source deepfake-env/bin/activate"
echo "2. Install PyTorch with CUDA support:"
echo "   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124"
echo "3. Test CUDA availability: python -c 'import torch; print(torch.cuda.is_available())'"
echo "============================================="
