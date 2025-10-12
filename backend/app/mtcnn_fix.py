#!/usr/bin/env python3
"""
Direct MTCNN LooseVersion fix - Nuclear approach
This module patches MTCNN at the system level to fix LooseVersion issues
"""
import sys
import types
import re

def apply_mtcnn_nuclear_fix():
    """Apply nuclear fix for MTCNN LooseVersion issues"""
    print("[START] Applying MTCNN nuclear fix...")
    
    try:
        from packaging.version import Version
        
        class LooseVersion:
            """Complete LooseVersion compatibility class for MTCNN"""
            def __init__(self, vstring=None):
                self.version = []
                self.vstring = vstring
                if vstring:
                    self.parse(vstring)
            
            def parse(self, vstring):
                """Parse version string into components"""
                self.vstring = vstring
                # Split version string into components
                components = re.split(r'[.-]', vstring)
                self.version = []
                for component in components:
                    # Try to convert to int, fallback to string
                    try:
                        self.version.append(int(component))
                    except ValueError:
                        self.version.append(component)
            
            def __str__(self):
                return self.vstring
            
            def __repr__(self):
                return f"LooseVersion('{self.vstring}')"
            
            def __cmp__(self, other):
                """Compare with another version"""
                if isinstance(other, str):
                    other = LooseVersion(other)
                elif not isinstance(other, LooseVersion):
                    return NotImplemented
                
                # Compare version components
                for i in range(max(len(self.version), len(other.version))):
                    a = self.version[i] if i < len(self.version) else 0
                    b = other.version[i] if i < len(other.version) else 0
                    
                    # Handle mixed types
                    if isinstance(a, int) and isinstance(b, str):
                        a = str(a)
                    elif isinstance(a, str) and isinstance(b, int):
                        b = str(b)
                    
                    if a < b:
                        return -1
                    elif a > b:
                        return 1
                return 0
            
            def __lt__(self, other):
                return self.__cmp__(other) < 0
            
            def __le__(self, other):
                return self.__cmp__(other) <= 0
            
            def __eq__(self, other):
                return self.__cmp__(other) == 0
            
            def __ne__(self, other):
                return self.__cmp__(other) != 0
            
            def __ge__(self, other):
                return self.__cmp__(other) >= 0
            
            def __gt__(self, other):
                return self.__cmp__(other) > 0
        
        # Create mock distutils module
        if 'distutils' not in sys.modules:
            mock_distutils = types.ModuleType('distutils')
            sys.modules['distutils'] = mock_distutils
        
        # Create mock distutils.version module
        mock_distutils_version = types.ModuleType('distutils.version')
        mock_distutils_version.LooseVersion = LooseVersion
        
        # Add it to sys.modules so imports work
        if 'distutils.version' not in sys.modules:
            sys.modules['distutils.version'] = mock_distutils_version
        
        # Fix pkgutil.ImpImporter first
        try:
            import pkgutil
            if not hasattr(pkgutil, 'ImpImporter'):
                class ImpImporter:
                    """Mock ImpImporter for Python 3.13 compatibility"""
                    def __init__(self, *args, **kwargs):
                        pass
                    
                    def find_module(self, *args, **kwargs):
                        return None
                    
                    def load_module(self, *args, **kwargs):
                        return None
                
                pkgutil.ImpImporter = ImpImporter
                print("[OK] pkgutil.ImpImporter fixed in MTCNN fix")
        except Exception as e:
            print(f"[WARNING] pkgutil.ImpImporter fix failed: {e}")
        
        # Also patch pkg_resources completely - create a dummy module
        dummy_pkg_resources = types.ModuleType('pkg_resources')
        dummy_pkg_resources.resource_stream = lambda *args, **kwargs: None
        dummy_pkg_resources.resource_string = lambda *args, **kwargs: ""
        dummy_pkg_resources.resource_filename = lambda *args, **kwargs: None
        dummy_pkg_resources.resource_listdir = lambda *args, **kwargs: []
        dummy_pkg_resources.resource_exists = lambda *args, **kwargs: False
        dummy_pkg_resources.get_distribution = lambda *args, **kwargs: None
        dummy_pkg_resources.working_set = lambda *args, **kwargs: []
        dummy_pkg_resources._initialize_master_working_set = lambda: None
        dummy_pkg_resources._call_aside = lambda f: f
        dummy_pkg_resources._handle_ns = lambda *args, **kwargs: None
        dummy_pkg_resources.declare_namespace = lambda *args, **kwargs: None
        dummy_pkg_resources.activate = lambda *args, **kwargs: None
        dummy_pkg_resources.find_spec = lambda *args, **kwargs: None
        dummy_pkg_resources.find_module = lambda *args, **kwargs: None
        
        # Add parse_version function to avoid test failures
        def dummy_parse_version(version_string):
            """Dummy parse_version function that returns a simple version object"""
            class DummyVersion:
                def __init__(self, version_string):
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
            return DummyVersion(version_string)
        
        dummy_pkg_resources.parse_version = dummy_parse_version
        
        # Replace pkg_resources completely
        sys.modules['pkg_resources'] = dummy_pkg_resources
        
        print("[OK] MTCNN nuclear fix applied successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] MTCNN nuclear fix failed: {e}")
        return False

# Apply the fix immediately
apply_mtcnn_nuclear_fix()
