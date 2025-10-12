@echo off
echo ========================================
echo SUPER NUCLEAR OPTION: ABSOLUTE CLEAN SLATE
echo ========================================
echo.
echo This will REMOVE ABSOLUTELY EVERYTHING and reinstall only what you need.
echo Make sure you're in the correct virtual environment!
echo.
echo WARNING: This is the most aggressive cleanup possible!
echo.
pause

echo.
echo Step 1: SUPER NUCLEAR CLEANUP - Removing ABSOLUTELY EVERYTHING...
echo.

echo Removing PyTorch stack...
pip uninstall torch torchvision torchaudio -y

echo Removing TensorFlow stack...
pip uninstall tensorflow tensorflow-gpu tensorboard -y

echo Removing OpenCV packages...
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y

echo Removing numpy...
pip uninstall numpy -y

echo Removing ML packages...
pip uninstall ultralytics mtcnn albumentations imgaug torchmetrics -y

echo Removing additional ML dependencies...
pip uninstall scikit-learn scipy matplotlib pillow -y

echo Removing ALL other packages that might conflict...
pip uninstall scikit-image face-recognition imageio librosa seaborn -y
pip uninstall albucore -y

echo.
echo Step 2: REMOVING ANY REMAINING PACKAGES...
echo.

echo Checking for any remaining packages...
pip list

echo.
echo If you see any packages above (besides pip, setuptools, wheel), 
echo manually remove them with: pip uninstall package_name -y
echo.
pause

echo.
echo Step 3: Installing ONLY essential packages with compatible versions...
echo.

echo Installing numpy 1.26.4...
pip install numpy==1.26.4

echo Installing OpenCV packages...
pip install opencv-python==4.9.0.80
pip install opencv-python-headless==4.9.0.80

echo Installing PyTorch with CUDA 12.1 support...
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

echo Installing core ML dependencies...
pip install scikit-learn==1.3.2
pip install scipy==1.11.4
pip install matplotlib==3.8.2
pip install pillow==10.1.0

echo Installing face detection packages...
pip install ultralytics==8.0.196
pip install mtcnn==0.1.1

echo.
echo Step 4: Installing additional packages ONLY if needed...
echo.

echo Installing albumentations...
pip install albumentations==2.0.8

echo Installing imgaug...
pip install imgaug==0.4.0

echo Installing torchmetrics...
pip install torchmetrics==1.8.1

echo.
echo ========================================
echo SUPER NUCLEAR RESET COMPLETE!
echo ========================================
echo.
echo To verify the fixes, run:
echo   python verify_installation.py
echo.
echo If successful, then run:
echo   python test_simple_opencv.py
echo.
pause
