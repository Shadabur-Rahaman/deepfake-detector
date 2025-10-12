# 🔧 Detailed Setup Guide

This guide provides step-by-step instructions for setting up the Deepfake Detection System from scratch. Follow these instructions carefully to ensure a successful installation.

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 11, Ubuntu 20.04+, or macOS 12+
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Python**: 3.11+ (3.13 tested)
- **Node.js**: 18+ (20+ recommended)

### Recommended Requirements
- **RAM**: 16GB+
- **Storage**: 20GB+ free space
- **GPU**: NVIDIA RTX 3060+ (optional, CPU mode works fine)
- **CPU**: 8+ cores (Intel i7/AMD Ryzen 7+)

## 🐍 Python Installation

### Windows
1. **Download Python**:
   - Visit [python.org](https://www.python.org/downloads/)
   - Download Python 3.11 or newer
   - **Important**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
   ```cmd
   python --version
   pip --version
   ```

3. **Install Git** (if not installed):
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use default settings during installation

### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python 3.11+
sudo apt install python3.11 python3.11-pip python3.11-venv

# Install Git
sudo apt install git

# Verify installation
python3.11 --version
pip3.11 --version
```

### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install Git
brew install git

# Verify installation
python3.11 --version
pip3.11 --version
```

## 📦 Node.js Installation

### Windows
1. **Download Node.js**:
   - Visit [nodejs.org](https://nodejs.org/)
   - Download LTS version (18+)
   - Run installer with default settings

2. **Verify Installation**:
   ```cmd
   node --version
   npm --version
   ```

### Ubuntu/Debian
```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### macOS
```bash
# Install Node.js
brew install node@18

# Verify installation
node --version
npm --version
```

## 🚀 Project Setup

### 1. Clone Repository
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/deepfake-detector.git
cd deepfake-detector

# Verify files are present
ls -la
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv deepfake-env

# Activate virtual environment
# Windows:
deepfake-env\Scripts\activate
# macOS/Linux:
source deepfake-env/bin/activate

# Verify activation (should show virtual env path)
which python
```

### 3. Install Python Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify key packages
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
```

### 4. Configure Environment
```bash
# Copy configuration template
cp config.env.example config.env

# Edit configuration file
# Windows: notepad config.env
# macOS/Linux: nano config.env
```

#### Required Configuration
Edit `config.env` with your settings:

```env
# Required API Keys (Get these from OpenAI and Google)
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Security (Generate a random 32+ character string)
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# Database (SQLite default - no setup needed)
DATABASE_URL=sqlite:///./deepfake_detection.db

# Server settings
HOST=0.0.0.0
PORT=8000

# CPU Mode (Default - works without GPU)
FORCE_CPU_MODE=1
CUDA_VISIBLE_DEVICES=

# CORS (Frontend URLs)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 5. Get API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Add to `config.env` as `OPENAI_API_KEY`

#### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign up or log in with Google account
3. Click "Create API key"
4. Copy the key
5. Add to `config.env` as `GEMINI_API_KEY`

### 6. Install Frontend Dependencies
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create frontend environment file
cp .env.example .env.local

# Edit frontend environment (optional)
# nano .env.local
```

Frontend `.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

## 🧪 Verification

### 1. Test Backend Installation
```bash
# Navigate to backend
cd backend/app

# Test Python imports
python -c "
import sys
print('Python version:', sys.version)

try:
    import torch
    print('✅ PyTorch:', torch.__version__)
    print('✅ CUDA available:', torch.cuda.is_available())
except ImportError as e:
    print('❌ PyTorch import failed:', e)

try:
    import fastapi
    print('✅ FastAPI:', fastapi.__version__)
except ImportError as e:
    print('❌ FastAPI import failed:', e)

try:
    import cv2
    print('✅ OpenCV:', cv2.__version__)
except ImportError as e:
    print('❌ OpenCV import failed:', e)

try:
    from transformers import AutoTokenizer
    print('✅ Transformers available')
except ImportError as e:
    print('❌ Transformers import failed:', e)
"
```

### 2. Test Model Files
```bash
# Check if model files exist
ls -la ../ml_artifacts/
ls -la models/

# Verify main model files
python -c "
import os
models = [
    '../ml_artifacts/deepfake_detector_finetuned1.pth',
    'models/efficientnet_b0.pth'
]
for model in models:
    if os.path.exists(model):
        size = os.path.getsize(model) / (1024*1024)
        print(f'✅ {model}: {size:.1f} MB')
    else:
        print(f'❌ {model}: Not found')
"
```

### 3. Test Frontend Installation
```bash
# Navigate to frontend
cd ../../frontend

# Test Node.js and npm
node --version
npm --version

# Test build process
npm run build

# Clean up build
rm -rf dist/
```

## 🚀 First Run

### 1. Start Backend Server
```bash
# Navigate to backend
cd backend/app

# Start server
python main.py
```

Expected output:
```
[INFO] Starting FastAPI server...
[OK] Enhanced warning suppression initialized
[OK] CUDA Safety Manager initialized: cpu
[INFO] Device info: {'cuda_available': False, 'fallback_reasons': ['CUDA not available']}
[OK] Services imported successfully
[INFO] Starting server on http://0.0.0.0:8000
```

### 2. Start Frontend (New Terminal)
```bash
# Navigate to frontend
cd frontend

# Start development server
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Verify Installation
1. **Backend**: Visit http://localhost:8000/docs
2. **Frontend**: Visit http://localhost:5173
3. **Test Upload**: Try uploading a test image
4. **Check Logs**: Monitor terminal output for errors

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'torch'"
```bash
# Reinstall PyTorch
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### "CUDA out of memory" or CUDA errors
```bash
# Force CPU mode
export FORCE_CPU_MODE=1
export CUDA_VISIBLE_DEVICES=""
# Or set in config.env
```

#### "Port 8000 already in use"
```bash
# Find and kill process
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

#### "API key invalid"
- Verify API keys are correct
- Check API key permissions
- Ensure no extra spaces in config.env
- Test API keys manually:
```bash
python -c "
import openai
import google.generativeai as genai

# Test OpenAI
try:
    client = openai.OpenAI(api_key='your-key-here')
    print('✅ OpenAI key valid')
except Exception as e:
    print('❌ OpenAI key invalid:', e)

# Test Gemini
try:
    genai.configure(api_key='your-key-here')
    print('✅ Gemini key valid')
except Exception as e:
    print('❌ Gemini key invalid:', e)
"
```

#### "Models not loading"
```bash
# Check model files
ls -la ml_artifacts/
ls -la backend/app/models/

# Verify file permissions
chmod 644 ml_artifacts/*.pth
chmod 644 backend/app/models/*.pth
```

#### "npm install fails"
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Performance Issues

#### Slow detection
- Ensure you have enough RAM (8GB+)
- Close other applications
- Use CPU mode if GPU is causing issues
- Check disk space (models need ~2GB)

#### High memory usage
- Reduce batch size in config
- Use smaller models for testing
- Monitor with task manager/htop

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update Node.js packages
cd frontend
npm update
```

### Backup Configuration
```bash
# Backup your configuration
cp config.env config.env.backup
cp frontend/.env.local frontend/.env.local.backup
```

### Reset Installation
```bash
# Remove virtual environment
rm -rf deepfake-env

# Remove node_modules
rm -rf frontend/node_modules

# Reinstall everything
python -m venv deepfake-env
source deepfake-env/bin/activate  # or deepfake-env\Scripts\activate on Windows
pip install -r requirements.txt
cd frontend && npm install
```

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs** in terminal output
2. **Search GitHub Issues** for similar problems
3. **Create a new issue** with:
   - Your OS and Python/Node.js versions
   - Complete error message
   - Steps to reproduce
   - Configuration (without API keys)

## ✅ Next Steps

After successful installation:

1. **Read the [API Documentation](API_DOCUMENTATION.md)**
2. **Explore the [Model Information](MODELS.md)**
3. **Try the detection features**
4. **Check out the [Contributing Guide](CONTRIBUTING.md)**

Congratulations! You now have a fully functional deepfake detection system. 🎉
