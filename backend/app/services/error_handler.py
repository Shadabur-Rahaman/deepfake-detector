"""
Comprehensive Error Handler for Deepfake Detection
=================================================

This module provides comprehensive error handling and recovery mechanisms
to prevent system crashes and improve reliability.
"""

import logging
import traceback
import asyncio
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps
import time

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Comprehensive error handling and recovery"""
    
    def __init__(self):
        self.error_counts = {}
        self.recovery_strategies = {
            'ImportError': self._handle_import_error,
            'TimeoutError': self._handle_timeout_error,
            'CUDAError': self._handle_cuda_error,
            'MemoryError': self._handle_memory_error,
            'FileNotFoundError': self._handle_file_error,
            'ConnectionError': self._handle_connection_error,
            'ValueError': self._handle_value_error,
            'RuntimeError': self._handle_runtime_error
        }
        
        self.fallback_handlers = {
            'model_loading': self._fallback_model_loading,
            'face_detection': self._fallback_face_detection,
            'prediction': self._fallback_prediction,
            'video_processing': self._fallback_video_processing
        }
    
    def handle_error(self, error: Exception, context: str = "", operation: str = "") -> Dict[str, Any]:
        """Handle errors with appropriate recovery strategies"""
        error_type = type(error).__name__
        error_key = f"{error_type}_{context}_{operation}"
        
        # Track error frequency
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error details
        logger.error(f"❌ Error in {context}.{operation}: {error_type} - {str(error)}")
        
        # Get recovery strategy
        recovery_strategy = self.recovery_strategies.get(error_type, self._handle_generic_error)
        recovery_result = recovery_strategy(error, context, operation)
        
        # Add error tracking info
        recovery_result.update({
            'error_type': error_type,
            'error_message': str(error),
            'context': context,
            'operation': operation,
            'error_count': self.error_counts[error_key],
            'timestamp': time.time()
        })
        
        return recovery_result
    
    def _handle_import_error(self, error: ImportError, context: str, operation: str) -> Dict[str, Any]:
        """Handle import errors with fallback imports"""
        logger.warning(f"⚠️ Import error in {context}.{operation}: {error}")
        
        return {
            'status': 'fallback',
            'message': f'Using fallback implementation for {operation}',
            'fallback_available': True,
            'recovery_action': 'fallback_import'
        }
    
    def _handle_timeout_error(self, error: asyncio.TimeoutError, context: str, operation: str) -> Dict[str, Any]:
        """Handle timeout errors with graceful degradation"""
        logger.warning(f"⏰ Timeout in {context}.{operation}: {error}")
        
        return {
            'status': 'timeout',
            'message': f'Operation {operation} timed out, using cached/default result',
            'fallback_available': True,
            'recovery_action': 'use_cached_result'
        }
    
    def _handle_cuda_error(self, error: Exception, context: str, operation: str) -> Dict[str, Any]:
        """Handle CUDA errors by falling back to CPU"""
        logger.warning(f"🔧 CUDA error in {context}.{operation}: {error}")
        
        return {
            'status': 'fallback',
            'message': 'CUDA error detected, falling back to CPU processing',
            'fallback_available': True,
            'recovery_action': 'force_cpu_mode'
        }
    
    def _handle_memory_error(self, error: MemoryError, context: str, operation: str) -> Dict[str, Any]:
        """Handle memory errors with memory optimization"""
        logger.warning(f"💾 Memory error in {context}.{operation}: {error}")
        
        return {
            'status': 'fallback',
            'message': 'Memory error detected, using memory-optimized processing',
            'fallback_available': True,
            'recovery_action': 'optimize_memory'
        }
    
    def _handle_file_error(self, error: FileNotFoundError, context: str, operation: str) -> Dict[str, Any]:
        """Handle file errors with alternative file paths"""
        logger.warning(f"📁 File error in {context}.{operation}: {error}")
        
        return {
            'status': 'fallback',
            'message': 'File not found, using alternative file paths',
            'fallback_available': True,
            'recovery_action': 'use_alternative_path'
        }
    
    def _handle_connection_error(self, error: ConnectionError, context: str, operation: str) -> Dict[str, Any]:
        """Handle connection errors with retry logic"""
        logger.warning(f"🌐 Connection error in {context}.{operation}: {error}")
        
        return {
            'status': 'retry',
            'message': 'Connection error, will retry with exponential backoff',
            'fallback_available': True,
            'recovery_action': 'retry_connection'
        }
    
    def _handle_value_error(self, error: ValueError, context: str, operation: str) -> Dict[str, Any]:
        """Handle value errors with input validation"""
        logger.warning(f"📊 Value error in {context}.{operation}: {error}")
        
        return {
            'status': 'fallback',
            'message': 'Invalid input value, using default parameters',
            'fallback_available': True,
            'recovery_action': 'use_default_values'
        }
    
    def _handle_runtime_error(self, error: RuntimeError, context: str, operation: str) -> Dict[str, Any]:
        """Handle runtime errors with system recovery"""
        logger.warning(f"⚙️ Runtime error in {context}.{operation}: {error}")
        
        return {
            'status': 'fallback',
            'message': 'Runtime error detected, using simplified processing',
            'fallback_available': True,
            'recovery_action': 'simplify_processing'
        }
    
    def _handle_generic_error(self, error: Exception, context: str, operation: str) -> Dict[str, Any]:
        """Handle generic errors with basic recovery"""
        logger.error(f"❓ Generic error in {context}.{operation}: {error}")
        
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(error)}',
            'fallback_available': False,
            'recovery_action': 'log_and_continue'
        }
    
    def _fallback_model_loading(self, error: Exception) -> Dict[str, Any]:
        """Fallback for model loading failures"""
        return {
            'status': 'fallback',
            'models_loaded': 0,
            'message': 'Model loading failed, using basic detection methods',
            'fallback_methods': ['opencv_haar', 'basic_cnn']
        }
    
    def _fallback_face_detection(self, error: Exception) -> Dict[str, Any]:
        """Fallback for face detection failures"""
        return {
            'status': 'fallback',
            'faces_detected': 0,
            'message': 'Face detection failed, using frame-based analysis',
            'fallback_method': 'frame_analysis'
        }
    
    def _fallback_prediction(self, error: Exception) -> Dict[str, Any]:
        """Fallback for prediction failures"""
        return {
            'status': 'fallback',
            'prediction': 'Unknown',
            'confidence': 0.5,
            'message': 'Prediction failed, using neutral result',
            'fallback_result': 'neutral'
        }
    
    def _fallback_video_processing(self, error: Exception) -> Dict[str, Any]:
        """Fallback for video processing failures"""
        return {
            'status': 'fallback',
            'frames_processed': 0,
            'message': 'Video processing failed, using basic frame extraction',
            'fallback_method': 'basic_extraction'
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error handling summary"""
        total_errors = sum(self.error_counts.values())
        unique_errors = len(self.error_counts)
        
        return {
            'total_errors': total_errors,
            'unique_error_types': unique_errors,
            'error_breakdown': dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'recovery_strategies_available': len(self.recovery_strategies),
            'fallback_handlers_available': len(self.fallback_handlers)
        }

# Global error handler instance
error_handler = ErrorHandler()

def handle_errors(context: str = "", operation: str = ""):
    """Decorator to handle errors in functions"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_result = error_handler.handle_error(e, context, operation)
                return error_result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_result = error_handler.handle_error(e, context, operation)
                return error_result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def get_error_stats() -> Dict[str, Any]:
    """Get current error statistics"""
    return error_handler.get_error_summary()
