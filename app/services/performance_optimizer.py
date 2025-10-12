# app/services/performance_optimizer_enhanced.py
import functools
import time
import asyncio
from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DetectionCache:
    """Enhanced detection cache with TTL support"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[Any, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: Any) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.default_ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: Any, value: Any) -> None:
        """Set cached value with current timestamp"""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

# Global cache instance
detection_cache = DetectionCache(default_ttl=1800)  # 30 minutes default

def cache_detection(cache_store: DetectionCache, cache_key: str, expire: int = 1800):
    """
    Decorator to cache detection results
    
    Args:
        cache_store: DetectionCache instance to use
        cache_key: Base key for caching
        expire: Expiration time in seconds
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create unique cache key from function name, cache_key, and arguments
            key = f"{cache_key}_{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            try:
                # Try to get cached result
                cached_result = cache_store.get(key)
                if cached_result is not None:
                    logger.info(f"✅ Cache hit for {cache_key}")
                    return cached_result
                
                # Cache miss - execute function
                logger.info(f"🔄 Cache miss for {cache_key} - executing function")
                result = await func(*args, **kwargs)
                
                # Store result in cache
                cache_store.set(key, result)
                logger.info(f"💾 Cached result for {cache_key}")
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Cache error for {cache_key}: {e}")
                # If caching fails, just execute the function normally
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Additional utility functions
def clear_detection_cache():
    """Clear all detection cache entries"""
    detection_cache.clear()
    logger.info("🗑️ Detection cache cleared")

def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache_size": detection_cache.size(),
        "cache_ttl": detection_cache.default_ttl
    }
