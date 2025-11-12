"""
Caching Utilities - Phase 4

Provides in-memory caching for expensive operations like vector searches.
Reduces load on Qdrant and improves response times for similar queries.
"""

import time
import hashlib
import json
from typing import Any, Callable, Optional, Dict
from functools import wraps
from collections import OrderedDict
from threading import RLock


class TTLCache:
    """
    Time-To-Live (TTL) cache with thread-safe operations.

    This cache stores items with an expiration time. Items are automatically
    removed when they expire. Uses LRU eviction when max_size is reached.
    """

    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        """
        Initialize TTL cache.

        Args:
            max_size: Maximum number of items to store (default: 1000)
            default_ttl: Default time-to-live in seconds (default: 300s = 5min)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = RLock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if it exists and hasn't expired.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            expiry = entry["expiry"]

            # Check if expired
            if time.time() > expiry:
                del self._cache[key]
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """
        Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
        """
        with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            expiry = time.time() + ttl

            # Remove oldest item if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)  # Remove oldest (FIFO)

            self._cache[key] = {
                "value": value,
                "expiry": expiry,
            }
            self._cache.move_to_end(key)

    def clear(self):
        """Clear all cached items."""
        with self._lock:
            self._cache.clear()

    def delete(self, key: str):
        """Remove a specific cache entry if it exists."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def size(self) -> int:
        """Get current number of cached items."""
        with self._lock:
            return len(self._cache)

    def cleanup_expired(self):
        """Remove all expired entries."""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now > entry["expiry"]
            ]
            for key in expired_keys:
                del self._cache[key]


# Global cache instances
_search_cache = TTLCache(max_size=500, default_ttl=300.0)  # 5 minutes
_patient_history_cache = TTLCache(max_size=200, default_ttl=600.0)  # 10 minutes


def get_search_cache() -> TTLCache:
    """Get the global search results cache."""
    return _search_cache


def get_patient_history_cache() -> TTLCache:
    """Get the global patient history cache."""
    return _patient_history_cache


def cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Uses JSON serialization and SHA256 hash for consistent keys.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Hex string cache key
    """
    # Create a stable representation of arguments
    key_data = {
        "args": args,
        "kwargs": kwargs,
    }

    # Serialize to JSON (sorted for consistency)
    try:
        json_str = json.dumps(key_data, sort_keys=True, default=str)
    except (TypeError, ValueError):
        # Fallback to string representation if JSON fails
        json_str = str(key_data)

    # Hash to create compact key
    return hashlib.sha256(json_str.encode()).hexdigest()[:16]


def cached(
    cache: TTLCache,
    ttl: Optional[float] = None,
    key_func: Optional[Callable] = None
):
    """
    Decorator to cache function results with TTL.

    Args:
        cache: TTLCache instance to use
        ttl: Time-to-live in seconds (uses cache default if None)
        key_func: Optional function to generate cache key from args/kwargs
                  Default: uses cache_key(*args, **kwargs)

    Returns:
        Decorated function with caching

    Example:
        >>> search_cache = TTLCache(max_size=100, default_ttl=300)
        >>>
        >>> @cached(search_cache, ttl=600)
        ... def expensive_search(query: str, limit: int = 10):
        ...     # Expensive operation
        ...     return results
        ...
        >>> result = expensive_search("query")  # Computed
        >>> result = expensive_search("query")  # Cached (fast!)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Skip 'self' argument for instance methods
                cache_args = args[1:] if args and hasattr(args[0], '__dict__') else args
                key = f"{func.__name__}:{cache_key(*cache_args, **kwargs)}"

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Compute value
            value = func(*args, **kwargs)

            # Store in cache
            cache.set(key, value, ttl=ttl)

            return value

        # Add cache control methods
        wrapper.cache_clear = cache.clear
        wrapper.cache_info = lambda: {"size": cache.size()}

        return wrapper
    return decorator


def clear_all_caches():
    """Clear all global caches."""
    _search_cache.clear()
    _patient_history_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics about all caches."""
    return {
        "search_cache": {
            "size": _search_cache.size(),
            "max_size": _search_cache.max_size,
            "default_ttl": _search_cache.default_ttl,
        },
        "patient_history_cache": {
            "size": _patient_history_cache.size(),
            "max_size": _patient_history_cache.max_size,
            "default_ttl": _patient_history_cache.default_ttl,
        },
    }


def invalidate_patient_history_cache(patient_id: str, limit: int = 10):
    """
    Invalidate cached history for a specific patient.

    The get_patient_history decorator uses function name + hashed args as key.
    """
    key = f"get_patient_history:{cache_key(patient_id, limit)}"
    _patient_history_cache.delete(key)
