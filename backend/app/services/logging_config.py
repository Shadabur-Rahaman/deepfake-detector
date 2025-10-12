# backend/app/services/logging_config.py - Enhanced Logging Configuration

import logging
import sys
import os
from typing import Dict, Any
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LoggingConfig:
    """Enhanced logging configuration with debug modes and filtering"""
    
    def __init__(self):
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.verbose_logging = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            # Determine log level
            if self.debug_mode:
                level = logging.DEBUG
            elif self.verbose_logging:
                level = logging.INFO
            else:
                level = getattr(logging, self.log_level, logging.INFO)
            
            # Create formatter
            if self.debug_mode:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s'
                )
            
            # Setup root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(level)
            
            # Remove existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
            # Create file handler if debug mode
            if self.debug_mode:
                file_handler = logging.FileHandler('deepfake_detector.log')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            
            # Configure specific loggers
            self._configure_specific_loggers()
            
            logger = logging.getLogger(__name__)
            logger.info(f"[OK] Logging configured - Level: {level}, Debug: {self.debug_mode}")
            
        except Exception as e:
            print(f"[ERROR] Logging setup failed: {e}")
    
    def _configure_specific_loggers(self):
        """Configure specific loggers with appropriate levels"""
        try:
            # Suppress verbose third-party logs unless in debug mode
            if not self.debug_mode:
                # Suppress OpenCV logs
                logging.getLogger('cv2').setLevel(logging.WARNING)
                
                # Suppress PyTorch logs
                logging.getLogger('torch').setLevel(logging.WARNING)
                logging.getLogger('torchvision').setLevel(logging.WARNING)
                
                # Suppress ultralytics logs
                logging.getLogger('ultralytics').setLevel(logging.WARNING)
                
                # Suppress transformers logs
                logging.getLogger('transformers').setLevel(logging.WARNING)
                
                # Suppress PIL logs
                logging.getLogger('PIL').setLevel(logging.WARNING)
                
                # Suppress requests logs
                logging.getLogger('requests').setLevel(logging.WARNING)
                logging.getLogger('urllib3').setLevel(logging.WARNING)
            
            # Configure our application loggers
            app_loggers = [
                'app.services.async_detector',
                'app.services.websocket_handler',
                'app.services.face_detector',
                'app.services.deepfake_detector',
                'app.main'
            ]
            
            for logger_name in app_loggers:
                logger = logging.getLogger(logger_name)
                if self.debug_mode:
                    logger.setLevel(logging.DEBUG)
                else:
                    logger.setLevel(logging.INFO)
            
        except Exception as e:
            print(f"[ERROR] Specific logger configuration failed: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with appropriate configuration"""
        return logging.getLogger(name)
    
    def log_detection_event(self, logger: logging.Logger, event_type: str, **kwargs):
        """Log detection events with structured data"""
        try:
            if event_type == "detection_started":
                logger.info(f"[START] Detection started - Client: {kwargs.get('client_id', 'unknown')}")
            
            elif event_type == "detection_stopped":
                logger.info(f"[SHUTDOWN] Detection stopped - Client: {kwargs.get('client_id', 'unknown')}, Frames: {kwargs.get('frames_processed', 0)}")
            
            elif event_type == "frame_processed":
                if self.debug_mode:
                    logger.debug(f"📥 Frame processed - ID: {kwargs.get('frame_id', 0)}, Faces: {kwargs.get('faces_detected', 0)}, Time: {kwargs.get('processing_time', 0)}ms")
                else:
                    # Only log every 10th frame in non-debug mode
                    if kwargs.get('frame_id', 0) % 10 == 0:
                        logger.info(f"📥 Processed {kwargs.get('frame_id', 0)} frames")
            
            elif event_type == "detection_result":
                result = kwargs.get('result', 'Unknown')
                confidence = kwargs.get('confidence', 0)
                logger.info(f"🎯 Detection: {result} ({confidence:.1f}%) - Faces: {kwargs.get('faces_detected', 0)}")
            
            elif event_type == "error":
                logger.error(f"[ERROR] Error - {kwargs.get('error_type', 'Unknown')}: {kwargs.get('message', 'No message')}")
            
            elif event_type == "gpu_memory":
                if self.debug_mode:
                    memory_used = kwargs.get('memory_used', 0)
                    logger.debug(f"💾 GPU Memory: {memory_used:.2f} GB")
            
            elif event_type == "batch_processed":
                if self.debug_mode:
                    batch_size = kwargs.get('batch_size', 0)
                    processing_time = kwargs.get('processing_time', 0)
                    logger.debug(f"[MODELS] Batch processed - Size: {batch_size}, Time: {processing_time:.2f}ms")
            
            else:
                logger.info(f"📝 Event: {event_type} - {kwargs}")
                
        except Exception as e:
            logger.error(f"[ERROR] Logging event failed: {e}")
    
    def log_performance_metrics(self, logger: logging.Logger, metrics: Dict[str, Any]):
        """Log performance metrics"""
        try:
            if self.debug_mode:
                logger.debug(f"[DATA] Performance Metrics: {metrics}")
            else:
                # Log summary metrics
                frames_processed = metrics.get('frames_processed', 0)
                avg_processing_time = metrics.get('average_processing_time', 0)
                gpu_memory = metrics.get('gpu_memory_used', 0)
                
                if frames_processed > 0:
                    logger.info(f"[DATA] Performance - Frames: {frames_processed}, Avg Time: {avg_processing_time:.2f}ms, GPU: {gpu_memory:.2f}GB")
                
        except Exception as e:
            logger.error(f"[ERROR] Performance logging failed: {e}")
    
    def log_websocket_event(self, logger: logging.Logger, event_type: str, **kwargs):
        """Log WebSocket events"""
        try:
            client_id = kwargs.get('client_id', 'unknown')
            
            if event_type == "client_connected":
                logger.info(f"🔌 Client connected - ID: {client_id}")
            
            elif event_type == "client_disconnected":
                reason = kwargs.get('reason', 'Unknown')
                logger.info(f"🔌 Client disconnected - ID: {client_id}, Reason: {reason}")
            
            elif event_type == "message_received":
                if self.debug_mode:
                    message_type = kwargs.get('message_type', 'unknown')
                    logger.debug(f"📨 Message received - Client: {client_id}, Type: {message_type}")
            
            elif event_type == "message_sent":
                if self.debug_mode:
                    message_type = kwargs.get('message_type', 'unknown')
                    logger.debug(f"📤 Message sent - Client: {client_id}, Type: {message_type}")
            
            elif event_type == "heartbeat":
                if self.debug_mode:
                    logger.debug(f"💓 Heartbeat - Client: {client_id}")
            
            else:
                logger.info(f"🔌 WebSocket Event: {event_type} - Client: {client_id}")
                
        except Exception as e:
            logger.error(f"[ERROR] WebSocket logging failed: {e}")
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.debug_mode
    
    def is_verbose_mode(self) -> bool:
        """Check if verbose mode is enabled"""
        return self.verbose_logging
    
    def get_log_level(self) -> str:
        """Get current log level"""
        return self.log_level

# Global logging configuration instance
logging_config = LoggingConfig()

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger"""
    return logging_config.get_logger(name)

def log_detection_event(logger: logging.Logger, event_type: str, **kwargs):
    """Log detection events"""
    logging_config.log_detection_event(logger, event_type, **kwargs)

def log_performance_metrics(logger: logging.Logger, metrics: Dict[str, Any]):
    """Log performance metrics"""
    logging_config.log_performance_metrics(logger, metrics)

def log_websocket_event(logger: logging.Logger, event_type: str, **kwargs):
    """Log WebSocket events"""
    logging_config.log_websocket_event(logger, event_type, **kwargs)
