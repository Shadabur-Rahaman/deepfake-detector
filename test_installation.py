#!/usr/bin/env python3
"""
Deepfake Detection System - Installation Test Script

This script verifies that the installation is working correctly by:
1. Checking Python version and dependencies
2. Verifying model files are present
3. Testing basic imports
4. Checking configuration
5. Testing API endpoints (if server is running)

Usage:
    python test_installation.py
"""

import sys
import os
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

class InstallationTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        
    def log_success(self, message: str):
        print(f"✅ {message}")
        self.success_count += 1
        self.total_tests += 1
        
    def log_warning(self, message: str):
        print(f"⚠️  {message}")
        self.warnings.append(message)
        self.total_tests += 1
        
    def log_error(self, message: str):
        print(f"❌ {message}")
        self.errors.append(message)
        self.total_tests += 1
        
    def log_info(self, message: str):
        print(f"ℹ️  {message}")

    def test_python_version(self) -> bool:
        """Test Python version compatibility"""
        print("\n🐍 Testing Python Version...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            self.log_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            self.log_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
            return False

    def test_dependencies(self) -> bool:
        """Test critical dependencies"""
        print("\n📦 Testing Dependencies...")
        
        critical_deps = [
            ("torch", "PyTorch"),
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("opencv-python", "OpenCV"),
            ("numpy", "NumPy"),
            ("pillow", "Pillow"),
            ("transformers", "Transformers"),
            ("ultralytics", "Ultralytics"),
            ("openai", "OpenAI"),
            ("google.generativeai", "Google Generative AI")
        ]
        
        all_good = True
        for module, name in critical_deps:
            try:
                importlib.import_module(module)
                self.log_success(f"{name} - Available")
            except ImportError as e:
                self.log_error(f"{name} - Missing: {e}")
                all_good = False
                
        return all_good

    def test_model_files(self) -> bool:
        """Test essential model files"""
        print("\n🤖 Testing Model Files...")
        
        essential_models = [
            "ml_artifacts/deepfake_detector_finetuned1.pth",
            "backend/app/models/efficientnet_b0.pth",
            "yolov8n-face.pt"
        ]
        
        all_good = True
        for model_path in essential_models:
            if os.path.exists(model_path):
                size = os.path.getsize(model_path) / (1024 * 1024)  # MB
                self.log_success(f"{model_path} - Present ({size:.1f} MB)")
            else:
                self.log_error(f"{model_path} - Missing")
                all_good = False
                
        # Check for additional model files
        ml_artifacts_dir = Path("ml_artifacts")
        if ml_artifacts_dir.exists():
            model_files = list(ml_artifacts_dir.glob("*.pth"))
            self.log_info(f"Found {len(model_files)} model files in ml_artifacts/")
            
            if len(model_files) < 5:
                self.log_warning(f"Only {len(model_files)} model files found, expected more")
        else:
            self.log_error("ml_artifacts/ directory not found")
            all_good = False
            
        return all_good

    def test_configuration(self) -> bool:
        """Test configuration files"""
        print("\n⚙️  Testing Configuration...")
        
        config_files = [
            ("config.env.example", "Configuration template"),
            ("requirements.txt", "Python dependencies"),
            ("frontend/package.json", "Frontend dependencies"),
            ("frontend/.env.example", "Frontend configuration template")
        ]
        
        all_good = True
        for file_path, description in config_files:
            if os.path.exists(file_path):
                self.log_success(f"{description} - Present")
            else:
                self.log_error(f"{description} - Missing: {file_path}")
                all_good = False
                
        # Check if config.env exists (should be created by user)
        if os.path.exists("config.env"):
            self.log_success("config.env - Present (user configuration)")
        else:
            self.log_warning("config.env - Missing (copy from config.env.example)")
            
        return all_good

    def test_imports(self) -> bool:
        """Test critical imports"""
        print("\n🔍 Testing Critical Imports...")
        
        try:
            # Test backend imports
            sys.path.append("backend/app")
            
            critical_imports = [
                ("main", "Main application"),
                ("services.deepfake_detector", "Deepfake detector"),
                ("services.model_loader", "Model loader"),
                ("routes.detection", "Detection routes"),
                ("auth.database", "Authentication database")
            ]
            
            all_good = True
            for module, description in critical_imports:
                try:
                    importlib.import_module(module)
                    self.log_success(f"{description} - Import successful")
                except ImportError as e:
                    self.log_error(f"{description} - Import failed: {e}")
                    all_good = False
                    
            return all_good
            
        except Exception as e:
            self.log_error(f"Import testing failed: {e}")
            return False

    def test_cuda_availability(self) -> bool:
        """Test CUDA availability"""
        print("\n🎮 Testing CUDA Availability...")
        
        try:
            import torch
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                self.log_success(f"CUDA - Available ({device_count} devices)")
                self.log_info(f"GPU: {device_name}")
                return True
            else:
                self.log_warning("CUDA - Not available (CPU mode will be used)")
                return True  # CPU mode is acceptable
        except ImportError:
            self.log_error("PyTorch not available for CUDA testing")
            return False

    def test_frontend_dependencies(self) -> bool:
        """Test frontend dependencies"""
        print("\n🎨 Testing Frontend Dependencies...")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            self.log_error("Frontend directory not found")
            return False
            
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            self.log_error("package.json not found in frontend directory")
            return False
            
        try:
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                
            required_deps = ["react", "typescript", "vite", "tailwindcss"]
            missing_deps = []
            
            all_deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
            
            for dep in required_deps:
                if not any(dep in pkg for pkg in all_deps.keys()):
                    missing_deps.append(dep)
                    
            if missing_deps:
                self.log_error(f"Missing frontend dependencies: {', '.join(missing_deps)}")
                return False
            else:
                self.log_success("Frontend dependencies - All present")
                return True
                
        except Exception as e:
            self.log_error(f"Frontend dependency check failed: {e}")
            return False

    def test_api_endpoints(self) -> bool:
        """Test API endpoints (if server is running)"""
        print("\n🌐 Testing API Endpoints...")
        
        try:
            import requests
            
            base_url = "http://localhost:8000"
            
            # Test health endpoint
            try:
                response = requests.get(f"{base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    self.log_success("API Health endpoint - Responding")
                    return True
                else:
                    self.log_warning(f"API Health endpoint - Status {response.status_code}")
                    return False
            except requests.exceptions.RequestException:
                self.log_warning("API server not running (start with: python backend/app/main.py)")
                return True  # Not an error, just not running
                
        except ImportError:
            self.log_warning("requests library not available for API testing")
            return True

    def test_file_permissions(self) -> bool:
        """Test file permissions"""
        print("\n📁 Testing File Permissions...")
        
        test_files = [
            "README.md",
            "requirements.txt",
            "config.env.example",
            "backend/app/main.py"
        ]
        
        all_good = True
        for file_path in test_files:
            if os.path.exists(file_path):
                if os.access(file_path, os.R_OK):
                    self.log_success(f"{file_path} - Readable")
                else:
                    self.log_error(f"{file_path} - Not readable")
                    all_good = False
            else:
                self.log_error(f"{file_path} - Not found")
                all_good = False
                
        return all_good

    def test_disk_space(self) -> bool:
        """Test available disk space"""
        print("\n💾 Testing Disk Space...")
        
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            
            free_gb = free // (1024**3)
            total_gb = total // (1024**3)
            
            if free_gb >= 5:  # At least 5GB free
                self.log_success(f"Disk space - {free_gb}GB free of {total_gb}GB total")
                return True
            else:
                self.log_warning(f"Low disk space - {free_gb}GB free (recommend 5GB+)")
                return True  # Warning, not error
                
        except Exception as e:
            self.log_error(f"Disk space check failed: {e}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all installation tests"""
        print("🚀 Deepfake Detection System - Installation Test")
        print("=" * 60)
        
        tests = [
            ("Python Version", self.test_python_version),
            ("Dependencies", self.test_dependencies),
            ("Model Files", self.test_model_files),
            ("Configuration", self.test_configuration),
            ("Critical Imports", self.test_imports),
            ("CUDA Availability", self.test_cuda_availability),
            ("Frontend Dependencies", self.test_frontend_dependencies),
            ("API Endpoints", self.test_api_endpoints),
            ("File Permissions", self.test_file_permissions),
            ("Disk Space", self.test_disk_space)
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log_error(f"{test_name} test failed with exception: {e}")
                results[test_name] = False
                
        return results

    def print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 INSTALLATION TEST SUMMARY")
        print("=" * 60)
        
        print(f"✅ Successful Tests: {self.success_count}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"📊 Total Tests: {self.total_tests}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
                
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        # Overall status
        if not self.errors:
            print(f"\n🎉 INSTALLATION SUCCESSFUL!")
            print("   The Deepfake Detection System is ready to use.")
            print("   Next steps:")
            print("   1. Copy config.env.example to config.env")
            print("   2. Add your OpenAI and Gemini API keys to config.env")
            print("   3. Start the backend: python backend/app/main.py")
            print("   4. Start the frontend: cd frontend && npm run dev")
        else:
            print(f"\n❌ INSTALLATION ISSUES DETECTED")
            print("   Please fix the errors above before proceeding.")
            print("   Check the documentation for troubleshooting help.")
            
        print("\n📚 For help, see:")
        print("   • README.md - Quick start guide")
        print("   • SETUP.md - Detailed installation guide")
        print("   • CONTRIBUTING.md - Development guidelines")

def main():
    """Main function"""
    tester = InstallationTester()
    results = tester.run_all_tests()
    tester.print_summary(results)
    
    # Exit with appropriate code
    if tester.errors:
        sys.exit(1)  # Error exit code
    else:
        sys.exit(0)  # Success exit code

if __name__ == "__main__":
    main()
