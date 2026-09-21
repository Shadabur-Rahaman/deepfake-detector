#!/usr/bin/env python3
"""
Unified CUDA Manager - Single device configuration, no repeated checks
"""

import os
import logging
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class UnifiedCudaManager:
    """
    Unified CUDA manager that configures device once and provides consistent access
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(UnifiedCudaManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._safe_device: Optional[str] = None
        self._device_info: Optional[Dict[str, Any]] = None
        self._initialized = True
    
    def configure_device(self) -> Dict[str, Any]:
        """Configure device once - no repeated checks"""
        if self._device_info is not None:
            return self._device_info
        
        # Check for forced CPU mode first - but only if explicitly set to "1"
        force_cpu = os.getenv("FORCE_CPU_MODE", "0") == "1"
        
        if force_cpu:
            self._safe_device = "cpu"
            self._device_info = {
                'safe_device': 'cpu',
                'cuda_available': False,
                'cuda_devices': [],
                'fallback_reasons': ['Force CPU mode enabled'],
                'device_count': 0
            }
            logger.info("🔧 Force CPU mode enabled")
            return self._device_info
        
        # Check CUDA availability
        try:
            import torch
            if torch.cuda.is_available():
                self._safe_device = "cuda:0"
                self._device_info = {
                    'safe_device': 'cuda:0',
                    'cuda_available': True,
                    'cuda_devices': [torch.cuda.get_device_name(0)],
                    'fallback_reasons': [],
                    'device_count': torch.cuda.device_count()
                }
                logger.info(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                self._safe_device = "cpu"
                self._device_info = {
                    'safe_device': 'cpu',
                    'cuda_available': False,
                    'cuda_devices': [],
                    'fallback_reasons': ['CUDA not available'],
                    'device_count': 0
                }
                logger.info("💻 Using CPU (CUDA not available)")
        except ImportError:
            self._safe_device = "cpu"
            self._device_info = {
                'safe_device': 'cpu',
                'cuda_available': False,
                'cuda_devices': [],
                'fallback_reasons': ['PyTorch not available'],
                'device_count': 0
            }
            logger.info("💻 Using CPU (PyTorch not available)")
        except Exception as e:
            self._safe_device = "cpu"
            self._device_info = {
                'safe_device': 'cpu',
                'cuda_available': False,
                'cuda_devices': [],
                'fallback_reasons': [f'CUDA error: {e}'],
                'device_count': 0
            }
            logger.warning(f"⚠️ CUDA error, using CPU: {e}")
        
        return self._device_info
    
    def get_safe_device(self) -> str:
        """Get the safe device"""
        if self._safe_device is None:
            self.configure_device()
        return self._safe_device or "cpu"
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        if self._device_info is None:
            self.configure_device()
        return self._device_info or {}
    
    def is_cuda_available(self) -> bool:
        """Check if CUDA is available"""
        if self._device_info is None:
            self.configure_device()
        return self._device_info.get('cuda_available', False)

# Global unified CUDA manager instance (singleton)
unified_cuda_manager = UnifiedCudaManager()

# Backward compatibility functions
def get_safe_device() -> str:
    """Get the safe device"""
    return unified_cuda_manager.get_safe_device()

def get_device_info() -> Dict[str, Any]:
    """Get device information"""
    return unified_cuda_manager.get_device_info()

def is_cuda_available() -> bool:
    """Check if CUDA is available"""
    return unified_cuda_manager.is_cuda_available()

def initialize_global_cuda() -> tuple:
    """Initialize global CUDA and return device info"""
    device_info = unified_cuda_manager.configure_device()
    return unified_cuda_manager.get_safe_device(), device_info.get('cuda_available', False)
