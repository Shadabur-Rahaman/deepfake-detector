#!/bin/bash

echo "🚀 Step 1: Removing conflicting NVIDIA/CUDA components..."
sudo apt --purge remove "*cublas*" "*cufft*" "*curand*" "*cusolver*" "*cusparse*" "*npp*" "*nvjpeg*" "cuda*" "nsight*" "nvidia-cuda-toolkit" -y
sudo apt autoremove -y

echo "✅ Step 2: Download CUDA 12.2..."
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda_12.2.0_535.54.03_linux.run

echo "✅ Step 3: Installing CUDA 12.2..."
chmod +x cuda_12.2.0_535.54.03_linux.run
sudo ./cuda_12.2.0_535.54.03_linux.run --silent --toolkit --override

echo "✅ Step 4: Configuring Environment Variables..."
echo 'export PATH=/usr/local/cuda-12.2/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

echo "✅ Step 5: Download cuDNN 8.9 manually"
echo "⚠️ Visit this URL and download cuDNN 8.9 tar for Linux with CUDA 12.2: https://developer.nvidia.com/rdp/cudnn-download"

echo "❗ After downloading, extract and copy files like this:"
echo "  tar -xzvf cudnn-linux-x86_64-8.9.*.tgz"
echo "  sudo cp cuda/include/* /usr/local/cuda-12.2/include/"
echo "  sudo cp cuda/lib64/* /usr/local/cuda-12.2/lib64/"

echo "✅ Step 6: After cuDNN setup, reboot your system."
echo "Then run this to test TensorFlow GPU detection:"
echo "  python -c \"import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))\""
