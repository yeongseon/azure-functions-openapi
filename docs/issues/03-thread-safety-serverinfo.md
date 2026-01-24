# Issue #3: Add Thread-Safety to ServerInfo Counter Operations

## Priority
🔴 **CRITICAL**

## Category
Concurrency Bug / Thread Safety

## Description
The `ServerInfo` class in `server_info.py` has race conditions in its counter increment methods. The methods `increment_request_count()` and `increment_error_count()` modify shared state without thread synchronization, which can lead to incorrect counts in multi-threaded environments like Azure Functions.

## Current Behavior
```python
# Lines 113-119 in server_info.py
def increment_request_count(self) -> None:
    """Increment request count."""
    self._request_count += 1  # ❌ Not thread-safe

def increment_error_count(self) -> None:
    """Increment error count."""
    self._error_count += 1  # ❌ Not thread-safe
```

## Problem
In a multi-threaded Azure Functions environment:
1. Thread A reads `_request_count = 100`
2. Thread B reads `_request_count = 100` (before Thread A writes)
3. Thread A writes `_request_count = 101`
4. Thread B writes `_request_count = 101` (overwrites Thread A's update)
5. Result: Lost update! Should be 102, but is 101

## Expected Behavior
Counter operations should be atomic and thread-safe, ensuring accurate counts even when multiple threads are incrementing simultaneously.

## Affected Files
- `src/azure_functions_openapi/server_info.py` (Lines 113-119, potentially other counter operations)

## Proposed Solution

### Option 1: Use Threading Lock (Recommended)
```python
import threading

class ServerInfo:
    """Server information manager with thread-safe counters."""
    
    def __init__(self) -> None:
        """Initialize the ServerInfo instance."""
        self._counter_lock = threading.Lock()
        self._request_count = 0
        self._error_count = 0
        # ... other fields ...
    
    def increment_request_count(self) -> None:
        """Increment request count (thread-safe)."""
        with self._counter_lock:
            self._request_count += 1
    
    def increment_error_count(self) -> None:
        """Increment error count (thread-safe)."""
        with self._counter_lock:
            self._error_count += 1
    
    def get_request_count(self) -> int:
        """Get request count (thread-safe)."""
        with self._counter_lock:
            return self._request_count
    
    def get_error_count(self) -> int:
        """Get error count (thread-safe)."""
        with self._counter_lock:
            return self._error_count
```

### Option 2: Use Atomic Operations (Alternative)
```python
from threading import Lock
from typing import Any

class AtomicCounter:
    """Thread-safe counter using locks."""
    
    def __init__(self, initial: int = 0) -> None:
        self._value = initial
        self._lock = Lock()
    
    def increment(self) -> None:
        with self._lock:
            self._value += 1
    
    def value(self) -> int:
        with self._lock:
            return self._value

class ServerInfo:
    def __init__(self) -> None:
        self._request_count = AtomicCounter()
        self._error_count = AtomicCounter()
    
    def increment_request_count(self) -> None:
        self._request_count.increment()
    
    def increment_error_count(self) -> None:
        self._error_count.increment()
```

## Impact
- **User-facing**: More accurate request and error counts in monitoring/metrics
- **Performance**: Minimal overhead (microseconds per lock acquisition)
- **Testing**: Requires concurrency tests to verify thread safety

## Test Case
```python
import threading
import time

def test_concurrent_increment():
    """Test that counter increments are thread-safe."""
    server_info = ServerInfo()
    
    def increment_many():
        for _ in range(1000):
            server_info.increment_request_count()
    
    threads = [threading.Thread(target=increment_many) for _ in range(10)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Should be exactly 10,000 (10 threads × 1000 increments)
    assert server_info.get_request_count() == 10000
```

## Related Issues
- Issue #4 (Performance Metrics) - Should also verify thread safety there

## Estimated Effort
🕐 Small (2-3 hours including tests)

## Labels
- bug
- critical
- concurrency
- thread-safety
- monitoring
