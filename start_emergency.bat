@echo off
echo 🚨 EMERGENCY STARTUP - ALL MODELS DISABLED
echo.
echo This will start the app with ALL model loading disabled to prevent hanging
echo.

echo 🔧 Killing any existing processes on port 8000...
netstat -ano | findstr :8000
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 🚀 Starting emergency mode...
echo ℹ️  All models are disabled - app will start quickly but detection won't work

set DISABLE_ENSEMBLE_LOADING=1
set DISABLE_YOLO_LOADING=1
set DISABLE_CUSTOM_MODEL_LOADING=1
set DISABLE_EFFICIENTNET_LOADING=1
set FAST_STARTUP=1
set MINIMAL_STARTUP=1
set EMERGENCY_MODE=1

echo.
echo ✅ Environment variables set for emergency mode
echo 🚀 Starting app...

python start_app_emergency.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Emergency startup failed, trying minimal mode...
    python start_app_minimal.py
)

echo.
echo ✅ Emergency startup complete!
echo ℹ️  The app should now be running at http://127.0.0.1:8000
echo ℹ️  Note: Detection features are disabled in emergency mode
