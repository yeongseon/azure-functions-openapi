# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with azure-functions-openapi.

## 🚨 Common Issues

### 1. Import Errors

#### Problem: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'azure_functions_openapi'
```

**Solutions:**
1. **Install the package:**
   ```bash
   pip install azure-functions-openapi
   ```

2. **Check virtual environment:**
   ```bash
   # Activate your virtual environment
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   
   # Install in the correct environment
   pip install azure-functions-openapi
   ```

3. **Verify installation:**
   ```bash
   pip list | grep azure-functions-openapi
   python -c "import azure_functions_openapi; print('OK')"
   ```

#### Problem: Import from wrong module

```python
# ❌ Wrong
from azure_functions_doctor import openapi

# ✅ Correct
from azure_functions_openapi.decorator import openapi
```

### 2. Decorator Issues

#### Problem: Decorator not working

```python
@openapi(summary="Test")
def my_function(req):
    return func.HttpResponse("Hello")
```

**Solutions:**
1. **Check decorator order:**
   ```python
   # ✅ Correct order
   @app.route(route="test", auth_level=func.AuthLevel.ANONYMOUS)
   @openapi(summary="Test")
   def my_function(req):
       return func.HttpResponse("Hello")
   ```

2. **Verify function registration:**
   ```python
   from azure_functions_openapi.decorator import get_openapi_registry
   
   registry = get_openapi_registry()
   print(f"Registered functions: {list(registry.keys())}")
   ```

#### Problem: Validation errors

```
ValidationError: Invalid route path: <script>alert('xss')</script>
```

**Solutions:**
1. **Use safe route paths:**
   ```python
   # ❌ Dangerous
   @openapi(route="<script>alert('xss')</script>")
   
   # ✅ Safe
   @openapi(route="/api/users")
   ```

2. **Check parameter validation:**
   ```python
   # ❌ Invalid parameters
   @openapi(parameters="not_a_list")
   
   # ✅ Valid parameters
   @openapi(parameters=[
       {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}
   ])
   ```

### 3. OpenAPI Generation Issues

#### Problem: Empty OpenAPI spec

```json
{
  "openapi": "3.0.0",
  "info": {"title": "API", "version": "1.0.0"},
  "paths": {}
}
```

**Solutions:**
1. **Check function registration:**
   ```python
   from azure_functions_openapi.decorator import get_openapi_registry
   
   registry = get_openapi_registry()
   if not registry:
       print("No functions registered with @openapi decorator")
   ```

2. **Verify decorator usage:**
   ```python
   # Make sure you're using the decorator correctly
   @openapi(summary="Test function")
   def test_function(req):
       return func.HttpResponse("OK")
   ```

#### Problem: Schema generation errors

```
OpenAPIError: Failed to generate OpenAPI specification
```

**Solutions:**
1. **Check Pydantic models:**
   ```python
   # ❌ Invalid model
   class InvalidModel:
       def __init__(self):
           self.name = "test"
   
   # ✅ Valid Pydantic model
   from pydantic import BaseModel
   
   class ValidModel(BaseModel):
       name: str
   ```

2. **Handle model errors gracefully:**
   ```python
   try:
       spec = generate_openapi_spec()
   except OpenAPIError as e:
       print(f"OpenAPI generation failed: {e}")
       # Check the error details
       print(f"Error details: {e.details}")
   ```

### 4. Swagger UI Issues

#### Problem: Swagger UI not loading

**Solutions:**
1. **Check route registration:**
   ```python
   @app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
   def swagger_ui(req):
       return render_swagger_ui()
   ```

2. **Verify OpenAPI JSON endpoint:**
   ```python
   @app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
   def openapi_json(req):
       return func.HttpResponse(get_openapi_json(), mimetype="application/json")
   ```

3. **Check browser console for errors:**
   - Open browser developer tools
   - Check for JavaScript errors
   - Verify network requests to `/api/openapi.json`

#### Problem: CSP (Content Security Policy) errors

```
Refused to load the script because it violates the following Content Security Policy directive
```

**Solutions:**
1. **Use custom CSP policy:**
   ```python
   custom_csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
   return render_swagger_ui(custom_csp=custom_csp)
   ```

2. **Disable CSP for development:**
   ```python
   # For development only
   custom_csp = "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
   return render_swagger_ui(custom_csp=custom_csp)
   ```

### 5. Performance Issues

#### Problem: Slow OpenAPI generation

**Solutions:**
1. **Enable caching:**
   ```python
   # Caching is enabled by default
   # Check cache statistics
   from azure_functions_openapi.cache import get_cache_stats
   
   stats = get_cache_stats()
   print(f"Cache hit rate: {stats}")
   ```

2. **Optimize Pydantic models:**
   ```python
   # Use simple models for better performance
   class SimpleModel(BaseModel):
       name: str
       age: int
   
   # Avoid complex nested models if possible
   ```

3. **Clear cache if needed:**
   ```python
   from azure_functions_openapi.cache import clear_all_cache
   
   # Clear cache (use sparingly)
   clear_all_cache()
   ```

#### Problem: Memory usage issues

**Solutions:**
1. **Monitor cache size:**
   ```python
   from azure_functions_openapi.cache import get_cache_manager
   
   cache = get_cache_manager()
   stats = cache.get_stats()
   print(f"Cache entries: {stats['total_entries']}")
   ```

2. **Configure cache limits:**
   ```python
   # Set smaller cache size
   cache = get_cache_manager()
   cache._max_response_times = 100  # Reduce from default 1000
   ```

### 6. CLI Tool Issues

#### Problem: CLI command not found

```bash
azure-functions-openapi: command not found
```

**Solutions:**
1. **Reinstall the package:**
   ```bash
   pip install --upgrade azure-functions-openapi
   ```

2. **Check installation:**
   ```bash
   pip show azure-functions-openapi
   ```

3. **Use Python module syntax:**
   ```bash
   python -m azure_functions_openapi.cli --help
   ```

#### Problem: CLI validation errors

```bash
azure-functions-openapi validate openapi.json
Validation errors found:
  - Missing required field: openapi
