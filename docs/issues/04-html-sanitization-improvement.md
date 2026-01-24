# Issue #4: Improve HTML Sanitization in Swagger UI

## Priority
🟠 **HIGH**

## Category
Security

## Description
The HTML sanitization function in `swagger_ui.py` currently removes raw special characters but doesn't handle HTML-encoded entities. This could allow injection of malicious content through encoded characters like `&lt;script&gt;` which browsers will decode and execute.

## Current Behavior
```python
# Lines 113-125 in swagger_ui.py
def _sanitize_html_content(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    if not content or not isinstance(content, str):
        return "API Documentation"
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "/"]
    sanitized = content
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")  # ❌ Doesn't handle encoded entities
    
    return sanitized[:100]
```

## Security Risks
1. **HTML Entity Bypass**: `&lt;script&gt;` passes through but browsers decode it to `<script>`
2. **Unicode Bypass**: `\u003cscript\u003e` can bypass character removal
3. **Case Variations**: Various encodings like `&#60;` (decimal) or `&#x3c;` (hex)

## Expected Behavior
The function should properly escape HTML content to prevent all forms of XSS attacks, including encoded entities.

## Affected Files
- `src/azure_functions_openapi/swagger_ui.py` (Lines 113-125)

## Proposed Solution
Use Python's built-in `html.escape()` which handles all HTML entities correctly:

```python
from html import escape

def _sanitize_html_content(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks.
    
    Escapes all HTML special characters including encoded entities.
    Limits output to 100 characters to prevent abuse.
    
    Args:
        content: Raw content string to sanitize
        
    Returns:
        Safely escaped HTML content, max 100 chars
        
    Example:
        >>> _sanitize_html_content("<script>alert('xss')</script>")
        "&lt;script&gt;alert('xss')&lt;/script&gt;"
    """
    if not content or not isinstance(content, str):
        return "API Documentation"
    
    # html.escape converts: < > & " ' to their HTML entities
    # This is safe for HTML context and prevents XSS
    escaped = escape(content, quote=True)
    
    # Limit length to prevent DoS via large strings
    return escaped[:100]
```

## Benefits
- ✅ Handles all HTML entities (encoded and raw)
- ✅ Handles Unicode representations
- ✅ Standard library solution (no dependencies)
- ✅ More maintainable and correct

## Impact
- **Security**: Significantly reduces XSS risk in Swagger UI
- **Compatibility**: No breaking changes (output is still safe HTML)
- **Performance**: Negligible (html.escape is optimized C code)

## Test Cases
```python
def test_html_sanitization():
    """Test HTML content sanitization."""
    # Raw characters
    assert _sanitize_html_content("<script>") == "&lt;script&gt;"
    
    # HTML entities (should still be escaped)
    assert _sanitize_html_content("&lt;script&gt;") == "&amp;lt;script&amp;gt;"
    
    # Mixed content
    assert _sanitize_html_content('a"b\'c<d>e&f') == 'a&quot;b&#x27;c&lt;d&gt;e&amp;f'
    
    # Unicode
    assert _sanitize_html_content("\u003cscript\u003e") == "&lt;script&gt;"
    
    # Length limiting
    long_str = "a" * 200
    assert len(_sanitize_html_content(long_str)) == 100
    
    # Invalid input
    assert _sanitize_html_content(None) == "API Documentation"
    assert _sanitize_html_content("") == "API Documentation"
```

## Related Issues
- Issue #5 (URL Sanitization) - Similar security concern

## Estimated Effort
🕐 Small (1-2 hours including tests)

## References
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Python html.escape documentation](https://docs.python.org/3/library/html.html#html.escape)

## Labels
- security
- high-priority
- xss-prevention
- swagger-ui
- good-first-issue
