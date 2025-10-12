#!/bin/bash
# Deepfake Detector Environment Fix Script for WSL
# Fixes missing dependencies and optimizes CUDA setup

echo "🔧 Fixing Deepfake Detector Environment..."

# Update pip and install wheel for better package compilation
echo "📦 Updating pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install critical missing packages
echo "🚀 Installing critical packages..."
pip install ultralytics==8.0.196
pip install timm>=0.9.12
pip install pretrainedmodels>=0.7.4

# Install system monitoring packages
echo "📊 Installing system monitoring packages..."
pip install psutil>=5.9.0
pip install py-cpuinfo>=9.0.0
pip install GPUtil>=1.4.0

# Install caching and optimization packages
echo "⚡ Installing caching and optimization packages..."
pip install redis>=5.0.0
pip install diskcache>=5.6.0
pip install joblib>=1.3.0

# Install acceleration packages
echo "🚀 Installing acceleration packages..."
pip install accelerate>=0.24.0
pip install optimum>=1.14.0

# Update PyTorch for better CUDA support
echo "🔥 Updating PyTorch for CUDA 12.1 support..."
pip uninstall torch torchvision torchaudio -y
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

# Install additional ML packages that might be missing
echo "🧠 Installing additional ML packages..."
pip install transformers>=4.35.0
pip install diffusers>=0.21.0
pip install datasets>=2.14.0

echo "✅ Verification..."
python -c "
import torch
import ultralytics
import timm
import psutil
import GPUtil
import redis
import diskcache
import joblib

print('✅ All packages installed successfully!')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA Version: {torch.version.cuda}')
    print(f'GPU Count: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        print(f'GPU {i}: {torch.cuda.get_device_name(i)}')

print(f'Ultralytics: {ultralytics.__version__}')
print(f'timm models available: {len(timm.list_models())}')
print(f'psutil: {psutil.__version__}')

# Test GPU monitoring
try:
    gpus = GPUtil.getGPUs()
    print(f'GPUtil detected {len(gpus)} GPU(s)')
except:
    print('GPUtil GPU detection: Not available')

print('🎉 Environment setup complete!')
"

echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Test YOLOv8: python -c \"from ultralytics import YOLO; print('YOLOv8 working!')\""
echo "2. Check CUDA: python -c \"import torch; print(f'CUDA: {torch.cuda.is_available()}')\""
echo "3. Verify timm: python -c \"import timm; print(f'Models: {len(timm.list_models())}')\""
echo "4. Start your deepfake detector backend"
echo ""
echo "🚀 Your environment is now optimized for deepfake detection!"
