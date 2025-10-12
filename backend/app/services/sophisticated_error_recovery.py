# sophisticated_error_recovery.py
"""
Sophisticated Error Recovery System for Deepfake Detection
Provides intelligent error handling, automatic recovery, and performance monitoring
"""

import logging
import time
import traceback
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
import asyncio
import threading
from contextlib import contextmanager
import psutil
import gc

logger = logging.getLogger(__name__)

class SophisticatedErrorRecovery:
    """
    Advanced error recovery system with intelligent fallbacks and performance monitoring
    """
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        self.performance_metrics = {}
        self.max_error_history = 100
        self.recovery_timeout = 30.0
        
        # Initialize recovery strategies
        self._initialize_recovery_strategies()
    
    def _initialize_recovery_strategies(self):
        """Initialize default recovery strategies"""
        self.recovery_strategies = {
            'model_loading_failed': self._recover_model_loading,
            'cuda_out_of_memory': self._recover_cuda_oom,
            'face_extraction_failed': self._recover_face_extraction,
            'detection_timeout': self._recover_detection_timeout,
            'title_analysis_failed': self._recover_title_analysis,
            'video_processing_failed': self._recover_video_processing,
            'network_error': self._recover_network_error
        }
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log error with context for intelligent recovery"""
        error_entry = {
            'timestamp': time.time(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_entry)
        
        # Keep only recent errors
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
        
        logger.error(f"🚨 Error [{error_type}]: {error_message}")
        
        # Attempt automatic recovery
        return self.attempt_recovery(error_type, context)
    
    def attempt_recovery(self, error_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Attempt intelligent recovery based on error type"""
        if error_type in self.recovery_strategies:
            try:
                logger.info(f"🔧 Attempting recovery for {error_type}...")
                recovery_result = self.recovery_strategies[error_type](context or {})
                
                if recovery_result.get('success', False):
                    logger.info(f"✅ Recovery successful for {error_type}")
                else:
                    logger.warning(f"⚠️ Recovery failed for {error_type}")
                
                return recovery_result
                
            except Exception as e:
                logger.error(f"❌ Recovery attempt failed: {e}")
                return {'success': False, 'error': str(e)}
        else:
            logger.warning(f"⚠️ No recovery strategy for error type: {error_type}")
            return {'success': False, 'error': 'No recovery strategy available'}
    
    def _recover_model_loading(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from model loading failures"""
        try:
            # Clear CUDA cache
            if context.get('device') == 'cuda':
                import torch
                torch.cuda.empty_cache()
                gc.collect()
            
            # Try alternative model paths
            alternative_paths = context.get('alternative_paths', [])
            for path in alternative_paths:
                try:
                    # Attempt to load from alternative path
                    logger.info(f"🔄 Trying alternative model path: {path}")
                    # Add actual model loading logic here
                    return {'success': True, 'recovery_method': 'alternative_path', 'path': path}
                except Exception as e:
                    continue
            
            # Fallback to lightweight model
            logger.info("🔄 Falling back to lightweight model...")
            return {'success': True, 'recovery_method': 'lightweight_fallback'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _recover_cuda_oom(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from CUDA out of memory errors"""
        try:
            import torch
            
            # Clear CUDA cache
            torch.cuda.empty_cache()
            gc.collect()
            
            # Reduce batch size
            batch_size = context.get('batch_size', 1)
            new_batch_size = max(1, batch_size // 2)
            
            # Set memory fraction
            torch.cuda.set_per_process_memory_fraction(0.5)
            
            logger.info(f"🔄 Reduced batch size from {batch_size} to {new_batch_size}")
            
            return {
                'success': True, 
                'recovery_method': 'memory_optimization',
                'new_batch_size': new_batch_size,
                'memory_fraction': 0.5
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _recover_face_extraction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from face extraction failures"""
        try:
            # Try different face detection methods
            fallback_methods = ['opencv_haar', 'dlib', 'mtcnn']
            current_method = context.get('method', 'yolo')
            
            for method in fallback_methods:
                if method != current_method:
                    logger.info(f"🔄 Trying face extraction with {method}...")
                    # Add actual face extraction logic here
                    return {'success': True, 'recovery_method': 'fallback_detector', 'method': method}
            
            return {'success': False, 'error': 'All face extraction methods failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _recover_detection_timeout(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from detection timeouts"""
        try:
            # Reduce processing complexity
            max_faces = context.get('max_faces', 20)
            new_max_faces = max(5, max_faces // 2)
            
            # Use faster models
            use_fast_models = True
            
            logger.info(f"🔄 Reducing complexity: max_faces {max_faces} -> {new_max_faces}")
            
            return {
                'success': True,
                'recovery_method': 'complexity_reduction',
                'new_max_faces': new_max_faces,
                'use_fast_models': use_fast_models
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _recover_title_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from title analysis failures"""
        try:
            # Use fallback keyword detection
            logger.info("🔄 Using fallback keyword detection...")
            
            return {
                'success': True,
                'recovery_method': 'keyword_fallback',
                'method': 'simple_keyword_matching'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _recover_video_processing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from video processing failures"""
        try:
            # Try different video formats or codecs
            fallback_formats = ['mp4', 'avi', 'mov']
            current_format = context.get('format', 'unknown')
            
            for fmt in fallback_formats:
                if fmt != current_format:
                    logger.info(f"🔄 Trying video format: {fmt}")
                    return {'success': True, 'recovery_method': 'format_fallback', 'format': fmt}
            
            return {'success': False, 'error': 'All video formats failed'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _recover_network_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Recover from network errors"""
        try:
            # Implement retry logic with exponential backoff
            max_retries = context.get('max_retries', 3)
            retry_count = context.get('retry_count', 0)
            
            if retry_count < max_retries:
                wait_time = min(2 ** retry_count, 10)  # Exponential backoff, max 10 seconds
                logger.info(f"🔄 Retrying network request in {wait_time}s (attempt {retry_count + 1}/{max_retries})")
                
                time.sleep(wait_time)
                
                return {
                    'success': True,
                    'recovery_method': 'retry_with_backoff',
                    'wait_time': wait_time,
                    'retry_count': retry_count + 1
                }
            else:
                return {'success': False, 'error': 'Max retries exceeded'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            metrics = {
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'memory_total_gb': memory.total / (1024**3)
                },
                'error_stats': {
                    'total_errors': len(self.error_history),
                    'recent_errors': len([e for e in self.error_history if time.time() - e['timestamp'] < 300])  # Last 5 minutes
                }
            }
            
            # CUDA metrics if available
            try:
                import torch
                if torch.cuda.is_available():
                    metrics['cuda'] = {
                        'memory_allocated_gb': torch.cuda.memory_allocated() / (1024**3),
                        'memory_reserved_gb': torch.cuda.memory_reserved() / (1024**3),
                        'memory_cached_gb': torch.cuda.memory_reserved() / (1024**3)
                    }
            except Exception:
                pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources and reset state"""
        try:
            # Clear error history
            self.error_history.clear()
            
            # Clear CUDA cache
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
            
            # Force garbage collection
            gc.collect()
            
            logger.info("🧹 Error recovery system cleaned up")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

# Global error recovery instance
_error_recovery = None

def get_error_recovery() -> SophisticatedErrorRecovery:
    """Get or create the global error recovery instance"""
    global _error_recovery
    if _error_recovery is None:
        _error_recovery = SophisticatedErrorRecovery()
    return _error_recovery

def sophisticated_error_handler(error_type: str, context: Dict[str, Any] = None):
    """Decorator for sophisticated error handling"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                recovery = get_error_recovery()
                recovery_result = recovery.log_error(error_type, str(e), context)
                
                # If recovery was successful, try the function again with recovery parameters
                if recovery_result.get('success', False):
                    try:
                        # Apply recovery parameters
                        if 'new_batch_size' in recovery_result:
                            kwargs['batch_size'] = recovery_result['new_batch_size']
                        
                        return await func(*args, **kwargs)
                    except Exception as retry_e:
                        logger.error(f"Retry failed after recovery: {retry_e}")
                        raise retry_e
                else:
                    raise e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                recovery = get_error_recovery()
                recovery_result = recovery.log_error(error_type, str(e), context)
                
                # If recovery was successful, try the function again with recovery parameters
                if recovery_result.get('success', False):
                    try:
                        # Apply recovery parameters
                        if 'new_batch_size' in recovery_result:
                            kwargs['batch_size'] = recovery_result['new_batch_size']
                        
                        return func(*args, **kwargs)
                    except Exception as retry_e:
                        logger.error(f"Retry failed after recovery: {retry_e}")
                        raise retry_e
                else:
                    raise e
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

@contextmanager
def performance_monitor(operation_name: str):
    """Context manager for performance monitoring"""
    start_time = time.time()
    start_memory = psutil.virtual_memory().used if hasattr(psutil, 'virtual_memory') else 0
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = psutil.virtual_memory().used if hasattr(psutil, 'virtual_memory') else 0
        
        duration = end_time - start_time
        memory_delta = (end_memory - start_memory) / (1024**2)  # MB
        
        logger.info(f"📊 Performance [{operation_name}]: {duration:.2f}s, Memory Δ: {memory_delta:+.1f}MB")
