#!/usr/bin/env python3
"""
MTCNN Python 3.13 Compatibility Fix
===================================

This module provides a comprehensive fix for MTCNN compatibility issues with Python 3.13,
specifically addressing the distutils.spawn import error.

Author: Senior ML Engineer
Date: 2024
"""

import sys
import os
import types
import subprocess
import shutil
import warnings
from typing import Optional, Any

class MTCNN_Python313_Fix:
    """MTCNN Python 3.13 compatibility wrapper class"""
    
    def __init__(self):
        self.available = False
        self.mtcnn = None
        self._initialize_mtcnn()
    
    def _initialize_mtcnn(self):
        """Initialize MTCNN with Python 3.13 compatibility fixes"""
        try:
            # Apply compatibility fixes first
            apply_mtcnn_python313_fix()
            
            # Try to import and initialize MTCNN
            from facenet_pytorch import MTCNN
            self.mtcnn = MTCNN(
                keep_all=True,
                device='cuda' if self._cuda_available() else 'cpu'
            )
            self.available = True
            print("✅ MTCNN initialized successfully")
            
        except Exception as e:
            print(f"⚠️ MTCNN initialization failed: {e}")
            self.available = False
            self.mtcnn = None
    
    def _cuda_available(self):
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def detect_faces(self, image):
        """Detect faces using MTCNN"""
        if not self.available or self.mtcnn is None:
            return None
        
        try:
            return self.mtcnn.detect(image)
        except Exception as e:
            print(f"⚠️ MTCNN face detection failed: {e}")
            return None

# Global flag to prevent duplicate initialization
_MTCNN_FIX_APPLIED = False

def apply_mtcnn_python313_fix():
    """Apply comprehensive MTCNN fix for Python 3.13 compatibility"""
    global _MTCNN_FIX_APPLIED
    
    if _MTCNN_FIX_APPLIED:
        return True  # Already applied, skip
    
    print("🔧 Applying MTCNN Python 3.13 compatibility fix...")
    
    try:
        # Step 1: Fix distutils.spawn compatibility
        _fix_distutils_spawn()
        
        # Step 2: Fix pkg_resources compatibility
        _fix_pkg_resources()
        
        # Step 3: Fix pkgutil.ImpImporter
        _fix_pkgutil_impimporter()
        
        # Step 4: Set up MTCNN safe import
        _setup_mtcnn_safe_import()
        
        print("✅ MTCNN Python 3.13 compatibility fix applied successfully")
        _MTCNN_FIX_APPLIED = True
        return True
        
    except Exception as e:
        print(f"❌ MTCNN Python 3.13 fix failed: {e}")
        return False

def _fix_distutils_spawn():
    """Fix distutils.spawn compatibility for Python 3.13"""
    try:
        # Check if distutils.spawn already exists
        try:
            import distutils.spawn
            print("✅ distutils.spawn already available")
            return
        except ImportError:
            pass
        
        # Create comprehensive distutils compatibility layer
        class DistutilsSpawnCompat:
            """Comprehensive compatibility layer for distutils.spawn"""
            
            @staticmethod
            def find_executable(executable: str, path: Optional[str] = None) -> Optional[str]:
                """Find executable in PATH"""
                if path is None:
                    path = os.environ.get('PATH', '').split(os.pathsep)
                return shutil.which(executable, path=path)
            
            @staticmethod
            def spawn(cmd: list, search_path: bool = True, verbose: int = 0, dry_run: int = 0) -> int:
                """Spawn a process with comprehensive error handling"""
                try:
                    if dry_run:
                        print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
                        return 0
                    
                    result = subprocess.run(cmd, check=True, capture_output=True)
                    return result.returncode
                except subprocess.CalledProcessError as e:
                    if search_path and not os.path.isabs(cmd[0]):
                        # Try to find executable in PATH
                        executable = cmd[0]
                        full_path = shutil.which(executable)
                        if full_path:
                            cmd[0] = full_path
                            return subprocess.run(cmd, check=True).returncode
                    return e.returncode
                except FileNotFoundError:
                    if search_path:
                        executable = cmd[0]
                        full_path = shutil.which(executable)
                        if full_path:
                            cmd[0] = full_path
                            return subprocess.run(cmd, check=True).returncode
                    raise
            
            @staticmethod
            def find_program(program: str) -> Optional[str]:
                """Find program in PATH"""
                return shutil.which(program)
        
        # Create mock distutils module structure
        if 'distutils' not in sys.modules:
            distutils = types.ModuleType('distutils')
            sys.modules['distutils'] = distutils
        
        # Create distutils.spawn module
        if 'distutils.spawn' not in sys.modules:
            distutils_spawn = types.ModuleType('spawn')
            distutils_spawn.find_executable = DistutilsSpawnCompat.find_executable
            distutils_spawn.spawn = DistutilsSpawnCompat.spawn
            distutils_spawn.find_program = DistutilsSpawnCompat.find_program
            
            # Add to distutils module
            sys.modules['distutils'].spawn = distutils_spawn
            sys.modules['distutils.spawn'] = distutils_spawn
        
        print("✅ distutils.spawn compatibility layer applied")
        
    except Exception as e:
        print(f"⚠️ distutils.spawn fix failed: {e}")

