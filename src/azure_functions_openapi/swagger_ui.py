import logging
from typing import Optional

from azure.functions import HttpResponse

logger = logging.getLogger(__name__)


def render_swagger_ui(
    title: str = "API Documentation",
    openapi_url: str = "/api/openapi.json",
    custom_csp: Optional[str] = None,
) -> HttpResponse:
    """
    Render Swagger UI with enhanced security headers and CSP protection.

    Parameters:
        title: Page title for the Swagger UI
        openapi_url: URL to the OpenAPI specification
        custom_csp: Custom Content Security Policy (optional)

    Returns:
        HttpResponse with Swagger UI HTML and security headers
    """
    # Enhanced CSP policy for better security
    default_csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )

    csp_policy = custom_csp or default_csp

    # Validate and sanitize inputs
    sanitized_title = _sanitize_html_content(title)
    sanitized_url = _sanitize_url(openapi_url)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="Content-Security-Policy" content="{csp_policy}">
        <meta http-equiv="X-Content-Type-Options" content="nosniff">
        <meta http-equiv="X-Frame-Options" content="DENY">
        <meta http-equiv="X-XSS-Protection" content="1; mode=block">
        <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
        <title>{sanitized_title}</title>
        <link rel="stylesheet" 
              type="text/css" 
              href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
        <script>
          // Enhanced security configuration
          const ui = SwaggerUIBundle({{
            url: '{sanitized_url}',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis],
            layout: 'BaseLayout',
            validatorUrl: null,  // Disable external validator for security
            tryItOutEnabled: true,
            supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
            requestInterceptor: function(request) {{
              // Add security headers to requests
              request.headers['X-Requested-With'] = 'XMLHttpRequest';
              return request;
            }},
            responseInterceptor: function(response) {{
              // Log responses for monitoring
              console.log('API Response:', response.status, response.url);
              return response;
            }}
          }});
        </script>
      </body>
    </html>
    """

    # Create response with security headers
    response = HttpResponse(html_content, mimetype="text/html")

    # Add additional security headers
    headers = {
        "Content-Security-Policy": csp_policy,
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    for header, value in headers.items():
        response.headers[header] = value

    logger.info(f"Swagger UI rendered with enhanced security headers for URL: {sanitized_url}")
    return response


def _sanitize_html_content(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    if not content or not isinstance(content, str):
        return "API Documentation"

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "\n", "\r", "\t"]
    sanitized = content
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    # Limit length
    return sanitized[:100] if len(sanitized) > 100 else sanitized


def _sanitize_url(url: str) -> str:
    """Sanitize URL to prevent injection attacks."""
    if not url or not isinstance(url, str):
        return "/api/openapi.json"

    # Remove dangerous patterns
    dangerous_patterns = ["javascript:", "data:", "vbscript:", "<script", "onload="]
    sanitized = url
    for pattern in dangerous_patterns:
        if pattern.lower() in sanitized.lower():
            logger.warning(f"Potentially dangerous URL pattern detected: {pattern}")
            return "/api/openapi.json"

    # Ensure URL starts with /
    if not sanitized.startswith("/"):
        sanitized = "/" + sanitized

    return sanitized
