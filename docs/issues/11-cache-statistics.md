# Issue #11: Add Cache Hit/Miss Statistics

## Priority
🟢 **LOW**

## Category
Observability / Monitoring

## Description
The `CacheManager` class tracks cache hits and misses internally but doesn't expose these metrics. This makes it impossible to measure cache effectiveness and tune cache parameters (TTL, size) for optimal performance.

## Current Behavior
```python
# Lines 15-110 in cache.py
class CacheManager:
    def __init__(self, default_ttl: int = 300, max_size: int = 1000) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._hits = 0  # ✅ Tracked internally
        self._misses = 0  # ✅ Tracked internally
        # ❌ But no public API to access these!
```

## Problems
1. **No Visibility**: Can't see if caching is effective
2. **Can't Tune**: No data to optimize TTL or cache size
3. **Hidden Metrics**: Stats exist but aren't accessible
4. **No Monitoring**: Can't track cache performance over time

## Expected Behavior
Expose cache statistics through a public API that returns hit rate, miss rate, total requests, and other useful metrics.

## Affected Files
- `src/azure_functions_openapi/cache.py` (Lines 15-110)

## Proposed Solution

### Add Statistics Methods
```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CacheStatistics:
    """Cache statistics data class."""
    
    hits: int
    misses: int
    total_requests: int
    hit_rate: float  # Percentage
    miss_rate: float  # Percentage
    current_size: int
    max_size: int
    evictions: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 2),
            "miss_rate": round(self.miss_rate, 2),
            "current_size": self.current_size,
            "max_size": self.max_size,
            "evictions": self.evictions,
        }


class CacheManager:
    """Enhanced cache manager with statistics."""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000) -> None:
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._hits = 0
        self._misses = 0
        self._evictions = 0  # Track evictions
    
    def get_statistics(self) -> CacheStatistics:
        """Get cache statistics.
        
        Returns:
            CacheStatistics object with current metrics
            
        Example:
            >>> cache = get_cache_manager()
            >>> stats = cache.get_statistics()
            >>> print(f"Hit rate: {stats.hit_rate:.1f}%")
            Hit rate: 85.3%
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0
        miss_rate = (self._misses / total * 100) if total > 0 else 0.0
        
        return CacheStatistics(
            hits=self._hits,
            misses=self._misses,
            total_requests=total,
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            current_size=len(self._cache),
            max_size=self._max_size,
            evictions=self._evictions,
        )
    
    def reset_statistics(self) -> None:
        """Reset cache statistics counters.
        
        Note: Does NOT clear the cache, only resets counters.
        Useful for measuring cache effectiveness over specific time periods.
        """
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _evict_oldest(self) -> None:
        """Evict oldest entry from cache."""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].timestamp
        )
        self._cache.pop(oldest_key, None)
        self._evictions += 1  # Track eviction
```

### CLI Integration
```python
# In cli.py
def handle_cache_stats(args: argparse.Namespace) -> int:
    """Handle 'cache-stats' command.
    
    Display cache performance statistics including hit rate,
    miss rate, and current cache size.
    """
    try:
        from azure_functions_openapi.cache import get_cache_manager
        
        cache = get_cache_manager()
        stats = cache.get_statistics()
        
        return _write_output(stats.to_dict(), args, "cache statistics")
        
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        return 1
```

## Benefits
- ✅ **Visibility**: Clear view of cache effectiveness
- ✅ **Tuning**: Data-driven cache optimization
- ✅ **Monitoring**: Track performance over time
- ✅ **Debugging**: Identify caching issues
- ✅ **CLI Integration**: Easy access to stats

## Usage Examples

### Example 1: Check Hit Rate
```python
from azure_functions_openapi.cache import get_cache_manager

cache = get_cache_manager()
stats = cache.get_statistics()

print(f"Cache hit rate: {stats.hit_rate:.1f}%")
print(f"Total requests: {stats.total_requests}")
print(f"Cache utilization: {stats.current_size}/{stats.max_size}")

# Output:
# Cache hit rate: 85.3%
# Total requests: 1543
# Cache utilization: 234/1000
```

### Example 2: Monitor Cache Performance
```python
import time

cache = get_cache_manager()

# Reset statistics to start fresh
cache.reset_statistics()

# Run application for 5 minutes
time.sleep(300)

# Check performance
stats = cache.get_statistics()
if stats.hit_rate < 50:
    print("⚠️  Low cache hit rate - consider increasing TTL")
elif stats.current_size >= stats.max_size * 0.9:
    print("⚠️  Cache near capacity - consider increasing max_size")
else:
    print("✅ Cache performing well")
```

### Example 3: CLI Usage
```bash
# Get cache statistics as JSON
azure-functions-openapi cache-stats --output json

# Output:
{
  "hits": 1234,
  "misses": 210,
  "total_requests": 1444,
  "hit_rate": 85.46,
  "miss_rate": 14.54,
  "current_size": 234,
  "max_size": 1000,
  "evictions": 12
}
```

## Impact
- **User-facing**: New feature for cache monitoring
- **Performance**: Negligible overhead (just counter reads)
- **Breaking Changes**: None (additive change)

## Test Cases
```python
def test_cache_statistics_initial():
    """Test initial cache statistics."""
    cache = CacheManager()
    stats = cache.get_statistics()
    
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.total_requests == 0
    assert stats.hit_rate == 0.0
    assert stats.current_size == 0


def test_cache_statistics_after_operations():
    """Test statistics after cache operations."""
    cache = CacheManager()
    
    # First get (miss)
    result = cache.get("key1")
    assert result == _CACHE_MISS
    
    # Set value
    cache.set("key1", "value1", ttl=60)
    
    # Second get (hit)
    result = cache.get("key1")
    assert result == "value1"
    
    # Check stats
    stats = cache.get_statistics()
    assert stats.hits == 1
    assert stats.misses == 1
    assert stats.total_requests == 2
    assert stats.hit_rate == 50.0
    assert stats.miss_rate == 50.0
    assert stats.current_size == 1


def test_cache_statistics_reset():
    """Test statistics reset."""
    cache = CacheManager()
    
    # Generate some stats
    cache.get("key1")  # Miss
    cache.set("key1", "value1")
    cache.get("key1")  # Hit
    
    stats = cache.get_statistics()
    assert stats.total_requests == 2
    
    # Reset stats
    cache.reset_statistics()
    
    stats = cache.get_statistics()
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.total_requests == 0
    assert stats.current_size == 1  # Cache not cleared


def test_cache_eviction_tracking():
    """Test that evictions are tracked."""
    cache = CacheManager(max_size=2)
    
    # Fill cache beyond capacity
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")  # Should evict key1
    
    stats = cache.get_statistics()
    assert stats.evictions == 1
    assert stats.current_size == 2
```

## Related Issues
- Issue #10 (Cache Key Performance) - Related caching improvement
- Issue #4 (Performance Metrics) - Similar monitoring enhancement

## Estimated Effort
🕐 Small (2-3 hours including tests and CLI integration)

## Labels
- enhancement
- observability
- caching
- monitoring
- low-priority
- good-first-issue
