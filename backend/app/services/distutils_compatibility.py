"""
Distutils Compatibility Fix for Python 3.13+
Provides compatibility layer for distutils.spawn which was removed in Python 3.13
"""

import sys
import subprocess
import shutil
from typing import Optional

# Compatibility layer for distutils.spawn
class DistutilsSpawnCompat:
    """Compatibility layer for distutils.spawn functionality"""
    
    @staticmethod
    def find_executable(executable: str, path: Optional[str] = None) -> Optional[str]:
        """Find executable in PATH, compatible with Python 3.13+"""
        if path is None:
            path = sys.path
        return shutil.which(executable, path=path)
    
    @staticmethod
    def spawn(cmd: list, search_path: bool = True) -> int:
        """Spawn a process, compatible with Python 3.13+"""
        try:
            return subprocess.run(cmd, check=True).returncode
        except subprocess.CalledProcessError as e:
            return e.returncode
        except FileNotFoundError:
            if search_path:
                # Try to find the executable in PATH
                executable = cmd[0]
                full_path = shutil.which(executable)
                if full_path:
                    cmd[0] = full_path
                    return subprocess.run(cmd, check=True).returncode
            raise

# Monkey patch distutils.spawn if it doesn't exist
try:
    import distutils.spawn
except (ImportError, ModuleNotFoundError):
    # Create a mock distutils module with spawn functionality
    import types
    
    # Create mock distutils module
    distutils = types.ModuleType('distutils')
    distutils.spawn = types.ModuleType('spawn')
    
    # Add the compatibility methods
    distutils.spawn.find_executable = DistutilsSpawnCompat.find_executable
    distutils.spawn.spawn = DistutilsSpawnCompat.spawn
    
    # Inject into sys.modules
    sys.modules['distutils'] = distutils
    sys.modules['distutils.spawn'] = distutils.spawn
    
    print("[OK] Distutils compatibility layer applied for Python 3.13+")
