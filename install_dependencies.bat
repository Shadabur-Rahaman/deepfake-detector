@echo off
echo 🚀 Installing missing dependencies for Deepfake Detector...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found, using system Python
)

echo.
echo 📋 Installing required packages...

REM Install core dependencies
pip install transformers
pip install google-generativeai
pip install pillow
pip install scikit-learn
pip install tensorflow
pip install torch torchvision

echo.
echo 📊 Installation complete!
echo.
echo 🎯 To run the application:
echo    uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
echo.
pause
