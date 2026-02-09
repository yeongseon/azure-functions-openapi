# Configuration Guide

This document lists common configuration options and recommended defaults.

## Cache Configuration

```python
from azure_functions_openapi.cache import get_cache_manager

cache = get_cache_manager()
cache.default_ttl = 600
```

## Swagger UI Configuration

```python
from azure_functions_openapi.swagger_ui import render_swagger_ui

response = render_swagger_ui(openapi_url="/api/openapi.json", title="API Docs")
```

## Security Configuration

```python
from azure_functions_openapi.swagger_ui import render_swagger_ui

custom_csp = "default-src 'self'; script-src 'self'"
response = render_swagger_ui(custom_csp=custom_csp)
```
