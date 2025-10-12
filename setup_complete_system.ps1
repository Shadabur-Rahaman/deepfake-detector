# Deepfake Detection System Setup Script (PowerShell)
# Run this script as Administrator for best results

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deepfake Detection System Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip found: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please install pip first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting setup process..." -ForegroundColor Yellow
Write-Host ""

# Run the Python setup script
try {
    python setup_complete_system.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Set your OpenAI API key in the .env file" -ForegroundColor White
        Write-Host "2. Run: python backend/app/main.py" -ForegroundColor White
        Write-Host "3. Check the logs for model availability" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "⚠️ Setup completed with warnings. Check the output above." -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "❌ Setup failed with error: $_" -ForegroundColor Red
    Write-Host "Please check the error messages above and try again." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
