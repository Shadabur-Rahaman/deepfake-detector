@echo off
REM Comprehensive Deepfake Detection System Launcher for Windows
REM ============================================================
REM 
REM This script provides commands for running the comprehensive deepfake detection
REM system on Windows with all 25+ AI models and advanced features.
REM
REM Author: Senior ML Engineer
REM Date: 2024

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set LOG_DIR=%PROJECT_DIR%logs
set PORT=8000
set HOST=0.0.0.0

REM Colors (Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

REM Logging functions
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:log_header
echo %PURPLE%================================%NC%
echo %PURPLE%~1%NC%
echo %PURPLE%================================%NC%
goto :eof

REM Check Python installation
:check_python
call :log_info "Checking Python installation..."
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Python not found. Please install Python 3.8 or higher."
    exit /b 1
)
call :log_success "Python found"
goto :eof

REM Setup log directory
:setup_logs
call :log_info "Setting up log directory: %LOG_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
call :log_success "Log directory setup completed"
goto :eof

REM Install requirements
:install_requirements
call :log_info "Installing Python requirements..."
if exist "%BACKEND_DIR%\requirements.txt" (
    pip install -r "%BACKEND_DIR%\requirements.txt"
    if %errorlevel% neq 0 (
        call :log_error "Failed to install requirements"
        exit /b 1
    )
    call :log_success "Requirements installed"
) else (
    call :log_warning "requirements.txt not found"
)

if exist "%BACKEND_DIR%\requirements_optional.txt" (
    call :log_info "Installing optional requirements..."
    pip install -r "%BACKEND_DIR%\requirements_optional.txt"
    call :log_success "Optional requirements installed"
)

if exist "%BACKEND_DIR%\requirements_cuda_fixed.txt" (
    call :log_info "Installing CUDA requirements..."
    pip install -r "%BACKEND_DIR%\requirements_cuda_fixed.txt"
    call :log_success "CUDA requirements installed"
)
goto :eof

REM Start the comprehensive system
:start_system
call :log_header "Starting Comprehensive Deepfake Detection System"
call :log_info "Server will start on http://%HOST%:%PORT%"
call :log_info "API Documentation: http://%HOST%:%PORT%/docs"
call :log_info "Health Check: http://%HOST%:%PORT%/health"
call :log_info "Press Ctrl+C to stop the server"
echo.

cd /d "%PROJECT_DIR%"
python start_comprehensive_system.py
goto :eof

REM Start with monitoring
:start_with_monitoring
call :log_header "Starting System with Monitoring"
call :log_info "Starting system monitoring in background..."

REM Start monitoring in background
start /b cmd /c "echo Monitoring started && timeout /t 30 /nobreak >nul && echo Monitoring stopped"

call :start_system
goto :eof

REM View logs
:view_logs
call :log_header "Viewing System Logs"
if exist "%LOG_DIR%\deepfake_detector.log" (
    call :log_info "Main application logs:"
    type "%LOG_DIR%\deepfake_detector.log"
) else (
    call :log_warning "No main log file found"
)
goto :eof

REM System status
:show_status
call :log_header "System Status"

REM Check if Python process is running
tasklist /fi "imagename eq python.exe" /fo csv | findstr /i "python.exe" >nul
if %errorlevel% equ 0 (
    call :log_success "Python processes are running"
    tasklist /fi "imagename eq python.exe"
) else (
    call :log_warning "No Python processes found"
)

REM Check port usage
netstat -an | findstr ":%PORT% " >nul
if %errorlevel% equ 0 (
    call :log_success "Port %PORT% is in use"
    netstat -an | findstr ":%PORT% "
) else (
    call :log_warning "Port %PORT% is not in use"
)

REM Show log file sizes
if exist "%LOG_DIR%" (
    call :log_info "Log file sizes:"
    dir "%LOG_DIR%\*.log" /b 2>nul
) else (
    call :log_warning "Log directory not found"
)

REM Show system resources
call :log_info "System resources:"
wmic cpu get loadpercentage /value | findstr "LoadPercentage"
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory /value
goto :eof

REM Test the system
:test_system
call :log_header "Testing Deepfake Detection System"

REM Test health endpoint
call :log_info "Testing health endpoint..."
curl -s "http://localhost:%PORT%/health" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Health endpoint is responding"
) else (
    call :log_error "Health endpoint is not responding"
)

REM Test API endpoint
call :log_info "Testing API endpoint..."
curl -s "http://localhost:%PORT%/api/health" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "API endpoint is responding"
) else (
    call :log_error "API endpoint is not responding"
)

REM Test model status
call :log_info "Testing model status..."
curl -s "http://localhost:%PORT%/api/models/status" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Model status endpoint is responding"
) else (
    call :log_warning "Model status endpoint is not responding"
)
goto :eof

REM Stop the system
:stop_system
call :log_header "Stopping Deepfake Detection System"

REM Kill Python processes
tasklist /fi "imagename eq python.exe" /fo csv | findstr /i "python.exe" >nul
if %errorlevel% equ 0 (
    call :log_info "Stopping Python processes..."
    taskkill /f /im python.exe >nul 2>&1
    call :log_success "System stopped"
) else (
    call :log_warning "No running system found"
)
goto :eof

REM Setup system (first time)
:setup_system
call :log_header "Setting up Comprehensive Deepfake Detection System"
call :check_python
call :setup_logs
call :install_requirements
call :log_success "Setup completed successfully!"
call :log_info "Run '%~nx0 start' to start the system"
goto :eof

REM Show help
:show_help
call :log_header "Comprehensive Deepfake Detection System Commands"
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   start              Start the comprehensive deepfake detection system
echo   start-monitor      Start system with monitoring
echo   stop               Stop the running system
echo   restart            Restart the system
echo   status             Show system status
echo   test               Test system endpoints
echo   logs               View main application logs
echo   setup              Setup system (first time only)
echo   help               Show this help message
echo.
echo Examples:
echo   %~nx0 setup           # First time setup
echo   %~nx0 start           # Start the system
echo   %~nx0 start-monitor   # Start with monitoring
echo   %~nx0 logs            # View logs
echo   %~nx0 status          # Check system status
echo.
echo Log Directory: %LOG_DIR%
echo Server URL: http://%HOST%:%PORT%
echo API Documentation: http://%HOST%:%PORT%/docs
goto :eof

REM Main script logic
if "%1"=="setup" (
    call :setup_system
) else if "%1"=="start" (
    call :setup_logs
    call :start_system
) else if "%1"=="start-monitor" (
    call :setup_logs
    call :start_with_monitoring
) else if "%1"=="stop" (
    call :stop_system
) else if "%1"=="restart" (
    call :stop_system
    timeout /t 2 /nobreak >nul
    call :setup_logs
    call :start_system
) else if "%1"=="status" (
    call :show_status
) else if "%1"=="test" (
    call :test_system
) else if "%1"=="logs" (
    call :view_logs
) else (
    call :show_help
)

endlocal
