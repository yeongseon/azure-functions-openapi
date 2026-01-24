# Issue #2: Fix Missing Return Statement in monitor_performance Decorator

## Priority
🔴 **CRITICAL**

## Category
Bug Fix

## Description
The `monitor_performance` decorator in `monitoring.py` is missing a `return wrapper` statement, which means the decorator doesn't actually return the wrapped function. This causes the decorator to return `None` instead of the wrapper function, breaking any function decorated with `@monitor_performance`.

## Current Behavior
```python
# Lines 80-102 in monitoring.py
def monitor_performance(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception:
            increment_error_count()
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            add_response_time(response_time)
            increment_request_count()
    # ❌ Missing: return wrapper
```

## Expected Behavior
The decorator should return the `wrapper` function:

```python
def monitor_performance(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # ... wrapper implementation ...
    return wrapper  # ✅ Add this line
```

## Affected Files
- `src/azure_functions_openapi/monitoring.py` (Lines 80-102)

## Impact
- **User-facing**: Any function decorated with `@monitor_performance` will be replaced with `None`, causing runtime errors
- **Testing**: All tests using this decorator should be failing
- **Severity**: This is a critical bug that breaks core functionality

## Steps to Reproduce
1. Decorate any function with `@monitor_performance`
2. Try to call the function
3. Observe `TypeError: 'NoneType' object is not callable`

## Test Case
```python
@monitor_performance
def test_function():
    return "Hello"

# This should work but currently fails
result = test_function()  # TypeError: 'NoneType' object is not callable
```

## Proposed Solution
Add `return wrapper` at line 103 (after the wrapper function definition):

```python
def monitor_performance(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        except Exception:
            increment_error_count()
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            add_response_time(response_time)
            increment_request_count()
    
    return wrapper  # Add this line
```

## Related Issues
- None

## Estimated Effort
🕐 Trivial (5-10 minutes)

## Labels
- bug
- critical
- monitoring
- quick-fix
