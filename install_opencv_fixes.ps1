# PowerShell script to install OpenCV fixes for Deepfake Detector
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installing OpenCV Fixes for Deepfake Detector" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Uninstalling conflicting packages..." -ForegroundColor Yellow
pip uninstall torch torchvision torchaudio -y
pip uninstall opencv-python opencv-python-headless -y

Write-Host ""
Write-Host "Step 2: Installing core packages to fixed versions..." -ForegroundColor Yellow
pip install --upgrade --force-reinstall numpy==1.26.4
pip install --upgrade --force-reinstall opencv-python==4.9.0.80
pip install --upgrade --force-reinstall opencv-python-headless==4.9.0.80

Write-Host ""
Write-Host "Step 3: Installing PyTorch with CUDA 12.1 support (COMPATIBLE VERSIONS)..." -ForegroundColor Yellow
pip install --upgrade --force-reinstall torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

Write-Host ""
Write-Host "Step 4: Installing additional dependencies..." -ForegroundColor Yellow
pip install --upgrade --force-reinstall scikit-learn==1.3.2 scipy==1.11.4 matplotlib==3.8.2 pillow==10.1.0

Write-Host ""
Write-Host "Step 5: Installing face detection packages..." -ForegroundColor Yellow
pip install --upgrade --force-reinstall ultralytics==8.0.196 mtcnn==0.1.1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To test the fixes, run:" -ForegroundColor Cyan
Write-Host "  python test_opencv_fixes.py" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see:" -ForegroundColor Cyan
Write-Host "  OPENCV_FIXES_README.md" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue..."
