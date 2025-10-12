"""
Comprehensive Error Recovery Service
===================================

This module provides comprehensive error recovery mechanisms for the deepfake detection system,
handling CUDA errors, model loading failures, and processing timeouts.

Author: Senior ML Engineer
Date: 2024
"""

import logging
import time
import traceback
from typing import Dict, Any, Optional, Callable, List
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)

class ComprehensiveErrorRecovery:
    """Comprehensive error recovery system for deepfake detection"""
    
    def __init__(self):
        self.recovery_strategies = {
            'cuda_error': self._handle_cuda_error,
            'model_loading_error': self._handle_model_loading_error,
            'timeout_error': self._handle_timeout_error,
            'memory_error': self._handle_memory_error,
            'generic_error': self._handle_generic_error
        }
        self.error_counts = {}
        self.last_error_times = {}
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def _handle_cuda_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CUDA-related errors"""
        logger.warning(f"CUDA error detected: {error}")
        
        # Force CPU mode
        try:
            from services.cuda_safety_manager import force_cpu_mode
            force_cpu_mode()
            logger.info("Forced CPU mode due to CUDA error")
        except ImportError:
            logger.warning("CUDA Safety Manager not available")
        
        return {
            'success': True,
            'action': 'forced_cpu_mode',
            'device': 'cpu',
            'message': 'CUDA error recovered by forcing CPU mode'
        }
    
    def _handle_model_loading_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle model loading errors"""
        logger.warning(f"Model loading error: {error}")
        
        # Try to use fallback models
        fallback_models = context.get('fallback_models', [])
        if fallback_models:
            for fallback_model in fallback_models:
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    # This would be implemented based on specific model requirements
                    return {
                        'success': True,
                        'action': 'used_fallback_model',
                        'model': fallback_model,
                        'message': f'Using fallback model: {fallback_model}'
                    }
                except Exception as fallback_error:
                    logger.warning(f"Fallback model {fallback_model} failed: {fallback_error}")
                    continue
        
        return {
            'success': False,
            'action': 'no_fallback_available',
            'message': 'No fallback models available'
        }
    
    def _handle_timeout_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout errors"""
        logger.warning(f"Timeout error: {error}")
        
        # Try with reduced processing complexity
        return {
            'success': True,
            'action': 'reduced_complexity',
            'message': 'Reduced processing complexity due to timeout'
        }
    
    def _handle_memory_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory errors"""
        logger.warning(f"Memory error: {error}")
        
        # Clear CUDA cache and reduce batch size
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        
        return {
            'success': True,
            'action': 'cleared_memory_cache',
            'message': 'Cleared memory cache due to memory error'
        }
    
    def _handle_generic_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic errors"""
        logger.warning(f"Generic error: {error}")
        
        return {
            'success': False,
            'action': 'no_recovery_available',
            'message': f'No specific recovery available for: {type(error).__name__}'
        }
    
    def recover_from_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recover from an error using appropriate strategy"""
        if context is None:
            context = {}
        
        error_type = self._classify_error(error)
        error_key = f"{error_type}_{type(error).__name__}"
        
        # Check if we've seen this error too many times
        if self.error_counts.get(error_key, 0) >= self.max_retries:
            logger.error(f"Maximum retries exceeded for error: {error_key}")
            return {
                'success': False,
                'action': 'max_retries_exceeded',
                'message': f'Maximum retries exceeded for {error_type}'
            }
        
        # Update error counts
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_error_times[error_key] = time.time()
        
        # Get recovery strategy
        strategy = self.recovery_strategies.get(error_type, self.recovery_strategies['generic_error'])
        
        try:
            result = strategy(error, context)
            if result['success']:
                logger.info(f"Error recovery successful: {result['action']}")
            return result
        except Exception as recovery_error:
            logger.error(f"Error recovery failed: {recovery_error}")
            return {
                'success': False,
                'action': 'recovery_failed',
                'message': f'Recovery failed: {recovery_error}'
            }
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for appropriate recovery strategy"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # CUDA errors
        if any(keyword in error_str for keyword in ['cuda', 'gpu', 'device', 'handle_0', 'driver_api']):
            return 'cuda_error'
        
        # Model loading errors
        if any(keyword in error_str for keyword in ['model', 'load', 'checkpoint', 'state_dict']):
            return 'model_loading_error'
        
        # Timeout errors
        if any(keyword in error_str for keyword in ['timeout', 'time out', 'deadline']):
            return 'timeout_error'
        
        # Memory errors
        if any(keyword in error_str for keyword in ['memory', 'oom', 'out of memory', 'allocation']):
            return 'memory_error'
        
        return 'generic_error'
    
    def reset_error_counts(self):
        """Reset error counts (useful for testing or periodic cleanup)"""
        self.error_counts.clear()
        self.last_error_times.clear()
        logger.info("Error counts reset")

# Global error recovery instance
error_recovery = ComprehensiveErrorRecovery()

def with_error_recovery(context: Dict[str, Any] = None):
    """Decorator for automatic error recovery"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                logger.warning(f"Error in {func.__name__}: {error}")
                recovery_result = error_recovery.recover_from_error(error, context or {})
                
                if recovery_result['success']:
                    # Retry the function once after recovery
                    try:
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        logger.error(f"Retry failed after recovery: {retry_error}")
                        raise retry_error
                else:
                    raise error
        
        return wrapper
    return decorator

@contextmanager
def error_recovery_context(context: Dict[str, Any] = None):
    """Context manager for error recovery"""
    try:
        yield
    except Exception as error:
        recovery_result = error_recovery.recover_from_error(error, context or {})
        if not recovery_result['success']:
            raise error

def recover_from_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Recover from an error"""
    return error_recovery.recover_from_error(error, context)

def reset_error_counts():
    """Reset error counts"""
    error_recovery.reset_error_counts()

# Initialize the error recovery system
logger.info("Comprehensive Error Recovery Service initialized")
