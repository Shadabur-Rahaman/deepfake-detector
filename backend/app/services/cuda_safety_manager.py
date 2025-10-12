"""
CUDA Safety Manager - Comprehensive CUDA Error Handling and Device Management
================================================================================

This module provides comprehensive CUDA safety measures to prevent the common
CUDA driver errors like "handle_0 INTERNAL ASSERT FAILED" and ensures graceful
fallback to CPU when CUDA is not available or unstable.

Author: Senior ML Engineer
Date: 2024
"""

import os
import logging
import torch
import warnings
from typing import Optional, Dict, Any, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class CUDASafetyManager:
    """Comprehensive CUDA safety manager with error handling and device management"""
    
    def __init__(self):
        self.cuda_available = False
        self.safe_device = "cpu"
        self.cuda_devices = []
        self.fallback_reasons = []
        self._initialize_safety_measures()
    
    def _initialize_safety_measures(self):
        """Initialize CUDA safety measures"""
        try:
            # Check for force CPU mode
            if (os.environ.get("FORCE_CPU_MODE", "0") == "1" or 
                os.environ.get("CUDA_VISIBLE_DEVICES", "") == "" or
                os.environ.get("MINIMAL_STARTUP_MODE", "0") == "1"):
                logger.info("Force CPU mode detected, skipping CUDA initialization")
                self.safe_device = "cpu"
                self.cuda_available = False
                self.fallback_reasons.append("Force CPU mode enabled")
                return
            
            # Set CUDA safety environment variables
            self._set_cuda_safety_env()
            
            # Test CUDA availability with comprehensive checks
            self._test_cuda_availability()
            
            # Configure PyTorch for stability
            self._configure_pytorch_safety()
            
        except Exception as e:
            logger.warning(f"CUDA safety initialization failed: {e}")
            self.safe_device = "cpu"
            self.fallback_reasons.append(f"Initialization failed: {e}")
    
    def _set_cuda_safety_env(self):
        """Set CUDA safety environment variables"""
        safety_env = {
            'CUDA_LAUNCH_BLOCKING': '0',
            'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:128',
            'CUDA_CACHE_DISABLE': '1',
            'TORCH_USE_CUDA_DSA': '1',
        }
        
        for key, value in safety_env.items():
            os.environ.setdefault(key, value)
        
        logger.info("CUDA safety environment variables set")
    
    def _test_cuda_availability(self):
        """Test CUDA availability with comprehensive error handling"""
        try:
            # Wrap in try-catch to catch driver errors early
            try:
                if not torch.cuda.is_available():
                    self.fallback_reasons.append("CUDA not available")
                    return
            except Exception as cuda_check_error:
                error_str = str(cuda_check_error)
                if "INTERNAL ASSERT FAILED" in error_str or "driver" in error_str.lower():
                    logger.warning(f"CUDA driver error detected: {cuda_check_error}")
                    self.fallback_reasons.append("CUDA driver error")
                    return
                raise
            
            device_count = torch.cuda.device_count()
            if device_count == 0:
                self.fallback_reasons.append("No CUDA devices found")
                return
            
            logger.info(f"Found {device_count} CUDA device(s)")
            
            # Test each device with comprehensive validation
            working_devices = []
            for device_id in range(device_count):
                if self._test_device_safety(device_id):
                    working_devices.append(f"cuda:{device_id}")
                    try:
                        self.cuda_devices.append({
                            'id': device_id,
                            'name': torch.cuda.get_device_name(device_id),
                            'memory': torch.cuda.get_device_properties(device_id).total_memory
                        })
                    except Exception as device_info_error:
                        logger.warning(f"Failed to get device {device_id} info: {device_info_error}")
                        self.cuda_devices.append({
                            'id': device_id,
                            'name': f"CUDA Device {device_id}",
                            'memory': 0
                        })
            
            if working_devices:
                self.cuda_available = True
                self.safe_device = working_devices[0]  # Use first working device
                logger.info(f"CUDA available, using device: {self.safe_device}")
            else:
                self.fallback_reasons.append("All CUDA devices failed validation")
                
        except Exception as e:
            logger.warning(f"CUDA availability test failed: {e}")
            self.fallback_reasons.append(f"Availability test failed: {e}")
    
    def _test_device_safety(self, device_id: int) -> bool:
        """Test if a specific CUDA device is safe to use with enhanced error handling"""
        try:
            device_name = f"cuda:{device_id}"
            
            # Test 1: Basic tensor operations with error handling - create on CPU first
            test_tensor = torch.tensor([1.0, 2.0, 3.0])
            try:
                test_tensor = test_tensor.to(device_name)
                result = test_tensor * 2
                del test_tensor, result
                torch.cuda.empty_cache()
            except Exception as move_error:
                if "INTERNAL ASSERT FAILED" in str(move_error):
                    logger.warning(f"Device {device_id} CUDA driver error")
                    return False
                raise
            
            # Test 2: Memory allocation (smaller size for safety)
            memory_test = torch.randn(50, 50)
            try:
                memory_test = memory_test.to(device_name)
                del memory_test
                torch.cuda.empty_cache()
            except Exception as mem_error:
                if "INTERNAL ASSERT FAILED" in str(mem_error):
                    logger.warning(f"Device {device_id} memory allocation driver error")
                    return False
                raise
            
            # Test 3: CUDA operations with synchronization
            try:
                torch.cuda.synchronize()
            except Exception as sync_error:
                if "INTERNAL ASSERT FAILED" in str(sync_error):
                    logger.warning(f"Device {device_id} synchronization driver error")
                    return False
                raise
            
            # Test 4: Additional safety check - try a simple model operation
            try:
                test_model = torch.nn.Linear(10, 5)
                test_input = torch.randn(1, 10)
                test_model = test_model.to(device_name)
                test_input = test_input.to(device_name)
                _ = test_model(test_input)
                del test_model, test_input
                torch.cuda.empty_cache()
            except Exception as model_error:
                error_str = str(model_error)
                if "INTERNAL ASSERT FAILED" in error_str:
                    logger.warning(f"Device {device_id} model test failed with driver error")
                    return False
                logger.warning(f"Device {device_id} model test failed: {model_error}")
                return False
            
            logger.info(f"Device {device_id} passed safety tests")
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "INTERNAL ASSERT FAILED" in error_msg:
                logger.warning(f"Device {device_id} failed with CUDA driver error: {error_msg}")
            elif "CUDA out of memory" in error_msg:
                logger.warning(f"Device {device_id} failed with memory error: {error_msg}")
            else:
                logger.warning(f"Device {device_id} failed safety test: {error_msg}")
            return False
    
    def _configure_pytorch_safety(self):
        """Configure PyTorch for CUDA safety"""
        try:
            # Configure cuDNN for stability
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                torch.backends.cudnn.enabled = True
            
            # Suppress CUDA warnings
            warnings.filterwarnings("ignore", category=UserWarning, module="torch.cuda")
            
            logger.info("PyTorch CUDA safety configuration applied")
            
        except Exception as e:
            logger.warning(f"PyTorch safety configuration failed: {e}")
    
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
    
    def force_cpu_mode(self):
        """Force CPU mode for all operations"""
        self.safe_device = "cpu"
        self.cuda_available = False
        self.fallback_reasons.append("Forced CPU mode")
        logger.info("Forced CPU mode activated")
    
    def is_cuda_safe(self) -> bool:
        """Check if CUDA is safe to use"""
        return self.cuda_available and self.safe_device != "cpu"

# Global CUDA safety manager instance
cuda_safety_manager = CUDASafetyManager()

def get_safe_device() -> str:
    """Get the safest available device"""
    return cuda_safety_manager.get_safe_device()

def get_device_info() -> Dict[str, Any]:
    """Get comprehensive device information"""
    return cuda_safety_manager.get_device_info()

def force_cpu_mode():
    """Force CPU mode for all operations"""
    cuda_safety_manager.force_cpu_mode()

def is_cuda_safe() -> bool:
    """Check if CUDA is safe to use"""
    return cuda_safety_manager.is_cuda_safe()

@contextmanager
def safe_device_context(device: Optional[str] = None):
    """Context manager for safe device operations"""
    with cuda_safety_manager.safe_device_context(device) as safe_dev:
        yield safe_dev

# Initialize the safety manager
logger.info("CUDA Safety Manager initialized")
device_info = get_device_info()
logger.info(f"Device configuration: {device_info}")
