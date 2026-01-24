# Issue #5: Fix URL Sanitization Bypass Risk

## Priority
🟠 **HIGH**

## Category
Security

## Description
The URL sanitization function in `swagger_ui.py` uses case-insensitive pattern matching to block dangerous protocols, but this approach has several bypass vulnerabilities. Attackers could use HTML-encoded characters (`Java&#x3A;script:`), null bytes (`data\x00:URI`), or other obfuscation techniques.

## Current Behavior
```python
# Lines 128-145 in swagger_ui.py
def _sanitize_url(url: str) -> str:
    """Sanitize URL to prevent XSS attacks."""
    if not url or not isinstance(url, str):
        return "/api/openapi.json"
    
    dangerous_patterns = [
        r"javascript:",
        r"data:",
        r"vbscript:",
        r"file:",
    ]
    
    url_lower = url.lower()
    for pattern in dangerous_patterns:
        if pattern in url_lower:  # ❌ Vulnerable to bypass
            logger.warning(f"Dangerous URL pattern detected: {pattern}")
            return "/api/openapi.json"
    
    return url
```

## Security Vulnerabilities

### 1. HTML Entity Encoding Bypass
```
java&#x3A;script:alert('xss')  # ✗ Bypasses check
java&#58;script:alert('xss')   # ✗ Bypasses check
```

### 2. Null Byte Injection
```
data\x00:text/html,<script>   # ✗ Bypasses check
```

### 3. URL Encoding Bypass
```
%6A%61%76%61%73%63%72%69%70%74:  # ✗ Bypasses check (URL-encoded "javascript:")
```

### 4. Mixed Case with Encoding
```
JaVaScRiPt:alert(1)  # ✓ Blocked (handled by .lower())
```

### 5. Absolute URLs
```
https://evil.com/malicious.js  # ✗ Allowed (could load external content)
```

## Expected Behavior
The sanitization should:
1. Only allow relative URLs that start with `/api/`
2. Properly validate URL structure
3. Block all absolute URLs
4. Handle all encoding variations

## Affected Files
- `src/azure_functions_openapi/swagger_ui.py` (Lines 128-145)

## Proposed Solution
Use proper URL parsing with strict validation:

```python
from urllib.parse import urlparse, unquote

def _sanitize_url(url: str) -> str:
    """Sanitize URL to prevent XSS and SSRF attacks.
    
    Only allows relative URLs that start with /api/.
    Blocks all absolute URLs, data URIs, and javascript: URIs.
    
    Args:
        url: URL string to sanitize
        
    Returns:
        Sanitized URL or default '/api/openapi.json'
        
    Example:
        >>> _sanitize_url("/api/openapi.json")
        "/api/openapi.json"
        >>> _sanitize_url("javascript:alert(1)")
        "/api/openapi.json"
        >>> _sanitize_url("https://evil.com/file.js")
        "/api/openapi.json"
    """
    if not url or not isinstance(url, str):
        return "/api/openapi.json"
    
    try:
        # Decode any URL encoding first
        decoded_url = unquote(url)
        
        # Parse the URL
        parsed = urlparse(decoded_url)
        
        # Block any URL with a scheme (http:, https:, javascript:, data:, etc.)
        if parsed.scheme:
            logger.warning(f"Blocked URL with scheme: {parsed.scheme}")
            return "/api/openapi.json"
        
        # Block any URL with a network location (domain/host)
        if parsed.netloc:
            logger.warning(f"Blocked URL with network location: {parsed.netloc}")
            return "/api/openapi.json"
        
        # Only allow paths that start with /api/
        path = parsed.path
        if not path.startswith("/api/"):
            logger.warning(f"Blocked URL not starting with /api/: {path}")
            return "/api/openapi.json"
        
        # Validate path contains only safe characters
        # Allow: alphanumeric, /, -, _, ., ~
        if not all(c.isalnum() or c in "/-_./~" for c in path):
            logger.warning(f"Blocked URL with invalid characters: {path}")
            return "/api/openapi.json"
        
        return path
        
    except Exception as e:
        logger.warning(f"URL parsing error: {e}")
        return "/api/openapi.json"
```

## Alternative: Whitelist Approach
For even stricter security, use a whitelist:

```python
ALLOWED_OPENAPI_URLS = {
    "/api/openapi.json",
    "/api/openapi.yaml",
    "/api/docs",
}

def _sanitize_url(url: str) -> str:
    """Sanitize URL using whitelist approach."""
    if not url or not isinstance(url, str):
        return "/api/openapi.json"
    
    # Only allow exact matches from whitelist
    if url in ALLOWED_OPENAPI_URLS:
        return url
    
    logger.warning(f"URL not in whitelist: {url}")
    return "/api/openapi.json"
```

## Impact
- **Security**: Prevents XSS and potential SSRF attacks
- **Compatibility**: May break if users are using absolute URLs (unlikely)
- **Performance**: Minimal overhead from URL parsing

## Test Cases
```python
def test_url_sanitization():
    """Test URL sanitization against various bypass attempts."""
    
    # Valid URLs
    assert _sanitize_url("/api/openapi.json") == "/api/openapi.json"
    assert _sanitize_url("/api/openapi.yaml") == "/api/openapi.yaml"
    assert _sanitize_url("/api/docs") == "/api/docs"
    
    # JavaScript protocol
    assert _sanitize_url("javascript:alert(1)") == "/api/openapi.json"
    assert _sanitize_url("JAVASCRIPT:alert(1)") == "/api/openapi.json"
    
    # HTML entity encoding
    assert _sanitize_url("java&#x3A;script:alert(1)") == "/api/openapi.json"
    assert _sanitize_url("java&#58;script:alert(1)") == "/api/openapi.json"
    
    # Data URI
    assert _sanitize_url("data:text/html,<script>") == "/api/openapi.json"
    
    # URL encoding
    assert _sanitize_url("%6A%61%76%61%73%63%72%69%70%74:alert(1)") == "/api/openapi.json"
    
    # Absolute URLs
    assert _sanitize_url("http://evil.com") == "/api/openapi.json"
    assert _sanitize_url("https://evil.com/file.js") == "/api/openapi.json"
    
    # Null byte
    assert _sanitize_url("data\x00:text/html") == "/api/openapi.json"
    
    # Non-API paths
    assert _sanitize_url("/etc/passwd") == "/api/openapi.json"
    assert _sanitize_url("/system/config") == "/api/openapi.json"
    
    # Invalid input
    assert _sanitize_url(None) == "/api/openapi.json"
    assert _sanitize_url("") == "/api/openapi.json"
```

## Related Issues
- Issue #4 (HTML Sanitization) - Similar security concern
- Issue #6 (Route Validation) - Related input validation

## Estimated Effort
🕐 Medium (2-3 hours including comprehensive tests)

## References
- [OWASP XSS Filter Evasion Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html)
- [OWASP Server Side Request Forgery Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

## Labels
- security
- high-priority
- xss-prevention
- ssrf-prevention
- swagger-ui
