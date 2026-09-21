"""
Sophisticated Error Recovery Module
Provides advanced error recovery and performance monitoring capabilities
"""

import logging
import time
import functools
from typing import Dict, Any, Optional, Callable, Union
from contextlib import contextmanager
import traceback

logger = logging.getLogger(__name__)

class ErrorRecovery:
    """
    Sophisticated error recovery system
    """
    
    def __init__(self):
        self.recovery_strategies = {}
        self.error_history = []
        self.recovery_stats = {
            'total_errors': 0,
            'recovered_errors': 0,
            'failed_recoveries': 0
        }
        
        logger.info("🛡️ Sophisticated error recovery system initialized")
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable) -> None:
        """
        Register a recovery strategy for a specific error type
        
        Args:
            error_type: Type of error to handle
            strategy: Recovery strategy function
        """
        self.recovery_strategies[error_type] = strategy
        logger.info(f"📝 Registered recovery strategy for: {error_type}")
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """
        Handle an error using registered recovery strategies
        
        Args:
            error: The error to handle
            context: Additional context information
            
        Returns:
            Recovery result or None if no recovery possible
        """
        self.recovery_stats['total_errors'] += 1
        error_type = type(error).__name__
        
        # Log error
        self.error_history.append({
            'error_type': error_type,
            'error_message': str(error),
            'context': context or {},
            'timestamp': time.time(),
            'traceback': traceback.format_exc()
        })
        
        logger.error(f"🚨 Error occurred: {error_type} - {str(error)}")
        
        # Try to find recovery strategy
        if error_type in self.recovery_strategies:
            try:
                result = self.recovery_strategies[error_type](error, context)
                self.recovery_stats['recovered_errors'] += 1
                logger.info(f"✅ Error recovered using strategy: {error_type}")
                return result
            except Exception as recovery_error:
                self.recovery_stats['failed_recoveries'] += 1
                logger.error(f"❌ Recovery failed: {recovery_error}")
                return None
        else:
            logger.warning(f"⚠️ No recovery strategy found for: {error_type}")
            return None
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None) -> None:
        """
        Log an error with error type and message
        
        Args:
            error_type: Type/category of the error
            error_message: Error message
            context: Additional context information
        """
        # Create an exception-like dict for compatibility
        error_entry = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
            'timestamp': time.time(),
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_entry)
        self.recovery_stats['total_errors'] += 1
        logger.error(f"🚨 Error occurred: {error_type} - {error_message}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error recovery statistics
        
        Returns:
            Error recovery statistics
        """
        return {
            'recovery_stats': self.recovery_stats.copy(),
            'recent_errors': self.error_history[-10:],  # Last 10 errors
            'registered_strategies': list(self.recovery_strategies.keys())
        }
    
    def clear_error_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()
        logger.info("🧹 Error history cleared")

class PerformanceMonitor:
    """
    Performance monitoring context manager
    """
    
    def __init__(self, operation_name: str):
        """
        Initialize performance monitor
        
        Args:
            operation_name: Name of the operation being monitored
        """
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        """Enter the performance monitoring context"""
        self.start_time = time.time()
        logger.info(f"⏱️ Starting performance monitoring: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the performance monitoring context"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        if exc_type is None:
            logger.info(f"✅ Performance monitoring completed: {self.operation_name} took {self.duration:.2f}s")
        else:
            logger.error(f"❌ Performance monitoring failed: {self.operation_name} failed after {self.duration:.2f}s")
        
        return False  # Don't suppress exceptions
    
    def get_duration(self) -> Optional[float]:
        """
        Get the duration of the monitored operation
        
        Returns:
            Duration in seconds or None if not completed
        """
        return self.duration

def performance_monitor(operation_name: str) -> PerformanceMonitor:
    """
    Create a performance monitor context manager
    
    Args:
        operation_name: Name of the operation to monitor
        
    Returns:
        PerformanceMonitor context manager
    """
    return PerformanceMonitor(operation_name)

def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on error
    
    Args:
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        backoff: Backoff multiplier for delay
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            current_delay = delay
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"🔄 Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"❌ All retries failed for {func.__name__}: {e}")
                        raise e
            
            raise last_error
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            current_delay = delay
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        logger.warning(f"🔄 Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"❌ All retries failed for {func.__name__}: {e}")
                        raise e
            
            raise last_error
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """
    Safely execute a function and return result with error
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, error)
    """
    try:
        result = func(*args, **kwargs)
        return result, None
    except Exception as e:
        logger.error(f"❌ Safe execution failed: {e}")
        return None, e

async def safe_execute_async(func: Callable, *args, **kwargs) -> tuple[Any, Optional[Exception]]:
    """
    Safely execute an async function and return result with error
    
    Args:
        func: Async function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (result, error)
    """
    try:
        result = await func(*args, **kwargs)
        return result, None
    except Exception as e:
        logger.error(f"❌ Safe async execution failed: {e}")
        return None, e

# Global instances
_error_recovery = None

def get_error_recovery() -> ErrorRecovery:
    """
    Get global error recovery instance
    
    Returns:
        ErrorRecovery instance
    """
    global _error_recovery
    
    if _error_recovery is None:
        _error_recovery = ErrorRecovery()
        
        # Register default recovery strategies
        _error_recovery.register_recovery_strategy('ImportError', lambda e, ctx: None)
        _error_recovery.register_recovery_strategy('ModuleNotFoundError', lambda e, ctx: None)
        _error_recovery.register_recovery_strategy('AttributeError', lambda e, ctx: None)
        _error_recovery.register_recovery_strategy('RuntimeError', lambda e, ctx: None)
    
    return _error_recovery
