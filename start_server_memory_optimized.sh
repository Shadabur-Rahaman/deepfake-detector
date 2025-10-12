#!/bin/bash

# Memory-Optimized Server Startup Script
# =====================================
# This script starts the server with memory optimizations for limited GPU memory

echo "🚀 Starting Deepfake Detector with Memory Optimization"
echo "======================================================"

# Set memory optimization environment variables
export MODEL_LOADING_VERBOSE=false
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:64,expandable_segments:True"
export CUDA_VISIBLE_DEVICES=0
export MEMORY_OPTIMIZED=true
export MINIMAL_STARTUP=1
export DISABLE_ENSEMBLE_LOADING=1

# Optional: Set fast startup mode
export FAST_STARTUP=true

echo "💾 Memory optimization settings:"
echo "  - MODEL_LOADING_VERBOSE: $MODEL_LOADING_VERBOSE"
echo "  - PYTORCH_CUDA_ALLOC_CONF: $PYTORCH_CUDA_ALLOC_CONF"
echo "  - MEMORY_OPTIMIZED: $MEMORY_OPTIMIZED"
echo "  - MINIMAL_STARTUP: $MINIMAL_STARTUP"
echo "  - FAST_STARTUP: $FAST_STARTUP"
echo ""

# Check if conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" == "deepfake-env" ]]; then
    echo "✅ Conda environment 'deepfake-env' is active"
else
    echo "⚠️  Warning: Conda environment 'deepfake-env' is not active"
    echo "   Please run: conda activate deepfake-env"
    echo ""
fi

# Start the server
echo "🚀 Starting server with memory optimization..."
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 --log-level info

echo ""
echo "🛑 Server stopped"
