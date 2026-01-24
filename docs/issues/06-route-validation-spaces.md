# Issue #6: Remove Spaces from Route Validation Pattern

## Priority
🟡 **MEDIUM**

## Category
Security / Input Validation

## Description
The route validation regex in `utils.py` includes `\s` (whitespace) in the allowed character set. Allowing spaces in routes can cause URL parsing issues, routing mismatches, and potential security vulnerabilities in some HTTP servers.

## Current Behavior
```python
# Line 177 in utils.py
if not re.match(r"^/?[a-zA-Z0-9_\-/{}\s]*$", route):
    #                                   ^^
    #                                   Allows whitespace
    raise ValidationError(f"Invalid route format: {route}")
```

This allows routes like:
- `/api/my route` ✗ (has space)
- `/api/ users /list` ✗ (has spaces)

## Problems with Spaces in Routes

### 1. URL Encoding Issues
- Spaces must be encoded as `%20` or `+` in URLs
- Raw spaces in routes cause parsing ambiguity
- Different clients may handle spaces inconsistently

### 2. HTTP Specification
- RFC 3986 doesn't allow spaces in URIs
- Spaces must be percent-encoded

### 3. Routing Mismatches
```python
# Route defined with space
"/api/my route"

# Client requests might use:
"/api/my%20route"  # Might not match
"/api/my+route"    # Might not match
"/api/my route"    # Might not match (depends on framework)
```

### 4. Security Concerns
- Spaces can be used in path traversal attacks with encoded slashes
- Inconsistent handling across reverse proxies and web servers

## Expected Behavior
Routes should only contain URL-safe characters:
- Alphanumeric: `a-z`, `A-Z`, `0-9`
- Path separators: `/`
- Common symbols: `-`, `_`
- Path parameters: `{}` (for Azure Functions route templates)

## Affected Files
- `src/azure_functions_openapi/utils.py` (Line 177)

## Proposed Solution
Remove `\s` from the regex pattern:

```python
def validate_route(route: str, func_name: str) -> str:
    """Validate and sanitize route.
    
    Routes must contain only URL-safe characters:
    - Alphanumeric: a-z, A-Z, 0-9
    - Path separators: /
    - Special chars: - _ (hyphen, underscore)
    - Templates: {} (for route parameters)
    
    Spaces and other whitespace are NOT allowed as they violate RFC 3986.
    
    Args:
        route: Route string to validate
        func_name: Function name for error messages
        
    Returns:
        Validated route string
        
    Raises:
        ValidationError: If route contains invalid characters
    """
    if not route or not isinstance(route, str):
        raise ValidationError(f"Invalid route for {func_name}: empty or non-string")
    
    # Remove \s from pattern - no whitespace allowed
    if not re.match(r"^/?[a-zA-Z0-9_\-/{}]*$", route):
        raise ValidationError(
            f"Invalid route format for {func_name}: {route}. "
            "Routes must contain only alphanumeric chars, /, -, _, and {{}} for parameters."
        )
    
    return route
```

## Impact
- **Breaking Change**: Routes with spaces will now be rejected ⚠️
- **Security**: Improved compliance with RFC 3986
- **Compatibility**: Better compatibility across HTTP clients and servers
- **User Experience**: Clearer error messages when invalid routes are used

## Migration Guide
If you have existing routes with spaces, replace them with hyphens or underscores:

```python
# Before (invalid)
@openapi(route="/api/my route")

# After (valid - option 1: hyphen)
@openapi(route="/api/my-route")

# After (valid - option 2: underscore)
@openapi(route="/api/my_route")

# After (valid - option 3: camelCase)
@openapi(route="/api/myRoute")
```

## Test Cases
```python
def test_route_validation():
    """Test route validation with various inputs."""
    
    # Valid routes
    assert validate_route("/api/users", "test_func") == "/api/users"
    assert validate_route("/api/user-profile", "test_func") == "/api/user-profile"
    assert validate_route("/api/user_profile", "test_func") == "/api/user_profile"
    assert validate_route("/api/users/{id}", "test_func") == "/api/users/{id}"
    
    # Invalid routes with spaces (should raise ValidationError)
    with pytest.raises(ValidationError):
        validate_route("/api/my route", "test_func")
    
    with pytest.raises(ValidationError):
        validate_route("/api/ users", "test_func")
    
    with pytest.raises(ValidationError):
        validate_route("/api/users /list", "test_func")
    
    # Other invalid characters
    with pytest.raises(ValidationError):
        validate_route("/api/users?id=1", "test_func")  # Query string
    
    with pytest.raises(ValidationError):
        validate_route("/api/users#section", "test_func")  # Fragment
```

## Related Issues
- Issue #4 (HTML Sanitization)
- Issue #5 (URL Sanitization)

## Estimated Effort
🕐 Small (1-2 hours including tests and documentation)

## References
- [RFC 3986 - URI Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986)
- [Azure Functions HTTP trigger - Route template](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger)

## Labels
- security
- input-validation
- breaking-change
- medium-priority
- routes
