# tests/test_cache.py

import time
import pytest
from typing import Any
from unittest.mock import patch, MagicMock

from azure_functions_openapi.cache import (
    CacheManager,
    get_cache_manager,
    generate_cache_key,
    cached,
    invalidate_cache,
    clear_all_cache,
    get_cache_stats,
    cached_openapi_spec,
    cached_openapi_json,
    cached_openapi_yaml,
)


class TestCacheManager:
    """Test CacheManager class."""

    def test_cache_manager_initialization(self) -> None:
        """Test CacheManager initialization."""
        cache = CacheManager(default_ttl=300)
        assert cache.default_ttl == 300
        assert len(cache._cache) == 0
        assert len(cache._access_times) == 0

    def test_set_and_get(self) -> None:
        """Test setting and getting cache values."""
        cache = CacheManager(default_ttl=300)

        # Set value
        cache.set("test_key", "test_value")

        # Get value
        value = cache.get("test_key")
        assert value == "test_value"

    def test_get_nonexistent_key(self) -> None:
        """Test getting non-existent key."""
        cache = CacheManager()
        value = cache.get("nonexistent")
        assert value is None

    def test_get_expired_key(self) -> None:
        """Test getting expired key."""
        cache = CacheManager(default_ttl=1)  # 1 second TTL

        # Set value
        cache.set("test_key", "test_value")

        # Wait for expiration
        time.sleep(1.1)

        # Get expired value
        value = cache.get("test_key")
        assert value is None

    def test_custom_ttl(self) -> None:
        """Test custom TTL."""
        cache = CacheManager(default_ttl=300)

        # Set with custom TTL
        cache.set("test_key", "test_value", ttl=1)

        # Should be available immediately
        assert cache.get("test_key") == "test_value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("test_key") is None

    def test_delete(self) -> None:
        """Test deleting cache entries."""
        cache = CacheManager()

        # Set value
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        # Delete value
        result = cache.delete("test_key")
        assert result is True
        assert cache.get("test_key") is None

        # Delete non-existent key
        result = cache.delete("nonexistent")
        assert result is False

    def test_clear(self) -> None:
        """Test clearing all cache entries."""
        cache = CacheManager()

        # Set multiple values
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache._cache) == 2

        # Clear cache
        cache.clear()
        assert len(cache._cache) == 0
        assert len(cache._access_times) == 0

    def test_cleanup_expired(self) -> None:
        """Test cleaning up expired entries."""
        cache = CacheManager(default_ttl=1)

        # Set values with different TTLs
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=5)

        # Wait for first key to expire
        time.sleep(1.1)

        # Cleanup expired entries
        removed_count = cache.cleanup_expired()
        assert removed_count == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_get_stats(self) -> None:
        """Test getting cache statistics."""
        cache = CacheManager(default_ttl=1)

        # Set values
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=5)

        # Get stats immediately
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2
        assert stats["expired_entries"] == 0
        assert stats["default_ttl"] == 1

        # Wait for expiration and get stats again
        time.sleep(1.1)
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 1
        assert stats["expired_entries"] == 1


class TestGenerateCacheKey:
    """Test generate_cache_key function."""

    def test_generate_cache_key_with_args(self) -> None:
        """Test generating cache key with arguments."""
        key1 = generate_cache_key("arg1", "arg2")
        key2 = generate_cache_key("arg1", "arg2")
        key3 = generate_cache_key("arg1", "arg3")

        # Same args should generate same key
        assert key1 == key2
        # Different args should generate different keys
        assert key1 != key3

    def test_generate_cache_key_with_kwargs(self) -> None:
        """Test generating cache key with keyword arguments."""
        key1 = generate_cache_key(param1="value1", param2="value2")
        key2 = generate_cache_key(param1="value1", param2="value2")
        key3 = generate_cache_key(param1="value1", param2="value3")

        # Same kwargs should generate same key
        assert key1 == key2
        # Different kwargs should generate different keys
        assert key1 != key3

    def test_generate_cache_key_mixed(self) -> None:
        """Test generating cache key with mixed args and kwargs."""
        key1 = generate_cache_key("arg1", param1="value1")
        key2 = generate_cache_key("arg1", param1="value1")
        key3 = generate_cache_key("arg2", param1="value1")

        # Same args and kwargs should generate same key
        assert key1 == key2
        # Different args should generate different keys
        assert key1 != key3


