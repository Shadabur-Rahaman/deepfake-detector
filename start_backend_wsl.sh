#!/bin/bash
echo "Starting Deepfake Detection Backend for WSL/Conda..."
echo ""
echo "This script starts the backend with proper network binding for WSL/Conda setup."
echo "The backend will be accessible from Windows frontend."
echo ""

# Activate conda environment (adjust environment name if needed)
source ~/miniconda3/etc/profile.d/conda.sh
conda activate deepfake-env

# Start backend with proper host binding
echo "Starting backend on 0.0.0.0:8000..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "Backend started!"
echo "Frontend should connect to: http://0.0.0.0:8000/api"
echo "WebSocket should connect to: ws://0.0.0.0:8000/api/ws/admin"
echo ""
echo "To get your WSL IP for frontend .env file, run: hostname -I"
