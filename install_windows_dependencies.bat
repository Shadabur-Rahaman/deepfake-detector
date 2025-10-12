@echo off
REM Install Windows Dependencies for Modern AI Deepfake Detection System
REM This script installs all required dependencies for the modern AI detection mode

echo 🚀 Installing Windows Dependencies for Modern AI Deepfake Detection System
echo ==================================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment
echo 🐍 Creating Python virtual environment...
python -m venv deepfake-env
call deepfake-env\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📚 Installing Python dependencies...

REM Core ML dependencies
echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Computer Vision
echo Installing OpenCV and image processing libraries...
pip install opencv-python==4.8.1.78
pip install opencv-contrib-python==4.8.1.78
pip install Pillow==10.0.1
pip install scikit-image==0.21.0

REM Deep Learning frameworks
echo Installing TensorFlow and Transformers...
pip install tensorflow==2.13.0
pip install transformers==4.35.0
pip install timm==0.9.12
pip install efficientnet-pytorch==0.7.1

REM Data processing
echo Installing data processing libraries...
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scipy==1.11.3

REM Web framework
echo Installing FastAPI and web dependencies...
pip install fastapi==0.104.0
pip install uvicorn==0.24.0
pip install python-multipart==0.0.6
pip install websockets==12.0

REM Database
echo Installing database dependencies...
pip install sqlalchemy==2.0.23
pip install alembic==1.12.0

REM Utilities
echo Installing utility libraries...
pip install python-dotenv==1.0.0
pip install pydantic==2.5.0
pip install httpx==0.25.0
pip install aiofiles==23.2.1
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4

REM Face detection and processing
echo Installing face detection libraries...
pip install mtcnn==0.1.1
pip install facenet-pytorch==2.5.3
pip install insightface==0.7.3

REM YOLO and object detection
echo Installing YOLO and object detection...
pip install ultralytics==8.0.0
pip install yolov8==1.0.0

REM Audio processing
echo Installing audio processing libraries...
pip install librosa==0.10.1
pip install soundfile==0.12.1

REM Additional ML libraries
echo Installing additional ML libraries...
pip install scikit-learn==1.3.0
pip install xgboost==2.0.0
pip install lightgbm==4.0.0

REM Visualization
echo Installing visualization libraries...
pip install matplotlib==3.7.2
pip install seaborn==0.12.2
pip install plotly==5.17.0

REM Progress bars and logging
echo Installing progress and logging libraries...
pip install tqdm==4.66.1
pip install rich==13.7.0

REM Image processing
echo Installing image processing libraries...
pip install imageio==2.31.5
pip install imageio-ffmpeg==0.4.9

REM Video processing
echo Installing video processing libraries...
pip install moviepy==1.0.3
pip install opencv-python-headless==4.8.1.78

REM Additional utilities
echo Installing additional utilities...
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3

REM Install project-specific requirements if they exist
if exist "requirements.txt" (
    echo 📋 Installing project-specific requirements...
    pip install -r requirements.txt
)

if exist "requirements_production.txt" (
    echo 📋 Installing production requirements...
    pip install -r requirements_production.txt
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data\sample_videos" mkdir "data\sample_videos"
if not exist "data\processed_faces" mkdir "data\processed_faces"
if not exist "data\processed_faces_optimized" mkdir "data\processed_faces_optimized"
if not exist "uploads" mkdir "uploads"
if not exist "downloaded_videos" mkdir "downloaded_videos"
if not exist "results" mkdir "results"
if not exist "storage" mkdir "storage"
if not exist "ml_artifacts" mkdir "ml_artifacts"
if not exist "model_weights" mkdir "model_weights"
if not exist "free_models" mkdir "free_models"

REM Verify installation
echo ✅ Verifying installation...
python -c "import torch; import cv2; import numpy as np; import fastapi; import sqlalchemy; print('✅ Core dependencies imported successfully'); print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"

echo.
echo 🎉 Installation completed successfully!
echo ==================================================================
echo Next steps:
echo 1. Activate the virtual environment: deepfake-env\Scripts\activate
echo 2. Run the test script: python test_modern_ai_detection.py
echo 3. Start the application: python start_app.py
echo ==================================================================
pause
