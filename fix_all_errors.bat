@echo off
echo ========================================
echo 🚀 ULTIMATE ERROR KILLER - WINDOWS
echo ========================================
echo.

echo 🔧 Installing Python 3.13 compatible dependencies...
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn[standard] python-multipart aiofiles
python -m pip install opencv-python pillow numpy
python -m pip install torch torchvision tensorflow scikit-learn
python -m pip install mtcnn transformers timm google-generativeai openai

echo.
echo 🧪 Testing imports...
python test_imports_fixed.py

echo.
echo 🎉 All errors should now be fixed!
echo 🚀 You can run your application now.
echo.
pause
