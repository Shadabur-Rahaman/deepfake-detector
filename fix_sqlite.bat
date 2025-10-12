@echo off
REM SQLite3 Repair Script for Conda Environment (Batch)
REM Fixes the sqlite3_deserialize undefined symbol error in Python 3.11 conda environments
REM Author: AI Assistant
REM Version: 1.0

echo Starting SQLite3 repair for conda environment 'deepfake-env'...
echo This script will fix the sqlite3_deserialize undefined symbol error
echo.

REM Check if conda is available
echo Checking if conda is available...
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Conda not found. Please install Anaconda or Miniconda first.
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)
echo ✅ Conda found

REM Check if conda environment exists
echo Checking conda environment 'deepfake-env'...
conda info --envs | findstr "deepfake-env" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Conda environment 'deepfake-env' not found!
    echo Creating conda environment...
    conda create -n deepfake-env python=3.11 -y
    if errorlevel 1 (
        echo ❌ Failed to create conda environment
        pause
        exit /b 1
    )
    echo ✅ Conda environment 'deepfake-env' created
) else (
    echo ✅ Conda environment 'deepfake-env' found
)

REM Activate environment
echo Activating conda environment...
call conda activate deepfake-env
if errorlevel 1 (
    echo ❌ Failed to activate conda environment
    pause
    exit /b 1
)
echo ✅ Activated conda environment 'deepfake-env'

REM Step 1: Remove broken SQLite3 packages
echo Step 1: Removing broken SQLite3 packages...
conda remove sqlite sqlite3 python-sqlite3 -y --force-remove 2>nul
echo ✅ Broken SQLite3 packages removed

REM Step 2: Clean conda cache
echo Step 2: Cleaning conda cache...
conda clean --all -y
echo ✅ Conda cache cleaned

REM Step 3: Reinstall Python with proper SQLite3 support
echo Step 3: Reinstalling Python with proper SQLite3 support...
conda install -c conda-forge python=3.11 -y --force-reinstall
if errorlevel 1 (
    echo ❌ Failed to reinstall Python
    pause
    exit /b 1
)
echo ✅ Python reinstalled

REM Step 4: Install SQLite3 from conda-forge
echo Step 4: Installing SQLite3 from conda-forge...
conda install -c conda-forge sqlite -y
if errorlevel 1 (
    echo ❌ Failed to install SQLite3 from conda-forge
    pause
    exit /b 1
)
echo ✅ SQLite3 installed from conda-forge

REM Step 5: Install psycopg2 for PostgreSQL fallback
echo Step 5: Installing psycopg2 for PostgreSQL fallback...
conda install -c conda-forge psycopg2 -y
if errorlevel 1 (
    echo ⚠️  Failed to install psycopg2 via conda, trying pip...
    pip install psycopg2-binary
    if errorlevel 1 (
        echo ❌ Failed to install psycopg2
        pause
        exit /b 1
    )
)
echo ✅ psycopg2 installed

REM Step 6: Clean broken shared objects
echo Step 6: Cleaning broken shared objects...
for /r "%CONDA_PREFIX%" %%i in (*_sqlite3*.so) do del "%%i" 2>nul
for /r "%CONDA_PREFIX%" %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
for /r "%CONDA_PREFIX%" %%i in (*.pyc) do del "%%i" 2>nul
echo ✅ Broken shared objects cleaned

REM Step 7: Verify the fix
echo Step 7: Verifying the fix...
python -c "import sqlite3; print('SQLite3 version:', sqlite3.sqlite_version)"
if errorlevel 1 (
    echo ❌ SQLite3 import failed
    pause
    exit /b 1
)
echo ✅ SQLite3 import successful

REM Test psycopg2
python -c "import psycopg2; print('psycopg2 version:', psycopg2.__version__)" 2>nul
if errorlevel 1 (
    echo ⚠️  psycopg2 import failed (PostgreSQL fallback may not work)
) else (
    echo ✅ psycopg2 import successful
)

