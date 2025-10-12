# SQLite3 Fix Instructions

This directory contains multiple scripts to fix the `sqlite3_deserialize` undefined symbol error in your conda environment.

## The Problem

You're getting this error:
```
ImportError: _sqlite3.cpython-311-x86_64-linux-gnu.so: undefined symbol: sqlite3_deserialize
```

This happens when Python's sqlite3 module is compiled against an older version of SQLite3 that doesn't have the `sqlite3_deserialize` function.

## Solutions

### Option 1: Python Script (Recommended)

Run the Python script directly:

```bash
python fix_sqlite3_direct.py
```

This script will:
1. Install system SQLite3 >= 3.41
2. Fix conda environment SQLite3 bindings
3. Install psycopg2 for PostgreSQL fallback
4. Clean broken shared objects
5. Verify the fix
6. Create a runtime workaround

### Option 2: Bash Script (Linux/WSL)

If you're on Linux or WSL, you can use the bash script:

```bash
chmod +x fix_sqlite_simple.sh
./fix_sqlite_simple.sh
```

### Option 3: PowerShell Script (Windows)

If you're on Windows PowerShell:

```powershell
.\fix_sqlite.ps1
```

### Option 4: Batch Script (Windows)

If you prefer batch files:

```cmd
fix_sqlite.bat
```

## Manual Steps (If Scripts Fail)

If the automated scripts don't work, you can try these manual steps:

### 1. Install System SQLite3

```bash
sudo apt update
sudo apt install -y libsqlite3-dev sqlite3
```

### 2. Fix Conda Environment

```bash
# Activate your environment
conda activate deepfake-env

# Remove broken packages
conda remove sqlite sqlite3 python-sqlite3 -y --force-remove

# Clean cache
conda clean --all -y

# Reinstall Python with proper SQLite3 support
conda install -c conda-forge python=3.11 -y --force-reinstall

# Install SQLite3 from conda-forge
conda install -c conda-forge sqlite -y

# Install psycopg2 for PostgreSQL fallback
conda install -c conda-forge psycopg2 -y
```

### 3. Clean Broken Objects

```bash
# Find and remove broken shared objects
find $CONDA_PREFIX -name "*_sqlite3*.so" -type f -delete

# Clean Python cache
find $CONDA_PREFIX -name "__pycache__" -type d -exec rm -rf {} +
find $CONDA_PREFIX -name "*.pyc" -type f -delete
```

### 4. Verify the Fix

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

The version should be >= 3.41.

## Runtime Workaround

If you still encounter issues, use the runtime workaround:

```bash
python sqlite3_workaround.py
```

This will:
- Try to use pysqlite3 as an alternative
- Add a dummy `sqlite3_deserialize` function
- Patch the existing sqlite3 module

## Troubleshooting

### If conda activation fails:

```bash
# Initialize conda properly
eval "$(conda shell.bash hook)"

# Or source the conda profile
source $(conda info --base)/etc/profile.d/conda.sh
```

### If you get permission errors:

```bash
# Make sure you have sudo access
sudo -v

# Or run the script with proper permissions
```

### If the environment doesn't exist:

```bash
# Create the environment first
conda create -n deepfake-env python=3.11 -y
```

## Verification

After running any of the scripts, verify the fix:

```bash
# Activate your environment
conda activate deepfake-env

# Test SQLite3
python -c "import sqlite3; print('SQLite3 version:', sqlite3.sqlite_version)"

# Test psycopg2
python -c "import psycopg2; print('psycopg2 version:', psycopg2.__version__)"
```

Both commands should work without errors.

## Files Created

- `sqlite3_workaround.py` - Runtime workaround script
- `fix_sqlite3_direct.py` - Python-based fix script
- `fix_sqlite_simple.sh` - Bash script for Linux/WSL
- `fix_sqlite.ps1` - PowerShell script for Windows
- `fix_sqlite.bat` - Batch script for Windows

## Support

If none of these solutions work, the issue might be:
1. A corrupted conda installation
2. System-level SQLite3 conflicts
3. Python compilation issues

In that case, consider:
1. Recreating the conda environment from scratch
2. Using a different Python version
3. Using a virtual environment instead of conda
