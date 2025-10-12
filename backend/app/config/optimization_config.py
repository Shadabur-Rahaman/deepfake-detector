"""
Optimization Configuration for Deepfake Detection System
Comprehensive configuration for all optimization features

This module provides:
- Performance thresholds and targets
- Model loading priorities and timeouts
- Memory management settings
- Monitoring and alerting configuration
- Production-ready defaults

Author: Senior Performance Engineer
Date: 2024
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

class OptimizationLevel(Enum):
    """Optimization level enumeration"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"

@dataclass
class PerformanceThresholds:
    """Performance threshold configuration"""
    # Startup performance
    target_startup_time: float = 5.0
    max_startup_time: float = 16.0
    critical_startup_time: float = 30.0
    
    # Model loading
    target_model_load_time: float = 15.0
    max_model_load_time: float = 30.0
    critical_model_load_time: float = 60.0
    
    # Inference performance
    target_inference_time: float = 2.0
    max_inference_time: float = 5.0
    critical_inference_time: float = 10.0
    
    # System resources
    cpu_usage_warning: float = 70.0
    cpu_usage_critical: float = 90.0
    memory_usage_warning: float = 75.0
    memory_usage_critical: float = 90.0
    gpu_usage_warning: float = 80.0
    gpu_usage_critical: float = 95.0
    gpu_memory_warning: float = 80.0
    gpu_memory_critical: float = 95.0
    
    # Error rates
    error_rate_warning: float = 2.0
    error_rate_critical: float = 5.0
    model_success_rate_minimum: float = 0.85

@dataclass
class ModelLoadingConfig:
    """Model loading configuration"""
    # Parallel loading settings
    max_concurrent_critical: int = 2
    max_concurrent_important: int = 3
    max_concurrent_optional: int = 5
    
    # Timeout settings
    critical_model_timeout: float = 20.0
    important_model_timeout: float = 25.0
    optional_model_timeout: float = 15.0
    
    # Retry settings
    max_retries: int = 2
    retry_delay: float = 1.0
    
    # Memory limits
    max_memory_per_model: float = 500.0  # MB
    total_memory_limit: float = 4000.0   # MB
    
    # Lazy loading
    enable_lazy_loading: bool = True
    lazy_load_threshold: float = 0.8  # Load when 80% of critical models are ready

@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    # Monitoring intervals
    system_health_interval: float = 5.0
    model_performance_interval: float = 10.0
    memory_cleanup_interval: float = 30.0
    
    # Data retention
    max_metrics_history: int = 1000
    max_alerts_history: int = 100
    max_performance_history: int = 500
    
    # Alerting
    enable_alerts: bool = True
    alert_cooldown: float = 60.0  # seconds
    max_alerts_per_hour: int = 10
    
    # Auto-optimization
    enable_auto_optimization: bool = True
    auto_cleanup_enabled: bool = True
    memory_cleanup_threshold: float = 80.0

@dataclass
class SQLite3Config:
    """SQLite3 optimization configuration"""
    # Compatibility settings
    enable_symbol_fix: bool = True
    enable_fallback_mode: bool = True
    enable_performance_monitoring: bool = True
    
    # Fallback priorities
    fallback_priorities: List[str] = None
    
    # Performance settings
    connection_timeout: float = 30.0
    query_timeout: float = 10.0
    enable_wal_mode: bool = True
    cache_size: int = 2000
    
    def __post_init__(self):
        if self.fallback_priorities is None:
            self.fallback_priorities = [
                "pysqlite3",
                "apsw",
                "symbol_patch",
                "custom_fallback"
            ]

@dataclass
class MemoryConfig:
    """Memory management configuration"""
    # Memory limits
    max_system_memory: float = 8000.0  # MB
    max_gpu_memory: float = 6000.0     # MB
    
    # Cleanup settings
    enable_auto_cleanup: bool = True
    cleanup_threshold: float = 80.0
    cleanup_interval: float = 30.0
    
    # Garbage collection
    enable_aggressive_gc: bool = True
    gc_threshold: float = 75.0
    
    # Model memory management
    enable_model_swapping: bool = False
    swap_threshold: float = 90.0

@dataclass
class LoggingConfig:
    """Logging configuration"""
    # Log levels
    startup_log_level: str = "INFO"
    runtime_log_level: str = "INFO"
    performance_log_level: str = "DEBUG"
    
    # Log files
    enable_file_logging: bool = True
    log_directory: str = "logs"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    max_log_files: int = 5
    
    # Performance logging
    enable_performance_logging: bool = True
    log_operation_times: bool = True
    log_memory_usage: bool = True
    log_model_performance: bool = True

