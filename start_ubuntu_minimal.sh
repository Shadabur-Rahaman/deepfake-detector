#!/bin/bash

# Ubuntu-Compatible Minimal Deepfake Detection System Startup Script
# =================================================================

echo "🚀 Starting Ubuntu-Compatible Minimal Deepfake Detection System..."
echo "📊 This version avoids hanging by using minimal imports"
echo "🐧 Ubuntu-compatible version"
echo ""

# Check if conda environment exists
if command -v conda &> /dev/null; then
    echo "🐍 Activating conda environment 'deepfake-env'..."
    conda activate deepfake-env
    if [ $? -eq 0 ]; then
        echo "✅ Conda environment activated successfully"
    else
        echo "⚠️  Warning: Failed to activate conda environment, using current Python"
    fi
else
    echo "⚠️  Warning: Conda not found, using current Python environment"
fi

echo ""
echo "🌐 Server will start on http://127.0.0.1:8000"
echo "📚 API Documentation: http://127.0.0.1:8000/docs"
echo "🔍 Health Check: http://127.0.0.1:8000/health"
echo "🐧 Ubuntu Status: http://127.0.0.1:8000/api/ubuntu/status"
echo ""
echo "Press CTRL+C to stop the server."
echo "============================================================"

# Start the Ubuntu minimal server
python start_ubuntu_minimal.py