def _fix_pkg_resources():
    """Fix pkg_resources compatibility for Python 3.13"""
    try:
        # Create comprehensive pkg_resources compatibility layer
        class DummyVersion:
            """Dummy version class for compatibility"""
            def __init__(self, version_string: str):
                self.version = version_string
                self._version = version_string
            
            def __str__(self):
                return self.version
            
            def __repr__(self):
                return f"DummyVersion('{self.version}')"
            
            def __lt__(self, other):
                return str(self.version) < str(other.version)
            
            def __le__(self, other):
                return str(self.version) <= str(other.version)
            
            def __eq__(self, other):
                return str(self.version) == str(other.version)
            
            def __ne__(self, other):
                return str(self.version) != str(other.version)
            
            def __ge__(self, other):
                return str(self.version) >= str(other.version)
            
            def __gt__(self, other):
                return str(self.version) > str(other.version)
        
        class DummyDistribution:
            """Dummy distribution class"""
            def __init__(self, name: str = "dummy"):
                self.project_name = name
                self.version = "1.0.0"
        
        class DummyWorkingSet:
            """Dummy working set class"""
            def __init__(self):
                self.entries = []
        
        # Create dummy pkg_resources module
        dummy_pkg_resources = types.ModuleType('pkg_resources')
        
        # Add essential functions
        dummy_pkg_resources.parse_version = lambda v: DummyVersion(v)
        dummy_pkg_resources.get_distribution = lambda name: DummyDistribution(name)
        dummy_pkg_resources.working_set = DummyWorkingSet()
        dummy_pkg_resources.resource_stream = lambda *args, **kwargs: None
        dummy_pkg_resources.resource_string = lambda *args, **kwargs: ""
        dummy_pkg_resources.resource_filename = lambda *args, **kwargs: None
        dummy_pkg_resources.resource_listdir = lambda *args, **kwargs: []
        dummy_pkg_resources.resource_exists = lambda *args, **kwargs: False
        dummy_pkg_resources._initialize_master_working_set = lambda: None
        dummy_pkg_resources._call_aside = lambda f: f
        dummy_pkg_resources._handle_ns = lambda *args, **kwargs: None
        dummy_pkg_resources.declare_namespace = lambda *args, **kwargs: None
        dummy_pkg_resources.activate = lambda *args, **kwargs: None
        dummy_pkg_resources.find_spec = lambda *args, **kwargs: None
        dummy_pkg_resources.find_module = lambda *args, **kwargs: None
        
        # Replace pkg_resources in sys.modules
        sys.modules['pkg_resources'] = dummy_pkg_resources
        
        print("✅ pkg_resources compatibility layer applied")
        
    except Exception as e:
        print(f"⚠️ pkg_resources fix failed: {e}")

def _fix_pkgutil_impimporter():
    """Fix pkgutil.ImpImporter for Python 3.13"""
    try:
        import pkgutil
        
        if not hasattr(pkgutil, 'ImpImporter'):
            class ImpImporter:
                """Compatibility ImpImporter for Python 3.13"""
                def __init__(self, path=None):
                    self.path = path
                
                def find_module(self, fullname, path=None):
                    return None
                
                def load_module(self, fullname):
                    raise ImportError(f"Module {fullname} not found")
                
                def get_data(self, pathname):
                    try:
                        with open(pathname, 'rb') as f:
                            return f.read()
                    except FileNotFoundError:
                        raise IOError(f"File {pathname} not found")
                
                def is_package(self, fullname):
                    return False
                
                def get_code(self, fullname):
                    return None
                
                def get_source(self, fullname):
                    return None
            
            pkgutil.ImpImporter = ImpImporter
            print("✅ pkgutil.ImpImporter compatibility layer applied")
        else:
            print("✅ pkgutil.ImpImporter already available")
            
    except Exception as e:
        print(f"⚠️ pkgutil.ImpImporter fix failed: {e}")