class OptimizationConfig:
    """Main optimization configuration class"""
    
    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.STANDARD):
        self.optimization_level = optimization_level
        
        # Initialize configurations based on optimization level
        self.performance_thresholds = self._get_performance_thresholds()
        self.model_loading = self._get_model_loading_config()
        self.monitoring = self._get_monitoring_config()
        self.sqlite3 = self._get_sqlite3_config()
        self.memory = self._get_memory_config()
        self.logging = self._get_logging_config()
        
        # Model priorities (same for all levels)
        self.model_priorities = self._get_model_priorities()
        
    def _get_performance_thresholds(self) -> PerformanceThresholds:
        """Get performance thresholds based on optimization level"""
        if self.optimization_level == OptimizationLevel.MINIMAL:
            return PerformanceThresholds(
                target_startup_time=10.0,
                max_startup_time=20.0,
                target_model_load_time=25.0,
                max_model_load_time=45.0,
                target_inference_time=3.0,
                max_inference_time=8.0
            )
        elif self.optimization_level == OptimizationLevel.STANDARD:
            return PerformanceThresholds()  # Use defaults
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return PerformanceThresholds(
                target_startup_time=3.0,
                max_startup_time=8.0,
                target_model_load_time=10.0,
                max_model_load_time=20.0,
                target_inference_time=1.5,
                max_inference_time=3.0,
                cpu_usage_warning=60.0,
                memory_usage_warning=65.0
            )
        else:  # MAXIMUM
            return PerformanceThresholds(
                target_startup_time=2.0,
                max_startup_time=5.0,
                target_model_load_time=8.0,
                max_model_load_time=15.0,
                target_inference_time=1.0,
                max_inference_time=2.0,
                cpu_usage_warning=50.0,
                memory_usage_warning=60.0,
                gpu_usage_warning=70.0
            )
    
    def _get_model_loading_config(self) -> ModelLoadingConfig:
        """Get model loading configuration based on optimization level"""
        if self.optimization_level == OptimizationLevel.MINIMAL:
            return ModelLoadingConfig(
                max_concurrent_critical=1,
                max_concurrent_important=2,
                max_concurrent_optional=3,
                enable_lazy_loading=False
            )
        elif self.optimization_level == OptimizationLevel.STANDARD:
            return ModelLoadingConfig()  # Use defaults
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return ModelLoadingConfig(
                max_concurrent_critical=3,
                max_concurrent_important=4,
                max_concurrent_optional=6,
                max_memory_per_model=400.0,
                total_memory_limit=3000.0
            )
        else:  # MAXIMUM
            return ModelLoadingConfig(
                max_concurrent_critical=4,
                max_concurrent_important=5,
                max_concurrent_optional=8,
                max_memory_per_model=300.0,
                total_memory_limit=2000.0,
                enable_lazy_loading=True,
                lazy_load_threshold=0.6
            )
    
    def _get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration based on optimization level"""
        if self.optimization_level == OptimizationLevel.MINIMAL:
            return MonitoringConfig(
                system_health_interval=10.0,
                model_performance_interval=30.0,
                enable_auto_optimization=False,
                auto_cleanup_enabled=False
            )
        elif self.optimization_level == OptimizationLevel.STANDARD:
            return MonitoringConfig()  # Use defaults
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return MonitoringConfig(
                system_health_interval=3.0,
                model_performance_interval=5.0,
                memory_cleanup_interval=15.0,
                max_metrics_history=2000
            )
        else:  # MAXIMUM
            return MonitoringConfig(
                system_health_interval=2.0,
                model_performance_interval=3.0,
                memory_cleanup_interval=10.0,
                max_metrics_history=5000,
                max_alerts_history=200
            )
    
    def _get_sqlite3_config(self) -> SQLite3Config:
        """Get SQLite3 configuration based on optimization level"""
        if self.optimization_level == OptimizationLevel.MINIMAL:
            return SQLite3Config(
                enable_performance_monitoring=False,
                cache_size=1000
            )
        elif self.optimization_level == OptimizationLevel.STANDARD:
            return SQLite3Config()  # Use defaults
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return SQLite3Config(
                cache_size=4000,
                connection_timeout=20.0,
                query_timeout=5.0
            )
        else:  # MAXIMUM
            return SQLite3Config(
                cache_size=8000,
                connection_timeout=15.0,
                query_timeout=3.0,
                enable_wal_mode=True
            )
    
    def _get_memory_config(self) -> MemoryConfig:
        """Get memory configuration based on optimization level"""
        if self.optimization_level == OptimizationLevel.MINIMAL:
            return MemoryConfig(
                enable_auto_cleanup=False,
                enable_aggressive_gc=False,
                enable_model_swapping=False
            )
        elif self.optimization_level == OptimizationLevel.STANDARD:
            return MemoryConfig()  # Use defaults
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return MemoryConfig(
                cleanup_threshold=70.0,
                cleanup_interval=20.0,
                gc_threshold=65.0,
                enable_model_swapping=True,
                swap_threshold=85.0
            )
        else:  # MAXIMUM
            return MemoryConfig(
                cleanup_threshold=60.0,
                cleanup_interval=15.0,
                gc_threshold=55.0,
                enable_model_swapping=True,
                swap_threshold=80.0
            )
    
    def _get_logging_config(self) -> LoggingConfig:
        """Get logging configuration based on optimization level"""
        if self.optimization_level == OptimizationLevel.MINIMAL:
            return LoggingConfig(
                startup_log_level="WARNING",
                runtime_log_level="WARNING",
                performance_log_level="WARNING",
                enable_performance_logging=False
            )
        elif self.optimization_level == OptimizationLevel.STANDARD:
            return LoggingConfig()  # Use defaults
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            return LoggingConfig(
                startup_log_level="DEBUG",
                runtime_log_level="INFO",
                performance_log_level="DEBUG",
                log_operation_times=True,
                log_memory_usage=True,
                log_model_performance=True
            )
        else:  # MAXIMUM
            return LoggingConfig(
                startup_log_level="DEBUG",
                runtime_log_level="DEBUG",
                performance_log_level="DEBUG",
                log_operation_times=True,
                log_memory_usage=True,
                log_model_performance=True,
                max_log_size=20 * 1024 * 1024,  # 20MB
                max_log_files=10
            )
    
    def _get_model_priorities(self) -> Dict[str, int]:
        """Get model loading priorities"""
        return {
            # Critical models (priority 1)
            'efficientnet_b0': 1,
            'custom_finetuned': 1,
            
            # Important models (priority 2)
            'production_advanced_detector': 2,
            'deterministic_ensemble': 2,
            'yolov8': 2,
            
            # Optional models (priority 3)
            'gemini': 3,
            'openai': 3,
            'unite': 3,
            'hybrid': 3,
            'divid': 3,
            'ensemble': 3,
            'mesonet': 3,
            'classifier': 3,
            'lstm': 3,
            'vivit': 3,
            'vit': 3,
            'resnet50': 3,
            'realtime_detector': 3
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "optimization_level": self.optimization_level.value,
            "performance_thresholds": {
                "target_startup_time": self.performance_thresholds.target_startup_time,
                "target_model_load_time": self.performance_thresholds.target_model_load_time,
                "target_inference_time": self.performance_thresholds.target_inference_time,
                "cpu_usage_warning": self.performance_thresholds.cpu_usage_warning,
                "memory_usage_warning": self.performance_thresholds.memory_usage_warning
            },
            "model_loading": {
                "max_concurrent_critical": self.model_loading.max_concurrent_critical,
                "max_concurrent_important": self.model_loading.max_concurrent_important,
                "max_concurrent_optional": self.model_loading.max_concurrent_optional,
                "enable_lazy_loading": self.model_loading.enable_lazy_loading
            },
            "monitoring": {
                "system_health_interval": self.monitoring.system_health_interval,
                "enable_auto_optimization": self.monitoring.enable_auto_optimization,
                "auto_cleanup_enabled": self.monitoring.auto_cleanup_enabled
            },
            "sqlite3": {
                "enable_symbol_fix": self.sqlite3.enable_symbol_fix,
                "enable_fallback_mode": self.sqlite3.enable_fallback_mode,
                "cache_size": self.sqlite3.cache_size
            },
            "memory": {
                "enable_auto_cleanup": self.memory.enable_auto_cleanup,
                "cleanup_threshold": self.memory.cleanup_threshold,
                "enable_aggressive_gc": self.memory.enable_aggressive_gc
            },
            "logging": {
                "startup_log_level": self.logging.startup_log_level,
                "runtime_log_level": self.logging.runtime_log_level,
                "enable_performance_logging": self.logging.enable_performance_logging
            }
        }

# Global configuration instance
_optimization_config = None

def get_optimization_config(optimization_level: OptimizationLevel = OptimizationLevel.STANDARD) -> OptimizationConfig:
    """Get global optimization configuration instance"""
    global _optimization_config
    if _optimization_config is None:
        _optimization_config = OptimizationConfig(optimization_level)
    return _optimization_config

def set_optimization_level(level: OptimizationLevel):
    """Set optimization level and update configuration"""
    global _optimization_config
    _optimization_config = OptimizationConfig(level)

# Predefined configurations for common use cases
PRODUCTION_CONFIG = OptimizationConfig(OptimizationLevel.AGGRESSIVE)
DEVELOPMENT_CONFIG = OptimizationConfig(OptimizationLevel.STANDARD)
MINIMAL_CONFIG = OptimizationConfig(OptimizationLevel.MINIMAL)
MAXIMUM_CONFIG = OptimizationConfig(OptimizationLevel.MAXIMUM)
