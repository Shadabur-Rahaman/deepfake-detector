@echo off
REM Windows batch file to run the bash repair script
REM This requires WSL, Git Bash, or similar bash environment

echo Starting Auth System Repair...
echo.

REM Check if WSL is available
wsl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Using WSL to run the repair script...
    wsl bash repair_auth_system.sh
    goto :end
)

REM Check if Git Bash is available
where bash >nul 2>&1
if %errorlevel% equ 0 (
    echo Using Git Bash to run the repair script...
    bash repair_auth_system.sh
    goto :end
)

REM If neither WSL nor Git Bash is available
echo ERROR: Neither WSL nor Git Bash is available
echo.
echo Please install one of the following:
echo 1. Windows Subsystem for Linux (WSL)
echo 2. Git for Windows (includes Git Bash)
echo 3. Or run the PowerShell version: repair_auth_system_windows.ps1
echo.
pause
exit /b 1

:end
echo.
echo Repair script completed.
pause
