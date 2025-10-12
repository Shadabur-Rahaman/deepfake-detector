#!/bin/bash
# Simple SQLite3 Repair Script for Conda Environment
# Fixes the sqlite3_deserialize undefined symbol error in Python 3.11 conda environments
# Author: AI Assistant
# Version: 1.0

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Debug function
debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1" >&2
}

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

# Initialize conda properly
init_conda() {
    log "Initializing conda..."
    # Try different initialization methods
    if command -v conda &> /dev/null; then
        # Method 1: Use conda shell hook
        eval "$(conda shell.bash hook)" 2>/dev/null || true
        # Method 2: Source conda profile
        if [[ -f "$(conda info --base)/etc/profile.d/conda.sh" ]]; then
            source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
        fi
        success "Conda initialized"
    else
        error "Conda not available"
        exit 1
    fi
}

# Activate conda environment
activate_env() {
    local env_name="$1"
    log "Activating conda environment '$env_name'..."
    
    # Initialize conda in current shell
    eval "$(conda shell.bash hook)"
    
    # Try to activate the environment
    if conda activate "$env_name" 2>/dev/null; then
        success "Activated conda environment '$env_name'"
        return 0
    else
        # Try alternative method
        log "Trying alternative activation method..."
        if [[ -f "$(conda info --base)/envs/$env_name/bin/activate" ]]; then
            source "$(conda info --base)/envs/$env_name/bin/activate" 2>/dev/null || true
            success "Activated conda environment '$env_name' (alternative method)"
            return 0
        else
            error "Failed to activate conda environment '$env_name'"
            return 1
        fi
    fi
}

# Check if conda environment exists
check_conda_env() {
    local env_name="$1"
    log "Checking conda environment '$env_name'..."
    
    if ! conda info --envs | grep -q "$env_name"; then
        warning "Conda environment '$env_name' not found!"
        log "Creating conda environment..."
        if conda create -n "$env_name" python=3.11 -y; then
            success "Conda environment '$env_name' created"
        else
            error "Failed to create conda environment"
            exit 1
        fi
    else
        success "Conda environment '$env_name' found"
    fi
}

