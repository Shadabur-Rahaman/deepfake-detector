@echo off
echo ========================================
echo Installing OpenCV Fixes for Deepfake Detector
echo ========================================
echo.

echo Step 1: Uninstalling conflicting packages...
pip uninstall torch torchvision torchaudio -y
pip uninstall opencv-python opencv-python-headless -y

echo.
echo Step 2: Installing core packages to fixed versions...
pip install --upgrade --force-reinstall numpy==1.26.4
pip install --upgrade --force-reinstall opencv-python==4.9.0.80
pip install --upgrade --force-reinstall opencv-python-headless==4.9.0.80

echo.
echo Step 3: Installing PyTorch with CUDA 12.1 support (COMPATIBLE VERSIONS)...
pip install --upgrade --force-reinstall torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

echo.
echo Step 4: Installing additional dependencies...
pip install --upgrade --force-reinstall scikit-learn==1.3.2 scipy==1.11.4 matplotlib==3.8.2 pillow==10.1.0

echo.
echo Step 5: Installing face detection packages...
pip install --upgrade --force-reinstall ultralytics==8.0.196 mtcnn==0.1.1

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To test the fixes, run:
echo   python test_opencv_fixes.py
echo.
echo For more information, see:
echo   OPENCV_FIXES_README.md
echo.
pause
