@echo off
echo ============================================================
echo 🚀 DEEPFAKE DETECTION SYSTEM - FIXED VERSION
echo ============================================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Conda not found in PATH
    echo Please ensure conda is installed and added to PATH
    pause
    exit /b 1
)

REM Activate conda environment
echo 🔧 Activating conda environment...
call conda activate deepfake-env
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate conda environment 'deepfake-env'
    echo Please create the environment first:
    echo   conda create -n deepfake-env python=3.11
    echo   conda activate deepfake-env
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run the fixed application
echo 🚀 Starting fixed application...
python start_fixed_app.py

REM Check if the application started successfully
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Application failed to start
    echo Check the logs for details:
    echo - app_startup.log
    echo - Check console output above
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Application started successfully!
echo Access the application at: http://127.0.0.1:8000
echo API documentation: http://127.0.0.1:8000/docs
echo.
pause
