#!/bin/bash

# Production-Grade Deepfake Detection Dependencies Installation Script
# This script installs all required dependencies for a comprehensive deepfake detection system

echo "🚀 Installing Production-Grade Deepfake Detection Dependencies"
echo "=============================================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y \
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
    libgl1-mesa-dri \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    libsqlite3-dev \
    libbz2-dev \
    libreadline-dev \
    libncurses-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev

# Install Python 3.11 if not present
echo "🐍 Installing Python 3.11..."
# Check if Python 3.11 is already available
if ! command -v python3.11 &> /dev/null; then
    echo "Adding deadsnakes PPA for Python 3.11..."
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-dev python3.11-venv python3.11-distutils
else
    echo "Python 3.11 is already installed"
fi

# Create virtual environment
echo "🏗️ Creating virtual environment..."
python3.11 -m venv deepfake-env
source deepfake-env/bin/activate

# Upgrade pip and install wheel
echo "⬆️ Upgrading pip and installing wheel..."
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support
echo "🔥 Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install core ML dependencies
echo "🧠 Installing core ML dependencies..."
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

# Install deep learning frameworks
echo "🤖 Installing deep learning frameworks..."
pip install \
    timm==0.9.2 \
    transformers==4.33.2 \
    accelerate==0.21.0 \
    datasets==2.14.4 \
    tokenizers==0.13.3 \
    safetensors==0.3.1 \
    huggingface-hub==0.16.4

# Install computer vision libraries
echo "👁️ Installing computer vision libraries..."
pip install \
    ultralytics==8.0.196 \
    albumentations==1.3.1 \
    imgaug==0.4.0 \
    mediapipe==0.10.3 \
    dlib==19.24.2 \
    face-recognition==1.3.0 \
    mtcnn==0.1.1 \
    retina-face==0.0.13

# Install video processing libraries
echo "🎬 Installing video processing libraries..."
pip install \
    ffmpeg-python==0.2.0 \
    moviepy==1.0.3 \
    yt-dlp==2023.7.6 \
    pafy==0.5.5 \
    youtube-dl==2021.12.17

# Install audio processing for lip-sync detection
echo "🎵 Installing audio processing libraries..."
pip install \
    librosa==0.10.1 \
    soundfile==0.12.1 \
    pyaudio==0.2.11 \
    webrtcvad==2.0.10 \
    speechrecognition==3.10.0

# Install advanced ML models
echo "🔬 Installing advanced ML models..."
pip install \
    efficientnet-pytorch==0.7.1 \
    pretrainedmodels==0.7.4 \
    torchvision==0.15.2 \
    torch-audiomentations==0.11.0 \
    torchmetrics==1.0.3 \
    pytorch-lightning==2.0.6

# Install ensemble and ensemble learning
echo "🎯 Installing ensemble learning libraries..."
pip install \
    optuna==3.2.0 \
    hyperopt==0.2.7 \
    bayesian-optimization==1.4.3 \
    scikit-optimize==0.9.0

# Install web framework and API dependencies
echo "🌐 Installing web framework dependencies..."
pip install \
    fastapi==0.101.1 \
    uvicorn[standard]==0.23.2 \
    python-multipart==0.0.6 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-dotenv==1.0.0 \
    pydantic==2.1.1 \
    pydantic-settings==2.0.2 \
    sqlalchemy==2.0.19 \
    alembic==1.11.1 \
    redis==4.6.0 \
    celery==5.3.1 \
    websockets==11.0.3

# Install database dependencies
echo "🗄️ Installing database dependencies..."
pip install \
    psycopg2-binary==2.9.7 \
    pymongo==4.4.1 \
    motor==3.2.0 \
    asyncpg==0.28.0 \
    aiosqlite==0.19.0

# Install monitoring and logging
echo "📊 Installing monitoring and logging..."
pip install \
    prometheus-client==0.17.1 \
    structlog==23.1.0 \
    loguru==0.7.0 \
    sentry-sdk[fastapi]==1.29.2

# Install testing and development tools
echo "🧪 Installing testing and development tools..."
pip install \
    pytest==7.4.0 \
    pytest-asyncio==0.21.1 \
    pytest-cov==4.1.0 \
    black==23.7.0 \
    flake8==6.0.0 \
    mypy==1.5.1 \
    pre-commit==3.3.3

# Install specific deepfake detection libraries
echo "🎭 Installing deepfake detection libraries..."
pip install \
    facexlib==0.3.0 \
    insightface==0.7.3 \
    onnxruntime==1.15.1 \
    onnx==1.14.1 \
    onnxruntime-gpu==1.15.1

# Install additional utilities
echo "🛠️ Installing additional utilities..."
pip install \
    tqdm==4.65.0 \
    rich==13.4.2 \
    typer==0.9.0 \
    click==8.1.7 \
    colorama==0.4.6 \
    termcolor==2.3.0

# Install specific model weights and checkpoints
echo "📥 Downloading model weights..."
mkdir -p ml_artifacts
cd ml_artifacts

# Download YOLOv8 face detection model
echo "📥 Downloading YOLOv8 face detection model..."
wget -O yolov8n-face.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Download EfficientNet models
echo "📥 Downloading EfficientNet models..."
wget -O efficientnet_b0.pth https://download.pytorch.org/models/efficientnet_b0_rwightman-3dd342df.pth

# Download ResNet models
echo "📥 Downloading ResNet models..."
wget -O resnet50.pth https://download.pytorch.org/models/resnet50-0676ba61.pth

# Download Vision Transformer models
echo "📥 Downloading Vision Transformer models..."
wget -O vit_base_patch16_224.pth https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-vitjx/jx_vit_base_patch16_224-80ecf9dd.pth

cd ..

# Create requirements.txt
echo "📝 Creating requirements.txt..."
pip freeze > requirements_production.txt

# Install additional system packages for CUDA
echo "🔥 Installing CUDA dependencies..."
sudo apt-get install -y \
    nvidia-cuda-toolkit \
    nvidia-cuda-dev \
    nvidia-cuda-runtime

# Set environment variables
echo "🔧 Setting environment variables..."
echo 'export CUDA_VISIBLE_DEVICES=0' >> ~/.bashrc
echo 'export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512' >> ~/.bashrc
echo 'export OMP_NUM_THREADS=4' >> ~/.bashrc

# Create startup script
echo "🚀 Creating startup script..."
cat > start_production_detection.sh << 'EOF'
#!/bin/bash
source deepfake-env/bin/activate
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export OMP_NUM_THREADS=4
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --log-level info --reload
EOF

chmod +x start_production_detection.sh

echo "✅ Installation completed successfully!"
echo "🎉 You can now run: ./start_production_detection.sh"
echo "📊 All dependencies installed for production-grade deepfake detection"
