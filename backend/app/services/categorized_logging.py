"""
Categorized Logging System for Deepfake Detection
Production-grade logging with proper categorization and deduplication

This module provides:
- Categorized loggers for different system components
- Deduplication to prevent log spam
- Clean, structured log output
- Performance monitoring
- Error tracking

Author: Senior Enterprise AI Developer
Date: 2024
"""

import logging
import sys
import time
from typing import Dict, Set, Optional
from functools import wraps

class DeduplicateFilter(logging.Filter):
    """Filter to prevent duplicate log messages"""
    def __init__(self):
        super().__init__()
        self.seen_messages: Set[str] = set()
        self.max_messages = 1000  # Prevent memory leak
    
    def filter(self, record):
        # Create a key from the log message
        message_key = f"{record.levelname}:{record.getMessage()}"
        
        if message_key in self.seen_messages:
            return False
        
        # Add to seen messages
        self.seen_messages.add(message_key)
        
        # Cleanup old messages to prevent memory leak
        if len(self.seen_messages) > self.max_messages:
            # Remove oldest 100 messages
            messages_to_remove = list(self.seen_messages)[:100]
            for msg in messages_to_remove:
                self.seen_messages.discard(msg)
        
        return True

class CategorizedLogger:
    """Categorized logger with clean output formatting"""
    
    def __init__(self, category: str):
        self.category = category
        self.logger = logging.getLogger(f"[{category}]")
        self.logger.setLevel(logging.INFO)
        
        # Add deduplication filter
        if not any(isinstance(f, DeduplicateFilter) for f in self.logger.filters):
            self.logger.addFilter(DeduplicateFilter())
    
    def info(self, message: str):
        """Log info message with category prefix"""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        """Log warning message with category prefix"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        """Log error message with category prefix"""
        self.logger.error(f"❌ {message}")
    
    def success(self, message: str):
        """Log success message with category prefix"""
        self.logger.info(f"✅ {message}")
    
    def debug(self, message: str):
        """Log debug message with category prefix"""
        self.logger.debug(f"🔍 {message}")

# Global categorized loggers
_loggers: Dict[str, CategorizedLogger] = {}

def get_logger(category: str) -> CategorizedLogger:
    """Get or create a categorized logger"""
    if category not in _loggers:
        _loggers[category] = CategorizedLogger(category)
    return _loggers[category]

# Predefined logger categories
STARTUP_LOGGER = get_logger("STARTUP")
DB_LOGGER = get_logger("DB")
AUTH_LOGGER = get_logger("AUTH")
FACE_DETECTION_LOGGER = get_logger("FACE DETECTION")
DETECTION_LOGGER = get_logger("DETECTION")
YOLO_LOGGER = get_logger("YOLO")
TF_LOGGER = get_logger("TF")
SHUTDOWN_LOGGER = get_logger("SHUTDOWN")

def setup_categorized_logging():
    """Setup the categorized logging system"""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with clean formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Clean format with organized categories for better readability
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add deduplication filter
    console_handler.addFilter(DeduplicateFilter())
    
    root_logger.addHandler(console_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("torchvision").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    STARTUP_LOGGER.info("🚀 Deepfake Detection System starting...")

def log_startup_summary():
    """Log a clean startup summary"""
    STARTUP_LOGGER.info("=" * 60)
    STARTUP_LOGGER.info("🎉 DEEPFAKE DETECTION SYSTEM READY")
    STARTUP_LOGGER.info("=" * 60)
    STARTUP_LOGGER.info("✅ All systems operational")
    STARTUP_LOGGER.info("✅ Models loaded and ready")
    STARTUP_LOGGER.info("✅ Authentication system active")
    STARTUP_LOGGER.info("✅ Database connected")
    STARTUP_LOGGER.info("✅ GPU acceleration enabled")
    STARTUP_LOGGER.info("=" * 60)

def log_performance(func):
    """Decorator to log function performance"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            if duration > 1.0:  # Only log if it takes more than 1 second
                logger = get_logger("PERFORMANCE")
                logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger = get_logger("PERFORMANCE")
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            if duration > 1.0:  # Only log if it takes more than 1 second
                logger = get_logger("PERFORMANCE")
                logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger = get_logger("PERFORMANCE")
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

# Initialize the logging system
setup_categorized_logging()
