# Issue #9: Add Input Type Validation in validate_openapi_spec

## Priority
🟡 **MEDIUM**

## Category
Input Validation / Bug Prevention

## Description
The `validate_openapi_spec()` function in `cli.py` doesn't validate that the parsed YAML/JSON is actually a dictionary before attempting to access dictionary keys. When the YAML parser encounters invalid input, it may return `None` or other non-dict types, causing `AttributeError` or `TypeError`.

## Current Behavior
```python
# Line 289 in cli.py
def validate_openapi_spec(spec: Any) -> list[str]:
    """Validate OpenAPI specification."""
    errors: list[str] = []
    
    # ❌ No type check - assumes spec is a dict
    if "openapi" not in spec:  # TypeError if spec is None
        errors.append("Missing 'openapi' field")
    
    if "info" not in spec:  # TypeError if spec is None
        errors.append("Missing 'info' section")
    # ... more dict access without type check ...
```

## Problem Scenarios

### Scenario 1: Empty File
```yaml
# Empty YAML file
```
Result: `yaml.safe_load()` returns `None` → `TypeError: argument of type 'NoneType' is not iterable`

### Scenario 2: Scalar Value
```yaml
just a string
```
Result: Returns `"just a string"` → `TypeError: argument of type 'str' is not iterable`

### Scenario 3: List Instead of Object
```yaml
- item1
- item2
```
Result: Returns `["item1", "item2"]` → `TypeError: argument of type 'list' is not iterable`

### Scenario 4: Invalid JSON
```json
{invalid json}
```
Result: Exception during parsing, but might return non-dict in edge cases

## Expected Behavior
The function should:
1. Check if the parsed spec is a dictionary
2. Return a clear error message if it's not
3. Continue validation only if type is correct

## Affected Files
- `src/azure_functions_openapi/cli.py` (Line 289)

## Proposed Solution

### Add Type Validation
```python
def validate_openapi_spec(spec: Any) -> list[str]:
    """Validate OpenAPI specification.
    
    Checks that the spec is a valid dictionary and contains required fields
    according to OpenAPI 3.0 specification.
    
    Args:
        spec: Parsed OpenAPI spec (from JSON/YAML)
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: list[str] = []
    
    # Type validation - must be a dict
    if not isinstance(spec, dict):
        errors.append(
            f"OpenAPI spec must be a JSON/YAML object (got {type(spec).__name__}). "
            "Check file format and syntax."
        )
        return errors  # Stop validation - can't check fields on non-dict
    
    # Required top-level fields
    if "openapi" not in spec:
        errors.append("Missing required 'openapi' field")
    elif not isinstance(spec["openapi"], str):
        errors.append(f"Field 'openapi' must be string (got {type(spec['openapi']).__name__})")
    
    if "info" not in spec:
        errors.append("Missing required 'info' section")
    elif not isinstance(spec["info"], dict):
        errors.append(f"Field 'info' must be object (got {type(spec['info']).__name__})")
    else:
        # Validate info section
        info = spec["info"]
        if "title" not in info:
            errors.append("Missing 'info.title' field")
        if "version" not in info:
            errors.append("Missing 'info.version' field")
    
    if "paths" not in spec:
        errors.append("Missing required 'paths' section")
    elif not isinstance(spec["paths"], dict):
        errors.append(f"Field 'paths' must be object (got {type(spec['paths']).__name__})")
    
    return errors
```

## Benefits
- ✅ Prevents `TypeError` and `AttributeError` crashes
- ✅ Provides clear error messages for invalid input
- ✅ Improves user experience with helpful feedback
- ✅ Makes validation more robust
- ✅ Better type safety

## Impact
- **User-facing**: Better error messages for invalid specs
- **Stability**: Prevents crashes on malformed input
- **Breaking Changes**: None (only improves error handling)

## Test Cases
```python
def test_validate_spec_none():
    """Test validation with None input."""
    errors = validate_openapi_spec(None)
    assert len(errors) == 1
    assert "must be a JSON/YAML object" in errors[0]
    assert "NoneType" in errors[0]


def test_validate_spec_string():
    """Test validation with string input."""
    errors = validate_openapi_spec("not a dict")
    assert len(errors) == 1
    assert "must be a JSON/YAML object" in errors[0]
    assert "str" in errors[0]


def test_validate_spec_list():
    """Test validation with list input."""
    errors = validate_openapi_spec(["item1", "item2"])
    assert len(errors) == 1
    assert "must be a JSON/YAML object" in errors[0]
    assert "list" in errors[0]


def test_validate_spec_empty_dict():
    """Test validation with empty dict."""
    errors = validate_openapi_spec({})
    assert len(errors) >= 3  # Missing openapi, info, paths
    assert any("openapi" in e for e in errors)
    assert any("info" in e for e in errors)
    assert any("paths" in e for e in errors)


def test_validate_spec_wrong_field_types():
    """Test validation with correct structure but wrong types."""
    spec = {
        "openapi": 3.0,  # Should be string
        "info": "not a dict",  # Should be dict
        "paths": [],  # Should be dict
    }
    errors = validate_openapi_spec(spec)
    assert any("openapi" in e and "string" in e for e in errors)
    assert any("info" in e and "object" in e for e in errors)
    assert any("paths" in e and "object" in e for e in errors)


def test_validate_spec_valid():
    """Test validation with valid spec."""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {}
    }
    errors = validate_openapi_spec(spec)
    assert len(errors) == 0


def test_validate_command_with_invalid_file(tmp_path):
    """Test validate command with non-dict YAML."""
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("just a string, not an object")
    
    args = argparse.Namespace(spec_file=str(invalid_file))
    result = handle_validate(args)
    
    assert result == 1  # Error exit code
```

## Additional Improvements
While implementing this fix, consider:
1. Add validation for OpenAPI version format (e.g., "3.0.0", "3.1.0")
2. Validate nested structure types (info.title, info.version)
3. Add validation for paths structure
4. Consider using a proper OpenAPI validation library for comprehensive checks

## Related Issues
- Issue #8 (CLI Code Duplication) - Both improve CLI robustness

## Estimated Effort
🕐 Small (1-2 hours including tests)

## References
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

## Labels
- bug-prevention
- input-validation
- cli
- medium-priority
- robustness
- good-first-issue
