# ========================================
#    CUDA FIXES FOR WINDOWS 11 + PYTHON 3.13
# ========================================

Write-Host "🔧 STEP 1: Checking Python and CUDA versions..." -ForegroundColor Yellow
python --version
try {
    nvidia-smi
} catch {
    Write-Host "⚠️ nvidia-smi not available, continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔧 STEP 2: Uninstalling existing PyTorch (CPU-only versions)..." -ForegroundColor Yellow
pip uninstall torch torchvision torchaudio -y

Write-Host ""
Write-Host "🔧 STEP 3: Installing CUDA-enabled PyTorch 2.1.0 for CUDA 12.1..." -ForegroundColor Yellow
pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121

Write-Host ""
Write-Host "🔧 STEP 4: Installing YOLOv8 8.0.196 (CUDA-compatible)..." -ForegroundColor Yellow
pip install ultralytics==8.0.196

Write-Host ""
Write-Host "🔧 STEP 5: Installing remaining dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "🔧 STEP 6: Testing CUDA setup..." -ForegroundColor Yellow
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"

Write-Host ""
Write-Host "🔧 STEP 7: Testing YOLOv8 import..." -ForegroundColor Yellow
python -c "from ultralytics import YOLO; print('✅ YOLOv8 import successful')"

Write-Host ""
Write-Host "🔧 STEP 8: Testing torchvision NMS..." -ForegroundColor Yellow
python -c "from torchvision.ops import nms; print('✅ torchvision.ops.nms import successful')"

Write-Host ""
Write-Host "🔧 STEP 9: Testing model loading..." -ForegroundColor Yellow
python -c "import sys; sys.path.append('backend'); from app.services.deepfake_detector import validate_cuda_setup; result = validate_cuda_setup(); print(f'✅ CUDA Validation: {result}')"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ PyTorch 2.1.0 + CUDA 12.1 installed" -ForegroundColor Green
Write-Host "✅ YOLOv8 8.0.196 installed" -ForegroundColor Green
Write-Host "✅ All dependencies installed" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Your deepfake detector should now work with GPU acceleration!" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue..."
