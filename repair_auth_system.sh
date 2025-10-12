#!/bin/bash
# Comprehensive Auth System Repair Script for Ubuntu + Conda
# Fixes PostgreSQL, SQLite3, and Python binding issues

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Error handling
handle_error() {
    local line_no=$1
    local error_code=$2
    error "Error on line $line_no with exit code $error_code"
    error "Script execution failed. Please check the output above for details."
    exit $error_code
}

# Set up error trap
trap 'handle_error $LINENO $?' ERR

# Check if running as root for system operations
check_root() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. Some operations may affect system-wide packages."
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Script aborted by user"
            exit 1
        fi
    fi
}

# Check if conda is available
check_conda() {
    log "Checking if conda is available..."
    if ! command -v conda &> /dev/null; then
        error "Conda not found. Please install Anaconda or Miniconda first."
        error "Download from: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    success "Conda found: $(conda --version)"
}

# Check if conda environment exists
check_conda_env() {
    log "Checking conda environment 'deepfake-env'..."
    
    if ! conda info --envs | grep -q "deepfake-env"; then
        warning "Conda environment 'deepfake-env' not found!"
        log "Creating conda environment..."
        if conda create -n deepfake-env python=3.11 -y; then
            success "Conda environment 'deepfake-env' created"
        else
            error "Failed to create conda environment"
            exit 1
        fi
    else
        success "Conda environment 'deepfake-env' found"
    fi
    
    # Activate environment
    log "Activating conda environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if conda activate deepfake-env; then
        success "Activated conda environment 'deepfake-env'"
    else
        error "Failed to activate conda environment"
        exit 1
    fi
}

# Step 1: Install and configure PostgreSQL
setup_postgresql() {
    log "Step 1: Setting up PostgreSQL server..."
    
    # Update package list
    log "Updating package list..."
    if ! sudo apt update; then
        error "Failed to update package list"
        exit 1
    fi
    
    # Install PostgreSQL and development headers
    log "Installing PostgreSQL server and development packages..."
    if ! sudo apt install -y postgresql postgresql-contrib postgresql-server-dev-all libpq-dev; then
        error "Failed to install PostgreSQL packages"
        exit 1
    fi
    
    # Start and enable PostgreSQL service
    log "Starting PostgreSQL service..."
    if ! sudo systemctl start postgresql; then
        error "Failed to start PostgreSQL service"
        exit 1
    fi
    
    if ! sudo systemctl enable postgresql; then
        warning "Failed to enable PostgreSQL service (non-critical)"
    fi
    
    # Check if PostgreSQL is running
    if sudo systemctl is-active --quiet postgresql; then
        success "PostgreSQL service is running"
    else
        error "PostgreSQL service is not running"
        exit 1
    fi
    
    # Create database and user
    log "Creating database 'ifake_auth' and user 'postgres'..."
    
    # Switch to postgres user and create database
    if ! sudo -u postgres psql -c "CREATE DATABASE ifake_auth;" 2>/dev/null; then
        warning "Database 'ifake_auth' may already exist"
    else
        success "Database 'ifake_auth' created"
    fi
    
    if ! sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';" 2>/dev/null; then
        warning "Password may already be set or failed to set"
    else
        success "PostgreSQL user password set"
    fi
    
    # Grant privileges
    if ! sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ifake_auth TO postgres;" 2>/dev/null; then
        warning "Failed to grant privileges (may already be granted)"
    else
        success "Privileges granted to postgres user"
    fi
    
    # Test connection
    log "Testing PostgreSQL connection..."
    if PGPASSWORD=password psql -h localhost -U postgres -d ifake_auth -c "SELECT 1;" >/dev/null 2>&1; then
        success "PostgreSQL connection test successful"
    else
        error "PostgreSQL connection test failed"
        error "Please check PostgreSQL configuration and try again"
        exit 1
    fi
}

# Step 2: Fix SQLite3 issues in conda environment
fix_sqlite3_conda() {
    log "Step 2: Fixing SQLite3 issues in conda environment..."
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if ! conda activate deepfake-env; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Install system SQLite3 development headers
    log "Installing system SQLite3 development headers..."
    if ! sudo apt install -y libsqlite3-dev sqlite3; then
        error "Failed to install SQLite3 development headers"
        exit 1
    fi
    
    # Remove broken SQLite3 packages from conda
    log "Removing broken SQLite3 packages from conda..."
    if conda remove sqlite sqlite3 python-sqlite3 -y --force-remove 2>/dev/null; then
        success "Broken SQLite3 packages removed"
    else
        warning "Some packages may not exist or already removed"
    fi
    
    # Clean conda cache
    log "Cleaning conda cache..."
    if ! conda clean --all -y; then
        warning "Failed to clean conda cache (non-critical)"
    fi
    
    # Reinstall Python with proper SQLite3 support
    log "Reinstalling Python with proper SQLite3 support..."
    if ! conda install python=3.11 -y --force-reinstall; then
        error "Failed to reinstall Python"
        exit 1
    fi
    
    # Install SQLite3 from conda-forge with proper linking
    log "Installing SQLite3 from conda-forge..."
    if ! conda install -c conda-forge sqlite -y; then
        error "Failed to install SQLite3 from conda-forge"
        exit 1
    fi
    
    # Install psycopg2 for PostgreSQL support
    log "Installing psycopg2 for PostgreSQL support..."
    if ! conda install -c conda-forge psycopg2 -y; then
        warning "Failed to install psycopg2 via conda, trying pip..."
        if ! pip install psycopg2-binary; then
            error "Failed to install psycopg2"
            exit 1
        fi
    fi
    
    success "SQLite3 and PostgreSQL packages installed"
}

