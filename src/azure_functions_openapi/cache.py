# src/azure_functions_openapi/cache.py

from functools import wraps
import hashlib
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache manager for OpenAPI specifications and related data."""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default TTL
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._access_times: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None

        cache_entry = self._cache[key]
        current_time = time.time()

        # Check if expired
        if current_time > cache_entry["expires_at"]:
            self.delete(key)
            return None

        # Update access time for LRU
        self._access_times[key] = current_time
        return cache_entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        current_time = time.time()
        expires_at = current_time + (ttl or self.default_ttl)

        self._cache[key] = {"value": value, "expires_at": expires_at, "created_at": current_time}
        self._access_times[key] = current_time

        logger.debug(f"Cached value for key: {key} (TTL: {ttl or self.default_ttl}s)")

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        deleted = key in self._cache
        if deleted:
            del self._cache[key]
            if key in self._access_times:
                del self._access_times[key]
            logger.debug(f"Deleted cache entry for key: {key}")
        return deleted

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() if current_time > entry["expires_at"]
        ]

        for key in expired_keys:
            self.delete(key)

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        current_time = time.time()
        active_entries = sum(
            1 for entry in self._cache.values() if current_time <= entry["expires_at"]
        )

        return {
            "total_entries": len(self._cache),
            "active_entries": active_entries,
            "expired_entries": len(self._cache) - active_entries,
            "default_ttl": self.default_ttl,
        }


# Global cache instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a cache key from arguments."""
    # Create a deterministic string representation
    key_data = {"args": args, "kwargs": sorted(kwargs.items()) if kwargs else {}}

    # Convert to JSON string and hash
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode(), usedforsecurity=False).hexdigest()  # nosec B324


def cached(
    ttl: Optional[int] = None, key_prefix: str = ""
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to cache function results.

    Parameters:
        ttl: Time to live in seconds (uses cache manager default if None)
        key_prefix: Prefix for cache key
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{generate_cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_result = _cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)
            _cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern.

    Parameters:
        pattern: Pattern to match against cache keys

    Returns:
        Number of entries invalidated
    """
    keys_to_delete = [key for key in _cache_manager._cache.keys() if pattern in key]

    for key in keys_to_delete:
        _cache_manager.delete(key)

    if keys_to_delete:
        logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}")

    return len(keys_to_delete)


def clear_all_cache() -> None:
    """Clear all cache entries."""
    _cache_manager.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return _cache_manager.get_stats()


# Convenience functions for common caching scenarios
@cached(ttl=600, key_prefix="openapi_spec")  # 10 minutes
def cached_openapi_spec(title: str, version: str) -> Dict[str, Any]:
    """Cache OpenAPI specification generation."""
    from azure_functions_openapi.openapi import generate_openapi_spec

    return generate_openapi_spec(title, version)


@cached(ttl=300, key_prefix="openapi_json")  # 5 minutes
def cached_openapi_json(title: str, version: str) -> str:
    """Cache OpenAPI JSON generation."""
    from azure_functions_openapi.openapi import get_openapi_json

    return get_openapi_json()


@cached(ttl=300, key_prefix="openapi_yaml")  # 5 minutes
def cached_openapi_yaml(title: str, version: str) -> str:
    """Cache OpenAPI YAML generation."""
    from azure_functions_openapi.openapi import get_openapi_yaml

    return get_openapi_yaml()
