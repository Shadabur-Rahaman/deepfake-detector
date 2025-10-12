"""
Performance Monitor - Model Loading Performance Tracking
======================================================

This module tracks and reports model loading performance to help identify bottlenecks.
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LoadingMetric:
    """Model loading performance metric"""
    model_name: str
    load_time: float
    success: bool
    method: str
    error: Optional[str] = None

class PerformanceMonitor:
    """Monitor model loading performance"""
    
    def __init__(self):
        self.metrics: List[LoadingMetric] = []
        self.start_times: Dict[str, float] = {}
    
    def start_timing(self, model_name: str):
        """Start timing a model load"""
        self.start_times[model_name] = time.time()
    
    def end_timing(self, model_name: str, success: bool, method: str = "standard", error: Optional[str] = None):
        """End timing and record metric"""
        if model_name in self.start_times:
            load_time = time.time() - self.start_times[model_name]
            metric = LoadingMetric(
                model_name=model_name,
                load_time=load_time,
                success=success,
                method=method,
                error=error
            )
            self.metrics.append(metric)
            del self.start_times[model_name]
            
            # Log performance
            status = "✅" if success else "❌"
            logger.info(f"{status} {model_name}: {load_time:.2f}s ({method})")
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        if not self.metrics:
            return {"total_models": 0, "avg_load_time": 0, "success_rate": 0}
        
        successful_loads = [m for m in self.metrics if m.success]
        total_time = sum(m.load_time for m in self.metrics)
        avg_load_time = total_time / len(self.metrics) if self.metrics else 0
        success_rate = len(successful_loads) / len(self.metrics) * 100
        
        # Find slowest and fastest models
        slowest = max(self.metrics, key=lambda m: m.load_time) if self.metrics else None
        fastest = min(self.metrics, key=lambda m: m.load_time) if self.metrics else None
        
        return {
            "total_models": len(self.metrics),
            "successful_models": len(successful_loads),
            "failed_models": len(self.metrics) - len(successful_loads),
            "avg_load_time": avg_load_time,
            "total_load_time": total_time,
            "success_rate": success_rate,
            "slowest_model": {
                "name": slowest.model_name,
                "time": slowest.load_time,
                "method": slowest.method
            } if slowest else None,
            "fastest_model": {
                "name": fastest.model_name,
                "time": fastest.load_time,
                "method": fastest.method
            } if fastest else None
        }
    
    def print_performance_report(self):
        """Print detailed performance report"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("🚀 MODEL LOADING PERFORMANCE REPORT")
        print("="*60)
        print(f"Total Models: {summary['total_models']}")
        print(f"Successful: {summary['successful_models']}")
        print(f"Failed: {summary['failed_models']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Average Load Time: {summary['avg_load_time']:.2f}s")
        print(f"Total Load Time: {summary['total_load_time']:.2f}s")
        
        if summary['slowest_model']:
            print(f"\n🐌 Slowest: {summary['slowest_model']['name']} ({summary['slowest_model']['time']:.2f}s)")
        if summary['fastest_model']:
            print(f"⚡ Fastest: {summary['fastest_model']['name']} ({summary['fastest_model']['time']:.2f}s)")
        
        print("\n📊 Individual Model Performance:")
        print("-" * 60)
        for metric in self.metrics:
            status = "✅" if metric.success else "❌"
            print(f"{status} {metric.model_name:<20} {metric.load_time:>6.2f}s ({metric.method})")
            if metric.error:
                print(f"    Error: {metric.error}")
        
        print("="*60)

# Global performance monitor
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def start_timing(model_name: str):
    """Start timing model load"""
    monitor = get_performance_monitor()
    monitor.start_timing(model_name)

def end_timing(model_name: str, success: bool, method: str = "standard", error: Optional[str] = None):
    """End timing and record metric"""
    monitor = get_performance_monitor()
    monitor.end_timing(model_name, success, method, error)

def print_performance_report():
    """Print performance report"""
    monitor = get_performance_monitor()
    monitor.print_performance_report()

def get_performance_summary() -> Dict:
    """Get performance summary"""
    monitor = get_performance_monitor()
    return monitor.get_summary()