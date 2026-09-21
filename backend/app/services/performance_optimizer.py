"""
Performance Optimizer for Deepfake Detection
============================================

This module provides performance optimization utilities to prevent timeouts
and improve overall system performance.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.timeout_configs = {
            'model_initialization': 60.0,
            'model_prediction': 90.0,
            'face_extraction': 120.0,
            'advanced_ai_analysis': 20.0,
            'aggressive_detection': 30.0,
            'clip_detection': 30.0,
            'vision_transformer': 45.0,
            'ultra_ensemble_init': 60.0,
            'ultra_ensemble_pred': 90.0
        }
        
        self.performance_stats = {
            'total_operations': 0,
            'timeout_operations': 0,
            'average_time': 0.0,
            'slow_operations': []
        }
    
    def with_timeout(self, operation_name: str, timeout: Optional[float] = None):
        """Decorator to add timeout to async operations"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                operation_timeout = timeout or self.timeout_configs.get(operation_name, 30.0)
                start_time = time.time()
                
                try:
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=operation_timeout)
                    execution_time = time.time() - start_time
                    
                    # Update performance stats
                    self.performance_stats['total_operations'] += 1
                    self.performance_stats['average_time'] = (
                        (self.performance_stats['average_time'] * (self.performance_stats['total_operations'] - 1) + execution_time) 
                        / self.performance_stats['total_operations']
                    )
                    
                    if execution_time > operation_timeout * 0.8:  # 80% of timeout
                        self.performance_stats['slow_operations'].append({
                            'operation': operation_name,
                            'time': execution_time,
                            'timeout': operation_timeout
                        })
                    
                    logger.info(f"✅ {operation_name} completed in {execution_time:.2f}s")
                    return result
                    
                except asyncio.TimeoutError:
                    execution_time = time.time() - start_time
                    self.performance_stats['timeout_operations'] += 1
                    logger.warning(f"⏰ {operation_name} timed out after {execution_time:.2f}s (limit: {operation_timeout}s)")
                    
                    # Return fallback result
                    return self._get_fallback_result(operation_name)
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"❌ {operation_name} failed after {execution_time:.2f}s: {e}")
                    return self._get_fallback_result(operation_name)
            
            return wrapper
        return decorator
    
    def _get_fallback_result(self, operation_name: str) -> Dict[str, Any]:
        """Get fallback result for failed operations"""
        fallback_results = {
            'model_initialization': {'status': 'failed', 'models_loaded': 0},
            'model_prediction': {'prediction': 'Unknown', 'confidence': 0.5},
            'face_extraction': {'faces': [], 'count': 0},
            'advanced_ai_analysis': {'prediction': 'uncertain', 'confidence': 0.5},
            'aggressive_detection': {'prediction': 'Unknown', 'confidence': 0.5},
            'clip_detection': {'prediction': 'uncertain', 'confidence': 0.5},
            'vision_transformer': {'prediction': 'uncertain', 'confidence': 0.5},
            'ultra_ensemble_init': {'status': 'failed', 'models_initialized': 0},
            'ultra_ensemble_pred': {'prediction': 'Unknown', 'confidence': 0.5}
        }
        
        return fallback_results.get(operation_name, {'status': 'failed', 'error': 'Unknown operation'})
    
    def optimize_model_loading(self, models_to_load: list) -> list:
        """Optimize model loading order based on priority and performance"""
        # Priority order: Core models first, then advanced models
        priority_order = [
            'efficientnet_b0', 'resnet50', 'yolo_face',  # Core models
            'vision_transformer', 'clip',  # Modern AI
            'ultra_ensemble', 'advanced_ai'  # Advanced models
        ]
        
        optimized_order = []
        for priority_model in priority_order:
            if priority_model in models_to_load:
                optimized_order.append(priority_model)
        
        # Add any remaining models
        for model in models_to_load:
            if model not in optimized_order:
                optimized_order.append(model)
        
        return optimized_order
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance optimization summary"""
        total_ops = self.performance_stats['total_operations']
        timeout_rate = (self.performance_stats['timeout_operations'] / total_ops * 100) if total_ops > 0 else 0
        
        return {
            'total_operations': total_ops,
            'timeout_operations': self.performance_stats['timeout_operations'],
            'timeout_rate_percent': round(timeout_rate, 2),
            'average_operation_time': round(self.performance_stats['average_time'], 2),
            'slow_operations_count': len(self.performance_stats['slow_operations']),
            'slow_operations': self.performance_stats['slow_operations'][-5:],  # Last 5 slow operations
            'optimization_recommendations': self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> list:
        """Get optimization recommendations based on performance stats"""
        recommendations = []
        
        if self.performance_stats['timeout_operations'] > 0:
            recommendations.append("Consider increasing timeout limits for frequently timing out operations")
        
        if self.performance_stats['average_time'] > 30:
            recommendations.append("Average operation time is high - consider model optimization")
        
        if len(self.performance_stats['slow_operations']) > 5:
            recommendations.append("Multiple slow operations detected - consider parallel processing")
        
        return recommendations

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Convenience decorators
def with_model_timeout(operation_name: str, timeout: Optional[float] = None):
    """Convenience decorator for model operations"""
    return performance_optimizer.with_timeout(operation_name, timeout)

def with_analysis_timeout(operation_name: str, timeout: Optional[float] = None):
    """Convenience decorator for analysis operations"""
    return performance_optimizer.with_timeout(operation_name, timeout)

def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    return performance_optimizer.get_performance_summary()