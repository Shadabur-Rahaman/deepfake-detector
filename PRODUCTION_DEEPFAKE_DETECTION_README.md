# Production-Grade Deepfake Detection System

A comprehensive, production-ready deepfake detection system that eliminates randomness and provides deterministic results for real video analysis.

## 🎯 Key Features

- **100% Deterministic Results**: Same input always produces same output
- **Real Video Optimized**: Advanced anomaly detection for real videos
- **Advanced Model Ensemble**: ResNet, LSTM, YOLOv8, MesoNet, Vision Transformers
- **Lip-Sync Analysis**: Audio-video correlation detection
- **Facial Anomaly Detection**: Geometry, texture, lighting consistency
- **Temporal Analysis**: Frame-to-frame consistency checks
- **Production-Grade**: Comprehensive error handling and monitoring

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd deepfake-detector

# Run automated setup
python setup_production_system.py

# Start the system
# Windows:
start_production.bat

# Linux/Mac:
./start_production.sh
```

### Option 2: Manual Setup

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y build-essential cmake pkg-config libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran wget curl git unzip libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgcc-s1 libc6-dev libffi-dev libssl-dev libsqlite3-dev libbz2-dev libreadline-dev libncurses5-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev liblzma-dev

# 2. Create virtual environment
python -m venv deepfake-env
source deepfake-env/bin/activate  # Linux/Mac
# deepfake-env\Scripts\activate   # Windows

# 3. Install Python dependencies
pip install --upgrade pip
pip install -r requirements_production.txt

# 4. Download model weights
python -c "
import urllib.request
import os
os.makedirs('model_weights', exist_ok=True)
urllib.request.urlretrieve('https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt', 'model_weights/yolov8n.pt')
urllib.request.urlretrieve('https://download.pytorch.org/models/efficientnet_b0_rwightman-3dd342df.pth', 'model_weights/efficientnet_b0.pth')
urllib.request.urlretrieve('https://download.pytorch.org/models/resnet50-0676ba61.pth', 'model_weights/resnet50.pth')
"

# 5. Start the system
python start_production_detection.py
```

## 📋 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **CPU**: 4 cores recommended

### Recommended Requirements
- **OS**: Linux (Ubuntu 22.04+)
- **Python**: 3.11
- **RAM**: 16GB or more
- **Storage**: 50GB free space
- **GPU**: NVIDIA GPU with CUDA support
- **CPU**: 8+ cores

## 🔧 Installation Commands

### 1. Install System Dependencies

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y build-essential cmake pkg-config libjpeg-dev libtiff5-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran wget curl git unzip libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgcc-s1 libc6-dev libffi-dev libssl-dev libsqlite3-dev libbz2-dev libreadline-dev libncurses5-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev liblzma-dev nvidia-cuda-toolkit nvidia-cuda-dev nvidia-cuda-runtime
```

#### macOS:
```bash
brew install cmake pkg-config jpeg libtiff libpng ffmpeg gtk+3 wget curl git
```

#### Windows:
```powershell
# Install Visual Studio Build Tools
# Install CUDA Toolkit from NVIDIA
# Install Git for Windows
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python -m venv deepfake-env
source deepfake-env/bin/activate  # Linux/Mac
# deepfake-env\Scripts\activate   # Windows

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install all other dependencies
pip install -r requirements_production.txt
```

### 3. Download Model Weights

```bash
# Create model weights directory
mkdir -p model_weights

# Download YOLOv8
wget -O model_weights/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Download EfficientNet
wget -O model_weights/efficientnet_b0.pth https://download.pytorch.org/models/efficientnet_b0_rwightman-3dd342df.pth

# Download ResNet50
wget -O model_weights/resnet50.pth https://download.pytorch.org/models/resnet50-0676ba61.pth

# Download Vision Transformer
wget -O model_weights/vit_base_patch16_224.pth https://github.com/rwightman/pytorch-image-models/releases/download/v0.1-vitjx/jx_vit_base_patch16_224-80ecf9dd.pth
```

## 🚀 Running the System

### Start the Production Server

```bash
# Method 1: Using startup script
python start_production_detection.py

# Method 2: Using uvicorn directly
uvicorn backend.app.main_production:app --host 0.0.0.0 --port 8000 --log-level info

# Method 3: Using the batch/shell scripts
# Windows:
start_production.bat

# Linux/Mac:
./start_production.sh
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Models Status**: http://localhost:8000/models
- **Performance Stats**: http://localhost:8000/stats

## 🔍 Detection Modes

### 1. Comprehensive Mode (Default)
Uses all available detection methods for maximum accuracy.

```python
import requests
import numpy as np

# Prepare face data
faces = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8).tolist() for _ in range(5)]

# Make detection request
response = requests.post("http://localhost:8000/detect", json={
    "faces": faces,
    "detection_mode": "comprehensive"
})

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.3f}")
```

