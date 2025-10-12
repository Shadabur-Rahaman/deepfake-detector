"""
Simple Logging Configuration - No complex dependencies
Produces the exact clean format you requested
"""

import logging
import sys
from datetime import datetime

def setup_simple_clean_logging():
    """Setup simple clean logging that works without hanging"""
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create the exact formatter you requested
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # Suppress noisy loggers
    noisy_loggers = [
        'matplotlib', 'PIL', 'urllib3', 'requests', 'httpx',
        'torch.distributed', 'torch.nn', 'torch.optim',
        'transformers', 'timm', 'ultralytics', 'cv2',
        'numpy', 'scipy', 'sklearn', 'tensorflow'
    ]
    
    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    return root_logger

def log_startup_message(message: str):
    """Log a startup message with the clean format"""
    logger = logging.getLogger(__name__)
    logger.info(message)

def log_model_loading(model_name: str, status: str):
    """Log model loading with clean format"""
    logger = logging.getLogger(__name__)
    if status == "start":
        logger.info(f"[LOADING] Loading {model_name}...")
    elif status == "success":
        logger.info(f"[OK] {model_name} loaded successfully")
    elif status == "error":
        logger.warning(f"[WARNING] {model_name} loading failed")

def log_system_info(device_name: str, cuda_version: str, gpu_memory: str):
    """Log system information"""
    logger = logging.getLogger(__name__)
    logger.info(f"[OK] CUDA device: {device_name}")
    logger.info(f"[OK] CUDA version: {cuda_version}")
    logger.info(f"[OK] GPU memory: {gpu_memory}")

def log_startup_summary(total_time: float, models_loaded: int, success_rate: float):
    """Log startup summary"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("[COMPLETE] STARTUP SUMMARY")
    logger.info("=" * 50)
    logger.info(f"[TIME]  Total startup time: {total_time:.2f}s")
    logger.info(f"[DEVICE]  Device: cuda")
    logger.info(f"[DATA] Models loaded: {models_loaded}")
    logger.info(f"[OK] Success rate: {success_rate:.1f}%")
    logger.info("=" * 50)
    logger.info("[START] Server ready to accept requests")
    logger.info("=" * 50)
