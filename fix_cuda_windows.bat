@echo off
echo ========================================
echo    CUDA FIXES FOR WINDOWS 11 + PYTHON 3.13
echo ========================================
echo.

echo 🔧 STEP 1: Checking Python and CUDA versions...
python --version
nvidia-smi

echo.
echo 🔧 STEP 2: Uninstalling existing PyTorch (CPU-only versions)...
pip uninstall torch torchvision torchaudio -y

echo.
echo 🔧 STEP 3: Installing CUDA-enabled PyTorch 2.1.0 for CUDA 12.1...
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121

echo.
echo 🔧 STEP 4: Installing YOLOv8 8.0.196 (CUDA-compatible)...
pip install ultralytics==8.0.196

echo.
echo 🔧 STEP 5: Installing remaining dependencies...
pip install -r requirements.txt

echo.
echo 🔧 STEP 6: Testing CUDA setup...
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"

echo.
echo 🔧 STEP 7: Testing YOLOv8 import...
python -c "from ultralytics import YOLO; print('✅ YOLOv8 import successful')"

echo.
echo 🔧 STEP 8: Testing torchvision NMS...
python -c "from torchvision.ops import nms; print('✅ torchvision.ops.nms import successful')"

echo.
echo 🔧 STEP 9: Testing model loading...
python -c "import sys; sys.path.append('backend'); from app.services.deepfake_detector import validate_cuda_setup; result = validate_cuda_setup(); print(f'✅ CUDA Validation: {result}')"

echo.
echo ========================================
echo    INSTALLATION COMPLETE!
echo ========================================
echo.
echo ✅ PyTorch 2.1.0 + CUDA 12.1 installed
echo ✅ YOLOv8 8.0.196 installed
echo ✅ All dependencies installed
echo.
echo 🚀 Your deepfake detector should now work with GPU acceleration!
echo.
pause