### 2. Deterministic Mode
Uses only deterministic models for reproducible results.

```python
response = requests.post("http://localhost:8000/detect", json={
    "faces": faces,
    "detection_mode": "deterministic"
})
```

### 3. Real Video Optimized
Optimized for detecting real videos with advanced anomaly detection.

```python
response = requests.post("http://localhost:8000/detect", json={
    "faces": faces,
    "detection_mode": "real_video"
})
```

### 4. All Models Mode
Uses all available models including advanced ensemble methods.

```python
response = requests.post("http://localhost:8000/detect", json={
    "faces": faces,
    "detection_mode": "all_models"
})
```

## 📊 API Endpoints

### POST /detect
Main detection endpoint.

**Request Body:**
```json
{
    "faces": [[[224, 224, 3]]],  // List of face images as 3D arrays
    "audio_data": [0.1, 0.2, ...],  // Optional audio data for lip-sync
    "detection_mode": "comprehensive"  // Detection mode
}
```

**Response:**
```json
{
    "prediction": "Real Video",
    "confidence": 0.85,
    "processing_time": 2.3,
    "detection_methods": ["deterministic", "real_video_analysis", "advanced_ensemble"],
    "individual_results": {...},
    "anomaly_scores": {...},
    "metadata": {...},
    "success": true
}
```

### POST /detect/file
Detect deepfake from uploaded video file.

**Form Data:**
- `file`: Video file
- `detection_mode`: Detection mode (optional)

### GET /health
Health check endpoint.

### GET /models
Get list of available models.

### GET /stats
Get performance statistics.

## 🧪 Testing the System

### Test with Sample Data

```python
import requests
import numpy as np

# Test with random faces
faces = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8).tolist() for _ in range(5)]

response = requests.post("http://localhost:8000/detect", json={
    "faces": faces,
    "detection_mode": "comprehensive"
})

print(f"Status: {response.status_code}")
print(f"Result: {response.json()}")
```

### Test with Video File

```python
import requests

# Upload video file
with open("test_video.mp4", "rb") as f:
    files = {"file": f}
    data = {"detection_mode": "comprehensive"}
    response = requests.post("http://localhost:8000/detect/file", files=files, data=data)

print(f"Result: {response.json()}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Set for deterministic behavior
export PYTHONHASHSEED=42
export CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=4

# CUDA settings
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Model Configuration

Edit `backend/app/services/production_pipeline.py` to modify:
- Model weights
- Detection thresholds
- Confidence levels
- Processing parameters

## 📈 Performance Optimization

### GPU Acceleration

```bash
# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Set GPU memory allocation
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### CPU Optimization

```bash
# Set number of threads
export OMP_NUM_THREADS=4

# Enable MKL optimizations
export MKL_NUM_THREADS=4
```

### Memory Optimization

```python
# In your detection code
import torch
torch.cuda.empty_cache()  # Clear GPU memory
```

## 🐛 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```bash
   export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256
   ```

2. **Import Errors**
   ```bash
   pip install --upgrade pip
   pip install -r requirements_production.txt
   ```

3. **Model Loading Failures**
   ```bash
   # Check model weights exist
   ls -la model_weights/
   
   # Re-download if needed
   python -c "import urllib.request; urllib.request.urlretrieve('URL', 'PATH')"
   ```

4. **Performance Issues**
   ```bash
   # Check GPU usage
   nvidia-smi
   
   # Check CPU usage
   htop
   ```

### Debug Mode

```bash
# Run with debug logging
PYTHONPATH=. python -m uvicorn backend.app.main_production:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 📚 Advanced Usage

### Custom Model Integration

```python
# Add custom model to the pipeline
from backend.app.services.production_pipeline import get_production_pipeline

pipeline = get_production_pipeline()
# Add your custom model to the pipeline
```

### Batch Processing

```python
import asyncio
from backend.app.services.production_pipeline import detect_deepfake_production

async def process_batch(video_files):
    results = []
    for video_file in video_files:
        faces = extract_faces_from_video(video_file)
        result = await detect_deepfake_production(faces)
        results.append(result)
    return results

# Process multiple videos
results = asyncio.run(process_batch(video_files))
```

### Real-time Processing

```python
import cv2
from backend.app.services.production_pipeline import detect_deepfake_production

def real_time_detection(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Extract faces
        faces = extract_faces_from_frame(frame)
        
        if faces:
            # Detect deepfake
            result = asyncio.run(detect_deepfake_production(faces))
            print(f"Prediction: {result.prediction} ({result.confidence:.3f})")
        
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation at `/docs`

## 🔄 Updates

To update the system:

```bash
git pull origin main
pip install -r requirements_production.txt --upgrade
python start_production_detection.py
```

---

**Note**: This system is designed for production use and provides deterministic results. All randomness has been eliminated to ensure consistent, reliable deepfake detection.