```

**Solutions:**
1. **Check OpenAPI spec format:**
   ```json
   {
     "openapi": "3.0.0",
     "info": {
       "title": "API",
       "version": "1.0.0"
     },
     "paths": {}
   }
   ```

2. **Use correct file format:**
   ```bash
   # For JSON files
   azure-functions-openapi validate spec.json
   
   # For YAML files
   azure-functions-openapi validate spec.yaml --format yaml
   ```

## 🔍 Debugging Techniques

### 1. Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('azure_functions_openapi')
logger.setLevel(logging.DEBUG)
```

### 2. Check Registry State

```python
from azure_functions_openapi.decorator import get_openapi_registry

registry = get_openapi_registry()
print("Registered functions:")
for func_name, metadata in registry.items():
    print(f"  {func_name}: {metadata}")
```

### 3. Test OpenAPI Generation

```python
from azure_functions_openapi.openapi import generate_openapi_spec

try:
    spec = generate_openapi_spec()
    print("OpenAPI spec generated successfully")
    print(f"Paths: {list(spec.get('paths', {}).keys())}")
except Exception as e:
    print(f"OpenAPI generation failed: {e}")
    import traceback
    traceback.print_exc()
```

### 4. Monitor Performance

```python
from azure_functions_openapi.monitoring import get_performance_monitor

monitor = get_performance_monitor()
stats = monitor.get_response_time_stats()
print(f"Response time stats: {stats}")

throughput = monitor.get_throughput_stats()
print(f"Throughput: {throughput}")
```

### 5. Check Health Status

```python
from azure_functions_openapi.monitoring import run_all_health_checks

health = run_all_health_checks()
print(f"Health status: {health['overall_status']}")
for check_name, check_result in health['checks'].items():
    print(f"  {check_name}: {check_result['status']}")
```

## 🛠️ Development Tools

### 1. Use Make Commands

```bash
# Run tests
make test

# Check code quality
make check

# Run all checks
make check-all

# Format code
make format
```

### 2. Use CLI for Testing

```bash
# Generate OpenAPI spec
azure-functions-openapi generate --title "Test API" --version "1.0.0"

# Check health
azure-functions-openapi health

# Get metrics
azure-functions-openapi metrics
```

### 3. Use Development Mode

```python
# Enable development mode for more detailed errors
import os
os.environ['AZURE_FUNCTIONS_OPENAPI_DEBUG'] = '1'
```

## 📞 Getting Help

### 1. Check Documentation

- [API Reference](./api.md)
- [Security Guide](./SECURITY.md)
- [Performance Guide](./PERFORMANCE.md)
- [CLI Guide](./CLI.md)

### 2. Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Report Issues

When reporting issues, include:

1. **Python version**: `python --version`
2. **Package version**: `pip show azure-functions-openapi`
3. **Error traceback**: Full stack trace
4. **Code example**: Minimal reproducible example
5. **Environment**: OS, Azure Functions version, etc.

### 4. Community Support

- [GitHub Issues](https://github.com/yeongseon/azure-functions-openapi/issues)
- [GitHub Discussions](https://github.com/yeongseon/azure-functions-openapi/discussions)

## 🔧 Configuration

### Environment Variables

```bash
# Debug mode
export AZURE_FUNCTIONS_OPENAPI_DEBUG=1

# Cache TTL (seconds)
export AZURE_FUNCTIONS_OPENAPI_CACHE_TTL=300

# Log level
export AZURE_FUNCTIONS_OPENAPI_LOG_LEVEL=DEBUG
```

### Configuration File

Create `azure_functions_openapi_config.json`:

```json
{
  "debug": true,
  "cache_ttl": 300,
  "log_level": "DEBUG",
  "security": {
    "csp_enabled": true,
    "input_validation": true
  }
}
```