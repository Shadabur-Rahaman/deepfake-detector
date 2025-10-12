"""
Advanced Logging Filters for Deepfake Detection System
Provides deduplication, phase grouping, and structured logging
"""

import logging
import time
from typing import Dict, Set, Optional
from collections import defaultdict, deque
from threading import Lock
import re


class DeduplicatingFilter(logging.Filter):
    """
    Filter that suppresses identical consecutive log messages within a time window
    """
    
    def __init__(self, time_window: float = 5.0, max_recent_messages: int = 100):
        super().__init__()
        self.time_window = time_window
        self.max_recent_messages = max_recent_messages
        self.recent_messages = deque(maxlen=max_recent_messages)
        self.message_times = {}
        self.lock = Lock()
        
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter duplicate messages within time window"""
        with self.lock:
            current_time = time.time()
            message = record.getMessage()
            
            # Check if this message was logged recently
            if message in self.message_times:
                last_time = self.message_times[message]
                if current_time - last_time < self.time_window:
                    # Suppress duplicate message
                    return False
            
            # Update message time and add to recent messages
            self.message_times[message] = current_time
            self.recent_messages.append((message, current_time))
            
            # Clean up old messages
            self._cleanup_old_messages(current_time)
            
            return True
    
    def _cleanup_old_messages(self, current_time: float):
        """Remove old message timestamps"""
        messages_to_remove = []
        for message, timestamp in self.message_times.items():
            if current_time - timestamp > self.time_window * 2:
                messages_to_remove.append(message)
        
        for message in messages_to_remove:
            del self.message_times[message]


class PhaseGroupingFilter(logging.Filter):
    """
    Filter that groups logs by phase and adds phase headers
    """
    
    def __init__(self):
        super().__init__()
        self.current_phase = None
        self.phase_start_time = None
        self.phase_logs = defaultdict(list)
        self.lock = Lock()
        
    def filter(self, record: logging.LogRecord) -> bool:
        """Add phase grouping to log records"""
        with self.lock:
            message = record.getMessage()
            
            # Detect phase changes
            new_phase = self._detect_phase(message)
            if new_phase and new_phase != self.current_phase:
                self._log_phase_summary()
                self._start_new_phase(new_phase)
            
            # Store log for current phase
            if self.current_phase:
                self.phase_logs[self.current_phase].append({
                    'message': message,
                    'level': record.levelname,
                    'time': time.time()
                })
            
            return True
    
    def _detect_phase(self, message: str) -> Optional[str]:
        """Detect phase from log message"""
        phase_patterns = {
            'STARTUP': [r'[START].*starting', r'initializing.*system', r'loading.*models'],
            'MODEL_LOADING': [r'loading.*model', r'[OK].*model.*initialized', r'🤖.*detector.*enabled'],
            'DETECTION': [r'detecting.*deepfake', r'🎯.*running.*detection', r'processing.*faces'],
            'INFERENCE': [r'running.*inference', r'forward.*pass', r'prediction.*result'],
            'SHUTDOWN': [r'[SHUTDOWN].*shutting.*down', r'cleanup.*resources']
        }
        
        message_lower = message.lower()
        for phase, patterns in phase_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return phase
        
        return None
    
    def _start_new_phase(self, phase: str):
        """Start a new phase"""
        self.current_phase = phase
        self.phase_start_time = time.time()
        
        # Log phase header
        logger = logging.getLogger()
        logger.info(f"\n{'='*60}")
        logger.info(f"=== {phase} PHASE ===")
        logger.info(f"{'='*60}")
    
    def _log_phase_summary(self):
        """Log summary of completed phase"""
        if not self.current_phase or not self.phase_logs[self.current_phase]:
            return
        
        phase_logs = self.phase_logs[self.current_phase]
        duration = time.time() - self.phase_start_time if self.phase_start_time else 0
        
        # Count log levels
        level_counts = defaultdict(int)
        for log_entry in phase_logs:
            level_counts[log_entry['level']] += 1
        
        # Log phase summary
        logger = logging.getLogger()
        logger.info(f"\n--- {self.current_phase} PHASE SUMMARY ---")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info(f"Total logs: {len(phase_logs)}")
        for level, count in level_counts.items():
            logger.info(f"{level}: {count}")
        logger.info(f"{'='*60}\n")


class ModelSuccessFilter(logging.Filter):
    """
    Filter that tracks model initialization success rates
    """
    
    def __init__(self):
        super().__init__()
        self.model_stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'models': {}
        }
        self.lock = Lock()
        
    def filter(self, record: logging.LogRecord) -> bool:
        """Track model initialization success"""
        with self.lock:
            message = record.getMessage()
            
            # Track model initialization attempts
            if re.search(r'loading.*model|initializing.*detector', message, re.IGNORECASE):
                self.model_stats['total_attempts'] += 1
                
                # Extract model name
                model_name = self._extract_model_name(message)
                if model_name:
                    self.model_stats['models'][model_name] = {
                        'status': 'loading',
                        'start_time': time.time()
                    }
            
            # Track successful initializations
            elif re.search(r'[OK].*initialized|[OK].*enabled|successfully.*loaded', message, re.IGNORECASE):
                self.model_stats['successful'] += 1
                model_name = self._extract_model_name(message)
                if model_name and model_name in self.model_stats['models']:
                    self.model_stats['models'][model_name]['status'] = 'success'
            
            # Track failures
            elif re.search(r'[ERROR].*failed|error.*loading|warning.*not.*available', message, re.IGNORECASE):
                self.model_stats['failed'] += 1
                model_name = self._extract_model_name(message)
                if model_name and model_name in self.model_stats['models']:
                    self.model_stats['models'][model_name]['status'] = 'failed'
            
            return True
    
    def _extract_model_name(self, message: str) -> Optional[str]:
        """Extract model name from log message"""
        patterns = [
            r'(\w+)\s+detector',
            r'(\w+)\s+model',
            r'(\w+)\s+initialized',
            r'loading\s+(\w+)',
            r'(\w+)\s+enabled'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return None
    
    def get_success_rate(self) -> Dict[str, any]:
        """Get model initialization success rate"""
        with self.lock:
            total = self.model_stats['total_attempts']
            if total == 0:
                return {'success_rate': 0.0, 'stats': self.model_stats}
            
            success_rate = (self.model_stats['successful'] / total) * 100
            return {
                'success_rate': success_rate,
                'stats': self.model_stats.copy()
            }


class StructuredLoggingFormatter(logging.Formatter):
    """
    Custom formatter that provides structured, clean logging output
    """
    
    def __init__(self):
        super().__init__()
        self.phase_colors = {
            'STARTUP': '\033[94m',      # Blue
            'MODEL_LOADING': '\033[92m', # Green
            'DETECTION': '\033[93m',     # Yellow
            'INFERENCE': '\033[95m',     # Magenta
            'SHUTDOWN': '\033[91m'       # Red
        }
        self.reset_color = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structure and colors"""
        # Get base format
        base_format = super().format(record)
        
        # Add phase coloring if available
        if hasattr(record, 'phase'):
            color = self.phase_colors.get(record.phase, '')
            return f"{color}{base_format}{self.reset_color}"
        
        return base_format


