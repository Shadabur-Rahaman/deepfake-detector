# Model Dependencies and Troubleshooting Guide

This document provides information about model dependencies, installation instructions, and troubleshooting for the deepfake detection system.

## Model Dependencies

### Required Models
These models are essential for basic deepfake detection functionality:

- **EfficientNet-B0**: Core classification model
- **YOLOv8 Face**: Face detection and extraction

### Optional Models
These models enhance detection capabilities but are not required for basic functionality:

- **MesoNet**: Lightweight CNN for deepfake detection (requires `timm`)
- **ResNet50**: Spatial analysis and artifact detection (requires `torchvision`)
- **Vision Transformer (ViT)**: Advanced spatial analysis (requires `vit-pytorch`)
- **ViViT**: Video-based temporal analysis (requires `vit-pytorch`)
- **LSTM**: Temporal sequence analysis (built into PyTorch)

## Installation Instructions

### Core Dependencies
```bash
# PyTorch (with CUDA support if available)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Basic computer vision
pip install opencv-python pillow numpy

# YOLOv8 for face detection
pip install ultralytics

# EfficientNet and other models
pip install timm
```

### Optional Dependencies
```bash
# Vision Transformer
pip install vit-pytorch

# Additional computer vision tools
pip install scikit-image albumentations

# Video processing
pip install moviepy
```

### Complete Installation
```bash
# Install all dependencies at once
pip install torch torchvision torchaudio ultralytics timm vit-pytorch opencv-python pillow numpy scikit-image albumentations moviepy
```

## Troubleshooting

### Common Issues

#### 1. "TIMM_AVAILABLE" Local Variable Error
**Error**: `cannot access local variable 'TIMM_AVAILABLE' where it is not associated with a value`

**Solution**: This has been fixed in the latest version. The availability flags are now properly managed at module level.

#### 2. YOLOv8 Import Error
**Error**: `ModuleNotFoundError: No module named 'ultralytics'`

**Solution**:
```bash
pip install ultralytics
```

#### 3. TIMM Import Error
**Error**: `ModuleNotFoundError: No module named 'timm'`

**Solution**:
```bash
pip install timm
```

#### 4. Vision Transformer Import Error
**Error**: `ModuleNotFoundError: No module named 'vit_pytorch'`

**Solution**:
```bash
pip install vit-pytorch
```

#### 5. CUDA/GPU Issues
**Error**: CUDA-related errors or models not using GPU

**Solutions**:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For older CUDA versions
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

#### 6. Model Loading Failures
**Error**: Models fail to load during startup

**Solutions**:
1. Check available disk space
2. Verify model files are not corrupted
3. Check internet connection for model downloads
4. Run the startup check tool:
   ```bash
   python backend/app/tools/check_startup_models.py
   ```

### Model-Specific Issues

#### EfficientNet-B0
- **Issue**: Model file not found
- **Solution**: The model will be downloaded automatically on first use

#### YOLOv8 Face Detection
- **Issue**: Face detection not working
- **Solutions**:
  ```bash
  # Download face detection model manually
  python -c "from ultralytics import YOLO; YOLO('yolov8n-face.pt')"
  ```

#### MesoNet
- **Issue**: TIMM dependency issues
- **Solution**: MesoNet will fall back to a pure PyTorch implementation if TIMM is unavailable

#### ResNet50
- **Issue**: Torchvision not available
- **Solution**:
  ```bash
  pip install torchvision
  ```

#### Vision Transformer (ViT)
- **Issue**: vit-pytorch not available
- **Solution**:
  ```bash
  pip install vit-pytorch
  ```

#### ViViT
- **Issue**: vit-pytorch not available
- **Solution**:
  ```bash
  pip install vit-pytorch
  ```

#### LSTM
- **Issue**: LSTM modules not available
- **Solution**: LSTM is built into PyTorch core - check PyTorch installation

### Performance Issues

#### Slow Model Loading
- **Cause**: Large models or slow storage
- **Solutions**:
  - Use SSD storage
  - Enable model caching
  - Use smaller model variants

#### High Memory Usage
- **Cause**: Multiple large models loaded simultaneously
- **Solutions**:
  - Use model batching
  - Implement model unloading
  - Use CPU for non-critical models

#### CUDA Out of Memory
- **Cause**: GPU memory insufficient for all models
- **Solutions**:
  - Reduce batch size
  - Use model offloading
  - Use CPU fallback for some models

## Graceful Degradation

The system is designed to gracefully handle missing optional models:

- **Missing Optional Models**: The system continues to function with available models
- **Ensemble Adaptation**: The ensemble automatically adjusts to use only loaded models
- **Clear Logging**: Missing models are clearly logged with installation hints
- **No Crashes**: Missing optional models do not cause startup failures

### Model Priority
1. **Critical**: EfficientNet-B0, YOLOv8 Face (required for basic functionality)
2. **Important**: MesoNet (enhances detection accuracy)
3. **Optional**: ResNet50, ViT, ViViT, LSTM (provide additional analysis)

## Model Status Checking

### Using the Startup Check Tool
```bash
# Run comprehensive model check
python backend/app/tools/check_startup_models.py
```

### Programmatic Checking
```python
from backend.app.services.model_availability import get_availability_status
from backend.app.services.model_loader import get_startup_summary

# Check availability
status = get_availability_status()
print("Available models:", [k for k, v in status.items() if v])

# Check loading status
summary = get_startup_summary()
print("Loaded models:", summary['successful_models'])
```

## Configuration

### Model Weights
Model weights can be configured in the deterministic configuration:

```python
# Example configuration
model_weights = {
    'efficientnet_b0': 0.25,
    'yolov8_face': 0.15,
    'mesonet': 0.20,
    'resnet50': 0.15,
    'vit': 0.10,
    'vivit': 0.10,
    'lstm': 0.05
}
```

### Device Configuration
```python
# Force CPU usage
device = "cpu"

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"

# Use specific GPU
device = "cuda:0"
```

## Testing

### Unit Tests
```bash
# Run model loading tests
python -m pytest backend/app/tests/test_model_loading.py -v

# Run all tests
python -m pytest backend/app/tests/ -v
```

### Integration Tests
```bash
# Test deterministic behavior
python backend/app/tools/run_deterministic_check.py

# Test model loading
python backend/app/tools/check_startup_models.py
```

## Support

If you encounter issues not covered in this guide:

1. Check the logs for detailed error messages
2. Run the startup check tool
3. Verify all dependencies are installed
4. Check system requirements (Python 3.8+, PyTorch 1.9+)
5. Ensure sufficient disk space and memory

For additional help, please refer to the main project documentation or create an issue with:
- Error messages
- System specifications
- Steps to reproduce
- Output from the startup check tool
