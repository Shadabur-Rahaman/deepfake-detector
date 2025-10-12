# PowerShell script to fix PyTorch CUDA installation
# Run as Administrator if needed

Write-Host "🔧 Fixing PyTorch CUDA Installation..." -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Consider running as Administrator for better compatibility" -ForegroundColor Yellow
}

Write-Host "📦 Uninstalling current PyTorch CPU version..." -ForegroundColor Yellow
try {
    pip uninstall torch torchvision torchaudio -y
    Write-Host "✅ PyTorch CPU version uninstalled" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Uninstall completed (some packages may not have been installed)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Installing PyTorch 2.1.0 with CUDA 12.1 support..." -ForegroundColor Cyan

try {
    # Install PyTorch with CUDA support
    pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121
    
    Write-Host ""
    Write-Host "✅ PyTorch CUDA installation complete!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🔍 Verifying installation..." -ForegroundColor Cyan
    
    # Test the installation
    $testScript = @"
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'Device: {torch.device("cuda" if torch.cuda.is_available() else "cpu")}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')
"@
    
    $testScript | python
    
    Write-Host ""
    Write-Host "🎯 Next steps:" -ForegroundColor Cyan
    Write-Host "1. Install updated requirements: pip install -r requirements_cuda_fixed.txt" -ForegroundColor White
    Write-Host "2. Test the system: python test_cuda_fixes.py" -ForegroundColor White
    Write-Host "3. Verify GPU inference is working" -ForegroundColor White
    
} catch {
    Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Check internet connection" -ForegroundColor White
    Write-Host "2. Try: pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu121" -ForegroundColor White
    Write-Host "3. Verify NVIDIA drivers are installed" -ForegroundColor White
    Write-Host "4. Check CUDA compatibility" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
