@echo off
echo ========================================
echo COMPLETE DEPENDENCY FIX FOR DEEPFAKE DETECTOR
echo ========================================
echo.

echo Step 1: COMPLETE CLEANUP - Removing ALL conflicting packages...
echo.
pip uninstall torch torchvision torchaudio -y
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y
pip uninstall numpy -y
pip uninstall ultralytics mtcnn albumentations imgaug torchmetrics -y
pip uninstall scikit-learn scipy matplotlib pillow -y

echo.
echo Step 2: Installing COMPATIBLE numpy version...
pip install numpy==1.26.4

echo.
echo Step 3: Installing OpenCV packages...
pip install opencv-python==4.9.0.80
pip install opencv-python-headless==4.9.0.80

echo.
echo Step 4: Installing PyTorch with CUDA 12.1 support...
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

echo.
echo Step 5: Installing ML dependencies...
pip install scikit-learn==1.3.2
pip install scipy==1.11.4
pip install matplotlib==3.8.2
pip install pillow==10.1.0

echo.
echo Step 6: Installing face detection packages...
pip install ultralytics==8.0.196
pip install mtcnn==0.1.1

echo.
echo Step 7: Installing additional packages...
pip install albumentations==2.0.8
pip install imgaug==0.4.0
pip install torchmetrics==1.8.1

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo To verify the fixes, run:
echo   python test_simple_opencv.py
echo.
echo If successful, then run:
echo   python test_opencv_fixes.py
echo.
pause
