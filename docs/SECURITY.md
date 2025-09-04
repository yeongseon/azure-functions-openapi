# Security Guide

This document outlines the security features and best practices implemented in Azure Functions OpenAPI.

## Security Features

### Content Security Policy (CSP)

The Swagger UI is protected with a comprehensive Content Security Policy that:

- Restricts script sources to `'self'` and `https://cdn.jsdelivr.net`
- Prevents inline script execution except where necessary
- Blocks external validators for security
- Prevents frame embedding with `frame-ancestors 'none'`
- Restricts form actions to same origin

### Security Headers

All responses include the following security headers:

- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking attacks
- `X-XSS-Protection: 1; mode=block` - Enables XSS filtering
- `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information
- `Strict-Transport-Security` - Enforces HTTPS (when applicable)

### Input Validation and Sanitization

#### Route Path Validation

Route paths are validated to prevent:
- Path traversal attacks (`../`)
- XSS attempts (`<script>`)
- JavaScript injection (`javascript:`)
- Data URI injection (`data:`)

Valid route patterns:
- Must start with `/`
- Can contain alphanumeric characters, hyphens, underscores, slashes
- Can contain curly braces for path parameters (`{id}`)
- Can contain spaces

#### Operation ID Sanitization

Operation IDs are sanitized to:
- Remove dangerous characters
- Keep only alphanumeric characters and underscores
- Ensure they start with a letter (prefixed with `op_` if needed)

#### Parameter Validation

Parameters are validated to ensure:
- Required fields (`name`, `in`) are present
- Each parameter is a valid dictionary
- Parameter structure follows OpenAPI specification

#### Tag Validation

Tags are validated to:
- Ensure they are strings
- Remove whitespace
- Prevent empty tags

### Error Handling

#### Standardized Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "status_code": 400,
    "details": {
      "field": "additional context"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "unique-request-id"
}
```

#### Error Logging

All errors are logged with:
- Error code and message
- Request context
- Stack traces (in development mode)
- Request IDs for correlation

### Caching Security

The caching system includes:
- Input validation for cache keys
- TTL-based expiration
- Memory-safe operations
- No sensitive data caching

## Security Best Practices

### For Developers

1. **Always validate input**: Use the built-in validation functions
2. **Sanitize user data**: Let the library handle sanitization
3. **Use HTTPS**: Ensure your Azure Functions use HTTPS
4. **Monitor logs**: Check error logs for security issues
5. **Keep dependencies updated**: Regularly update the library

### For Deployment

1. **Environment Variables**: Use secure environment variables for configuration
2. **Network Security**: Configure proper network security groups
3. **Access Control**: Implement proper authentication and authorization
4. **Monitoring**: Set up security monitoring and alerting
5. **Regular Updates**: Keep the runtime and dependencies updated

### For API Design

1. **Minimal Information**: Don't expose sensitive information in OpenAPI specs
2. **Proper Authentication**: Document authentication requirements
3. **Rate Limiting**: Implement rate limiting for your APIs
4. **Input Validation**: Validate all inputs at the application level
5. **Error Messages**: Don't expose internal details in error messages

## Security Configuration

### Custom CSP Policy

You can provide a custom CSP policy:

```python
from azure_functions_openapi.swagger_ui import render_swagger_ui

custom_csp = "default-src 'self'; script-src 'self' 'unsafe-inline'"
response = render_swagger_ui(custom_csp=custom_csp)
```

### Security Headers

Security headers are automatically added to all responses. You can customize them by modifying the `render_swagger_ui` function.

### Error Handling

Customize error handling by:

```python
from azure_functions_openapi.errors import create_error_response, APIError

try:
    # Your code here
    pass
except APIError as e:
    response = create_error_response(e, include_stack_trace=False)
```

## Security Monitoring

### Health Checks

The library includes built-in health checks for:
- OpenAPI generation
- Swagger UI rendering
- Cache functionality

### Metrics

Monitor security-related metrics:
- Error rates
- Response times
- Request patterns
- Failed validations

### Logging

Security events are logged with appropriate levels:
- `INFO`: Normal operations
- `WARNING`: Security warnings (e.g., invalid input)
- `ERROR`: Security errors (e.g., validation failures)

## Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** create a public issue
2. Email security concerns to: security@example.com
3. Include detailed information about the vulnerability
4. Allow time for the issue to be addressed before disclosure

## Security Updates

Security updates are released as:
- **Patch versions** (e.g., 1.0.1) for critical security fixes
- **Minor versions** (e.g., 1.1.0) for security improvements
- **Major versions** (e.g., 2.0.0) for breaking security changes

Always update to the latest version to ensure you have the latest security fixes.