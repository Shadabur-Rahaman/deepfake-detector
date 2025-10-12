@echo off
REM Comprehensive Auth System Repair Script for Windows + Conda
REM Fixes PostgreSQL, SQLite3, and Python binding issues

echo Starting comprehensive auth system repair...
echo This script will fix PostgreSQL, SQLite3, and Python binding issues

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: PowerShell is required but not found
    echo Please install PowerShell or run the script manually
    pause
    exit /b 1
)

REM Run the PowerShell script
echo Running PowerShell repair script...
powershell -ExecutionPolicy Bypass -File "repair_auth_system_windows.ps1" %*

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Repair completed successfully!
    echo.
    echo Next steps:
    echo 1. Activate your conda environment: conda activate deepfake-env
    echo 2. Test the fix: python -c "import sqlite3, psycopg2; print(sqlite3.sqlite_version); print('Postgres OK')"
    echo 3. Run your app: python backend\app\main_production.py
    echo.
) else (
    echo.
    echo ERROR: Repair failed with error code %errorlevel%
    echo Please check the output above for details
    echo.
)

pause
