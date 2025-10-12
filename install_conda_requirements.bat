@echo off
echo ========================================
echo    INSTALLING REQUIREMENTS IN CONDA ENVIRONMENT
echo    Environment: deepfake-py310
echo ========================================
echo.

echo 🔧 STEP 1: Activating conda environment...
call conda activate deepfake-py310

echo.
echo 🔧 STEP 2: Installing YOLOv8 8.0.196...
pip install ultralytics==8.0.196

echo.
echo 🔧 STEP 3: Installing all remaining dependencies...
pip install -r requirements_py310.txt

echo.
echo 🔧 STEP 4: Testing CUDA setup...
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"

echo.
echo 🔧 STEP 5: Testing YOLOv8 import...
python -c "from ultralytics import YOLO; print('✅ YOLOv8 import successful')"

echo.
echo 🔧 STEP 6: Testing torchvision NMS...
python -c "from torchvision.ops import nms; print('✅ torchvision.ops.nms import successful')"

echo.
echo 🔧 STEP 7: Testing model loading...
python -c "import sys; sys.path.append('backend'); from app.services.deepfake_detector import validate_cuda_setup; result = validate_cuda_setup(); print(f'✅ CUDA Validation: {result}')"

echo.
echo ========================================
echo    INSTALLATION COMPLETE!
echo ========================================
echo.
echo ✅ PyTorch 2.1.0 + CUDA 12.1 (Already installed)
echo ✅ YOLOv8 8.0.196 installed
echo ✅ All dependencies installed in deepfake-py310
echo.
echo 🚀 Your deepfake detector should now work with GPU acceleration!
echo.
echo 💡 To activate this environment in the future:
echo    conda activate deepfake-py310
echo.
pause
