# Emergency startup script for Windows PowerShell
Write-Host "🚨 EMERGENCY STARTUP - ALL MODELS DISABLED" -ForegroundColor Red
Write-Host ""
Write-Host "This will start the app with ALL model loading disabled to prevent hanging" -ForegroundColor Yellow
Write-Host ""

# Kill existing processes
Write-Host "🔧 Killing any existing processes on port 8000..." -ForegroundColor Cyan
try {
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
    Write-Host "✅ Processes killed" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not kill processes (they might not be running)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting emergency mode..." -ForegroundColor Cyan
Write-Host "ℹ️  All models are disabled - app will start quickly but detection won't work" -ForegroundColor Yellow

# Set environment variables
$env:DISABLE_ENSEMBLE_LOADING = "1"
$env:DISABLE_YOLO_LOADING = "1"
$env:DISABLE_CUSTOM_MODEL_LOADING = "1"
$env:DISABLE_EFFICIENTNET_LOADING = "1"
$env:FAST_STARTUP = "1"
$env:MINIMAL_STARTUP = "1"
$env:EMERGENCY_MODE = "1"

Write-Host ""
Write-Host "✅ Environment variables set for emergency mode" -ForegroundColor Green
Write-Host "🚀 Starting app..." -ForegroundColor Cyan

try {
    python start_app_emergency.py
} catch {
    Write-Host ""
    Write-Host "⚠️ Emergency startup failed, trying minimal mode..." -ForegroundColor Yellow
    try {
        python start_app_minimal.py
    } catch {
        Write-Host "❌ All startup methods failed" -ForegroundColor Red
        Write-Host "Please check the error messages above" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "✅ Emergency startup complete!" -ForegroundColor Green
Write-Host "ℹ️  The app should now be running at http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "ℹ️  Note: Detection features are disabled in emergency mode" -ForegroundColor Yellow
