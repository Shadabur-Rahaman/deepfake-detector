# PowerShell script for NUCLEAR OPTION: Complete System Reset
Write-Host "========================================" -ForegroundColor Red
Write-Host "NUCLEAR OPTION: COMPLETE SYSTEM RESET" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "This will REMOVE ALL PACKAGES and reinstall only what you need." -ForegroundColor Yellow
Write-Host "Make sure you're in the correct virtual environment!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue..."

Write-Host ""
Write-Host "Step 1: NUCLEAR CLEANUP - Removing ALL packages..." -ForegroundColor Red
Write-Host ""

Write-Host "Removing PyTorch stack..." -ForegroundColor Yellow
pip uninstall torch torchvision torchaudio -y

Write-Host "Removing TensorFlow stack..." -ForegroundColor Yellow
pip uninstall tensorflow tensorflow-gpu tensorboard -y

Write-Host "Removing OpenCV packages..." -ForegroundColor Yellow
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y

Write-Host "Removing numpy..." -ForegroundColor Yellow
pip uninstall numpy -y

Write-Host "Removing ML packages..." -ForegroundColor Yellow
pip uninstall ultralytics mtcnn albumentations imgaug torchmetrics -y

Write-Host "Removing additional ML dependencies..." -ForegroundColor Yellow
pip uninstall scikit-learn scipy matplotlib pillow -y

Write-Host "Removing ALL other packages that might conflict..." -ForegroundColor Yellow
pip uninstall scikit-image face-recognition imageio librosa seaborn -y
pip uninstall albucore -y

Write-Host ""
Write-Host "Step 2: Installing ONLY essential packages with compatible versions..." -ForegroundColor Green
Write-Host ""

Write-Host "Installing numpy 1.26.4..." -ForegroundColor Cyan
pip install numpy==1.26.4

Write-Host "Installing OpenCV packages..." -ForegroundColor Cyan
pip install opencv-python==4.9.0.80
pip install opencv-python-headless==4.9.0.80

Write-Host "Installing PyTorch with CUDA 12.1 support..." -ForegroundColor Cyan
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

Write-Host "Installing core ML dependencies..." -ForegroundColor Cyan
pip install scikit-learn==1.3.2
pip install scipy==1.11.4
pip install matplotlib==3.8.2
pip install pillow==10.1.0

Write-Host "Installing face detection packages..." -ForegroundColor Cyan
pip install ultralytics==8.0.196
pip install mtcnn==0.1.1

Write-Host ""
Write-Host "Step 3: Installing additional packages ONLY if needed..." -ForegroundColor Green
Write-Host ""

Write-Host "Installing albumentations..." -ForegroundColor Cyan
pip install albumentations==2.0.8

Write-Host "Installing imgaug..." -ForegroundColor Cyan
pip install imgaug==0.4.0

Write-Host "Installing torchmetrics..." -ForegroundColor Cyan
pip install torchmetrics==1.8.1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "NUCLEAR RESET COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To verify the fixes, run:" -ForegroundColor Cyan
Write-Host "  python verify_installation.py" -ForegroundColor White
Write-Host ""
Write-Host "If successful, then run:" -ForegroundColor Cyan
Write-Host "  python test_simple_opencv.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue..."
