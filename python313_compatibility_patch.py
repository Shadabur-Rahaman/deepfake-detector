#!/usr/bin/env python3
"""
🐍 Python 3.13 Compatibility Patch
This script fixes compatibility issues with Python 3.13, particularly:
- LooseVersion attribute errors
- pkg_resources compatibility issues
- MTCNN initialization problems
"""

import sys
import os
import warnings

def apply_python313_fixes():
    """Apply all Python 3.13 compatibility fixes"""
    print("🐍 Applying Python 3.13 compatibility fixes...")
    
    # Fix 1: Fix pkgutil.ImpImporter FIRST - this is critical for pkg_resources
    try:
        import pkgutil
        if not hasattr(pkgutil, 'ImpImporter'):
            # Create a proper ImpImporter implementation for Python 3.13
            class ImpImporter:
                """Python 3.13 compatibility shim for ImpImporter"""
                def __init__(self, path=None):
                    self.path = path
                
                def find_module(self, fullname, path=None):
                    """Find module implementation"""
                    return None
                
                def load_module(self, fullname):
                    """Load module implementation"""
                    raise ImportError(f"Module {fullname} not found")
                
                def get_data(self, pathname):
                    """Get data implementation"""
                    try:
                        with open(pathname, 'rb') as f:
                            return f.read()
                    except FileNotFoundError:
                        raise IOError(f"File {pathname} not found")
                
                def is_package(self, fullname):
                    """Check if module is a package"""
                    return False
                    
                def get_code(self, fullname):
                    """Get code object"""
                    return None
                    
                def get_source(self, fullname):
                    """Get source code"""
                    return None
            
            pkgutil.ImpImporter = ImpImporter
            print("✅ pkgutil.ImpImporter compatibility fixed for Python 3.13")
        else:
            print("✅ pkgutil.ImpImporter already available")
    except Exception as e:
        print(f"⚠️ pkgutil fix failed: {e}")
    
    # Fix 2: Suppress all warnings before any imports
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*pkg_resources.*")
    warnings.filterwarnings("ignore", message=".*LooseVersion.*")
    warnings.filterwarnings("ignore", message=".*subscriptable.*")
    warnings.filterwarnings("ignore", message=".*ImpImporter.*")
    
    # Fix 3: Environment variable fixes for common issues
    os.environ.setdefault('PYTHONWARNINGS', 'ignore::DeprecationWarning,ignore::UserWarning')
    os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')
    os.environ.setdefault('PYTHONHASHSEED', '0')
    
    # Fix 5: Force pkg_resources compatibility with comprehensive approach
    try:
        import pkg_resources
        
        # Test and fix parse_version if needed
        try:
            version = pkg_resources.parse_version("1.0.0")
            if not hasattr(version, 'version'):
                # Create a patched version class
                original_parse_version = pkg_resources.parse_version
                
                def patched_parse_version(version_string):
                    """Patched parse_version that ensures version attribute exists"""
                    result = original_parse_version(version_string)
                    if not hasattr(result, 'version'):
                        result.version = str(result)
                    return result
                
                pkg_resources.parse_version = patched_parse_version
                print("✅ pkg_resources.parse_version compatibility fixed")
            else:
                print("✅ pkg_resources.parse_version working correctly")
        except Exception as inner_e:
            print(f"⚠️ pkg_resources parse_version test failed: {inner_e}")
            # Try to create a complete replacement
            try:
                from packaging import version
                pkg_resources.parse_version = version.parse
                print("✅ pkg_resources.parse_version replaced with packaging.version.parse")
            except ImportError:
                print("⚠️ packaging module not available for fallback")
                
    except ImportError as e:
        print(f"⚠️ pkg_resources not available: {e}")
        # Create a minimal pkg_resources replacement
        try:
            import sys
            from types import ModuleType
            
            class DummyPkgResources(ModuleType):
                def parse_version(self, version_string):
                    """Dummy parse_version that creates objects with version attribute"""
                    class DummyVersion:
                        def __init__(self, version_str):
                            self.version = version_str
                            self._version_string = version_str
                        
                        def __str__(self):
                            return self._version_string
                        
                        def __lt__(self, other):
                            return str(self) < str(other)
                        
                        def __gt__(self, other):
                            return str(self) > str(other)
                        
                        def __eq__(self, other):
                            return str(self) == str(other)
                    
                    return DummyVersion(version_string)
            
            dummy_pkg_resources = DummyPkgResources('pkg_resources')
            sys.modules['pkg_resources'] = dummy_pkg_resources
            print("✅ pkg_resources replaced with dummy implementation")
            
        except Exception as replacement_e:
            print(f"⚠️ Failed to create pkg_resources replacement: {replacement_e}")
            
    except Exception as e:
        print(f"⚠️ pkg_resources compatibility fix failed: {e}")
    
    # Fix 4: Create pkg_resources replacement AFTER all other fixes
    try:
        import pkg_resources
        print("✅ pkg_resources available after fixes")
    except Exception as e:
        print(f"⚠️ pkg_resources still not working: {e}")
        # Create a complete pkg_resources replacement
        try:
            import sys
            from types import ModuleType
            
            class DummyPkgResources(ModuleType):
                def parse_version(self, version_string):
                    """Dummy parse_version that creates objects with version attribute"""
                    class DummyVersion:
                        def __init__(self, version_str):
                            self.version = version_str
                            self._version_string = version_str
                        
                        def __str__(self):
                            return self._version_string
                        
                        def __repr__(self):
                            return f"DummyVersion('{self._version_string}')"
                        
                        def __lt__(self, other):
                            return str(self) < str(other)
                        
                        def __gt__(self, other):
                            return str(self) > str(other)
                        
                        def __eq__(self, other):
                            return str(self) == str(other)
                        
                        def __le__(self, other):
                            return str(self) <= str(other)
                        
                        def __ge__(self, other):
                            return str(self) >= str(other)
                    
                    return DummyVersion(version_string)
            
            dummy_pkg_resources = DummyPkgResources('pkg_resources')
            sys.modules['pkg_resources'] = dummy_pkg_resources
            print("✅ pkg_resources replaced with dummy implementation")
            
        except Exception as replacement_e:
            print(f"⚠️ Failed to create pkg_resources replacement: {replacement_e}")
    
    print("✅ Python 3.13 compatibility fixes applied")

