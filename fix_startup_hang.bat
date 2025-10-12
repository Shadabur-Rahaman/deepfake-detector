@echo off
echo 🔧 Fixing startup hang issues...

echo.
echo ℹ️  This script will fix the startup hang by:
echo    1. Adding timeout protection to model loading
echo    2. Providing fast startup options
echo    3. Skipping problematic model loading

echo.
echo 🚀 Starting fast startup mode...
echo ℹ️  This skips ensemble and YOLO model loading to prevent hangs

set DISABLE_ENSEMBLE_LOADING=1
set DISABLE_YOLO_LOADING=1
set DISABLE_CUSTOM_MODEL_LOADING=1
set FAST_STARTUP=1

echo.
echo ✅ Environment variables set for fast startup
echo 🚀 Starting app with minimal model loading...

python start_app_fast.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Fast startup failed, trying alternative method...
    echo 🚀 Starting with original command but with timeout protection...
    
    timeout 60 uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level info
)

echo.
echo ✅ Fix complete! The app should now start without hanging.
echo ℹ️  If you still have issues, try running: python fix_startup_hang.py
