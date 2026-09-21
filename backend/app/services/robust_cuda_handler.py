"""
Robust CUDA Handler - Prevents CUDA Driver Errors and Segmentation Faults
========================================================================

This module provides comprehensive CUDA error handling to prevent the common
CUDA driver errors and segmentation faults.

Author: Senior ML Engineer
Date: 2024
"""

import os
import sys
import logging
import warnings
import torch
from typing import Optional, Dict, Any, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class RobustCUDAHandler:
    """Robust CUDA handler with comprehensive error prevention"""
    
    def __init__(self):
        self.cuda_available = False
        self.safe_device = "cpu"
        self.cuda_devices = []
        self.fallback_reasons = []
        self._initialize_robust_cuda()
    
    def _initialize_robust_cuda(self):
        """Initialize robust CUDA with comprehensive error handling"""
        try:
            # Set CUDA safety environment variables first
            self._set_cuda_safety_env()
            
            # Check for force CPU mode - but only if explicitly set to "1"
            force_cpu = os.environ.get("FORCE_CPU_MODE", "0") == "1"
            
            if force_cpu:
                logger.info("Force CPU mode detected, skipping CUDA initialization")
                self.safe_device = "cpu"
                self.cuda_available = False
                self.fallback_reasons.append("Force CPU mode enabled")
                return
            
            # Test CUDA availability with comprehensive error handling
            self._test_cuda_robustly()
            
        except Exception as e:
            logger.warning(f"Robust CUDA initialization failed: {e}")
            self.safe_device = "cpu"
            self.fallback_reasons.append(f"Initialization failed: {e}")
    
    def _set_cuda_safety_env(self):
        """Set comprehensive CUDA safety environment variables"""
        safety_env = {
            'CUDA_LAUNCH_BLOCKING': '0',
            'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:64',
            'CUDA_CACHE_DISABLE': '1',
            'TORCH_USE_CUDA_DSA': '0',  # Disable DSA to prevent driver issues
            'CUDA_VISIBLE_DEVICES': '0',  # Use only first GPU
            'TF_CPP_MIN_LOG_LEVEL': '3',
            'TF_ENABLE_ONEDNN_OPTS': '0',
            'TF_DISABLE_MKL': '1',
            'TF_FORCE_GPU_ALLOW_GROWTH': 'true',
            'TF_GPU_THREAD_MODE': 'gpu_private',
        }
        
        for key, value in safety_env.items():
            os.environ.setdefault(key, value)
        
        logger.info("Robust CUDA safety environment variables set")
    
    def _test_cuda_robustly(self):
        """Test CUDA availability with robust error handling"""
        try:
            # Test 1: Basic CUDA availability
            if not torch.cuda.is_available():
                self.fallback_reasons.append("CUDA not available")
                return
            
            # Test 2: Device count
            device_count = torch.cuda.device_count()
            if device_count == 0:
                self.fallback_reasons.append("No CUDA devices found")
                return
            
            logger.info(f"Found {device_count} CUDA device(s)")
            
            # Test 3: Safe device testing with comprehensive error handling
            for device_id in range(device_count):
                if self._test_device_robustly(device_id):
                    self.cuda_devices.append({
                        'id': device_id,
                        'name': torch.cuda.get_device_name(device_id),
                        'memory': torch.cuda.get_device_properties(device_id).total_memory
                    })
            
            if self.cuda_devices:
                self.cuda_available = True
                self.safe_device = f"cuda:{self.cuda_devices[0]['id']}"
                logger.info(f"CUDA available, using device: {self.safe_device}")
            else:
                self.fallback_reasons.append("All CUDA devices failed robust testing")
                
        except Exception as e:
            logger.warning(f"CUDA robust testing failed: {e}")
            self.fallback_reasons.append(f"Robust testing failed: {e}")
    
    def _test_device_robustly(self, device_id: int) -> bool:
        """Test CUDA device with comprehensive error handling"""
        try:
            device_name = f"cuda:{device_id}"
            
            # Test 1: Basic tensor operations with minimal memory usage
            test_tensor = torch.tensor([1.0, 2.0, 3.0])
            try:
                test_tensor = test_tensor.to(device_name)
                result = test_tensor * 2
                del test_tensor, result
                torch.cuda.empty_cache()
            except Exception as e:
                error_str = str(e)
                if "INTERNAL ASSERT FAILED" in error_str:
                    logger.warning(f"Device {device_id} CUDA driver error: {error_str}")
                    return False
                elif "CUDA out of memory" in error_str:
                    logger.warning(f"Device {device_id} memory error: {error_str}")
                    return False
                else:
                    logger.warning(f"Device {device_id} tensor test failed: {error_str}")
                    return False
            
            # Test 2: Memory allocation with very small size
            try:
                memory_test = torch.randn(10, 10)  # Very small tensor
                memory_test = memory_test.to(device_name)
                del memory_test
                torch.cuda.empty_cache()
            except Exception as e:
                error_str = str(e)
                if "INTERNAL ASSERT FAILED" in error_str:
                    logger.warning(f"Device {device_id} memory allocation driver error: {error_str}")
                    return False
                else:
                    logger.warning(f"Device {device_id} memory test failed: {error_str}")
                    return False
            
            # Test 3: CUDA synchronization with error handling
            try:
                torch.cuda.synchronize()
            except Exception as e:
                error_str = str(e)
                if "INTERNAL ASSERT FAILED" in error_str:
                    logger.warning(f"Device {device_id} synchronization driver error: {error_str}")
                    return False
                else:
                    logger.warning(f"Device {device_id} synchronization test failed: {error_str}")
                    return False
            
            logger.info(f"Device {device_id} passed robust safety tests")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "INTERNAL ASSERT FAILED" in error_msg:
                logger.warning(f"Device {device_id} failed with CUDA driver error: {error_msg}")
            elif "CUDA out of memory" in error_msg:
                logger.warning(f"Device {device_id} failed with memory error: {error_msg}")
            else:
                logger.warning(f"Device {device_id} failed robust test: {error_msg}")
            return False
    
    def get_safe_device(self) -> str:
        """Get the safest available device"""
        return self.safe_device
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get comprehensive device information"""
        return {
            'safe_device': self.safe_device,
            'cuda_available': self.cuda_available,
            'cuda_devices': self.cuda_devices,
            'fallback_reasons': self.fallback_reasons,
            'device_count': len(self.cuda_devices)
        }
    
    def force_cpu_mode(self):
        """Force CPU mode for all operations"""
        self.safe_device = "cpu"
        self.cuda_available = False
        self.fallback_reasons.append("Forced CPU mode")
        logger.info("Forced CPU mode activated")
    
    def is_cuda_safe(self) -> bool:
        """Check if CUDA is safe to use"""
        return self.cuda_available and self.safe_device != "cpu"
    
    @contextmanager
    def safe_device_context(self, device: Optional[str] = None):
        """Context manager for safe device operations"""
        if device is None:
            device = self.safe_device
        
        try:
            yield device
        except Exception as e:
            logger.warning(f"Device operation failed on {device}: {e}")
            if device != "cpu":
                logger.info("Falling back to CPU")
                yield "cpu"
            else:
                raise

# Global robust CUDA handler instance
robust_cuda_handler = RobustCUDAHandler()

def get_robust_safe_device() -> str:
    """Get the safest available device using robust handler"""
    return robust_cuda_handler.get_safe_device()

def get_robust_device_info() -> Dict[str, Any]:
    """Get comprehensive device information using robust handler"""
    return robust_cuda_handler.get_device_info()

def force_robust_cpu_mode():
    """Force CPU mode using robust handler"""
    robust_cuda_handler.force_cpu_mode()

def is_robust_cuda_safe() -> bool:
    """Check if CUDA is safe to use using robust handler"""
    return robust_cuda_handler.is_cuda_safe()

@contextmanager
def robust_safe_device_context(device: Optional[str] = None):
    """Context manager for safe device operations using robust handler"""
    with robust_cuda_handler.safe_device_context(device) as safe_dev:
        yield safe_dev

# Initialize the robust handler
logger.info("Robust CUDA Handler initialized")
device_info = get_robust_device_info()
logger.info(f"Robust device configuration: {device_info}")
