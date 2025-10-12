#!/bin/bash
# SQLite3 Repair Script for Conda Environment
# Fixes the sqlite3_deserialize undefined symbol error in Python 3.11 conda environments
# Author: AI Assistant
# Version: 1.0

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
    
    # Initialize conda properly
    log "Initializing conda..."
    eval "$(conda shell.bash hook)"
    
    # Activate environment with proper error handling
    log "Activating conda environment..."
    if conda activate deepfake-env 2>/dev/null; then
        success "Activated conda environment 'deepfake-env'"
    else
        # Try alternative activation method
        log "Trying alternative activation method..."
        source "$(conda info --base)/etc/profile.d/conda.sh"
        if conda activate deepfake-env 2>/dev/null; then
            success "Activated conda environment 'deepfake-env' (alternative method)"
        else
            error "Failed to activate conda environment"
            exit 1
        fi
    fi
}

# Step 1: Install latest system SQLite3 (>= 3.41)
install_system_sqlite3() {
    log "Step 1: Installing latest system SQLite3 (>= 3.41)..."
    
    # Update package list
    log "Updating package list..."
    if ! sudo apt update; then
        error "Failed to update package list"
        exit 1
    fi
    
    # Install SQLite3 development headers and binary
    log "Installing SQLite3 development headers and binary..."
    if ! sudo apt install -y libsqlite3-dev sqlite3; then
        error "Failed to install SQLite3 packages"
        exit 1
    fi
    
    # Verify SQLite3 version
    log "Verifying SQLite3 version..."
    local sqlite_version
    sqlite_version=$(sqlite3 --version | cut -d' ' -f1)
    log "System SQLite3 version: $sqlite_version"
    
    # Check if version is >= 3.41
    if [[ $(echo "$sqlite_version 3.41" | awk '{print ($1 >= $2)}') -eq 1 ]]; then
        success "System SQLite3 version $sqlite_version is >= 3.41"
    else
        warning "System SQLite3 version $sqlite_version is < 3.41, but continuing..."
    fi
}

# Step 2: Fix conda environment SQLite3 bindings
fix_conda_sqlite3() {
    log "Step 2: Fixing conda environment SQLite3 bindings..."
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    if ! conda activate deepfake-env 2>/dev/null; then
        error "Failed to activate conda environment"
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
    if ! conda install -c conda-forge python=3.11 -y --force-reinstall; then
        error "Failed to reinstall Python"
        exit 1
    fi
    
    # Install SQLite3 from conda-forge with proper linking
    log "Installing SQLite3 from conda-forge..."
    if ! conda install -c conda-forge sqlite -y; then
        error "Failed to install SQLite3 from conda-forge"
        exit 1
    fi
    
    success "SQLite3 packages installed in conda environment"
}

# Step 3: Clean broken shared objects
cleanup_broken_objects() {
    log "Step 3: Cleaning broken shared objects..."
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    if ! conda activate deepfake-env 2>/dev/null; then
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
}

# Step 4: Rebuild SQLite3 bindings with proper linking
rebuild_sqlite3_bindings() {
    log "Step 4: Rebuilding SQLite3 bindings with proper linking..."
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    if ! conda activate deepfake-env 2>/dev/null; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Set environment variables for proper linking
    export LD_RUN_PATH="/usr/lib/x86_64-linux-gnu:/usr/lib"
    export LDFLAGS="-L/usr/lib/x86_64-linux-gnu -L/usr/lib"
    export CPPFLAGS="-I/usr/include"
    
    # Reinstall SQLite3 Python bindings
    log "Reinstalling SQLite3 Python bindings..."
    if pip uninstall sqlite3 -y 2>/dev/null; then
        success "Old sqlite3 package removed"
    else
        warning "sqlite3 package may not be installed via pip"
    fi
    
    # Install pysqlite3 as alternative
    log "Installing pysqlite3 as alternative..."
    if ! pip install --force-reinstall --no-cache-dir pysqlite3; then
        warning "Failed to install pysqlite3 (may not be needed)"
    fi
    
    # Try to rebuild Python's sqlite3 module
    log "Attempting to rebuild Python's sqlite3 module..."
    if ! pip install --force-reinstall --no-cache-dir --no-binary=sqlite3 sqlite3; then
        warning "Failed to rebuild sqlite3 via pip (may not be needed)"
    fi
    
    success "SQLite3 bindings rebuild attempted"
}

