"""
Enhanced Logging Configuration with Emojis and Detailed Information
Provides rich, detailed logging with emojis and comprehensive information
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading

class EnhancedLogger:
    """Enhanced logger with emojis and detailed information"""
    
    def __init__(self):
        self.startup_phase = "initialization"
        self.model_loading_phase = False
        self.server_ready = False
        self.startup_start_time = datetime.now()
        self._lock = threading.Lock()
        self._setup_enhanced_logging()
    
    def _setup_enhanced_logging(self):
        """Setup enhanced logging with emojis and detailed formatting"""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create enhanced formatter with emojis
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add custom filter for enhanced formatting
        console_handler.addFilter(self._enhanced_log_filter)
        
        # Add handler to root logger
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.INFO)
        
        # Suppress noisy loggers
        self._suppress_noisy_loggers()
    
    def _enhanced_log_filter(self, record):
        """Custom filter to add emojis and enhance log messages"""
        # Add emojis based on log level and content
        if record.levelname == "INFO":
            if "[OK]" in record.getMessage():
                record.msg = f"✅ {record.msg}"
            elif "[START]" in record.getMessage():
                record.msg = f"🚀 {record.msg}"
            elif "[LOADING]" in record.getMessage():
                record.msg = f"⏳ {record.msg}"
            elif "[COMPLETE]" in record.getMessage():
                record.msg = f"🎉 {record.msg}"
            elif "[READY]" in record.getMessage():
                record.msg = f"🟢 {record.msg}"
            elif "[WARNING]" in record.getMessage():
                record.msg = f"⚠️ {record.msg}"
            elif "[ERROR]" in record.getMessage():
                record.msg = f"❌ {record.msg}"
            elif "[MODELS]" in record.getMessage():
                record.msg = f"🤖 {record.msg}"
            elif "[TESTS]" in record.getMessage():
                record.msg = f"🧪 {record.msg}"
            elif "[TIME]" in record.getMessage():
                record.msg = f"⏱️ {record.msg}"
            elif "[DEVICE]" in record.getMessage():
                record.msg = f"💻 {record.msg}"
            elif "[DATA]" in record.getMessage():
                record.msg = f"📊 {record.msg}"
            elif "[AUTH]" in record.getMessage():
                record.msg = f"🔐 {record.msg}"
            elif "[API]" in record.getMessage():
                record.msg = f"🌐 {record.msg}"
            elif "[WEBSOCKET]" in record.getMessage():
                record.msg = f"🔌 {record.msg}"
            elif "[DETECTION]" in record.getMessage():
                record.msg = f"🔍 {record.msg}"
            elif "[ENVIRONMENT]" in record.getMessage():
                record.msg = f"🌍 {record.msg}"
            elif "[PYTHON]" in record.getMessage():
                record.msg = f"🐍 {record.msg}"
            elif "[CUDA]" in record.getMessage():
                record.msg = f"⚡ {record.msg}"
            elif "[STATIC]" in record.getMessage():
                record.msg = f"📁 {record.msg}"
            elif "[ROUTE]" in record.getMessage():
                record.msg = f"🛣️ {record.msg}"
            elif "[SHUTDOWN]" in record.getMessage():
                record.msg = f"🛑 {record.msg}"
            else:
                record.msg = f"ℹ️ {record.msg}"
        elif record.levelname == "WARNING":
            record.msg = f"⚠️ {record.msg}"
        elif record.levelname == "ERROR":
            record.msg = f"❌ {record.msg}"
        elif record.levelname == "CRITICAL":
            record.msg = f"🚨 {record.msg}"
        
        return True
    
    def _suppress_noisy_loggers(self):
        """Suppress noisy third-party loggers"""
        noisy_loggers = [
            'matplotlib', 'PIL', 'urllib3', 'requests', 'httpx',
            'torch.distributed', 'torch.nn', 'torch.optim',
            'transformers', 'timm', 'ultralytics', 'cv2',
            'numpy', 'scipy', 'sklearn', 'tensorflow',
            'uvicorn.access', 'uvicorn.error'
        ]
        
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def log_startup_message(self, message: str, phase: str = None):
        """Log a startup message with enhanced formatting"""
        logger = logging.getLogger(__name__)
        if phase:
            self.startup_phase = phase
        logger.info(f"[{self.startup_phase.upper()}] {message}")
    
    def log_model_loading(self, model_name: str, status: str, details: str = None):
        """Log model loading with detailed information"""
        logger = logging.getLogger(__name__)
        if status == "start":
            logger.info(f"[LOADING] Loading {model_name}...")
            if details:
                logger.info(f"[LOADING] Details: {details}")
        elif status == "success":
            logger.info(f"[OK] {model_name} loaded successfully")
            if details:
                logger.info(f"[OK] Details: {details}")
        elif status == "error":
            logger.warning(f"[WARNING] {model_name} loading failed")
            if details:
                logger.warning(f"[WARNING] Error details: {details}")
    
    def log_system_info(self, device_name: str, cuda_version: str, gpu_memory: str):
        """Log detailed system information"""
        logger = logging.getLogger(__name__)
        logger.info(f"[OK] CUDA device: {device_name}")
        logger.info(f"[OK] CUDA version: {cuda_version}")
        logger.info(f"[OK] GPU memory: {gpu_memory}")
        logger.info(f"[OK] Python version: {sys.version.split()[0]}")
        logger.info(f"[OK] Platform: {sys.platform}")
    
    def log_startup_summary(self, total_time: float, models_loaded: int, success_rate: float):
        """Log detailed startup summary"""
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("[COMPLETE] STARTUP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"[TIME] Total startup time: {total_time:.2f}s")
        logger.info(f"[DEVICE] Device: cuda")
        logger.info(f"[DATA] Models loaded: {models_loaded}")
        logger.info(f"[OK] Success rate: {success_rate:.1f}%")
        logger.info(f"[OK] Server ready: {self.server_ready}")
        logger.info("=" * 60)
        logger.info("[READY] Server fully initialized - Ready to accept requests")
        logger.info("=" * 60)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, response_time: float = None):
        """Log API requests with detailed information"""
        logger = logging.getLogger(__name__)
        status_emoji = "✅" if 200 <= status_code < 300 else "❌" if status_code >= 400 else "⚠️"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        logger.info(f"[API] {status_emoji} {method} {endpoint} - {status_code}{time_info}")
    
    def log_websocket_event(self, event_type: str, user_id: str = None, details: str = None):
        """Log WebSocket events with detailed information"""
        logger = logging.getLogger(__name__)
        if event_type == "connect":
            logger.info(f"[WEBSOCKET] 🔌 User {user_id} connected")
        elif event_type == "disconnect":
            logger.info(f"[WEBSOCKET] 🔌 User {user_id} disconnected")
        elif event_type == "auth_success":
            logger.info(f"[WEBSOCKET] 🔐 Authentication successful for user {user_id}")
        elif event_type == "auth_failed":
            logger.warning(f"[WEBSOCKET] 🔐 Authentication failed for user {user_id}")
        elif event_type == "message":
            logger.info(f"[WEBSOCKET] 📨 Message received from user {user_id}")
        if details:
            logger.info(f"[WEBSOCKET] Details: {details}")
    
    def log_detection_event(self, event_type: str, filename: str = None, confidence: float = None, processing_time: float = None):
        """Log detection events with detailed information"""
        logger = logging.getLogger(__name__)
        if event_type == "start":
            logger.info(f"[DETECTION] 🔍 Starting detection for file: {filename}")
        elif event_type == "complete":
            logger.info(f"[DETECTION] ✅ Detection completed for {filename}")
            if confidence is not None:
                logger.info(f"[DETECTION] 📊 Confidence: {confidence:.3f}")
            if processing_time is not None:
                logger.info(f"[DETECTION] ⏱️ Processing time: {processing_time:.3f}s")
        elif event_type == "error":
            logger.error(f"[DETECTION] ❌ Detection failed for {filename}")
    
    def log_authentication_event(self, event_type: str, user_email: str = None, success: bool = None):
        """Log authentication events with detailed information"""
        logger = logging.getLogger(__name__)
        if event_type == "login_attempt":
            logger.info(f"[AUTH] 🔐 Login attempt for user: {user_email}")
        elif event_type == "login_success":
            logger.info(f"[AUTH] ✅ Login successful for user: {user_email}")
        elif event_type == "login_failed":
            logger.warning(f"[AUTH] ❌ Login failed for user: {user_email}")
        elif event_type == "token_validation":
            status = "✅ Valid" if success else "❌ Invalid"
            logger.info(f"[AUTH] 🔐 Token validation: {status}")

# Global enhanced logger instance
enhanced_logger = EnhancedLogger()

def setup_enhanced_logging():
    """Setup enhanced logging configuration"""
    return enhanced_logger

def log_startup_message(message: str, phase: str = None):
    """Log a startup message with enhanced formatting"""
    enhanced_logger.log_startup_message(message, phase)

def log_model_loading(model_name: str, status: str, details: str = None):
    """Log model loading with detailed information"""
    enhanced_logger.log_model_loading(model_name, status, details)

def log_system_info(device_name: str, cuda_version: str, gpu_memory: str):
    """Log detailed system information"""
    enhanced_logger.log_system_info(device_name, cuda_version, gpu_memory)

def log_startup_summary(total_time: float, models_loaded: int, success_rate: float):
    """Log detailed startup summary"""
    enhanced_logger.log_startup_summary(total_time, models_loaded, success_rate)

def log_api_request(method: str, endpoint: str, status_code: int, response_time: float = None):
    """Log API requests with detailed information"""
    enhanced_logger.log_api_request(method, endpoint, status_code, response_time)

def log_websocket_event(event_type: str, user_id: str = None, details: str = None):
    """Log WebSocket events with detailed information"""
    enhanced_logger.log_websocket_event(event_type, user_id, details)

def log_detection_event(event_type: str, filename: str = None, confidence: float = None, processing_time: float = None):
    """Log detection events with detailed information"""
    enhanced_logger.log_detection_event(event_type, filename, confidence, processing_time)

def log_authentication_event(event_type: str, user_email: str = None, success: bool = None):
    """Log authentication events with detailed information"""
    enhanced_logger.log_authentication_event(event_type, user_email, success)
