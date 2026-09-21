"""
Advanced Resource Manager
Provides comprehensive resource management, memory cleanup, and thread safety
"""

import asyncio
import threading
import time
import os
import gc
import logging
from typing import Dict, Set, Optional
from collections import OrderedDict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available for CUDA memory management")


class ThreadSafeDict:
    """Thread-safe dictionary with automatic cleanup"""
    
    def __init__(self, max_size: int = 100, cleanup_interval: int = 300):
        self._dict = {}
        self._lock = threading.RLock()
        self._access_times = OrderedDict()
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
    
    def get(self, key: str, default=None):
        with self._lock:
            if key in self._dict:
                if key in self._access_times:
                    self._access_times.move_to_end(key)
                self._access_times[key] = time.time()
            return self._dict.get(key, default)
    
    def __setitem__(self, key: str, value):
        with self._lock:
            self._dict[key] = value
            self._access_times[key] = time.time()
            self._access_times.move_to_end(key)
            self._maybe_cleanup()
    
    def __getitem__(self, key: str):
        with self._lock:
            return self._dict[key]
    
    def __contains__(self, key: str):
        with self._lock:
            return key in self._dict
    
    def __delitem__(self, key: str):
        with self._lock:
            if key in self._dict:
                del self._dict[key]
            if key in self._access_times:
                del self._access_times[key]
    
    def pop(self, key: str, default=None):
        with self._lock:
            if key in self._access_times:
                del self._access_times[key]
            return self._dict.pop(key, default)
    
    def keys(self):
        with self._lock:
            return list(self._dict.keys())
    
    def values(self):
        with self._lock:
            return list(self._dict.values())
    
    def items(self):
        with self._lock:
            return list(self._dict.items())
    
    def update(self, *args, **kwargs):
        with self._lock:
            self._dict.update(*args, **kwargs)
            for key in kwargs.keys():
                if key in self._access_times:
                    self._access_times.move_to_end(key)
                self._access_times[key] = time.time()
            self._maybe_cleanup()
    
    def _maybe_cleanup(self):
        """Clean up old entries if needed"""
        current_time = time.time()
        
        if (current_time - self._last_cleanup > self._cleanup_interval) or \
           (len(self._dict) > self._max_size):
            
            if len(self._dict) > self._max_size:
                remove_count = int(self._max_size * 0.2)
                for _ in range(remove_count):
                    if self._access_times:
                        oldest_key = next(iter(self._access_times))
                        del self._dict[oldest_key]
                        del self._access_times[oldest_key]
            
            cutoff_time = current_time - 3600  # 1 hour
            keys_to_remove = [
                key for key, access_time in list(self._access_times.items())
                if access_time < cutoff_time
            ]
            
            for key in keys_to_remove:
                if key in self._dict:
                    del self._dict[key]
                if key in self._access_times:
                    del self._access_times[key]
            
            self._last_cleanup = current_time
            if keys_to_remove:
                logger.info(f"🧹 Cleaned up {len(keys_to_remove)} old entries from cache")


class ThreadSafeSet:
    """Thread-safe set with automatic cleanup"""
    
    def __init__(self, max_size: int = 200):
        self._set = set()
        self._lock = threading.RLock()
        self._max_size = max_size
    
    def add(self, item):
        with self._lock:
            self._set.add(item)
            if len(self._set) > self._max_size:
                items_list = list(self._set)
                remove_count = int(self._max_size * 0.2)
                for item_to_remove in items_list[:remove_count]:
                    self._set.discard(item_to_remove)
                logger.info(f"🧹 Cleaned up {remove_count} old items from set")
    
    def discard(self, item):
        with self._lock:
            self._set.discard(item)
    
    def __contains__(self, item):
        with self._lock:
            return item in self._set
    
    def __len__(self):
        with self._lock:
            return len(self._set)
    
    def __iter__(self):
        with self._lock:
            return iter(list(self._set))
    
    def clear(self):
        with self._lock:
            self._set.clear()


class AdvancedResourceManager:
    """Comprehensive resource manager for cleanup, memory management, and thread safety"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._file_cleanup_queue = []
        self._cuda_memory_cleanup_enabled = True
        self._cleanup_interval = 300  # 5 minutes
        self._last_cuda_cleanup = time.time()
        self._active_detections = set()
        self._start_background_cleanup()
    
    def _start_background_cleanup(self):
        """Start background cleanup task"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self._cleanup_interval)
                    self._perform_periodic_cleanup()
                except Exception as e:
                    logger.error(f"Background cleanup error: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("✅ Background cleanup worker started")
    
    def register_file_for_cleanup(self, file_path: str, delay_seconds: int = 300):
        """Register a file for automatic cleanup after delay"""
        with self._lock:
            cleanup_time = time.time() + delay_seconds
            self._file_cleanup_queue.append((file_path, cleanup_time))
    
    def cleanup_files(self):
        """Clean up files that have passed their cleanup time"""
        current_time = time.time()
        files_to_remove = []
        
        with self._lock:
            remaining_files = []
            for file_path, cleanup_time in self._file_cleanup_queue:
                if current_time >= cleanup_time:
                    files_to_remove.append(file_path)
                else:
                    remaining_files.append((file_path, cleanup_time))
            self._file_cleanup_queue = remaining_files
        
        cleaned_count = 0
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup file {file_path}: {e}")
        
        return cleaned_count
    
    def cleanup_cuda_memory(self, force: bool = False):
        """Clean up CUDA memory"""
        if not TORCH_AVAILABLE or not torch.cuda.is_available():
            return
        
        current_time = time.time()
        if not force and (current_time - self._last_cuda_cleanup) < self._cleanup_interval:
            return
        
        try:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
            torch.cuda.empty_cache()
            
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / (1024**3)
                reserved = torch.cuda.memory_reserved() / (1024**3)
                logger.info(f"🧹 CUDA memory cleanup: {allocated:.2f}GB allocated, {reserved:.2f}GB reserved")
            
            self._last_cuda_cleanup = current_time
        except Exception as e:
            logger.warning(f"⚠️ CUDA memory cleanup failed: {e}")
    
    def _perform_periodic_cleanup(self):
        """Perform periodic cleanup tasks"""
        self.cleanup_files()
        if self._cuda_memory_cleanup_enabled:
            self.cleanup_cuda_memory()
        gc.collect()
    
    def register_active_detection(self, video_id: str):
        """Register an active detection"""
        with self._lock:
            self._active_detections.add(video_id)
    
    def unregister_active_detection(self, video_id: str):
        """Unregister an active detection"""
        with self._lock:
            self._active_detections.discard(video_id)


_resource_manager = None

def get_resource_manager() -> AdvancedResourceManager:
    """Get global resource manager instance"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = AdvancedResourceManager()
    return _resource_manager
