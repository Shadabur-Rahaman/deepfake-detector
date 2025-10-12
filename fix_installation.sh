#!/bin/bash

echo "🔧 Fixing Installation Issues for Ubuntu 24.04"
echo "=============================================="

# Check if we're in the virtual environment
if [[ "$VIRTUAL_ENV" != *"deepfake-env"* ]]; then
    echo "⚠️  Activating virtual environment..."
    source deepfake-env/bin/activate
fi

echo "📦 Installing missing system packages..."
sudo apt-get install -y \
    libgl1-mesa-dri \
    libncurses-dev \
    software-properties-common

echo "🐍 Adding deadsnakes PPA for Python 3.11..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

echo "🐍 Installing Python 3.11..."
sudo apt-get install -y python3.11 python3.11-dev python3.11-venv python3.11-distutils

echo "⬆️ Upgrading pip and installing wheel..."
pip install --upgrade pip setuptools wheel

echo "🧠 Continuing with ML dependencies installation..."
pip install \
    numpy==1.24.3 \
    scipy==1.11.1 \
    scikit-learn==1.3.0 \
    pandas==2.0.3 \
    matplotlib==3.7.2 \
    seaborn==0.12.2 \
    plotly==5.15.0 \
    opencv-python==4.8.0.76 \
    opencv-contrib-python==4.8.0.76 \
    pillow==10.0.0 \
    imageio==2.31.3 \
    imageio-ffmpeg==0.4.9

echo "✅ Fix completed! You can now continue with the main installation script."
