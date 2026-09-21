"""
CUDA Safety Manager Module
Provides safe CUDA device management and fallback mechanisms
"""

import logging
import os
import torch
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class CUDASafetyManager:
    """
    Manages CUDA device safety and provides fallback mechanisms
    """
    
    def __init__(self):
        self.safe_device = None
        self.cuda_available = False
        self.device_info = {}
        self.fallback_reasons = []
        
        self._initialize_device()
    
    def _initialize_device(self):
        """Initialize safe device configuration"""
        try:
            # Check if CUDA is forced to be disabled
            if os.environ.get('FORCE_CPU', '').lower() in ('true', '1', 'yes'):
                self.safe_device = 'cpu'
                self.fallback_reasons.append('Force CPU mode enabled')
                logger.info("🔧 Force CPU mode enabled via environment variable")
                return
            
            # Test CUDA availability
            if not torch.cuda.is_available():
                self.safe_device = 'cpu'
                self.fallback_reasons.append('CUDA not available')
                logger.info("🔧 CUDA not available, using CPU")
                return
            
            # Test CUDA devices
            device_count = torch.cuda.device_count()
            if device_count == 0:
                self.safe_device = 'cpu'
                self.fallback_reasons.append('No CUDA devices found')
                logger.info("🔧 No CUDA devices found, using CPU")
                return
            
            # Test each CUDA device
            for device_id in range(device_count):
                try:
                    device_name = f"cuda:{device_id}"
                    
                    # Test basic tensor operations
                    test_tensor = torch.tensor([1.0], device=device_name)
                    result = test_tensor * 2
                    del test_tensor, result
                    
                    # Test memory allocation
                    memory_tensor = torch.randn(100, 100, device=device_name)
                    del memory_tensor
                    
                    # Test CUDA memory management
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
                    
                    # If we get here, the device works
                    self.safe_device = device_name
                    self.cuda_available = True
                    self.device_info = {
                        'device_name': torch.cuda.get_device_name(device_id),
                        'device_id': device_id,
                        'memory_total': torch.cuda.get_device_properties(device_id).total_memory,
                        'memory_allocated': torch.cuda.memory_allocated(device_id),
                        'memory_cached': torch.cuda.memory_reserved(device_id)
                    }
                    
                    logger.info(f"✅ CUDA device {device_id} working correctly: {self.device_info['device_name']}")
                    return
                    
                except Exception as e:
                    error_msg = str(e)
                    if "INTERNAL ASSERT FAILED" in error_msg:
                        logger.warning(f"⚠️ CUDA device {device_id} failed with driver error: {error_msg}")
                        self.fallback_reasons.append(f"CUDA device {device_id} driver error")
                    else:
                        logger.warning(f"⚠️ CUDA device {device_id} failed: {error_msg}")
                        self.fallback_reasons.append(f"CUDA device {device_id} test failed")
                    continue
            
            # If no CUDA devices worked, fall back to CPU
            self.safe_device = 'cpu'
            self.fallback_reasons.append('All CUDA devices failed validation')
            logger.warning("⚠️ All CUDA devices failed, falling back to CPU")
            
        except Exception as e:
            self.safe_device = 'cpu'
            self.fallback_reasons.append(f'CUDA initialization error: {str(e)}')
            logger.error(f"❌ CUDA initialization failed: {e}, using CPU")
    
    def get_safe_device(self) -> str:
        """
        Get the safe device to use
        
        Returns:
            Safe device string ('cpu' or 'cuda:X')
        """
        return self.safe_device or 'cpu'
    
    def is_cuda_available(self) -> bool:
        """
        Check if CUDA is available and working
        
        Returns:
            True if CUDA is available and working
        """
        return self.cuda_available
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get device information
        
        Returns:
            Dictionary containing device information
        """
        return {
            'safe_device': self.safe_device,
            'cuda_available': self.cuda_available,
            'device_info': self.device_info,
            'fallback_reasons': self.fallback_reasons
        }
    
    def force_cpu_mode(self):
        """Force CPU mode"""
        self.safe_device = 'cpu'
        self.cuda_available = False
        self.fallback_reasons.append('Force CPU mode called')
        logger.info("🔧 Forced CPU mode")
    
    def clear_cuda_cache(self):
        """Clear CUDA cache if available"""
        if self.cuda_available and torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
                logger.info("🧹 CUDA cache cleared")
            except Exception as e:
                logger.warning(f"⚠️ Failed to clear CUDA cache: {e}")

# Global instance
_cuda_safety_manager = None

def get_cuda_safety_manager() -> CUDASafetyManager:
    """
    Get global CUDA safety manager instance
    
    Returns:
        CUDASafetyManager instance
    """
    global _cuda_safety_manager
    
    if _cuda_safety_manager is None:
        _cuda_safety_manager = CUDASafetyManager()
    
    return _cuda_safety_manager

def get_safe_device() -> str:
    """
    Get safe device for use
    
    Returns:
        Safe device string
    """
    return get_cuda_safety_manager().get_safe_device()

def is_cuda_safe() -> bool:
    """
    Check if CUDA is safe to use
    
    Returns:
        True if CUDA is safe to use
    """
    return get_cuda_safety_manager().is_cuda_available()

def force_cpu_mode():
    """Force CPU mode globally"""
    get_cuda_safety_manager().force_cpu_mode()

def clear_cuda_cache():
    """Clear CUDA cache globally"""
    get_cuda_safety_manager().clear_cuda_cache()