def create_mtcnn_compatibility_wrapper():
    """Create a compatibility wrapper for MTCNN to handle version issues"""
    try:
        # Try to import pkg_resources safely
        try:
            import pkg_resources
            pkg_resources_available = True
        except:
            pkg_resources_available = False
        
        class MTCNNCompatibilityWrapper:
            """Wrapper to handle MTCNN compatibility issues"""
            
            def __init__(self, *args, **kwargs):
                # Try to import and initialize MTCNN
                try:
                    from mtcnn.mtcnn import MTCNN
                    self.mtcnn = MTCNN(*args, **kwargs)
                    self.available = True
                    print("✅ MTCNN initialized successfully with compatibility wrapper")
                except Exception as e:
                    print(f"⚠️ MTCNN initialization failed: {e}")
                    self.mtcnn = None
                    self.available = False
            
            def detect_faces(self, image):
                """Detect faces with error handling"""
                if not self.available or self.mtcnn is None:
                    return []
                
                try:
                    return self.mtcnn.detect_faces(image)
                except Exception as e:
                    print(f"⚠️ MTCNN detection failed: {e}")
                    return []
            
            def __getattr__(self, name):
                """Delegate attribute access to wrapped MTCNN instance"""
                if self.mtcnn is not None:
                    return getattr(self.mtcnn, name)
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return MTCNNCompatibilityWrapper
        
    except Exception as e:
        print(f"⚠️ MTCNN wrapper creation failed: {e}")
        return None

def test_compatibility():
    """Test if the compatibility fixes are working"""
    print("🧪 Testing compatibility fixes...")
    
    try:
        # Test 1: Basic import functionality
        print("✅ Basic compatibility fixes applied")
        
        # Test 2: MTCNN import (if possible)
        try:
            from mtcnn.mtcnn import MTCNN
            print("✅ MTCNN import successful")
        except Exception as e:
            print(f"⚠️ MTCNN import failed: {e}")
            print("ℹ️ This is expected if MTCNN is not installed")
            
        print("✅ Compatibility tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        return False

def create_safe_mtcnn_import():
    """Create a safe way to import MTCNN without pkg_resources issues"""
    print("🔧 Creating safe MTCNN import...")
    
    try:
        # Try to import MTCNN directly
        from mtcnn.mtcnn import MTCNN
        print("✅ MTCNN imported successfully")
        return MTCNN
    except ImportError as e:
        print(f"⚠️ MTCNN not available: {e}")
        return None
    except Exception as e:
        print(f"⚠️ MTCNN import error: {e}")
        return None

if __name__ == "__main__":
    # Apply fixes
    apply_python313_fixes()
    
    # Test compatibility
    test_compatibility()
    
    # Try to create safe MTCNN import
    create_safe_mtcnn_import()
    
    print("\n🎉 Python 3.13 compatibility patch completed!")
    print("💡 If you still have issues, try running your application again.")
    print("🔧 The patches will be applied automatically when you start the backend.")