class TestCachedDecorator:
    """Test @cached decorator."""

    def test_cached_decorator_basic(self) -> None:
        """Test basic caching functionality."""
        call_count = 0

        @cached(ttl=300)
        def test_function(value: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # First call should execute function
        result1 = test_function("test")
        assert result1 == "result_test"
        assert call_count == 1

        # Second call should use cache
        result2 = test_function("test")
        assert result2 == "result_test"
        assert call_count == 1  # Should not increment

        # Different argument should execute function again
        result3 = test_function("different")
        assert result3 == "result_different"
        assert call_count == 2

    def test_cached_decorator_with_key_prefix(self) -> None:
        """Test cached decorator with key prefix."""
        call_count = 0

        @cached(ttl=300, key_prefix="test_prefix")
        def test_function(value: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # Call function
        result = test_function("test")
        assert result == "result_test"
        assert call_count == 1

        # Verify cache key includes prefix
        cache_manager = get_cache_manager()
        cache_keys = list(cache_manager._cache.keys())
        assert any("test_prefix" in key for key in cache_keys)

    def test_cached_decorator_expiration(self) -> None:
        """Test cached decorator with expiration."""
        call_count = 0

        @cached(ttl=1, key_prefix="expiration_test")  # 1 second TTL
        def test_function(value: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"result_{value}"

        # Clear any existing cache for this test
        invalidate_cache("expiration_test")

        # First call
        result1 = test_function("test")
        assert result1 == "result_test"
        assert call_count == 1

        # Second call (should use cache)
        result2 = test_function("test")
        assert result2 == "result_test"
        assert call_count == 1

        # Wait for expiration
        time.sleep(1.1)

        # Third call (should execute function again)
        result3 = test_function("test")
        assert result3 == "result_test"
        assert call_count == 2


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_invalidate_cache(self) -> None:
        """Test invalidate_cache function."""
        cache_manager = get_cache_manager()

        # Clear any existing cache first
        cache_manager.clear()

        # Set some cache entries
        cache_manager.set("test_prefix:key1", "value1")
        cache_manager.set("test_prefix:key2", "value2")
        cache_manager.set("other_prefix:key3", "value3")

        # Invalidate entries with pattern
        invalidated_count = invalidate_cache("test_prefix")
        assert invalidated_count == 2

        # Verify entries are gone
        assert cache_manager.get("test_prefix:key1") is None
        assert cache_manager.get("test_prefix:key2") is None
        assert cache_manager.get("other_prefix:key3") == "value3"

    def test_clear_all_cache(self) -> None:
        """Test clear_all_cache function."""
        cache_manager = get_cache_manager()

        # Set some cache entries
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")

        # Clear all cache
        clear_all_cache()

        # Verify all entries are gone
        assert len(cache_manager._cache) == 0

    def test_get_cache_stats(self) -> None:
        """Test get_cache_stats function."""
        cache_manager = get_cache_manager()

        # Set some cache entries
        cache_manager.set("key1", "value1")
        cache_manager.set("key2", "value2")

        # Get stats
        stats = get_cache_stats()
        assert stats["total_entries"] == 2
        assert stats["active_entries"] == 2


class TestCachedOpenAPIFunctions:
    """Test cached OpenAPI functions."""

    @patch("azure_functions_openapi.openapi.generate_openapi_spec")
    def test_cached_openapi_spec(self, mock_generate: Any) -> None:
        """Test cached_openapi_spec function."""
        mock_generate.return_value = {"openapi": "3.0.0", "info": {"title": "Test API"}}

        # First call should execute function
        result1 = cached_openapi_spec("Test API", "1.0.0")
        assert result1 == {"openapi": "3.0.0", "info": {"title": "Test API"}}
        assert mock_generate.call_count == 1

        # Second call should use cache
        result2 = cached_openapi_spec("Test API", "1.0.0")
        assert result2 == {"openapi": "3.0.0", "info": {"title": "Test API"}}
        assert mock_generate.call_count == 1  # Should not increment

    @patch("azure_functions_openapi.openapi.get_openapi_json")
    def test_cached_openapi_json(self, mock_get_json: Any) -> None:
        """Test cached_openapi_json function."""
        mock_get_json.return_value = '{"openapi": "3.0.0"}'

        # First call should execute function
        result1 = cached_openapi_json("Test API", "1.0.0")
        assert result1 == '{"openapi": "3.0.0"}'
        assert mock_get_json.call_count == 1

        # Second call should use cache
        result2 = cached_openapi_json("Test API", "1.0.0")
        assert result2 == '{"openapi": "3.0.0"}'
        assert mock_get_json.call_count == 1  # Should not increment

    @patch("azure_functions_openapi.openapi.get_openapi_yaml")
    def test_cached_openapi_yaml(self, mock_get_yaml: Any) -> None:
        """Test cached_openapi_yaml function."""
        mock_get_yaml.return_value = "openapi: 3.0.0"

        # First call should execute function
        result1 = cached_openapi_yaml("Test API", "1.0.0")
        assert result1 == "openapi: 3.0.0"
        assert mock_get_yaml.call_count == 1

        # Second call should use cache
        result2 = cached_openapi_yaml("Test API", "1.0.0")
        assert result2 == "openapi: 3.0.0"
        assert mock_get_yaml.call_count == 1  # Should not increment


class TestGlobalCacheManager:
    """Test global cache manager."""

    def test_get_cache_manager_singleton(self) -> None:
        """Test that get_cache_manager returns singleton."""
        cache1 = get_cache_manager()
        cache2 = get_cache_manager()

        assert cache1 is cache2

    def test_global_cache_isolation(self) -> None:
        """Test that global cache operations work correctly."""
        cache = get_cache_manager()

        # Clear any existing cache
        cache.clear()

        # Set value
        cache.set("global_test", "global_value")

        # Get value
        value = cache.get("global_test")
        assert value == "global_value"
