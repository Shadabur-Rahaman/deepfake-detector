# 🚨 MANUAL FIX STEPS - Complete Dependency Resolution

## 🔍 **Problem Summary**

Your system has **multiple dependency conflicts**:

1. **numpy 2.2.6** is incompatible with scikit-learn 1.3.2 (needs numpy<2.0)
2. **Missing OpenCV packages** (opencv-python, opencv-python-headless)
3. **PyTorch stack not properly installed**
4. **Package version conflicts** between multiple ML libraries

## ✅ **Solution: Complete Clean Installation**

### **Step 1: COMPLETE CLEANUP (Remove ALL conflicting packages)**

```bash
# Remove PyTorch stack
pip uninstall torch torchvision torchaudio -y

# Remove OpenCV packages
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y

# Remove numpy (the problematic version)
pip uninstall numpy -y

# Remove ML packages that depend on the above
pip uninstall ultralytics mtcnn albumentations imgaug torchmetrics -y

# Remove additional ML dependencies
pip uninstall scikit-learn scipy matplotlib pillow -y
```

### **Step 2: Install COMPATIBLE numpy version**

```bash
pip install numpy==1.26.4
```

**Why this version?**
- ✅ Compatible with scikit-learn 1.3.2 (requires numpy<2.0)
- ✅ Stable and well-tested
- ✅ Works with Python 3.10

### **Step 3: Install OpenCV packages**

```bash
pip install opencv-python==4.9.0.80
pip install opencv-python-headless==4.9.0.80
```

**Why these versions?**
- ✅ Stable OpenCV 4.9.0.80
- ✅ Compatible with numpy 1.26.4
- ✅ Meets requirements for albumentations, imgaug, mtcnn, ultralytics

### **Step 4: Install PyTorch with CUDA 12.1 support**

```bash
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
```

**Why these versions?**
- ✅ **torch 2.1.2+cu121** is compatible with **torchvision 0.16.2+cu121**
- ✅ CUDA 12.1 support
- ✅ No version conflicts between PyTorch components

### **Step 5: Install ML dependencies**

```bash
pip install scikit-learn==1.3.2
pip install scipy==1.11.4
pip install matplotlib==3.8.2
pip install pillow==10.1.0
```

**Why these versions?**
- ✅ **scikit-learn 1.3.2** works with **numpy 1.26.4**
- ✅ All versions are compatible with each other
- ✅ Stable and well-tested

### **Step 6: Install face detection packages**

```bash
pip install ultralytics==8.0.196
pip install mtcnn==0.1.1
```

**Why these versions?**
- ✅ **ultralytics 8.0.196** works with **torch 2.1.2**
- ✅ **mtcnn 0.1.1** works with **opencv-python 4.9.0.80**

### **Step 7: Install additional packages**

```bash
pip install albumentations==2.0.8
pip install imgaug==0.4.0
pip install torchmetrics==1.8.1
```

**Why these versions?**
- ✅ **albumentations 2.0.8** works with **opencv-python-headless 4.9.0.80**
- ✅ **imgaug 0.4.0** works with **opencv-python 4.9.0.80**
- ✅ **torchmetrics 1.8.1** works with **torch 2.1.2**

## 🧪 **Verification Steps**

### **After each step, verify the installation:**

```bash
# Check numpy version
python -c "import numpy; print(f'numpy version: {numpy.__version__}')"

# Check OpenCV
python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"

# Check PyTorch
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"

# Check if CUDA is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### **Run the test scripts:**

```bash
# First, test basic OpenCV
python test_simple_opencv.py

# If successful, test full integration
python test_opencv_fixes.py
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: "Permission denied" during uninstall**
**Solution**: Run as administrator or use `--user` flag
```bash
pip uninstall --user package_name -y
```

### **Issue 2: "Package not found" during uninstall**
**Solution**: This is normal - it means the package wasn't installed
```bash
# Continue to next step
```

### **Issue 3: "pip cache issues"**
**Solution**: Clear pip cache
```bash
pip cache purge
```

### **Issue 4: "Still getting version conflicts"**
**Solution**: Check what's still installed
```bash
pip list | grep -E "(numpy|torch|opencv|scikit)"
```

## ✅ **Expected Final State**

After completing all steps, you should have:

```
Package                    Version
------------------------- ---------
numpy                     1.26.4
opencv-python            4.9.0.80
opencv-python-headless   4.9.0.80
torch                     2.1.2+cu121
torchvision              0.16.2+cu121
torchaudio               2.1.2+cu121
scikit-learn             1.3.2
ultralytics              8.0.196
mtcnn                    0.1.1
albumentations           2.0.8
imgaug                   0.4.0
torchmetrics             1.8.1
```

## 🎯 **Why This Approach Works**

1. **Complete cleanup** removes all conflicting packages
2. **Sequential installation** ensures dependencies are met
3. **Compatible versions** prevent conflicts
4. **Proper order** installs base packages first, then dependent ones

## 🚀 **Alternative: Use the Automated Scripts**

If you prefer automation, use one of these:

**Windows Batch File:**
```cmd
fix_all_dependencies.bat
```

**PowerShell Script:**
```powershell
.\fix_all_dependencies.ps1
```

## 🎉 **After Installation**

Once all dependencies are properly installed:

1. ✅ **No more version conflicts**
2. ✅ **OpenCV works correctly**
3. ✅ **PyTorch stack is stable**
4. ✅ **All ML packages are compatible**
5. ✅ **Your deepfake detector should work without errors**

## 🔍 **Troubleshooting**

If you still encounter issues:

1. **Check Python version**: Ensure you're using Python 3.10
2. **Check pip version**: Update pip if needed: `python -m pip install --upgrade pip`
3. **Check virtual environment**: Ensure you're in the correct virtual environment
4. **Check CUDA**: Verify CUDA 12.1 is properly installed on your system

The manual approach gives you full control over the installation process and helps identify exactly where any issues occur.
