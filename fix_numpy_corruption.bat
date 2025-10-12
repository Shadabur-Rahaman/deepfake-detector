@echo off
REM Batch script to fix numpy corruption and -umpy warning
echo ========================================
echo NUMPY CORRUPTION FIX SCRIPT
echo ========================================
echo.
echo This script will fix the corrupted numpy installation
echo and resolve the '-umpy' warning in your conda environment.
echo.
echo Target Environment: deepfake-py310
echo.

REM Check if we're in the right environment
echo Checking current conda environment...
conda info --envs | findstr "deepfake-py310" | findstr "*" >nul
if %errorlevel% equ 0 (
    echo ✅ Currently in deepfake-py310 environment
) else (
    echo ⚠️  WARNING: Not in deepfake-py310 environment!
    echo Please activate it first with: conda activate deepfake-py310
    pause
)

echo.
echo Step 1: Locating corrupted numpy directories...
echo.

REM Define the site-packages path
set "sitePackagesPath=C:\Users\raham\anaconda3\envs\deepfake-py310\Lib\site-packages"

if exist "%sitePackagesPath%" (
    echo ✅ Found site-packages directory: %sitePackagesPath%
    
    REM Look for corrupted numpy directories
    echo Searching for corrupted numpy directories...
    dir "%sitePackagesPath%" | findstr /i "umpy" >nul
    if %errorlevel% equ 0 (
        echo Found potentially corrupted directories:
        dir "%sitePackagesPath%" | findstr /i "umpy"
        
        echo.
        echo Step 2: Removing corrupted directories...
        echo.
        
        REM Remove directories starting with -umpy
        for /d %%i in ("%sitePackagesPath%\-umpy*") do (
            echo Removing %%~nxi...
            rmdir /s /q "%%i" 2>nul
            if exist "%%i" (
                echo   ❌ Failed to remove %%~nxi
            ) else (
                echo   ✅ Removed %%~nxi
            )
        )
        
        REM Remove directories containing -umpy
        for /d %%i in ("%sitePackagesPath%*-umpy*") do (
            echo Removing %%~nxi...
            rmdir /s /q "%%i" 2>nul
            if exist "%%i" (
                echo   ❌ Failed to remove %%~nxi
            ) else (
                echo   ✅ Removed %%~nxi
            )
        )
    ) else (
        echo ✅ No corrupted numpy directories found
    )
) else (
    echo ❌ Site-packages directory not found at expected location
    echo Expected: %sitePackagesPath%
    pause
)

echo.
echo Step 3: Clean numpy installation...
echo.

REM Uninstall numpy completely
echo Uninstalling numpy...
pip uninstall numpy -y

REM Force reinstall numpy with specific version
echo Installing numpy 1.26.4...
pip install --force-reinstall numpy==1.26.4

echo.
echo Step 4: Verifying installation...
echo.

REM Test numpy import
echo Testing numpy import...
python -c "import numpy; print(f'✅ Numpy {numpy.__version__} imported successfully')"
if %errorlevel% equ 0 (
    echo ✅ Numpy installation verified
) else (
    echo ❌ Numpy import failed
)

echo.
echo Step 5: Checking environment health...
echo.

REM Run pip check
echo Running pip check...
pip check

echo.
echo Step 6: Installing compatible scipy version...
echo.

REM Install compatible scipy version
echo Installing scipy 1.11.4 (compatible with scikit-learn 1.3.2)...
pip install scipy==1.11.4

echo.
echo Step 7: Installing compatible pillow version...
echo.

REM Install compatible pillow version
echo Installing pillow 10.1.0...
pip install pillow==10.1.0

echo.
echo ========================================
echo NUMPY CORRUPTION FIX COMPLETE!
echo ========================================
echo.
echo To verify everything is working, run:
echo   python verify_installation.py
echo.
echo If you still see warnings, run:
echo   pip check
echo.
pause