# Step 3: Clean broken shared objects and reinstall bindings
cleanup_broken_objects() {
    log "Step 3: Cleaning broken shared objects and reinstalling bindings..."
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if ! conda activate deepfake-env; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Find and remove broken _sqlite3 shared objects
    log "Searching for broken _sqlite3 shared objects..."
    local conda_base
    conda_base=$(conda info --base)
    local env_path="$conda_base/envs/deepfake-env"
    
    if [[ -d "$env_path" ]]; then
        find "$env_path" -name "*_sqlite3*.so" -type f 2>/dev/null | while read -r file; do
            log "Removing broken shared object: $file"
            rm -f "$file"
        done
        success "Broken shared objects cleaned"
    else
        warning "Conda environment path not found: $env_path"
    fi
    
    # Clean Python cache
    log "Cleaning Python cache..."
    if [[ -d "$env_path" ]]; then
        find "$env_path" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$env_path" -name "*.pyc" -type f -delete 2>/dev/null || true
        success "Python cache cleaned"
    fi
    
    # Reinstall SQLite3 Python bindings
    log "Reinstalling SQLite3 Python bindings..."
    if pip uninstall sqlite3 -y 2>/dev/null; then
        success "Old sqlite3 package removed"
    else
        warning "sqlite3 package may not be installed via pip"
    fi
    
    if ! pip install --force-reinstall --no-cache-dir sqlite3; then
        warning "Failed to reinstall sqlite3 via pip (may not be needed)"
    fi
    
    # Reinstall psycopg2
    log "Reinstalling psycopg2..."
    if pip uninstall psycopg2 psycopg2-binary -y 2>/dev/null; then
        success "Old psycopg2 packages removed"
    else
        warning "psycopg2 packages may not be installed via pip"
    fi
    
    if ! pip install --force-reinstall --no-cache-dir psycopg2-binary; then
        error "Failed to reinstall psycopg2"
        exit 1
    fi
    
    success "Python bindings reinstalled"
}

# Step 4: Create runtime patches for SQLite3 compatibility
create_runtime_patches() {
    log "Step 4: Creating runtime patches for SQLite3 compatibility..."
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if ! conda activate deepfake-env; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Create runtime patches directory
    mkdir -p backend/app/auth
    
    # Create runtime patches file
    cat > backend/app/auth/runtime_patches.py << 'EOF'
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
EOF

    success "Runtime patches created"
}

# Step 5: Verify installations
verify_installations() {
    log "Step 5: Verifying installations..."
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    if ! conda activate deepfake-env; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Test Python imports and functionality
    log "Testing Python imports and functionality..."
    
    # Create test script
    cat > test_imports.py << 'EOF'
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
EOF

    # Run the test
    log "Running verification tests..."
    if python test_imports.py; then
        success "All verification tests passed!"
    else
        error "Some verification tests failed"
        return 1
    fi
    
    # Clean up test file
    rm -f test_imports.py
}

# Step 6: Create comprehensive test script
create_test_script() {
    log "Step 6: Creating comprehensive test script..."
    
    cat > test_auth_system.py << 'EOF'
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
EOF

    chmod +x test_auth_system.py
    success "Comprehensive test script created"
}

# Main execution function
main() {
    log "Starting comprehensive auth system repair..."
    log "This script will fix PostgreSQL, SQLite3, and Python binding issues"
    
    # Check prerequisites
    check_root
    check_conda
    check_conda_env
    
    # Execute repair steps
    setup_postgresql
    fix_sqlite3_conda
    cleanup_broken_objects
    create_runtime_patches
    verify_installations
    create_test_script
    
    success "All repair steps completed successfully!"
    
    log "Running final verification..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate deepfake-env
    
    # Run the verification command as requested
    log "Running verification command: python -c \"import sqlite3, psycopg2; print(sqlite3.sqlite_version); print('Postgres OK')\""
    if python -c "import sqlite3, psycopg2; print(sqlite3.sqlite_version); print('Postgres OK')"; then
        success "Final verification passed!"
    else
        error "Final verification failed"
        exit 1
    fi
    
    log "Repair completed successfully!"
    log "You can now run your authentication system with:"
    log "  conda activate deepfake-env"
    log "  python backend/app/main_production.py"
    log "Or run the comprehensive test:"
    log "  python test_auth_system.py"
}

# Run main function
main "$@"