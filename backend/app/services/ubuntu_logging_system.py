"""
Ubuntu Logging System for Deepfake Detection
===========================================

This module provides comprehensive logging capabilities specifically designed
for Ubuntu environments, including system monitoring, performance tracking,
and detailed model execution logs.

Features:
- System resource monitoring
- Model performance tracking
- Real-time log streaming
- Log rotation and management
- Performance metrics collection
- Error tracking and reporting

Author: Senior ML Engineer
Date: 2024
"""

import logging
import logging.handlers
import os
import sys
import time
import psutil
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import queue

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    gpu_memory_percent: Optional[float]
    disk_usage_percent: float
    network_io: Dict[str, int]
    active_processes: int
    load_average: List[float]

@dataclass
class ModelPerformanceMetrics:
    """Model performance metrics"""
    model_name: str
    timestamp: str
    inference_time: float
    memory_usage: float
    gpu_utilization: Optional[float]
    batch_size: int
    success: bool
    error_message: Optional[str]

class UbuntuLoggingSystem:
    """
    Comprehensive logging system for Ubuntu environments
    
    Provides system monitoring, performance tracking, and detailed logging
    capabilities specifically optimized for Ubuntu/Linux systems.
    """
    
    def __init__(self, log_dir: str = "/var/log/deepfake-detector"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log files
        self.main_log_file = self.log_dir / "deepfake_detector.log"
        self.error_log_file = self.log_dir / "errors.log"
        self.performance_log_file = self.log_dir / "performance.log"
        self.system_log_file = self.log_dir / "system_metrics.log"
        self.model_log_file = self.log_dir / "model_performance.log"
        
        # Metrics collection
        self.metrics_queue = queue.Queue()
        self.metrics_collection_active = False
        self.metrics_thread = None
        
        # Performance tracking
        self.model_performance_history = []
        self.system_metrics_history = []
        
        # Initialize logging
        self._setup_logging()
        
        logger.info(f"🐧 Ubuntu Logging System initialized - Logs: {self.log_dir}")
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Main application logger
        main_logger = logging.getLogger('deepfake_detector')
        main_logger.setLevel(logging.INFO)
        
        # Main log file handler with rotation
        main_handler = logging.handlers.RotatingFileHandler(
            self.main_log_file,
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        main_handler.setFormatter(detailed_formatter)
        main_handler.setLevel(logging.INFO)
        main_logger.addHandler(main_handler)
        
        # Error log file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.error_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=5
        )
        error_handler.setFormatter(detailed_formatter)
        error_handler.setLevel(logging.ERROR)
        main_logger.addHandler(error_handler)
        
        # Console handler for real-time monitoring
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        console_handler.setLevel(logging.INFO)
        main_logger.addHandler(console_handler)
        
        # Performance logger
        perf_logger = logging.getLogger('performance')
        perf_logger.setLevel(logging.INFO)
        
        perf_handler = logging.handlers.RotatingFileHandler(
            self.performance_log_file,
            maxBytes=30*1024*1024,  # 30MB
            backupCount=7
        )
        perf_handler.setFormatter(detailed_formatter)
        perf_logger.addHandler(perf_handler)
        
        # System metrics logger
        system_logger = logging.getLogger('system_metrics')
        system_logger.setLevel(logging.INFO)
        
        system_handler = logging.handlers.RotatingFileHandler(
            self.system_log_file,
            maxBytes=25*1024*1024,  # 25MB
            backupCount=5
        )
        system_handler.setFormatter(simple_formatter)
        system_logger.addHandler(system_handler)
        
        # Model performance logger
        model_logger = logging.getLogger('model_performance')
        model_logger.setLevel(logging.INFO)
        
        model_handler = logging.handlers.RotatingFileHandler(
            self.model_log_file,
            maxBytes=40*1024*1024,  # 40MB
            backupCount=8
        )
        model_handler.setFormatter(detailed_formatter)
        model_logger.addHandler(model_handler)
    
    def start_metrics_collection(self, interval: int = 30):
        """Start system metrics collection in background thread"""
        if self.metrics_collection_active:
            return
        
        self.metrics_collection_active = True
        self.metrics_thread = threading.Thread(
            target=self._collect_metrics_loop,
            args=(interval,),
            daemon=True
        )
        self.metrics_thread.start()
        
        logger.info(f"📊 Started metrics collection with {interval}s interval")
    
    def stop_metrics_collection(self):
        """Stop system metrics collection"""
        self.metrics_collection_active = False
        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)
        
        logger.info("📊 Stopped metrics collection")
    
    def _collect_metrics_loop(self, interval: int):
        """Background loop for collecting system metrics"""
        system_logger = logging.getLogger('system_metrics')
        
        while self.metrics_collection_active:
            try:
                metrics = self._collect_system_metrics()
                self.system_metrics_history.append(metrics)
                
                # Log metrics
                system_logger.info(json.dumps(asdict(metrics)))
                
                # Keep only last 1000 entries in memory
                if len(self.system_metrics_history) > 1000:
                    self.system_metrics_history = self.system_metrics_history[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # GPU memory (if available)
            gpu_memory_percent = None
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_percent = (gpu_memory_info.used / gpu_memory_info.total) * 100
            except:
                pass
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Network I/O
            network_io = psutil.net_io_counters()._asdict()
            
            # Active processes
            active_processes = len(psutil.pids())
            
            # Load average (Linux specific)
            load_average = list(os.getloadavg()) if hasattr(os, 'getloadavg') else [0.0, 0.0, 0.0]
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                gpu_memory_percent=gpu_memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                active_processes=active_processes,
                load_average=load_average
            )
            
        except Exception as e:
            logger.error(f"❌ System metrics collection failed: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                gpu_memory_percent=None,
                disk_usage_percent=0.0,
                network_io={},
                active_processes=0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    def log_model_performance(self, model_name: str, inference_time: float, 
                            memory_usage: float, batch_size: int = 1, 
                            success: bool = True, error_message: Optional[str] = None):
        """Log model performance metrics"""
        model_logger = logging.getLogger('model_performance')
        
        # Get GPU utilization if available
        gpu_utilization = None
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_utilization = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
        except:
            pass
        
        metrics = ModelPerformanceMetrics(
            model_name=model_name,
            timestamp=datetime.now().isoformat(),
            inference_time=inference_time,
            memory_usage=memory_usage,
            gpu_utilization=gpu_utilization,
            batch_size=batch_size,
            success=success,
            error_message=error_message
        )
        
        # Store in history
        self.model_performance_history.append(metrics)
        
        # Keep only last 2000 entries
        if len(self.model_performance_history) > 2000:
            self.model_performance_history = self.model_performance_history[-2000:]
        
        # Log metrics
        model_logger.info(json.dumps(asdict(metrics)))
        
        # Log performance summary
        perf_logger = logging.getLogger('performance')
        status = "✅" if success else "❌"
        perf_logger.info(
            f"{status} {model_name} | "
            f"Time: {inference_time:.3f}s | "
            f"Memory: {memory_usage:.1f}MB | "
            f"Batch: {batch_size} | "
            f"GPU: {gpu_utilization}%" if gpu_utilization else f"GPU: N/A"
        )
    
    def log_detection_event(self, event_type: str, details: Dict[str, Any]):
        """Log detection events with detailed information"""
        main_logger = logging.getLogger('deepfake_detector')
        
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        
        main_logger.info(f"🔍 Detection Event: {json.dumps(event_data)}")
    
    def log_startup_event(self, component: str, status: str, details: Dict[str, Any] = None):
        """Log startup events for components"""
        main_logger = logging.getLogger('deepfake_detector')
        
        status_emoji = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        
        message = f"{status_emoji} {component} startup: {status}"
        if details:
            message += f" | Details: {json.dumps(details)}"
        
        main_logger.info(message)
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log errors with context"""
        error_logger = logging.getLogger('deepfake_detector')
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        error_logger.error(f"❌ Error: {json.dumps(error_data)}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent metrics
        recent_model_metrics = [
            m for m in self.model_performance_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        recent_system_metrics = [
            m for m in self.system_metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        # Calculate summary statistics
        summary = {
            'time_range_hours': hours,
            'model_performance': {
                'total_inferences': len(recent_model_metrics),
                'successful_inferences': len([m for m in recent_model_metrics if m.success]),
                'failed_inferences': len([m for m in recent_model_metrics if not m.success]),
                'average_inference_time': np.mean([m.inference_time for m in recent_model_metrics]) if recent_model_metrics else 0,
                'models_used': list(set([m.model_name for m in recent_model_metrics]))
            },
            'system_performance': {
                'average_cpu_usage': np.mean([m.cpu_percent for m in recent_system_metrics]) if recent_system_metrics else 0,
                'average_memory_usage': np.mean([m.memory_percent for m in recent_system_metrics]) if recent_system_metrics else 0,
                'average_gpu_usage': np.mean([m.gpu_memory_percent for m in recent_system_metrics if m.gpu_memory_percent is not None]) if recent_system_metrics else None,
                'peak_cpu_usage': max([m.cpu_percent for m in recent_system_metrics]) if recent_system_metrics else 0,
                'peak_memory_usage': max([m.memory_percent for m in recent_system_metrics]) if recent_system_metrics else 0
            }
        }
        
        return summary
    
    def cleanup_old_logs(self, days: int = 30):
        """Clean up log files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob("*.log.*"):  # Rotated log files
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    logger.info(f"🗑️ Cleaned up old log file: {log_file}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to clean up {log_file}: {e}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about log files"""
        stats = {}
        
        for log_file in [self.main_log_file, self.error_log_file, self.performance_log_file, 
                        self.system_log_file, self.model_log_file]:
            if log_file.exists():
                size_mb = log_file.stat().st_size / (1024 * 1024)
                modified_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                stats[log_file.name] = {
                    'size_mb': round(size_mb, 2),
                    'last_modified': modified_time.isoformat(),
                    'exists': True
                }
            else:
                stats[log_file.name] = {'exists': False}
        
        return stats

# Global logging system instance
_ubuntu_logging_system = None

def get_ubuntu_logging_system() -> UbuntuLoggingSystem:
    """Get global Ubuntu logging system instance"""
    global _ubuntu_logging_system
    if _ubuntu_logging_system is None:
        _ubuntu_logging_system = UbuntuLoggingSystem()
    return _ubuntu_logging_system

def setup_ubuntu_logging(log_dir: str = "/var/log/deepfake-detector", 
                        start_metrics: bool = True, 
                        metrics_interval: int = 30) -> UbuntuLoggingSystem:
    """Setup Ubuntu logging system with configuration"""
    logging_system = UbuntuLoggingSystem(log_dir)
    
    if start_metrics:
        logging_system.start_metrics_collection(metrics_interval)
    
    return logging_system

# Convenience functions for common logging operations
def log_model_performance(model_name: str, inference_time: float, memory_usage: float, 
                         batch_size: int = 1, success: bool = True, error_message: Optional[str] = None):
    """Log model performance metrics"""
    logging_system = get_ubuntu_logging_system()
    logging_system.log_model_performance(model_name, inference_time, memory_usage, 
                                       batch_size, success, error_message)

def log_detection_event(event_type: str, details: Dict[str, Any]):
    """Log detection events"""
    logging_system = get_ubuntu_logging_system()
    logging_system.log_detection_event(event_type, details)

def log_startup_event(component: str, status: str, details: Dict[str, Any] = None):
    """Log startup events"""
    logging_system = get_ubuntu_logging_system()
    logging_system.log_startup_event(component, status, details)

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None):
    """Log errors"""
    logging_system = get_ubuntu_logging_system()
    logging_system.log_error(error_type, error_message, context)
