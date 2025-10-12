#!/bin/bash
# Manual Fix Commands for Deepfake Detector

echo "🔧 Manual Deepfake Detector Fix Commands"
echo "========================================"
echo ""
echo "Run these commands one by one in your WSL terminal:"
echo ""

echo "1️⃣ First, activate your conda environment:"
echo "   conda activate deepfake-env"
echo ""

echo "2️⃣ Set CUDA environment variables:"
echo "   export CUDA_VISIBLE_DEVICES=0"
echo "   export CUDA_LAUNCH_BLOCKING=0"
echo "   export TORCH_USE_CUDA_DSA=0"
echo "   export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32,expandable_segments:False"
echo "   export CUDA_CACHE_DISABLE=1"
echo "   export CUDA_MODULE_LOADING=LAZY"
echo ""

echo "3️⃣ Clear corrupted model cache:"
echo "   rm -rf ~/.cache/torch/hub/checkpoints/*"
echo "   rm -rf ~/.cache/torch/checkpoints/*"
echo ""

echo "4️⃣ Test CUDA:"
echo "   python -c \"import torch; print('CUDA Available:', torch.cuda.is_available())\""
echo ""

echo "5️⃣ Test safe model loading:"
echo "   python test_safe_model_loading.py"
echo ""

echo "6️⃣ Start the backend:"
echo "   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level info"
echo ""

echo "📋 If any step fails, try the CPU fallback:"
echo "   export CUDA_VISIBLE_DEVICES=\"\""
echo "   export FORCE_CPU=1"
echo "   export DISABLE_GPU=1"
echo "   uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level info"
echo ""

echo "✅ Copy and paste these commands one by one into your terminal"