def setup_advanced_logging():
    """
    Setup advanced logging with all filters and formatters
    """
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add filters
    dedup_filter = DeduplicatingFilter(time_window=3.0)
    phase_filter = PhaseGroupingFilter()
    success_filter = ModelSuccessFilter()
    
    console_handler.addFilter(dedup_filter)
    console_handler.addFilter(phase_filter)
    console_handler.addFilter(success_filter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # Return filters for external access
    return {
        'dedup_filter': dedup_filter,
        'phase_filter': phase_filter,
        'success_filter': success_filter
    }


def log_model_summary(success_filter: ModelSuccessFilter):
    """
    Log a summary of model initialization results
    """
    stats = success_filter.get_success_rate()
    logger = logging.getLogger(__name__)
    
    logger.info(f"\n{'='*60}")
    logger.info("=== MODEL INITIALIZATION SUMMARY ===")
    logger.info(f"{'='*60}")
    logger.info(f"Total Models Attempted: {stats['stats']['total_attempts']}")
    logger.info(f"Successfully Initialized: {stats['stats']['successful']}")
    logger.info(f"Failed to Initialize: {stats['stats']['failed']}")
    logger.info(f"Success Rate: {stats['success_rate']:.1f}%")
    
    # Log individual model status
    if stats['stats']['models']:
        logger.info("\nIndividual Model Status:")
        for model_name, model_info in stats['stats']['models'].items():
            status_emoji = "[OK]" if model_info['status'] == 'success' else "[ERROR]" if model_info['status'] == 'failed' else "⏳"
            logger.info(f"  {status_emoji} {model_name}: {model_info['status']}")
    
    logger.info(f"{'='*60}\n")
