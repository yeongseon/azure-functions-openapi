# Issue #14: Replace Placeholder Response Time Estimation with Real Metrics

## Priority
🟡 **MEDIUM**

## Category
Monitoring / Implementation Gap

## Description
The `_estimate_response_time()` method in `ServerInfo` class returns a hardcoded placeholder value of `0.1` seconds. This is misleading and should either be integrated with the actual `PerformanceMonitor` or removed entirely.

## Current Behavior
```python
# Lines 186-189 in server_info.py
def _estimate_response_time(self) -> float:
    """Estimate average response time."""
    # Placeholder implementation
    return 0.1  # ❌ Hardcoded placeholder - not real data
```

## Problems
1. **Misleading Data**: Always returns 0.1s regardless of actual performance
2. **Broken Feature**: Method exists but doesn't work
3. **User Confusion**: Developers might rely on this incorrect data
4. **Incomplete Integration**: `PerformanceMonitor` exists but isn't used here

## Expected Behavior
Either:
1. **Option A**: Integrate with `PerformanceMonitor` to return real metrics
2. **Option B**: Remove the method entirely and use `PerformanceMonitor` directly

## Affected Files
- `src/azure_functions_openapi/server_info.py` (Lines 186-189)
- `src/azure_functions_openapi/monitoring.py` (PerformanceMonitor integration)

## Proposed Solution

### Option A: Integrate with PerformanceMonitor (Recommended)
```python
class ServerInfo:
    """Server information with real performance metrics."""
    
    def _estimate_response_time(self) -> float:
        """Get average response time from performance monitor.
        
        Returns:
            Average response time in seconds, or 0.0 if no data available
        """
        try:
            from azure_functions_openapi.monitoring import get_performance_monitor
            
            monitor = get_performance_monitor()
            stats = monitor.get_response_time_stats()
            
            # Return average response time
            return stats.get("avg", 0.0)
            
        except ImportError:
            # Performance monitoring not available
            logger.debug("Performance monitoring not available")
            return 0.0
        except Exception as e:
            # Error getting metrics
            logger.warning(f"Failed to get response time metrics: {e}")
            return 0.0
    
    def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics.
        
        Returns:
            Dictionary with performance statistics including:
            - avg_response_time: Average response time in seconds
            - min_response_time: Minimum response time
            - max_response_time: Maximum response time
            - median_response_time: Median response time
            - request_count: Total number of requests
            - error_count: Total number of errors
            - error_rate: Percentage of requests that errored
        """
        try:
            from azure_functions_openapi.monitoring import get_performance_monitor
            
            monitor = get_performance_monitor()
            stats = monitor.get_response_time_stats()
            
            total_requests = self._request_count
            error_rate = (
                (self._error_count / total_requests * 100)
                if total_requests > 0
                else 0.0
            )
            
            return {
                "avg_response_time": stats.get("avg", 0.0),
                "min_response_time": stats.get("min", 0.0),
                "max_response_time": stats.get("max", 0.0),
                "median_response_time": stats.get("median", 0.0),
                "p95_response_time": stats.get("p95", 0.0),
                "p99_response_time": stats.get("p99", 0.0),
                "request_count": total_requests,
                "error_count": self._error_count,
                "error_rate": round(error_rate, 2),
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
                "median_response_time": 0.0,
                "request_count": self._request_count,
                "error_count": self._error_count,
                "error_rate": 0.0,
            }
```

### Option B: Remove and Document Alternative (Simpler)
```python
class ServerInfo:
    """Server information manager.
    
    For performance metrics like response times, use the PerformanceMonitor
    directly via `get_performance_monitor().get_response_time_stats()`.
    """
    
    # Remove _estimate_response_time() method entirely
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.
        
        Note: For performance metrics (response times, etc.), use
        PerformanceMonitor.get_response_time_stats() instead.
        """
        return {
            "server": {
                "name": self._name,
                "version": self._version,
                # ... other fields ...
            },
            "stats": {
                "request_count": self._request_count,
                "error_count": self._error_count,
                # Remove avg_response_time from here
            },
        }
```

## Benefits

### Option A (Recommended)
- ✅ **Real Data**: Returns actual performance metrics
- ✅ **Complete Feature**: Finishes incomplete implementation
- ✅ **Single Source**: Uses PerformanceMonitor as source of truth
- ✅ **Comprehensive**: Provides full performance metrics

### Option B (Simpler)
- ✅ **Cleaner**: Removes confusing placeholder
- ✅ **Simpler**: Less code to maintain
- ✅ **Direct Access**: Users access PerformanceMonitor directly
- ✅ **Less Coupling**: Reduces dependencies

## Impact
- **User-facing**: More accurate performance metrics
- **Breaking Changes**: 
  - Option A: None (improves existing feature)
  - Option B: Removes a method (breaking)
- **Performance**: Negligible

## Usage Examples

### Option A: Integrated Metrics
```python
from azure_functions_openapi.server_info import get_server_info

server_info = get_server_info()

# Now returns real data
metrics = server_info.get_performance_metrics()
print(f"Average response time: {metrics['avg_response_time']:.3f}s")
print(f"95th percentile: {metrics['p95_response_time']:.3f}s")
print(f"Error rate: {metrics['error_rate']:.1f}%")
```

### Option B: Direct Access
```python
from azure_functions_openapi.monitoring import get_performance_monitor

monitor = get_performance_monitor()

# Direct access to performance stats
stats = monitor.get_response_time_stats()
print(f"Average: {stats['avg']:.3f}s")
print(f"Median: {stats['median']:.3f}s")
```

## Test Cases
```python
def test_response_time_integration():
    """Test that response time comes from PerformanceMonitor."""
    from azure_functions_openapi.server_info import get_server_info
    from azure_functions_openapi.monitoring import get_performance_monitor
    
    # Add some response times
    monitor = get_performance_monitor()
    monitor.add_response_time(0.5)
    monitor.add_response_time(0.3)
    monitor.add_response_time(0.7)
    
    # ServerInfo should return real average
    server_info = get_server_info()
    avg = server_info._estimate_response_time()
    
    # Should be (0.5 + 0.3 + 0.7) / 3 = 0.5
    assert abs(avg - 0.5) < 0.01
    
    # Should NOT be 0.1 (placeholder)
    assert avg != 0.1


def test_performance_metrics_comprehensive():
    """Test comprehensive performance metrics."""
    server_info = get_server_info()
    
    metrics = server_info.get_performance_metrics()
    
    # Should have all expected fields
    assert "avg_response_time" in metrics
    assert "min_response_time" in metrics
    assert "max_response_time" in metrics
    assert "median_response_time" in metrics
    assert "p95_response_time" in metrics
    assert "p99_response_time" in metrics
    assert "request_count" in metrics
    assert "error_count" in metrics
    assert "error_rate" in metrics
```

## Related Issues
- Issue #12 (Deque for Response Times) - Performance monitoring improvement
- Issue #13 (Median Calculation) - Statistics accuracy
- Issue #11 (Cache Statistics) - Similar metrics integration

## Recommendation
**Choose Option A (Integration)** because:
1. The method already exists and is part of public API
2. Users expect it to work
3. PerformanceMonitor exists and has the data
4. Removing it (Option B) is a breaking change

## Estimated Effort
🕐 Small (2-3 hours including tests)
- Option A: 2-3 hours
- Option B: 1 hour

## Labels
- enhancement
- monitoring
- integration
- medium-priority
- incomplete-feature