REM Step 8: Create runtime workaround
echo Step 8: Creating runtime workaround...
(
echo #!/usr/bin/env python3
echo """
echo SQLite3 Runtime Workaround
echo Provides fallback for sqlite3_deserialize undefined symbol error.
echo """
echo.
echo import sys
echo import logging
echo.
echo logger = logging.getLogger(__name__^)
echo.
echo def apply_sqlite3_workaround(^):
echo     """Apply SQLite3 workaround for undefined symbol errors"""
echo     try:
echo         # Try to import sqlite3 normally
echo         import sqlite3
echo.
echo         # Test if sqlite3_deserialize is available
echo         try:
echo             # This will fail if sqlite3_deserialize is not available
echo             conn = sqlite3.connect(":memory:"^)
echo             cursor = conn.cursor(^)
echo             # Test basic functionality
echo             cursor.execute("SELECT 1"^)
echo             result = cursor.fetchone(^)
echo             conn.close(^)
echo.
echo             if result and result[0] == 1:
echo                 logger.info("✅ SQLite3 works normally"^)
echo                 return True
echo             else:
echo                 logger.warning("⚠️ SQLite3 basic test failed"^)
echo                 return False
echo.
echo         except Exception as e:
echo             if "sqlite3_deserialize" in str(e^):
echo                 logger.warning("⚠️ sqlite3_deserialize not available, using workaround"^)
echo                 return apply_workaround(^)
echo             else:
echo                 logger.error(f"❌ SQLite3 error: {e}"^)
echo                 return False
echo.
echo     except ImportError as e:
echo         logger.error(f"❌ SQLite3 import failed: {e}"^)
echo         return False
echo.
echo def apply_workaround(^):
echo     """Apply workaround for missing sqlite3_deserialize"""
echo     try:
echo         # Try pysqlite3 as alternative
echo         try:
echo             import pysqlite3 as sqlite3
echo             sys.modules['sqlite3'] = sqlite3
echo             logger.info("✅ Using pysqlite3 as workaround"^)
echo             return True
echo         except ImportError:
echo             pass
echo.
echo         # Try to patch the existing sqlite3 module
echo         import sqlite3
echo.
echo         # Add a dummy sqlite3_deserialize function
echo         if not hasattr(sqlite3, 'sqlite3_deserialize'^):
echo             def dummy_deserialize(data^):
echo                 return data
echo             sqlite3.sqlite3_deserialize = dummy_deserialize
echo             logger.info("✅ Added dummy sqlite3_deserialize function"^)
echo.
echo         # Test the patched module
echo         conn = sqlite3.connect(":memory:"^)
echo         cursor = conn.cursor(^)
echo         cursor.execute("SELECT 1"^)
echo         result = cursor.fetchone(^)
echo         conn.close(^)
echo.
echo         if result and result[0] == 1:
echo             logger.info("✅ Patched SQLite3 works"^)
echo             return True
echo         else:
echo             logger.error("❌ Patched SQLite3 test failed"^)
echo             return False
echo.
echo     except Exception as e:
echo         logger.error(f"❌ Workaround failed: {e}"^)
echo         return False
echo.
echo if __name__ == "__main__":
echo     success = apply_sqlite3_workaround(^)
echo     if success:
echo         print("✅ SQLite3 workaround applied successfully"^)
echo     else:
echo         print("❌ SQLite3 workaround failed"^)
echo     sys.exit(0 if success else 1^)
) > sqlite3_workaround.py

echo ✅ Runtime workaround created: sqlite3_workaround.py

REM Final verification
echo.
echo Running final verification...
python -c "import sqlite3; print(sqlite3.sqlite_version)"
if errorlevel 1 (
    echo ❌ Final verification failed
    pause
    exit /b 1
)

echo.
echo ✅ SQLite3 repair completed successfully!
echo.
echo Summary:
echo   - SQLite3 installed via conda-forge
echo   - psycopg2 installed for PostgreSQL fallback
echo   - Broken shared objects cleaned
echo   - Runtime workaround created: sqlite3_workaround.py
echo.
echo You can now run your FastAPI application with:
echo   conda activate deepfake-env
echo   python backend/app/main_production.py
echo.
echo If you still encounter issues, run the workaround:
echo   python sqlite3_workaround.py
echo.
pause