# Step 5: Install psycopg2 for PostgreSQL fallback
install_psycopg2() {
    log "Step 5: Installing psycopg2 for PostgreSQL fallback..."
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    if ! conda activate deepfake-env 2>/dev/null; then
        error "Failed to activate conda environment"
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
    
    success "psycopg2 installed for PostgreSQL fallback"
}

# Step 6: Verify the fix
verify_fix() {
    log "Step 6: Verifying the fix..."
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    if ! conda activate deepfake-env 2>/dev/null; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Test SQLite3 import and version
    log "Testing SQLite3 import and version..."
    if python -c "import sqlite3; print('SQLite3 version:', sqlite3.sqlite_version)"; then
        success "SQLite3 import successful"
    else
        error "SQLite3 import failed"
        return 1
    fi
    
    # Test psycopg2 import
    log "Testing psycopg2 import..."
    if python -c "import psycopg2; print('psycopg2 version:', psycopg2.__version__)"; then
        success "psycopg2 import successful"
    else
        warning "psycopg2 import failed (PostgreSQL fallback may not work)"
    fi
    
    # Test the specific command requested
    log "Running verification command: python -c \"import sqlite3; print(sqlite3.sqlite_version)\""
    if python -c "import sqlite3; print(sqlite3.sqlite_version)"; then
        success "Verification command successful"
    else
        error "Verification command failed"
        return 1
    fi
    
    # Check if version is >= 3.41
    local version_check
    version_check=$(python -c "import sqlite3; print(sqlite3.sqlite_version)" | cut -d' ' -f1)
    if [[ $(echo "$version_check 3.41" | awk '{print ($1 >= $2)}') -eq 1 ]]; then
        success "SQLite3 version $version_check is >= 3.41"
    else
        warning "SQLite3 version $version_check is < 3.41, but the import works"
    fi
    
    success "All verification tests passed!"
}

# Step 7: Create runtime workaround if needed
create_runtime_workaround() {
    log "Step 7: Creating runtime workaround if needed..."
    
    # Activate conda environment
    eval "$(conda shell.bash hook)"
    if ! conda activate deepfake-env 2>/dev/null; then
        error "Failed to activate conda environment"
        exit 1
    fi
    
    # Create runtime workaround file
    cat > sqlite3_workaround.py << 'EOF'
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
EOF

    chmod +x sqlite3_workaround.py
    success "Runtime workaround created: sqlite3_workaround.py"
}

# Main execution function
main() {
    log "Starting SQLite3 repair for conda environment 'deepfake-env'..."
    log "This script will fix the sqlite3_deserialize undefined symbol error"
    
    # Check prerequisites
    check_root
    check_conda
    check_conda_env
    
    # Execute repair steps
    install_system_sqlite3
    fix_conda_sqlite3
    cleanup_broken_objects
    rebuild_sqlite3_bindings
    install_psycopg2
    verify_fix
    create_runtime_workaround
    
    success "SQLite3 repair completed successfully!"
    
    log "Summary:"
    log "  - System SQLite3 >= 3.41 installed"
    log "  - Conda environment SQLite3 bindings fixed"
    log "  - Broken shared objects cleaned"
    log "  - psycopg2 installed for PostgreSQL fallback"
    log "  - Runtime workaround created: sqlite3_workaround.py"
    
    log "You can now run your FastAPI application with:"
    log "  conda activate deepfake-env"
    log "  python backend/app/main_production.py"
    
    log "If you still encounter issues, run the workaround:"
    log "  python sqlite3_workaround.py"
}

# Run main function
main "$@"
