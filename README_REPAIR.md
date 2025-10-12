# Auth System Repair Scripts

This repository contains comprehensive repair scripts to fix common issues with Python authentication systems running in conda environments. The scripts address:

- **PostgreSQL connection issues** (connection refused on localhost:5432)
- **SQLite3 undefined symbol errors** (`sqlite3_deserialize` in `_sqlite3.cpython-311-x86_64-linux-gnu.so`)
- **FallbackConnection object attribute errors**
- **SQLite3 dbapi2 import failures**

## Quick Start

### For Ubuntu/Linux Users
```bash
# Make the script executable
chmod +x repair_auth_system.sh

# Run the repair script
./repair_auth_system.sh
```

### For Windows Users
```cmd
# Option 1: Run the batch file (recommended)
repair_auth_system.bat

# Option 2: Run PowerShell directly
powershell -ExecutionPolicy Bypass -File repair_auth_system_windows.ps1
```

## What the Scripts Do

### 1. PostgreSQL Setup
- **Linux**: Installs PostgreSQL server, creates `ifake_auth` database, sets up user `postgres`
- **Windows**: Verifies PostgreSQL installation and creates the database

### 2. SQLite3 Conda Fix
- Removes broken SQLite3 packages from conda
- Reinstalls Python with proper SQLite3 support
- Installs SQLite3 from conda-forge with proper linking

### 3. Cleanup Broken Objects
- Finds and removes broken `_sqlite3` shared objects
- Cleans Python cache and compiled files
- Reinstalls SQLite3 and psycopg2 Python bindings

### 4. Runtime Patches
- Creates compatibility patches for SQLite3 issues
- Implements fallback connection handling
- Fixes common import and symbol resolution problems

### 5. Verification
- Tests SQLite3 basic operations and version
- Tests PostgreSQL connection and queries
- Verifies both databases work correctly

## Prerequisites

### Linux/Ubuntu
- Ubuntu 18.04+ or similar Linux distribution
- Conda (Anaconda or Miniconda)
- sudo access for system package installation

### Windows
- Windows 10/11
- Conda (Anaconda or Miniconda)
- PowerShell 5.1+
- PostgreSQL installed manually (download from https://www.postgresql.org/download/windows/)

## Manual Installation (Windows)

If you prefer to install PostgreSQL manually on Windows:

1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer with default settings
3. Remember the password you set for the `postgres` user
4. Make sure PostgreSQL service is running
5. Run the repair script

## Verification

After running the repair script, verify the fix:

```bash
# Activate your conda environment
conda activate deepfake-env

# Test both SQLite3 and PostgreSQL
python -c "import sqlite3, psycopg2; print(sqlite3.sqlite_version); print('Postgres OK')"
```

Expected output:
```
SQLite3 version: 3.42.0
Postgres OK
```

## Troubleshooting

### PostgreSQL Issues

#### Linux
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check if port 5432 is listening
sudo netstat -tlnp | grep 5432
```

#### Windows
```cmd
# Check PostgreSQL service
sc query postgresql-x64-14

# Start PostgreSQL service
net start postgresql-x64-14

# Check if port 5432 is listening
netstat -an | findstr 5432
```

### SQLite3 Issues

```bash
# Check SQLite3 version
sqlite3 --version

# Test SQLite3 directly
python -c "import sqlite3; print(sqlite3.sqlite_version)"

# If still failing, try manual reinstall
conda remove sqlite sqlite3 -y
conda install -c conda-forge sqlite -y
```

### Conda Environment Issues

```bash
# Recreate the environment
conda deactivate
conda env remove -n deepfake-env
conda create -n deepfake-env python=3.11 -y
conda activate deepfake-env

# Reinstall packages
pip install -r requirements.txt
```

## Files Created

The repair scripts create several files:

- `backend/app/auth/runtime_patches.py` - SQLite3 compatibility patches
- `test_auth_system.py` - Comprehensive test script
- Various temporary files during execution (cleaned up automatically)

## Advanced Usage

### Custom Conda Environment Name

#### Linux
```bash
# Edit the script to change the environment name
sed -i 's/deepfake-env/your-env-name/g' repair_auth_system.sh
./repair_auth_system.sh
```

#### Windows
```cmd
# Use PowerShell with custom environment name
powershell -ExecutionPolicy Bypass -File repair_auth_system_windows.ps1 -CondaEnv "your-env-name"
```

### Force Reinstall

#### Windows
```cmd
# Force reinstall all packages
powershell -ExecutionPolicy Bypass -File repair_auth_system_windows.ps1 -Force
```

## Testing Your Application

After successful repair, test your authentication system:

```bash
# Activate environment
conda activate deepfake-env

# Run comprehensive test
python test_auth_system.py

# Start your application
python backend/app/main_production.py
```

## Support

If you encounter issues:

1. Check the script output for specific error messages
2. Verify your conda environment is properly activated
3. Ensure you have sufficient permissions for system package installation
4. Check that PostgreSQL service is running
5. Verify network connectivity if using remote databases

The scripts include comprehensive error handling and will stop if any critical step fails, providing clear error messages to help diagnose issues.

## Contributing

If you find issues or have improvements:

1. Check the existing issues
2. Create a new issue with detailed error messages
3. Include your operating system and conda version
4. Provide the full output of the repair script

## License

This repair script is provided as-is for educational and troubleshooting purposes. Use at your own risk.