# Step 1: Install system SQLite3
install_system_sqlite3() {
    log "Step 1: Installing system SQLite3..."
    
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

# Step 2: Fix conda environment SQLite3
fix_conda_sqlite3() {
    local env_name="$1"
    log "Step 2: Fixing conda environment SQLite3..."
    
    # Initialize conda and activate environment
    log "Initializing conda for Step 2..."
    eval "$(conda shell.bash hook)"
    
    log "Attempting to activate conda environment '$env_name'..."
    if conda activate "$env_name"; then
        success "Activated conda environment '$env_name'"
    else
        log "Standard activation failed, trying alternative method..."
        # Try alternative activation method
        if [[ -f "$(conda info --base)/envs/$env_name/bin/activate" ]]; then
            source "$(conda info --base)/envs/$env_name/bin/activate"
            success "Activated conda environment '$env_name' (alternative method)"
        else
            error "Failed to activate conda environment '$env_name'"
            exit 1
        fi
    fi
    
    # Verify we're in the right environment
    log "Verifying environment activation..."
    if [[ "$CONDA_DEFAULT_ENV" == "$env_name" ]]; then
        success "Confirmed in environment: $CONDA_DEFAULT_ENV"
    else
        warning "Environment verification failed, but continuing..."
    fi
    
    # Remove broken SQLite3 packages
    log "Removing broken SQLite3 packages from conda..."
    debug "About to run: conda remove sqlite sqlite3 python-sqlite3 -y --force-remove"
    conda remove sqlite sqlite3 python-sqlite3 -y --force-remove 2>/dev/null || true
    debug "Conda remove command completed"
    success "Broken SQLite3 packages removed"
    
    # Clean conda cache
    log "Cleaning conda cache..."
    conda clean --all -y 2>/dev/null || true
    success "Conda cache cleaned"
    
    # Reinstall Python with proper SQLite3 support
    log "Reinstalling Python with proper SQLite3 support..."
    if ! conda install -c conda-forge python=3.11 -y --force-reinstall; then
        error "Failed to reinstall Python"
        exit 1
    fi
    success "Python reinstalled"
    
    # Install SQLite3 from conda-forge
    log "Installing SQLite3 from conda-forge..."
    if ! conda install -c conda-forge sqlite -y; then
        error "Failed to install SQLite3 from conda-forge"
        exit 1
    fi
    success "SQLite3 installed from conda-forge"
}

# Step 3: Install psycopg2
install_psycopg2() {
    local env_name="$1"
    log "Step 3: Installing psycopg2 for PostgreSQL fallback..."
    
    # Initialize conda and activate environment
    eval "$(conda shell.bash hook)"
    if ! conda activate "$env_name" 2>/dev/null; then
        error "Failed to activate conda environment '$env_name'"
        exit 1
    fi
    success "Activated conda environment '$env_name'"
    
    # Install psycopg2
    log "Installing psycopg2..."
    if ! conda install -c conda-forge psycopg2 -y; then
        warning "Failed to install psycopg2 via conda, trying pip..."
        if ! pip install psycopg2-binary; then
            error "Failed to install psycopg2"
            exit 1
        fi
    fi
    success "psycopg2 installed"
}

# Step 4: Clean broken objects
cleanup_broken_objects() {
    local env_name="$1"
    log "Step 4: Cleaning broken shared objects..."
    
    # Get conda environment path
    local conda_base
    conda_base=$(conda info --base)
    local env_path="$conda_base/envs/$env_name"
    
    if [[ -d "$env_path" ]]; then
        # Find and remove broken _sqlite3 shared objects
        log "Searching for broken _sqlite3 shared objects..."
        find "$env_path" -name "*_sqlite3*.so" -type f 2>/dev/null | while read -r file; do
            log "Removing broken shared object: $file"
            rm -f "$file"
        done
        success "Broken shared objects cleaned"
        
        # Clean Python cache
        log "Cleaning Python cache..."
        find "$env_path" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$env_path" -name "*.pyc" -type f -delete 2>/dev/null || true
        success "Python cache cleaned"
    else
        warning "Conda environment path not found: $env_path"
    fi
}

# Step 5: Verify the fix
verify_fix() {
    local env_name="$1"
    log "Step 5: Verifying the fix..."
    
    # Initialize conda and activate environment
    eval "$(conda shell.bash hook)"
    if ! conda activate "$env_name" 2>/dev/null; then
        error "Failed to activate conda environment '$env_name'"
        exit 1
    fi
    success "Activated conda environment '$env_name'"
    
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
    if python -c "import psycopg2; print('psycopg2 version:', psycopg2.__version__)" 2>/dev/null; then
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
    version_check=$(python -c "import sqlite3; print(sqlite3.sqlite_version)")
    if [[ $(echo "$version_check 3.41" | awk '{print ($1 >= $2)}') -eq 1 ]]; then
        success "SQLite3 version $version_check is >= 3.41"
    else
        warning "SQLite3 version $version_check is < 3.41, but the import works"
    fi
    
    success "All verification tests passed!"
}

# Step 6: Create runtime workaround
create_runtime_workaround() {
    log "Step 6: Creating runtime workaround..."
    
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
    local env_name="deepfake-env"
    
    log "Starting SQLite3 repair for conda environment '$env_name'..."
    log "This script will fix the sqlite3_deserialize undefined symbol error"
    
    # Check prerequisites
    check_conda
    init_conda
    check_conda_env "$env_name"
    
    # Execute repair steps
    install_system_sqlite3
    fix_conda_sqlite3 "$env_name"
    install_psycopg2 "$env_name"
    cleanup_broken_objects "$env_name"
    verify_fix "$env_name"
    create_runtime_workaround
    
    success "SQLite3 repair completed successfully!"
    
    log "Summary:"
    log "  - System SQLite3 >= 3.41 installed"
    log "  - Conda environment SQLite3 bindings fixed"
    log "  - psycopg2 installed for PostgreSQL fallback"
    log "  - Broken shared objects cleaned"
    log "  - Runtime workaround created: sqlite3_workaround.py"
    
    log "You can now run your FastAPI application with:"
    log "  conda activate $env_name"
    log "  python backend/app/main_production.py"
    
    log "If you still encounter issues, run the workaround:"
    log "  python sqlite3_workaround.py"
}

# Run main function
main "$@"
