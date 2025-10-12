# PowerShell script to fix numpy corruption and -umpy warning
Write-Host "========================================" -ForegroundColor Red
Write-Host "NUMPY CORRUPTION FIX SCRIPT" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "This script will fix the corrupted numpy installation" -ForegroundColor Yellow
Write-Host "and resolve the '-umpy' warning in your conda environment." -ForegroundColor Yellow
Write-Host ""
Write-Host "Target Environment: deepfake-py310" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right environment
$envName = conda info --envs | Select-String "deepfake-py310"
if ($envName -and $envName.ToString().Contains("*")) {
    Write-Host "✅ Currently in deepfake-py310 environment" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: Not in deepfake-py310 environment!" -ForegroundColor Yellow
    Write-Host "Please activate it first with: conda activate deepfake-py310" -ForegroundColor Yellow
    Read-Host "Press Enter to continue anyway..."
}

Write-Host ""
Write-Host "Step 1: Locating corrupted numpy directories..." -ForegroundColor Green
Write-Host ""

# Define the site-packages path
$sitePackagesPath = "C:\Users\raham\anaconda3\envs\deepfake-py310\Lib\site-packages"

if (Test-Path $sitePackagesPath) {
    Write-Host "✅ Found site-packages directory: $sitePackagesPath" -ForegroundColor Green
    
    # Look for corrupted numpy directories
    Write-Host "Searching for corrupted numpy directories..." -ForegroundColor Cyan
    $corruptedDirs = Get-ChildItem -Path $sitePackagesPath -Directory | Where-Object { $_.Name -like "*-umpy*" -or $_.Name -like "-umpy*" }
    
    if ($corruptedDirs) {
        Write-Host "Found corrupted directories:" -ForegroundColor Yellow
        foreach ($dir in $corruptedDirs) {
            Write-Host "  ❌ $($dir.Name)" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "Step 2: Removing corrupted directories..." -ForegroundColor Green
        
        foreach ($dir in $corruptedDirs) {
            try {
                Write-Host "Removing $($dir.Name)..." -ForegroundColor Yellow
                Remove-Item -Path $dir.FullName -Recurse -Force
                Write-Host "  ✅ Removed $($dir.Name)" -ForegroundColor Green
            } catch {
                Write-Host "  ❌ Failed to remove $($dir.Name): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "✅ No corrupted numpy directories found" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Site-packages directory not found at expected location" -ForegroundColor Red
    Write-Host "Expected: $sitePackagesPath" -ForegroundColor Yellow
    Read-Host "Press Enter to continue with pip commands..."
}

Write-Host ""
Write-Host "Step 3: Clean numpy installation..." -ForegroundColor Green
Write-Host ""

# Uninstall numpy completely
Write-Host "Uninstalling numpy..." -ForegroundColor Yellow
pip uninstall numpy -y

# Force reinstall numpy with specific version
Write-Host "Installing numpy 1.26.4..." -ForegroundColor Cyan
pip install --force-reinstall numpy==1.26.4

Write-Host ""
Write-Host "Step 4: Verifying installation..." -ForegroundColor Green
Write-Host ""

# Test numpy import
Write-Host "Testing numpy import..." -ForegroundColor Cyan
try {
    python -c "import numpy; print(f'✅ Numpy {numpy.__version__} imported successfully')"
    Write-Host "✅ Numpy installation verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Numpy import failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 5: Checking environment health..." -ForegroundColor Green
Write-Host ""

# Run pip check
Write-Host "Running pip check..." -ForegroundColor Cyan
pip check

Write-Host ""
Write-Host "Step 6: Installing compatible scipy version..." -ForegroundColor Green
Write-Host ""

# Install compatible scipy version
Write-Host "Installing scipy 1.11.4 (compatible with scikit-learn 1.3.2)..." -ForegroundColor Cyan
pip install scipy==1.11.4

Write-Host ""
Write-Host "Step 7: Installing compatible pillow version..." -ForegroundColor Green
Write-Host ""

# Install compatible pillow version
Write-Host "Installing pillow 10.1.0..." -ForegroundColor Cyan
pip install pillow==10.1.0

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "NUMPY CORRUPTION FIX COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To verify everything is working, run:" -ForegroundColor Cyan
Write-Host "  python verify_installation.py" -ForegroundColor White
Write-Host ""
Write-Host "If you still see warnings, run:" -ForegroundColor Cyan
Write-Host "  pip check" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue..."