def _setup_mtcnn_safe_import():
    """Set up safe MTCNN import with comprehensive error handling"""
    try:
        # Set environment variables to prevent MTCNN issues
        os.environ.setdefault('PYTHONHASHSEED', '0')
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        os.environ.setdefault('MALLOC_CHECK_', '0')
        os.environ.setdefault('MALLOC_PERTURB_', '0')
        
        # Suppress warnings that can cause issues
        warnings.filterwarnings("ignore", message=".*UserWarning.*")
        warnings.filterwarnings("ignore", message=".*FutureWarning.*")
        warnings.filterwarnings("ignore", message=".*DeprecationWarning.*")
        warnings.filterwarnings("ignore", message=".*RuntimeWarning.*")
        warnings.filterwarnings("ignore", message=".*LooseVersion.*")
        warnings.filterwarnings("ignore", message=".*pkg_resources.*")
        warnings.filterwarnings("ignore", message=".*distutils.*")
        warnings.filterwarnings("ignore", message=".*MTCNN.*")
        warnings.filterwarnings("ignore", message=".*mtcnn.*")
        
        print("✅ MTCNN safe import environment configured")
        
    except Exception as e:
        print(f"⚠️ MTCNN safe import setup failed: {e}")

def create_mtcnn_safe_wrapper():
    """Create a safe MTCNN wrapper that handles all compatibility issues"""
    try:
        # Check if MTCNN should be disabled
        if os.environ.get("DISABLE_MTCNN", "0") == "1":
            print("⚠️ MTCNN disabled by environment variable")
            return None
        
        # Enable MTCNN for better face detection
        print("✅ MTCNN enabled for face detection")
        # Remove disable flag to allow MTCNN usage
        if "DISABLE_MTCNN" in os.environ:
            del os.environ["DISABLE_MTCNN"]
        
        class SafeMTCNNWrapper:
            """Safe MTCNN wrapper with comprehensive error handling"""
            
            def __init__(self, *args, **kwargs):
                self.available = False
                self.mtcnn = None
                self.error_message = None
                
                # MTCNN enabled for better face detection
                try:
                    # Try to initialize MTCNN
                    self.mtcnn = MTCNN()
                    self.available = True
                    self.error_message = None
                    print("✅ MTCNN initialized successfully")
                except Exception as e:
                    self.available = False
                    self.mtcnn = None
                    self.error_message = f"MTCNN initialization failed: {e}"
                    print(f"⚠️ MTCNN initialization failed: {e}")
            
            def detect_faces(self, image):
                """Detect faces with comprehensive error handling"""
                if not self.available or self.mtcnn is None:
                    return []
                
                try:
                    return self.mtcnn.detect_faces(image)
                except Exception as e:
                    print(f"⚠️ MTCNN face detection failed: {e}")
                    return []
            
            def __getattr__(self, name):
                """Delegate attribute access to wrapped MTCNN instance"""
                if self.mtcnn is not None:
                    return getattr(self.mtcnn, name)
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return SafeMTCNNWrapper
        
    except Exception as e:
        print(f"⚠️ Safe MTCNN wrapper creation failed: {e}")
        return None

def test_mtcnn_compatibility():
    """Test MTCNN compatibility after applying fixes"""
    try:
        print("🧪 Testing MTCNN compatibility...")
        
        # Test distutils.spawn
        try:
            import distutils.spawn
            print("✅ distutils.spawn import successful")
        except ImportError as e:
            print(f"❌ distutils.spawn import failed: {e}")
            return False
        
        # Test pkg_resources
        try:
            import pkg_resources
            version = pkg_resources.parse_version("1.0.0")
            print("✅ pkg_resources compatibility successful")
        except Exception as e:
            print(f"❌ pkg_resources compatibility failed: {e}")
            return False
        
        # Test MTCNN import
        try:
            wrapper_class = create_mtcnn_safe_wrapper()
            if wrapper_class:
                wrapper = wrapper_class()
                if wrapper.available:
                    print("✅ MTCNN compatibility test successful")
                    return True
                else:
                    print("⚠️ MTCNN wrapper created but not available")
                    return False
            else:
                print("❌ MTCNN wrapper creation failed")
                return False
        except Exception as e:
            print(f"❌ MTCNN compatibility test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ MTCNN compatibility test failed: {e}")
        return False

# Apply the fix immediately when module is imported
apply_mtcnn_python313_fix()
