"""
Clean Logging Configuration for Deepfake Detector
Provides organized, clean logging output with proper formatting and filtering
"""

import logging
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import threading

class CleanLoggingConfig:
    """Clean logging configuration with organized output"""
    
    def __init__(self):
        self.startup_phase = "initialization"
        self.model_loading_phase = False
        self.server_ready = False
        self.startup_start_time = datetime.now()
        self._lock = threading.Lock()
        
        # Configure logging
        self._setup_clean_logging()
    
    def _setup_clean_logging(self):
        """Setup clean logging configuration"""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create clean formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add custom filter
        console_handler.addFilter(self._clean_log_filter)
        
        # Add handler to root logger
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.INFO)
        
        # Suppress noisy loggers
        self._suppress_noisy_loggers()
    
    def _suppress_noisy_loggers(self):
        """Suppress noisy third-party loggers"""
        noisy_loggers = [
            'matplotlib', 'PIL', 'urllib3', 'requests', 'httpx',
            'torch.distributed', 'torch.nn', 'torch.optim',
            'transformers', 'timm', 'ultralytics', 'cv2',
            'numpy', 'scipy', 'sklearn', 'tensorflow'
        ]
        
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def _clean_log_filter(self, record):
        """Filter and clean log messages"""
        with self._lock:
            # Skip certain noisy messages
            skip_patterns = [
                "LooseVersion compatibility fix applied",
                "pkgutil.ImpImporter already available",
                "pkg_resources available after fixes",
                "Python 3.13 compatibility fixes applied",
                "Deterministic preprocessing pipeline configured",
                "ProductionPreprocessor initialized",
                "ConservativeCalibrator initialized",
                "TemperatureCalibrator initialized",
                "Background tasks ready to start",
                "Model availability initialized",
                "Deterministic environment initialized",
                "Deterministic mode already enabled"
            ]
            
            message = record.getMessage()
            
            # Skip repetitive messages
            for pattern in skip_patterns:
                if pattern in message:
                    return False
            
            # Clean up message formatting
            if "[OK]" in message or "[START]" in message or "[FIX]" in message:
                # Keep important startup messages
                return True
            
            # Skip debug-level model loading details
            if "Model loaded with" in message and "missing keys" in message:
                return False
            
            if "Skipping classifier layer" in message:
                return False
            
            if "Detected" in message and "classes from checkpoint" in message:
                return False
            
            return True
    
    def log_startup_phase(self, phase: str):
        """Log startup phase transitions"""
        with self._lock:
            self.startup_phase = phase
            logger = logging.getLogger(__name__)
            
            if phase == "environment":
                logger.info("[FIX] Applying environment patches...")
            elif phase == "models":
                logger.info("[MODELS] Loading models...")
                self.model_loading_phase = True
            elif phase == "services":
                logger.info("🔗 Initializing services...")
            elif phase == "complete":
                logger.info("[COMPLETE] Server startup complete!")
                self.server_ready = True
    
    def log_model_loading(self, model_name: str, status: str, details: str = ""):
        """Log model loading with clean formatting"""
        logger = logging.getLogger(__name__)
        
        if status == "start":
            logger.info(f"[LOADING] Loading {model_name}...")
        elif status == "success":
            logger.info(f"[OK] {model_name} loaded successfully")
        elif status == "error":
            logger.warning(f"[WARNING] {model_name} loading failed: {details}")
    
    def log_system_info(self, info: Dict[str, Any]):
        """Log system information in clean format"""
        logger = logging.getLogger(__name__)
        
        if "cuda" in info:
            cuda_info = info["cuda"]
            logger.info(f"[OK] CUDA device: {cuda_info.get('device_name', 'Unknown')}")
            logger.info(f"[OK] CUDA version: {cuda_info.get('version', 'Unknown')}")
            logger.info(f"[OK] GPU memory: {cuda_info.get('memory', 'Unknown')}")
        
        if "models_loaded" in info:
            models = info["models_loaded"]
            logger.info(f"[OK] Models loaded: {len(models)}")
            for model_name in models:
                logger.info(f"   - {model_name}")
    
    def log_startup_summary(self, results: Dict[str, Any]):
        """Log startup summary in clean format"""
        logger = logging.getLogger(__name__)
        
        total_time = (datetime.now() - self.startup_start_time).total_seconds()
        
        logger.info("=" * 60)
        logger.info("[COMPLETE] STARTUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"[TIME]  Total startup time: {total_time:.2f}s")
        logger.info(f"[DEVICE]  Device: {results.get('device', 'Unknown')}")
        logger.info(f"[DATA] Models loaded: {len(results.get('models_loaded', {}))}")
        logger.info(f"[OK] Success rate: {results.get('success_rate', 0):.1f}%")
        logger.info("=" * 60)
        logger.info("[START] Server ready to accept requests")
        logger.info("=" * 60)

# Global instance
_clean_logging = None

def get_clean_logging() -> CleanLoggingConfig:
    """Get the global clean logging instance"""
    global _clean_logging
    if _clean_logging is None:
        _clean_logging = CleanLoggingConfig()
    return _clean_logging

def setup_clean_logging():
    """Setup clean logging configuration"""
    return get_clean_logging()

def log_startup_phase(phase: str):
    """Log startup phase"""
    get_clean_logging().log_startup_phase(phase)

def log_model_loading(model_name: str, status: str, details: str = ""):
    """Log model loading"""
    get_clean_logging().log_model_loading(model_name, status, details)

def log_system_info(info: Dict[str, Any]):
    """Log system information"""
    get_clean_logging().log_system_info(info)

def log_startup_summary(results: Dict[str, Any]):
    """Log startup summary"""
    get_clean_logging().log_startup_summary(results)
