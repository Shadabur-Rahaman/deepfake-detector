@echo off
echo ========================================
echo Deepfake Detection System Setup
echo ========================================
echo.
echo This script will install all dependencies and configure your system.
echo.
echo Press any key to continue...
pause >nul

echo.
echo Installing dependencies and setting up models...
python setup_complete_system.py

echo.
echo Setup completed! Check the output above for any issues.
echo.
echo Next steps:
echo 1. Set your OpenAI API key in the .env file
echo 2. Run: python backend/app/main.py
echo 3. Check the logs for model availability
echo.
pause
