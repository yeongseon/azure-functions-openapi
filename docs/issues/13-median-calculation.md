# Issue #13: Use statistics.median() for Accurate Median Calculation

## Priority
🟢 **LOW**

## Category
Correctness / Code Quality

## Description
The median calculation in `PerformanceMonitor` uses `count // 2` which gives the lower median for even-length lists. Python's `statistics.median()` provides the correct median calculation (average of two middle values for even-length sequences).

## Current Behavior
```python
# Line 51 in monitoring.py
def get_response_time_stats(self) -> dict[str, float]:
    # ...
    sorted_times = sorted(self._response_times)
    count = len(sorted_times)
    
    return {
        # ...
        "median": sorted_times[count // 2],  # ❌ Incorrect for even count
    }
```

## Problem Examples

### Even-Length List
```python
times = [1.0, 2.0, 3.0, 4.0]

# Current implementation
median = times[4 // 2]  # times[2] = 3.0 ❌

# Correct median
median = (times[1] + times[2]) / 2  # (2.0 + 3.0) / 2 = 2.5 ✅
```

### Odd-Length List
```python
times = [1.0, 2.0, 3.0, 4.0, 5.0]

# Current implementation
median = times[5 // 2]  # times[2] = 3.0 ✅ (happens to be correct)

# Correct median
median = times[2]  # 3.0 ✅
```

## Impact
For even-length lists (common with 1000 max entries):
- Current: Returns 501st value
- Correct: Returns average of 500th and 501st values

This can lead to slightly inaccurate median values, especially when there's variance in response times.

## Expected Behavior
Use Python's `statistics.median()` which handles both cases correctly.

## Affected Files
- `src/azure_functions_openapi/monitoring.py` (Line 51)

## Proposed Solution

### Use statistics.median()
```python
from statistics import median, mean
from collections import deque

class PerformanceMonitor:
    """Monitor performance metrics with accurate statistics."""
    
    def get_response_time_stats(self) -> dict[str, float]:
        """Get response time statistics.
        
        Uses Python's statistics module for accurate calculations:
        - median: Average of two middle values for even-length sequences
        - mean: More precise than manual sum/count division
        
        Returns:
            Dictionary with accurate statistical measures
        """
        if not self._response_times:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "median": 0.0,
                "p95": 0.0,  # Bonus: add 95th percentile
                "p99": 0.0,  # Bonus: add 99th percentile
            }
        
        sorted_times = sorted(self._response_times)
        count = len(sorted_times)
        
        return {
            "count": count,
            "min": min(sorted_times),  # More efficient than sorted_times[0]
            "max": max(sorted_times),  # More efficient than sorted_times[-1]
            "avg": mean(sorted_times),  # More accurate
            "median": median(sorted_times),  # Correct median calculation
            "p95": sorted_times[int(count * 0.95)] if count > 0 else 0.0,
            "p99": sorted_times[int(count * 0.99)] if count > 0 else 0.0,
        }
```

## Benefits
- ✅ **Correct**: Accurate median for all cases
- ✅ **Standard Library**: No dependencies
- ✅ **More Features**: Can add percentiles easily
- ✅ **Better Code**: Clearer intent
- ✅ **Well-Tested**: statistics module is thoroughly tested

## Additional Improvements
While updating, consider adding:
1. 95th and 99th percentiles (useful for SLAs)
2. Standard deviation (measure variability)
3. More efficient min/max calculation

### Enhanced Statistics
```python
from statistics import median, mean, stdev

def get_response_time_stats(self) -> dict[str, float]:
    """Get comprehensive response time statistics."""
    if not self._response_times:
        return _empty_stats()
    
    sorted_times = sorted(self._response_times)
    count = len(sorted_times)
    
    stats = {
        "count": count,
        "min": min(sorted_times),
        "max": max(sorted_times),
        "avg": mean(sorted_times),
        "median": median(sorted_times),
    }
    
    # Add percentiles if enough data
    if count >= 20:
        stats["p50"] = median(sorted_times)  # Same as median
        stats["p90"] = sorted_times[int(count * 0.90)]
        stats["p95"] = sorted_times[int(count * 0.95)]
        stats["p99"] = sorted_times[int(count * 0.99)]
    
    # Add standard deviation if enough data
    if count >= 2:
        stats["stdev"] = stdev(sorted_times)
    
    return stats
```

## Impact
- **User-facing**: More accurate median values in metrics
- **Breaking Changes**: Median values may change slightly
- **Performance**: Negligible (statistics module is optimized)

## Test Cases
```python
from statistics import median

def test_median_even_count():
    """Test median calculation for even-length list."""
    monitor = PerformanceMonitor()
    
    # Add even number of times
    times = [1.0, 2.0, 3.0, 4.0]
    for t in times:
        monitor.add_response_time(t)
    
    stats = monitor.get_response_time_stats()
    
    # Should be average of 2.0 and 3.0
    assert stats["median"] == 2.5


def test_median_odd_count():
    """Test median calculation for odd-length list."""
    monitor = PerformanceMonitor()
    
    # Add odd number of times
    times = [1.0, 2.0, 3.0, 4.0, 5.0]
    for t in times:
        monitor.add_response_time(t)
    
    stats = monitor.get_response_time_stats()
    
    # Should be middle value
    assert stats["median"] == 3.0


def test_percentiles():
    """Test percentile calculations."""
    monitor = PerformanceMonitor()
    
    # Add 100 times from 0.0 to 0.99
    for i in range(100):
        monitor.add_response_time(i / 100.0)
    
    stats = monitor.get_response_time_stats()
    
    # Check percentiles are approximately correct
    assert 0.89 <= stats["p90"] <= 0.91
    assert 0.94 <= stats["p95"] <= 0.96
    assert 0.98 <= stats["p99"] <= 1.00


def test_statistics_comparison():
    """Compare manual vs statistics module calculation."""
    times = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    
    # Manual calculation (current implementation)
    manual_median = times[len(times) // 2]  # 4.0
    
    # Correct calculation (statistics module)
    correct_median = median(times)  # 3.5
    
    # Should be different
    assert manual_median != correct_median
    assert correct_median == 3.5
```

## Related Issues
- Issue #12 (Deque for Response Times) - Related monitoring improvement
- Issue #11 (Cache Statistics) - Similar statistics improvement

## Estimated Effort
🕐 Small (1 hour including tests)

## References
- [Python statistics documentation](https://docs.python.org/3/library/statistics.html)
- [Median definition](https://en.wikipedia.org/wiki/Median)

## Labels
- correctness
- monitoring
- low-priority
- good-first-issue
- quick-fix
