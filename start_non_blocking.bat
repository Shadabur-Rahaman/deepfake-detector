@echo off
REM Non-Blocking Deepfake Detection System Startup for Windows
REM ==========================================================

echo 🚀 Starting Deepfake Detection System (Non-Blocking)...
echo 📊 Server will start immediately, models load in background
echo 🌐 Server URL: http://127.0.0.1:8000
echo 📚 API Docs: http://127.0.0.1:8000/docs
echo 🔍 Health Check: http://127.0.0.1:8000/health
echo ==========================================================

python start_non_blocking.py

pause
