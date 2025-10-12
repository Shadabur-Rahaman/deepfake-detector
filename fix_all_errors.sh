#!/bin/bash
# Comprehensive Fix for All Deepfake Detector Errors

echo "🔧 Comprehensive Deepfake Detector Fix"
echo "======================================"

# Activate conda environment
echo "📋 Step 0: Activating conda environment..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate deepfake-env
echo "✅ Conda environment activated"

# Step 1: Set CUDA environment variables (fixed syntax)
echo ""
echo "📋 Step 1: Setting CUDA environment variables..."
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=0
export TORCH_USE_CUDA_DSA=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32,expandable_segments:False
export CUDA_CACHE_DISABLE=1
export CUDA_MODULE_LOADING=LAZY
export TORCH_CUDA_ARCH_LIST="6.1;7.5;8.6"
echo "✅ CUDA environment variables set"

# Step 2: Clear corrupted model cache
echo ""
echo "📋 Step 2: Clearing corrupted model cache..."
rm -rf ~/.cache/torch/hub/checkpoints/*
rm -rf ~/.cache/torch/checkpoints/*
echo "✅ Model cache cleared"

# Step 3: Test safe model loading
echo ""
echo "📋 Step 3: Testing safe model loading..."
python test_safe_model_loading.py

if [ $? -eq 0 ]; then
    echo "✅ Safe model loading test passed"
else
    echo "⚠️ Safe model loading test failed, but continuing..."
fi

# Step 4: Test CUDA fix
echo ""
echo "📋 Step 4: Testing CUDA fix..."
python -c "
import torch
print('CUDA Available:', torch.cuda.is_available())
if torch.cuda.is_available():
    try:
        device = torch.device('cuda:0')
        test = torch.zeros(1, device=device)
        del test
        torch.cuda.empty_cache()
        print('CUDA test successful!')
    except Exception as e:
        print(f'CUDA test failed: {e}')
        print('Will use CPU fallback')
else:
    print('CUDA not available, will use CPU')
"

# Step 5: Start backend with error handling
echo ""
echo "📋 Step 5: Starting backend with fixes..."
echo "Starting uvicorn with error handling..."

# Set additional safety flags
export FORCE_CPU=0
export DISABLE_GPU=0
export MINIMAL_STARTUP=1

# Start backend
echo "🚀 Starting backend server..."
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level info

echo ""
echo "✅ Comprehensive fix complete!"
echo "📋 If backend started successfully, you can access it at: http://127.0.0.1:8000"
echo "📋 If there are still errors, check the logs above for specific issues"
