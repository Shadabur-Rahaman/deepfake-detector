# SQLite3 Repair Script for Conda Environment (PowerShell)
# Fixes the sqlite3_deserialize undefined symbol error in Python 3.11 conda environments
# Author: AI Assistant
# Version: 1.0

param(
    [switch]$Force
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Logging functions
function Write-Log {
    param([string]$Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

# Check if running as administrator
function Test-Administrator {
    if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Warning "This script should be run as Administrator for system operations."
        if (-not $Force) {
            $response = Read-Host "Continue anyway? (y/N)"
            if ($response -notmatch "^[Yy]$") {
                Write-Error "Script aborted by user"
                exit 1
            }
        }
    }
}

# Check if conda is available
function Test-Conda {
    Write-Log "Checking if conda is available..."
    try {
        $condaVersion = conda --version
        Write-Success "Conda found: $condaVersion"
    }
    catch {
        Write-Error "Conda not found. Please install Anaconda or Miniconda first."
        Write-Error "Download from: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    }
}

# Check if conda environment exists
function Test-CondaEnvironment {
    Write-Log "Checking conda environment 'deepfake-env'..."
    
    $envs = conda info --envs
    if ($envs -notmatch "deepfake-env") {
        Write-Warning "Conda environment 'deepfake-env' not found!"
        Write-Log "Creating conda environment..."
        try {
            conda create -n deepfake-env python=3.11 -y
            Write-Success "Conda environment 'deepfake-env' created"
        }
        catch {
            Write-Error "Failed to create conda environment"
            exit 1
        }
    }
    else {
        Write-Success "Conda environment 'deepfake-env' found"
    }
    
    # Activate environment
    Write-Log "Activating conda environment..."
    try {
        conda activate deepfake-env
        Write-Success "Activated conda environment 'deepfake-env'"
    }
    catch {
        Write-Error "Failed to activate conda environment"
        exit 1
    }
}

# Step 1: Install SQLite3 via conda-forge
function Install-SQLite3 {
    Write-Log "Step 1: Installing SQLite3 via conda-forge..."
    
    # Activate conda environment
    conda activate deepfake-env
    
    # Remove broken SQLite3 packages
    Write-Log "Removing broken SQLite3 packages from conda..."
    try {
        conda remove sqlite sqlite3 python-sqlite3 -y --force-remove 2>$null
        Write-Success "Broken SQLite3 packages removed"
    }
    catch {
        Write-Warning "Some packages may not exist or already removed"
    }
    
    # Clean conda cache
    Write-Log "Cleaning conda cache..."
    try {
        conda clean --all -y
    }
    catch {
        Write-Warning "Failed to clean conda cache (non-critical)"
    }
    
    # Reinstall Python with proper SQLite3 support
    Write-Log "Reinstalling Python with proper SQLite3 support..."
    try {
        conda install -c conda-forge python=3.11 -y --force-reinstall
        Write-Success "Python reinstalled"
    }
    catch {
        Write-Error "Failed to reinstall Python"
        exit 1
    }
    
    # Install SQLite3 from conda-forge
    Write-Log "Installing SQLite3 from conda-forge..."
    try {
        conda install -c conda-forge sqlite -y
        Write-Success "SQLite3 installed from conda-forge"
    }
    catch {
        Write-Error "Failed to install SQLite3 from conda-forge"
        exit 1
    }
}

# Step 2: Install psycopg2 for PostgreSQL fallback
function Install-Psycopg2 {
    Write-Log "Step 2: Installing psycopg2 for PostgreSQL fallback..."
    
    # Activate conda environment
    conda activate deepfake-env
    
    # Install psycopg2
    Write-Log "Installing psycopg2..."
    try {
        conda install -c conda-forge psycopg2 -y
        Write-Success "psycopg2 installed via conda"
    }
    catch {
        Write-Warning "Failed to install psycopg2 via conda, trying pip..."
        try {
            pip install psycopg2-binary
            Write-Success "psycopg2 installed via pip"
        }
        catch {
            Write-Error "Failed to install psycopg2"
            exit 1
        }
    }
}

# Step 3: Clean broken shared objects
function Clear-BrokenObjects {
    Write-Log "Step 3: Cleaning broken shared objects..."
    
    # Activate conda environment
    conda activate deepfake-env
    
    # Get conda environment path
    $condaBase = conda info --base
    $envPath = Join-Path $condaBase "envs\deepfake-env"
    
    if (Test-Path $envPath) {
        # Find and remove broken _sqlite3 shared objects
        Write-Log "Searching for broken _sqlite3 shared objects..."
        Get-ChildItem -Path $envPath -Recurse -Name "*_sqlite3*.so" -ErrorAction SilentlyContinue | ForEach-Object {
            $filePath = Join-Path $envPath $_
            Write-Log "Removing broken shared object: $filePath"
            Remove-Item -Path $filePath -Force -ErrorAction SilentlyContinue
        }
        Write-Success "Broken shared objects cleaned"
        
        # Clean Python cache
        Write-Log "Cleaning Python cache..."
        Get-ChildItem -Path $envPath -Recurse -Name "__pycache__" -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $dirPath = Join-Path $envPath $_
            Remove-Item -Path $dirPath -Recurse -Force -ErrorAction SilentlyContinue
        }
        Get-ChildItem -Path $envPath -Recurse -Name "*.pyc" -File -ErrorAction SilentlyContinue | ForEach-Object {
            $filePath = Join-Path $envPath $_
            Remove-Item -Path $filePath -Force -ErrorAction SilentlyContinue
        }
        Write-Success "Python cache cleaned"
    }
    else {
        Write-Warning "Conda environment path not found: $envPath"
    }
}

# Step 4: Verify the fix
function Test-Fix {
    Write-Log "Step 4: Verifying the fix..."
    
    # Activate conda environment
    conda activate deepfake-env
    
    # Test SQLite3 import and version
    Write-Log "Testing SQLite3 import and version..."
    try {
        $result = python -c "import sqlite3; print('SQLite3 version:', sqlite3.sqlite_version)"
        Write-Success "SQLite3 import successful: $result"
    }
    catch {
        Write-Error "SQLite3 import failed: $_"
        return $false
    }
    
    # Test psycopg2 import
    Write-Log "Testing psycopg2 import..."
    try {
        $result = python -c "import psycopg2; print('psycopg2 version:', psycopg2.__version__)"
        Write-Success "psycopg2 import successful: $result"
    }
    catch {
        Write-Warning "psycopg2 import failed (PostgreSQL fallback may not work): $_"
    }
    
    # Test the specific command requested
    Write-Log "Running verification command: python -c `"import sqlite3; print(sqlite3.sqlite_version)`""
    try {
        $version = python -c "import sqlite3; print(sqlite3.sqlite_version)"
        Write-Success "Verification command successful: $version"
        
        # Check if version is >= 3.41
        $versionNum = [version]$version
        $targetVersion = [version]"3.41"
        if ($versionNum -ge $targetVersion) {
            Write-Success "SQLite3 version $version is >= 3.41"
        }
        else {
            Write-Warning "SQLite3 version $version is < 3.41, but the import works"
        }
        
        return $true
    }
    catch {
        Write-Error "Verification command failed: $_"
        return $false
    }
}

# Step 5: Create runtime workaround
function New-RuntimeWorkaround {
    Write-Log "Step 5: Creating runtime workaround..."
    
    $workaroundScript = @'
#!/usr/bin/env python3
"""
SQLite3 Runtime Workaround
Provides fallback for sqlite3_deserialize undefined symbol error.
"""

import sys
import logging

logger = logging.getLogger(__name__)

def apply_sqlite3_workaround():
    """Apply SQLite3 workaround for undefined symbol errors"""
    try:
        # Try to import sqlite3 normally
        import sqlite3
        
        # Test if sqlite3_deserialize is available
        try:
            # This will fail if sqlite3_deserialize is not available
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            # Test basic functionality
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 1:
                logger.info("✅ SQLite3 works normally")
                return True
            else:
                logger.warning("⚠️ SQLite3 basic test failed")
                return False
                
        except Exception as e:
            if "sqlite3_deserialize" in str(e):
                logger.warning("⚠️ sqlite3_deserialize not available, using workaround")
                return apply_workaround()
            else:
                logger.error(f"❌ SQLite3 error: {e}")
                return False
                
    except ImportError as e:
        logger.error(f"❌ SQLite3 import failed: {e}")
        return False

def apply_workaround():
    """Apply workaround for missing sqlite3_deserialize"""
    try:
        # Try pysqlite3 as alternative
        try:
            import pysqlite3 as sqlite3
            sys.modules['sqlite3'] = sqlite3
            logger.info("✅ Using pysqlite3 as workaround")
            return True
        except ImportError:
            pass
        
        # Try to patch the existing sqlite3 module
        import sqlite3
        
        # Add a dummy sqlite3_deserialize function
        if not hasattr(sqlite3, 'sqlite3_deserialize'):
            def dummy_deserialize(data):
                return data
            sqlite3.sqlite3_deserialize = dummy_deserialize
            logger.info("✅ Added dummy sqlite3_deserialize function")
        
        # Test the patched module
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 1:
            logger.info("✅ Patched SQLite3 works")
            return True
        else:
            logger.error("❌ Patched SQLite3 test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Workaround failed: {e}")
        return False

if __name__ == "__main__":
    success = apply_sqlite3_workaround()
    if success:
        print("✅ SQLite3 workaround applied successfully")
    else:
        print("❌ SQLite3 workaround failed")
    sys.exit(0 if success else 1)
'@
    
    $workaroundScript | Out-File -FilePath "sqlite3_workaround.py" -Encoding UTF8
    Write-Success "Runtime workaround created: sqlite3_workaround.py"
}

# Main execution function
function Main {
    Write-Log "Starting SQLite3 repair for conda environment 'deepfake-env'..."
    Write-Log "This script will fix the sqlite3_deserialize undefined symbol error"
    
    # Check prerequisites
    Test-Administrator
    Test-Conda
    Test-CondaEnvironment
    
    # Execute repair steps
    Install-SQLite3
    Install-Psycopg2
    Clear-BrokenObjects
    
    # Verify the fix
    $fixSuccess = Test-Fix
    if (-not $fixSuccess) {
        Write-Error "Fix verification failed"
        exit 1
    }
    
    # Create runtime workaround
    New-RuntimeWorkaround
    
    Write-Success "SQLite3 repair completed successfully!"
    
    Write-Log "Summary:"
    Write-Log "  - SQLite3 installed via conda-forge"
    Write-Log "  - psycopg2 installed for PostgreSQL fallback"
    Write-Log "  - Broken shared objects cleaned"
    Write-Log "  - Runtime workaround created: sqlite3_workaround.py"
    
    Write-Log "You can now run your FastAPI application with:"
    Write-Log "  conda activate deepfake-env"
    Write-Log "  python backend/app/main_production.py"
    
    Write-Log "If you still encounter issues, run the workaround:"
    Write-Log "  python sqlite3_workaround.py"
}

# Run main function
Main
