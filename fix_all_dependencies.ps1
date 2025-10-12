# PowerShell script to COMPLETELY FIX all dependency issues
Write-Host "========================================" -ForegroundColor Green
Write-Host "COMPLETE DEPENDENCY FIX FOR DEEPFAKE DETECTOR" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: COMPLETE CLEANUP - Removing ALL conflicting packages..." -ForegroundColor Red
Write-Host ""
pip uninstall torch torchvision torchaudio -y
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y
pip uninstall numpy -y
pip uninstall ultralytics mtcnn albumentations imgaug torchmetrics -y
pip uninstall scikit-learn scipy matplotlib pillow -y

Write-Host ""
Write-Host "Step 2: Installing COMPATIBLE numpy version..." -ForegroundColor Yellow
pip install numpy==1.26.4

Write-Host ""
Write-Host "Step 3: Installing OpenCV packages..." -ForegroundColor Yellow
pip install opencv-python==4.9.0.80
pip install opencv-python-headless==4.9.0.80

Write-Host ""
Write-Host "Step 4: Installing PyTorch with CUDA 12.1 support..." -ForegroundColor Yellow
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

Write-Host ""
Write-Host "Step 5: Installing ML dependencies..." -ForegroundColor Yellow
pip install scikit-learn==1.3.2
pip install scipy==1.11.4
pip install matplotlib==3.8.2
pip install pillow==10.1.0

Write-Host ""
Write-Host "Step 6: Installing face detection packages..." -ForegroundColor Yellow
pip install ultralytics==8.0.196
pip install mtcnn==0.1.1

Write-Host ""
Write-Host "Step 7: Installing additional packages..." -ForegroundColor Yellow
pip install albumentations==2.0.8
pip install imgaug==0.4.0
pip install torchmetrics==1.8.1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To verify the fixes, run:" -ForegroundColor Cyan
Write-Host "  python test_simple_opencv.py" -ForegroundColor White
Write-Host ""
Write-Host "If successful, then run:" -ForegroundColor Cyan
Write-Host "  python test_opencv_fixes.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue..."
