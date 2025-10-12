#!/usr/bin/env python3
"""
Complete Deepfake Detection System Setup Script
This script will install all dependencies and configure models properly.
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepfakeSystemSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.advanced_models_dir = self.project_root / "advanced_models"
        self.ml_artifacts_dir = self.project_root / "ml_artifacts"
        
    def run_command(self, command, description):
        """Run a shell command with proper error handling"""
        logger.info(f"🔄 {description}...")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            logger.info(f"✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ {description} failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def install_pip_packages(self):
        """Install all required pip packages"""
        logger.info("📦 Installing pip packages...")
        
        # Core packages
        packages = [
            "ultralytics>=8.0.0",  # Critical for YOLOv8
            "openai>=1.0.0",      # Critical for OpenAI detection
            "torch>=2.0.0",
            "torchvision>=0.15.0",
            "tensorflow>=2.13.0",
            "transformers>=4.35.0",
            "timm>=0.9.12",
            "opencv-python>=4.8.0",
            "pillow>=10.0.0",
            "numpy>=1.24.0",
            "scikit-learn>=1.3.0",
            "mtcnn>=0.1.1",
            "google-generativeai>=0.3.0",
            "yt-dlp>=2023.12.30",
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "aiofiles>=23.2.1",
            "kagglehub>=0.3.0",
            "pytest>=7.4.0",
            "httpx>=0.25.0"
        ]
        
        for package in packages:
            if not self.run_command(f"pip install {package}", f"Installing {package}"):
                logger.warning(f"⚠️ Failed to install {package}, continuing...")
    
    def download_yolo_models(self):
        """Download YOLOv8 models for face detection"""
        logger.info("🤖 Downloading YOLO models...")
        
        yolo_models = {
            "yolov8n-face.pt": "https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8n-face.pt",
            "yolov8n-face-lindevs.pt": "https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8n-face-lindevs.pt"
        }
        
        for model_name, url in yolo_models.items():
            model_path = self.project_root / model_name
            if not model_path.exists():
                logger.info(f"📥 Downloading {model_name}...")
                try:
                    urllib.request.urlretrieve(url, model_path)
                    logger.info(f"✅ Downloaded {model_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to download {model_name}: {e}")
            else:
                logger.info(f"✅ {model_name} already exists")
    
    def setup_model_weights(self):
        """Setup model weights and configurations"""
        logger.info("⚙️ Setting up model weights...")
        
        # Create necessary directories
        (self.project_root / "model_weights").mkdir(exist_ok=True)
        (self.project_root / "configs").mkdir(exist_ok=True)
        
        # Copy existing model files to proper locations
        if self.ml_artifacts_dir.exists():
            for model_file in self.ml_artifacts_dir.glob("*.pth"):
                target_path = self.project_root / "model_weights" / model_file.name
                if not target_path.exists():
                    shutil.copy2(model_file, target_path)
                    logger.info(f"✅ Copied {model_file.name} to model_weights/")
        
        # Create model configuration file
        config_content = {
            "models": {
                "yolov8": {
                    "enabled": True,
                    "model_path": "yolov8n-face.pt",
                    "confidence_threshold": 0.5,
                    "iou_threshold": 0.45
                },
                "mesonet": {
                    "enabled": True,
                    "model_path": "model_weights/meso4_best.pth",
                    "input_size": [256, 256]
                },
                "openai": {
                    "enabled": True,
                    "api_key_env": "OPENAI_API_KEY",
                    "model": "gpt-4o"
                },
                "ensemble": {
                    "enabled": True,
                    "models": ["yolov8", "mesonet", "openai"],
                    "weights": [0.4, 0.4, 0.2]
                }
            },
            "face_detection": {
                "min_face_size": 20,
                "max_face_size": 1000,
                "detection_method": "yolo"
            },
            "processing": {
                "max_frames": 100,
                "frame_interval": 3,
                "batch_size": 8
            }
        }
        
        import json
        config_path = self.project_root / "configs" / "model_config.json"
        with open(config_path, 'w') as f:
            json.dump(config_content, f, indent=2)
        
        logger.info("✅ Model configuration created")
    
    def test_imports(self):
        """Test if all critical imports work"""
        logger.info("🧪 Testing imports...")
        
        test_imports = [
            ("ultralytics", "YOLOv8 models"),
            ("openai", "OpenAI API"),
            ("torch", "PyTorch"),
            ("tensorflow", "TensorFlow"),
            ("transformers", "Transformers library"),
            ("cv2", "OpenCV"),
            ("numpy", "NumPy")
        ]
        
        failed_imports = []
        
        for module, description in test_imports:
            try:
                __import__(module)
                logger.info(f"✅ {description} import successful")
            except ImportError as e:
                logger.error(f"❌ {description} import failed: {e}")
                failed_imports.append(module)
        
        if failed_imports:
            logger.warning(f"⚠️ Failed imports: {', '.join(failed_imports)}")
            return False
        else:
            logger.info("✅ All critical imports successful")
            return True
    
    def test_yolo_model(self):
        """Test YOLOv8 model loading"""
        logger.info("🤖 Testing YOLOv8 model...")
        
        try:
            from ultralytics import YOLO
            
            # Try to load a model
            model = YOLO('yolov8n.pt')
            logger.info("✅ YOLOv8 model loaded successfully")
            
            # Test inference on a dummy image
            import numpy as np
            dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            results = model(dummy_image)
            logger.info("✅ YOLOv8 inference test successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ YOLOv8 test failed: {e}")
            return False
    
    def create_environment_file(self):
        """Create .env file with necessary environment variables"""
        logger.info("🔧 Creating environment file...")
        
        env_content = """# Deepfake Detection System Environment Variables

# OpenAI API Key (required for OpenAI detection)
OPENAI_API_KEY=your_openai_api_key_here

# Google AI API Key (optional, for Gemini detection)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Model paths
YOLO_MODEL_PATH=yolov8n-face.pt
MESONET_MODEL_PATH=model_weights/meso4_best.pth

# Processing settings
MAX_FRAMES=100
FRAME_INTERVAL=3
BATCH_SIZE=8

# Logging
LOG_LEVEL=INFO
"""
        
        env_path = self.project_root / ".env"
        if not env_path.exists():
            with open(env_path, 'w') as f:
                f.write(env_content)
            logger.info("✅ Environment file created")
        else:
            logger.info("✅ Environment file already exists")
    
    def run_complete_setup(self):
        """Run the complete setup process"""
        logger.info("🚀 Starting complete deepfake detection system setup...")
        
        # Step 1: Install packages
        self.install_pip_packages()
        
        # Step 2: Download models
        self.download_yolo_models()
        
        # Step 3: Setup model weights
        self.setup_model_weights()
        
        # Step 4: Create environment file
        self.create_environment_file()
        
        # Step 5: Test imports
        if not self.test_imports():
            logger.warning("⚠️ Some imports failed, but continuing...")
        
        # Step 6: Test YOLO model
        if not self.test_yolo_model():
            logger.warning("⚠️ YOLO model test failed")
        
        logger.info("🎉 Setup completed! Check the logs above for any issues.")
        logger.info("💡 Next steps:")
        logger.info("   1. Set your OpenAI API key in the .env file")
        logger.info("   2. Run: python backend/app/main.py")
        logger.info("   3. Check the logs for model availability")

if __name__ == "__main__":
    setup = DeepfakeSystemSetup()
    setup.run_complete_setup()
