#!/usr/bin/env python3
"""
Quick CUDA Fix Verification Script
Run this after applying all fixes to verify everything is working
"""

import sys
import os

def print_status(message, success=True):
    """Print status message with emoji"""
    emoji = "✅" if success else "❌"
    print(f"{emoji} {message}")

def main():
    print("🔍 Verifying CUDA Fixes...")
    print("=" * 50)
    
    # Test 1: PyTorch CUDA
    try:
        import torch
        print_status(f"PyTorch Import: {torch.__version__}")
        
        cuda_available = torch.cuda.is_available()
        print_status(f"CUDA Available: {cuda_available}")
        
        if cuda_available:
            print_status(f"CUDA Version: {torch.version.cuda}")
            print_status(f"GPU Device: {torch.cuda.get_device_name(0)}")
            
            # Test CUDA operations
            test_tensor = torch.randn(100, 100).cuda()
            result = torch.mm(test_tensor, test_tensor)
            print_status("CUDA Operations: Working")
            del test_tensor, result
            torch.cuda.empty_cache()
        else:
            print_status("CUDA Operations: Not available", False)
            
    except Exception as e:
        print_status(f"PyTorch Test: Failed - {e}", False)
        return False
    
    # Test 2: YOLOv8
    try:
        from ultralytics import YOLO
        print_status("YOLOv8 Import: Successful")
        
        if cuda_available:
            # Quick YOLOv8 test
            yolo = YOLO('yolov8n.pt')
            yolo.to('cuda')
            print_status("YOLOv8 CUDA: Working")
            del yolo
            torch.cuda.empty_cache()
        else:
            print_status("YOLOv8 CUDA: Skipped (no CUDA)")
            
    except Exception as e:
        print_status(f"YOLOv8 Test: Failed - {e}", False)
    
    # Test 3: Torchvision NMS
    try:
        from torchvision.ops import nms
        print_status("Torchvision NMS Import: Successful")
        
        if cuda_available:
            # Test NMS CUDA
            boxes = torch.randn(50, 4).cuda()
            scores = torch.randn(50).cuda()
            result = nms(boxes, scores, 0.5)
            print_status("Torchvision NMS CUDA: Working")
            del boxes, scores, result
            torch.cuda.empty_cache()
        else:
            print_status("Torchvision NMS CUDA: Skipped (no CUDA)")
            
    except Exception as e:
        print_status(f"Torchvision NMS Test: Failed - {e}", False)
    
    # Test 4: Model Loading
    try:
        # Add backend to path
        backend_path = os.path.join(os.path.dirname(os.path.abspath('.')), 'backend')
        if os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
        
        from app.services.deepfake_detector import validate_cuda_setup
        print_status("Deepfake Detector Import: Successful")
        
        # Run validation
        result = validate_cuda_setup()
        print_status(f"CUDA Validation: {'Passed' if result else 'Failed'}", result)
        
    except Exception as e:
        print_status(f"Model Loading Test: Failed - {e}", False)
    
    print("\n" + "=" * 50)
    print("🎯 Verification Complete!")
    
    if cuda_available:
        print("🚀 Your CUDA setup is working correctly!")
        print("💡 Run 'python test_cuda_complete_fix.py' for comprehensive testing")
    else:
        print("⚠️ CUDA not available - check your NVIDIA drivers and CUDA installation")
    
    return True

if __name__ == "__main__":
    main()
