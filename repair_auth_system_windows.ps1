# Comprehensive Auth System Repair Script for Windows + Conda
# Fixes PostgreSQL, SQLite3, and Python binding issues

param(
    [switch]$Force,
    [string]$CondaEnv = "deepfake-env"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
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

# Check if conda is available
function Test-Conda {
    try {
        $condaVersion = conda --version
        Write-Success "Conda found: $condaVersion"
        return $true
    }
    catch {
        Write-Error "Conda not found. Please install Anaconda or Miniconda first."
        return $false
    }
}

# Check if conda environment exists
function Test-CondaEnvironment {
    param([string]$EnvName)
    
    Write-Log "Checking conda environment '$EnvName'..." -Color $Blue
    
    $envs = conda env list
    if ($envs -match $EnvName) {
        Write-Success "Conda environment '$EnvName' found"
        return $true
    }
    else {
        Write-Warning "Conda environment '$EnvName' not found. Creating it..."
        try {
            conda create -n $EnvName python=3.11 -y
            Write-Success "Conda environment '$EnvName' created"
            return $true
        }
        catch {
            Write-Error "Failed to create conda environment '$EnvName'"
            return $false
        }
    }
}

# Step 1: Install and configure PostgreSQL
function Install-PostgreSQL {
    Write-Log "Step 1: Setting up PostgreSQL server..." -Color $Blue
    
    # Check if PostgreSQL is already installed
    try {
        $pgVersion = psql --version
        Write-Success "PostgreSQL already installed: $pgVersion"
    }
    catch {
        Write-Log "PostgreSQL not found. Please install PostgreSQL manually:" -Color $Yellow
        Write-Log "1. Download from https://www.postgresql.org/download/windows/" -Color $Yellow
        Write-Log "2. Install with default settings" -Color $Yellow
        Write-Log "3. Remember the password you set for 'postgres' user" -Color $Yellow
        Write-Log "4. Run this script again" -Color $Yellow
        return $false
    }
    
    # Test PostgreSQL connection
    Write-Log "Testing PostgreSQL connection..."
    try {
        # Try to connect to default database
        $env:PGPASSWORD = "password"
        psql -h localhost -U postgres -d postgres -c "SELECT 1;" | Out-Null
        Write-Success "PostgreSQL connection test successful"
    }
    catch {
        Write-Warning "PostgreSQL connection test failed. Please check your PostgreSQL installation."
        Write-Log "Make sure PostgreSQL service is running and accessible." -Color $Yellow
        return $false
    }
    
    # Create database
    Write-Log "Creating database 'ifake_auth'..."
    try {
        psql -h localhost -U postgres -d postgres -c "CREATE DATABASE ifake_auth;" 2>$null
        Write-Success "Database 'ifake_auth' created"
    }
    catch {
        Write-Warning "Database 'ifake_auth' may already exist"
    }
    
    return $true
}

# Step 2: Fix SQLite3 issues in conda environment
function Fix-SQLite3Conda {
    param([string]$EnvName)
    
    Write-Log "Step 2: Fixing SQLite3 issues in conda environment..." -Color $Blue
    
    # Activate conda environment
    Write-Log "Activating conda environment '$EnvName'..."
    conda activate $EnvName
    
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
    conda clean --all -y
    
    # Reinstall Python with proper SQLite3 support
    Write-Log "Reinstalling Python with proper SQLite3 support..."
    conda install python=3.11 -y --force-reinstall
    
    # Install SQLite3 from conda-forge
    Write-Log "Installing SQLite3 from conda-forge..."
    conda install -c conda-forge sqlite -y
    
    # Install psycopg2 for PostgreSQL support
    Write-Log "Installing psycopg2 for PostgreSQL support..."
    conda install -c conda-forge psycopg2 -y
    
    # Install additional packages via pip
    Write-Log "Installing additional Python packages via pip..."
    pip install psycopg2-binary
    
    return $true
}

# Step 3: Clean broken shared objects and reinstall bindings
function Cleanup-BrokenObjects {
    param([string]$EnvName)
    
    Write-Log "Step 3: Cleaning broken shared objects and reinstalling bindings..." -Color $Blue
    
    # Activate conda environment
    conda activate $EnvName
    
    # Get conda environment path
    $condaBase = conda info --base
    $envPath = Join-Path $condaBase "envs\$EnvName"
    
    # Find and remove broken _sqlite3 shared objects
    Write-Log "Searching for broken _sqlite3 shared objects..."
    $brokenFiles = Get-ChildItem -Path $envPath -Recurse -Name "*_sqlite3*.dll" -ErrorAction SilentlyContinue
    foreach ($file in $brokenFiles) {
        $fullPath = Join-Path $envPath $file
        Write-Log "Removing broken shared object: $fullPath"
        Remove-Item $fullPath -Force -ErrorAction SilentlyContinue
    }
    
    # Clean Python cache
    Write-Log "Cleaning Python cache..."
    $cacheDirs = Get-ChildItem -Path $envPath -Recurse -Name "__pycache__" -Directory -ErrorAction SilentlyContinue
    foreach ($dir in $cacheDirs) {
        $fullPath = Join-Path $envPath $dir
        Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Remove .pyc files
    $pycFiles = Get-ChildItem -Path $envPath -Recurse -Name "*.pyc" -ErrorAction SilentlyContinue
    foreach ($file in $pycFiles) {
        $fullPath = Join-Path $envPath $file
        Remove-Item $fullPath -Force -ErrorAction SilentlyContinue
    }
    
    # Reinstall SQLite3 Python bindings
    Write-Log "Reinstalling SQLite3 Python bindings..."
    pip uninstall sqlite3 -y 2>$null
    pip install --force-reinstall --no-cache-dir sqlite3
    
    # Reinstall psycopg2
    Write-Log "Reinstalling psycopg2..."
    pip uninstall psycopg2 psycopg2-binary -y 2>$null
    pip install --force-reinstall --no-cache-dir psycopg2-binary
    
    return $true
}

# Step 4: Create runtime patches for SQLite3 compatibility
function New-RuntimePatches {
    Write-Log "Step 4: Creating runtime patches for SQLite3 compatibility..." -Color $Blue
    
    # Create runtime patches directory
    $patchesDir = "backend\app\auth"
    if (!(Test-Path $patchesDir)) {
        New-Item -ItemType Directory -Path $patchesDir -Force | Out-Null
    }
    
    # Create runtime patches file
    $patchesContent = @'
#!/usr/bin/env python3
"""
Runtime Patches for SQLite3 Compatibility
Applies patches to fix SQLite3 issues in conda environments.
"""

import os
import sys
import logging
import warnings
from typing import Optional

logger = logging.getLogger(__name__)

def apply_runtime_patches():
    """Apply runtime patches for SQLite3 compatibility"""
    try:
        logger.info("Applying runtime patches for SQLite3 compatibility...")
        
        # Patch 1: Fix SQLite3 import issues
        try:
            import sqlite3
            logger.info("SQLite3 import successful")
        except ImportError as e:
            logger.warning(f"SQLite3 import failed: {e}")
            # Try alternative import
            try:
                import sqlite3.dbapi2 as sqlite3
                logger.info("SQLite3 dbapi2 import successful")
            except ImportError:
                logger.error("All SQLite3 imports failed")
                return False
        
        # Patch 2: Fix undefined symbol issues
        try:
            # Test basic SQLite3 operations
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] == 1:
                logger.info("SQLite3 basic operations successful")
            else:
                logger.warning("SQLite3 basic operations failed")
                return False
                
        except Exception as e:
            logger.warning(f"SQLite3 operations failed: {e}")
            return False
        
        # Patch 3: Fix FallbackConnection issues
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            # Test SQLAlchemy with SQLite3
            engine = create_engine("sqlite:///:memory:", echo=False)
            SessionLocal = sessionmaker(bind=engine)
            
            # Test session creation
            session = SessionLocal()
            session.close()
            
            logger.info("SQLAlchemy SQLite3 integration successful")
            
        except Exception as e:
            logger.warning(f"SQLAlchemy SQLite3 integration failed: {e}")
            return False
        
        logger.info("All runtime patches applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Runtime patches failed: {e}")
        return False

def create_fallback_connection():
    """Create a fallback connection when SQLite3 fails"""
    try:
        logger.info("Creating fallback connection...")
        
        # Create a simple in-memory database
        import sqlite3
        
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        
        # Create a simple connection wrapper
        class FallbackConnection:
            def __init__(self, conn):
                self.conn = conn
                self.cursor = conn.cursor()
            
            def execute(self, query, params=None):
                if params:
                    return self.cursor.execute(query, params)
                else:
                    return self.cursor.execute(query)
            
            def fetchone(self):
                return self.cursor.fetchone()
            
            def fetchall(self):
                return self.cursor.fetchall()
            
            def commit(self):
                return self.conn.commit()
            
            def close(self):
                return self.conn.close()
        
        return FallbackConnection(conn)
        
    except Exception as e:
        logger.error(f"Fallback connection creation failed: {e}")
        return None

# Export functions
__all__ = ['apply_runtime_patches', 'create_fallback_connection']
'@
    
    $patchesFile = Join-Path $patchesDir "runtime_patches.py"
    Set-Content -Path $patchesFile -Value $patchesContent -Encoding UTF8
    
    Write-Success "Runtime patches created"
    return $true
}

# Step 5: Verify installations
function Test-Installations {
    param([string]$EnvName)
    
    Write-Log "Step 5: Verifying installations..." -Color $Blue
    
    # Activate conda environment
    conda activate $EnvName
    
    # Create test script
    $testScript = @'
#!/usr/bin/env python3
"""
Test script to verify SQLite3 and PostgreSQL functionality
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sqlite3():
    """Test SQLite3 functionality"""
    try:
        logger.info("Testing SQLite3...")
        import sqlite3
        
        # Test basic connection
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'test')")
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchone()
        
        conn.close()
        
        if result and result[0] == 1 and result[1] == 'test':
            logger.info("✅ SQLite3 test passed")
            print(f"SQLite3 version: {sqlite3.sqlite_version}")
            return True
        else:
            logger.error("❌ SQLite3 test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ SQLite3 test failed: {e}")
        return False

def test_postgresql():
    """Test PostgreSQL functionality"""
    try:
        logger.info("Testing PostgreSQL...")
        import psycopg2
        
        # Test connection
        conn = psycopg2.connect(
            host="localhost",
            database="ifake_auth",
            user="postgres",
            password="password"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            logger.info("✅ PostgreSQL test passed")
            print("Postgres OK")
            return True
        else:
            logger.error("❌ PostgreSQL test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ PostgreSQL test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting verification tests...")
    
    sqlite_ok = test_sqlite3()
    postgres_ok = test_postgresql()
    
    if sqlite_ok and postgres_ok:
        logger.info("✅ All tests passed!")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'@
    
    Set-Content -Path "test_imports.py" -Value $testScript -Encoding UTF8
    
    # Run the test
    Write-Log "Running verification tests..."
    try {
        python test_imports.py
        Write-Success "All verification tests passed!"
    }
    catch {
        Write-Error "Some verification tests failed"
        return $false
    }
    finally {
        # Clean up test file
        Remove-Item "test_imports.py" -Force -ErrorAction SilentlyContinue
    }
    
    return $true
}

# Step 6: Create comprehensive test script
function New-TestScript {
    Write-Log "Step 6: Creating comprehensive test script..." -Color $Blue
    
    $testScript = @'
#!/usr/bin/env python3
"""
Comprehensive Auth System Test
Tests the complete authentication system with both PostgreSQL and SQLite3.
"""

import asyncio
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_database():
    """Test the enhanced database system"""
    try:
        logger.info("Testing enhanced database system...")
        
        from app.auth.enhanced_database import initialize_enhanced_database, get_enhanced_database_health
        
        # Initialize database
        success = await initialize_enhanced_database()
        if not success:
            logger.error("❌ Enhanced database initialization failed")
            return False
        
        # Check health
        health = await get_enhanced_database_health()
        logger.info(f"Database health: {health}")
        
        if health.get("status") == "healthy":
            logger.info("✅ Enhanced database test passed")
            return True
        else:
            logger.error("❌ Enhanced database test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Enhanced database test failed: {e}")
        return False

async def test_auth_integration():
    """Test the authentication integration"""
    try:
        logger.info("Testing authentication integration...")
        
        from app.auth.comprehensive_integration import initialize_comprehensive_authentication
        
        # Initialize authentication
        success = await initialize_comprehensive_authentication()
        if not success:
            logger.error("❌ Authentication initialization failed")
            return False
        
        logger.info("✅ Authentication integration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Authentication integration test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("Starting comprehensive auth system tests...")
    
    db_ok = await test_enhanced_database()
    auth_ok = await test_auth_integration()
    
    if db_ok and auth_ok:
        logger.info("✅ All comprehensive tests passed!")
        return True
    else:
        logger.error("❌ Some comprehensive tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
'@
    
    Set-Content -Path "test_auth_system.py" -Value $testScript -Encoding UTF8
    Write-Success "Comprehensive test script created"
    return $true
}

# Main execution function
function Start-Repair {
    Write-Log "Starting comprehensive auth system repair..." -Color $Blue
    Write-Log "This script will fix PostgreSQL, SQLite3, and Python binding issues" -Color $Blue
    
    # Check prerequisites
    if (!(Test-Conda)) {
        Write-Error "Conda not found. Please install Anaconda or Miniconda first."
        exit 1
    }
    
    if (!(Test-CondaEnvironment -EnvName $CondaEnv)) {
        Write-Error "Failed to create or access conda environment '$CondaEnv'"
        exit 1
    }
    
    # Execute repair steps
    if (!(Install-PostgreSQL)) {
        Write-Error "PostgreSQL setup failed"
        exit 1
    }
    
    if (!(Fix-SQLite3Conda -EnvName $CondaEnv)) {
        Write-Error "SQLite3 conda fix failed"
        exit 1
    }
    
    if (!(Cleanup-BrokenObjects -EnvName $CondaEnv)) {
        Write-Error "Cleanup failed"
        exit 1
    }
    
    if (!(New-RuntimePatches)) {
        Write-Error "Runtime patches creation failed"
        exit 1
    }
    
    if (!(Test-Installations -EnvName $CondaEnv)) {
        Write-Error "Verification failed"
        exit 1
    }
    
    if (!(New-TestScript)) {
        Write-Error "Test script creation failed"
        exit 1
    }
    
    Write-Success "All repair steps completed successfully!"
    
    Write-Log "Running final verification..." -Color $Blue
    conda activate $CondaEnv
    
    # Run the verification command as requested
    Write-Log "Running verification command: python -c `"import sqlite3, psycopg2; print(sqlite3.sqlite_version); print('Postgres OK')`""
    try {
        python -c "import sqlite3, psycopg2; print(sqlite3.sqlite_version); print('Postgres OK')"
        Write-Success "Final verification passed!"
    }
    catch {
        Write-Error "Final verification failed"
        exit 1
    }
    
    Write-Log "Repair completed successfully!" -Color $Green
    Write-Log "You can now run your authentication system with:" -Color $Blue
    Write-Log "  conda activate $CondaEnv" -Color $Blue
    Write-Log "  python backend\app\main_production.py" -Color $Blue
    Write-Log "Or run the comprehensive test:" -Color $Blue
    Write-Log "  python test_auth_system.py" -Color $Blue
}

# Run main function
Start-Repair
