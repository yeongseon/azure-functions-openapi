# Issue #1: Fix Cache Logic Bug - Falsy Value Handling

## Priority
🔴 **CRITICAL**

## Category
Code Quality & Bug Fix

## Description
The cache implementation in `cache.py` has a critical bug where it incorrectly handles falsy values (0, False, empty strings, empty lists, etc.). The current condition `if cached_result is not None:` treats these falsy values as cache misses, causing the function to re-execute even when a valid cached value exists.

## Current Behavior
```python
# Line 150 in cache.py
cached_result = _cache_manager.get(cache_key)
if cached_result is not None:  # ❌ Bug: treats 0, False, "", [], etc. as None
    return cached_result
```

When a function returns:
- `0` → Cache miss (incorrect)
- `False` → Cache miss (incorrect)
- `""` → Cache miss (incorrect)
- `[]` → Cache miss (incorrect)
- `None` → Cache miss (correct)

## Expected Behavior
The cache should distinguish between:
1. Value not in cache (cache miss)
2. Value is in cache but happens to be falsy (cache hit)

## Affected Files
- `src/azure_functions_openapi/cache.py` (Lines 150-152)

## Proposed Solution
Use a sentinel value pattern to distinguish "not in cache" from "cached falsy value":

```python
# Add at module level
_CACHE_MISS = object()

# Update CacheManager.get() method to return _CACHE_MISS instead of None
def get(self, key: str) -> Any:
    """Get cached value by key."""
    entry = self._cache.get(key)
    if entry is None:
        self._misses += 1
        return _CACHE_MISS  # Changed from None
    
    if self._is_expired(entry):
        self._cache.pop(key, None)
        self._misses += 1
        return _CACHE_MISS  # Changed from None
    
    self._hits += 1
    return entry.value

# Update cached decorator
cached_result = _cache_manager.get(cache_key)
if cached_result is not _CACHE_MISS:  # Changed from is not None
    return cached_result
```

## Impact
- **User-facing**: Functions that return falsy values will have proper caching behavior
- **Performance**: Significant improvement for functions that return falsy values frequently
- **Testing**: Requires new test cases for falsy value caching

## Steps to Reproduce
1. Decorate a function with `@cached()`
2. Have the function return `0` or `False`
3. Call the function twice
4. Observe that the function executes both times instead of using cache

## Test Case
```python
@cached(ttl=60)
def get_zero():
    print("Function executed")
    return 0

result1 = get_zero()  # Prints "Function executed"
result2 = get_zero()  # Should NOT print, but currently does
assert result1 == 0
assert result2 == 0
```

## Related Issues
- None

## Estimated Effort
🕐 Small (1-2 hours)

## Labels
- bug
- critical
- caching
- good-first-issue (with guidance)
