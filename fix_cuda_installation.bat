@echo off
echo 🔧 Fixing PyTorch CUDA Installation...
echo.

echo 📦 Uninstalling current PyTorch CPU version...
pip uninstall torch torchvision torchaudio -y

echo.
echo 🚀 Installing PyTorch 2.1.0 with CUDA 12.1 support...
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu121

echo.
echo ✅ PyTorch CUDA installation complete!
echo.
echo 🔍 Verifying installation...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.device('cuda' if torch.cuda.is_available() else 'cpu'))"

echo.
echo 🎯 Next: Run the model loading test
pause
