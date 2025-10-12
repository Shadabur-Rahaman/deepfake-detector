@echo off
echo Starting Deepfake Detection Backend for WSL/Conda...
echo.
echo This script starts the backend with proper network binding for WSL/Conda setup.
echo The backend will be accessible from Windows frontend.
echo.

REM Activate conda environment (adjust environment name if needed)
call conda activate deepfake-env

REM Start backend with proper host binding
echo Starting backend on 0.0.0.0:8000...
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Backend started! 
echo Frontend should connect to: http://0.0.0.0:8000/api
echo WebSocket should connect to: ws://0.0.0.0:8000/api/ws/admin
echo.
echo To get your WSL IP for frontend .env file, run: wsl hostname -I
pause
