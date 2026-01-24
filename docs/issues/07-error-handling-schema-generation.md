# Issue #7: Improve Error Handling in OpenAPI Schema Generation

## Priority
🟡 **MEDIUM**

## Category
Error Handling / Observability

## Description
When Pydantic model conversion fails during OpenAPI schema generation, the code silently falls back to a generic `{"type": "object"}` schema with only a debug-level log message. This makes troubleshooting difficult and hides potential configuration issues.

## Current Behavior
```python
# Lines 126-133 and 166-173 in openapi.py
try:
    from azure_functions_openapi.decorator import _extract_pydantic_schema
    response_schema = _extract_pydantic_schema(response_model)
except Exception:
    logger.debug(
        f"Could not extract response schema for {func_name}, using generic object"
    )
    response_schema = {"type": "object"}  # ❌ Silent fallback
```

## Problems

### 1. Hidden Errors
When schema generation fails:
- Developers don't know WHY it failed
- No indication of what went wrong with the Pydantic model
- Swagger UI shows generic object instead of proper schema

### 2. Missing Context
The current log doesn't include:
- Exception type
- Exception message
- Which Pydantic model failed
- Stack trace for debugging

### 3. Wrong Log Level
Using `logger.debug()` means:
- Not visible in production logs by default
- Developers might not notice the issue
- Harder to diagnose problems

## Expected Behavior
1. Log detailed error information at WARNING level
2. Include exception details for troubleshooting
3. Preserve the generic fallback (non-breaking)
4. Help developers identify and fix model issues

## Affected Files
- `src/azure_functions_openapi/openapi.py` (Lines 126-133, 166-173)

## Proposed Solution

### Enhanced Error Logging
```python
try:
    from azure_functions_openapi.decorator import _extract_pydantic_schema
    response_schema = _extract_pydantic_schema(response_model)
except Exception as e:
    # Log at WARNING level with full context
    logger.warning(
        f"Failed to generate response schema for {func_name}: "
        f"{type(e).__name__}: {str(e)}. "
        f"Model: {response_model!r}. "
        f"Falling back to generic object schema.",
        exc_info=True  # Include stack trace in debug mode
    )
    response_schema = {"type": "object"}
```

### Even Better: Specific Error Types
```python
try:
    from azure_functions_openapi.decorator import _extract_pydantic_schema
    response_schema = _extract_pydantic_schema(response_model)
except ImportError as e:
    logger.warning(
        f"Pydantic not available for {func_name}: {e}. "
        f"Install pydantic to use model-based schemas."
    )
    response_schema = {"type": "object"}
except (AttributeError, TypeError, ValueError) as e:
    logger.warning(
        f"Invalid Pydantic model for {func_name}: {type(e).__name__}: {e}. "
        f"Model: {response_model!r}. Check model definition."
    )
    response_schema = {"type": "object"}
except Exception as e:
    logger.error(
        f"Unexpected error generating schema for {func_name}: {type(e).__name__}: {e}",
        exc_info=True
    )
    response_schema = {"type": "object"}
```

## Benefits
- ✅ Easier troubleshooting for developers
- ✅ Better visibility in production logs
- ✅ Helps identify misconfigured Pydantic models
- ✅ Maintains backward compatibility (still falls back)
- ✅ No performance impact

## Impact
- **User-facing**: Better error messages in logs
- **Breaking Changes**: None
- **Performance**: Negligible (only on error path)

## Example Scenarios

### Before (Current)
```
# Developer uses invalid model
@openapi(response_model={"name": "str"})  # Wrong: dict instead of Pydantic model

# Log output (debug level - might not see):
DEBUG: Could not extract response schema for my_function, using generic object

# Swagger UI: Shows generic "object" schema (confusing)
```

### After (Improved)
```
# Same invalid model
@openapi(response_model={"name": "str"})

# Log output (warning level - visible):
WARNING: Failed to generate response schema for my_function: AttributeError: 
'dict' object has no attribute '__fields__'. Model: {'name': 'str'}. 
Falling back to generic object schema.

# Developer sees the problem and fixes it:
class ResponseModel(BaseModel):
    name: str

@openapi(response_model=ResponseModel)  # ✅ Correct
```

## Files to Update
1. `src/azure_functions_openapi/openapi.py`:
   - Lines 126-133 (request schema generation)
   - Lines 166-173 (response schema generation)

## Test Cases
```python
def test_schema_generation_error_logging(caplog):
    """Test that schema generation errors are properly logged."""
    
    # Invalid model (dict instead of Pydantic)
    invalid_model = {"name": "str"}
    
    # Should log warning with details
    with caplog.at_level(logging.WARNING):
        spec = generate_openapi_spec(
            functions=[some_function_with_invalid_model]
        )
    
    # Check log contains helpful info
    assert "Failed to generate" in caplog.text
    assert "AttributeError" in caplog.text
    assert "{'name': 'str'}" in caplog.text
    
    # Should still generate spec (fallback)
    assert spec["paths"]["/api/test"]["post"]["responses"]["200"]
```

## Related Issues
- None

## Estimated Effort
🕐 Small (1-2 hours including tests)

## Labels
- enhancement
- error-handling
- observability
- logging
- medium-priority
- good-first-issue
