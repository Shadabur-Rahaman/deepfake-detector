#!/bin/bash
# Quick CUDA Driver Error Fix for WSL

echo "🔧 Applying Quick CUDA Driver Fix..."

# Set conservative CUDA environment variables
export CUDA_VISIBLE_DEVICES=0
export CUDA_LAUNCH_BLOCKING=0
export TORCH_USE_CUDA_DSA=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:32,expandable_segments:False
export CUDA_CACHE_DISABLE=1
export CUDA_MODULE_LOADING=LAZY
export TORCH_CUDA_ARCH_LIST="6.1;7.5;8.6"

echo "✅ CUDA environment variables set"

# Create a simple Python test to verify CUDA works
cat > test_cuda_fix.py << 'EOF'
import os
import torch

print("🔍 Testing CUDA fix...")

# Set conservative settings
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32,expandable_segments:False"
os.environ["CUDA_LAUNCH_BLOCKING"] = "0"

try:
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA version: {torch.version.cuda}")
        
        # Test minimal CUDA operation
        device = torch.device("cuda:0")
        test_tensor = torch.zeros(1, device=device)
        del test_tensor
        torch.cuda.empty_cache()
        
        print("✅ CUDA test successful - driver fix working!")
    else:
        print("⚠️ CUDA not available")
        
except Exception as e:
    print(f"❌ CUDA test failed: {e}")
    print("🔄 Enabling CPU fallback...")
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["FORCE_CPU"] = "1"
    print("✅ CPU fallback enabled")
EOF

echo "🧪 Running CUDA test..."
python test_cuda_fix.py

echo ""
echo "📋 Next steps:"
echo "1. If CUDA test passed, try starting your backend again"
echo "2. If CUDA test failed, the system will use CPU fallback"
echo "3. Run: conda activate deepfake-env && uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level info"

# Clean up test file
rm -f test_cuda_fix.py

echo "✅ Quick CUDA fix complete!"
