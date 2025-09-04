# Architecture Guide

This document provides an overview of the azure-functions-openapi library architecture, design decisions, and internal components.

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Functions App                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   @openapi      │  │   Error         │  │   Cache      │ │
│  │   Decorator     │  │   Handling      │  │   System     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│           │                     │                   │        │
│           ▼                     ▼                   ▼        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              OpenAPI Registry                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              OpenAPI Generation                         │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │   JSON      │  │   YAML      │  │   Swagger UI    │ │ │
│  │  │   Spec      │  │   Spec      │  │   Rendering     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Decorator System (`decorator.py`)

The `@openapi` decorator is the heart of the system:

```python
@openapi(
    summary="API endpoint",
    description="Detailed description",
    tags=["API"],
    request_model=RequestModel,
    response_model=ResponseModel
)
def my_function(req: func.HttpRequest) -> func.HttpResponse:
    # Function implementation
```

**Key Features:**
- **Metadata Collection**: Stores OpenAPI metadata in a global registry
- **Input Validation**: Validates and sanitizes all decorator parameters
- **Error Handling**: Comprehensive error handling with detailed logging
- **Type Safety**: Full type hints and validation

### 2. OpenAPI Generation (`openapi.py`)

Converts registered metadata into OpenAPI 3.0 specifications:

```python
# Generate OpenAPI spec
spec = generate_openapi_spec(title="My API", version="1.0.0")

# Get JSON/YAML formats
json_spec = get_openapi_json()
yaml_spec = get_openapi_yaml()
```

**Key Features:**
- **Schema Generation**: Automatic Pydantic model to JSON Schema conversion
- **Error Resilience**: Graceful handling of schema generation failures
- **Caching**: Built-in caching for performance optimization
- **Validation**: Comprehensive input validation

### 3. Swagger UI (`swagger_ui.py`)

Renders interactive API documentation:

```python
# Render Swagger UI with enhanced security
response = render_swagger_ui(
    title="API Documentation",
    openapi_url="/api/openapi.json",
    custom_csp="custom-csp-policy"
)
```

**Key Features:**
- **Security Headers**: CSP, X-Frame-Options, X-XSS-Protection
- **Input Sanitization**: XSS protection and content validation
- **Customization**: Configurable CSP policies and UI options
- **Monitoring**: Request/response interceptors for logging

### 4. Error Handling System (`errors.py`)

Standardized error handling across the library:

```python
# Custom error types
class ValidationError(APIError): ...
class NotFoundError(APIError): ...
class OpenAPIError(APIError): ...

# Error response creation
response = create_error_response(error, include_stack_trace=False)
```

**Key Features:**
- **Standardized Format**: Consistent error response structure
- **Error Codes**: Categorized error codes for different scenarios
- **Logging**: Comprehensive error logging with context
- **Request Tracking**: Unique request IDs for correlation

### 5. Caching System (`cache.py`)

High-performance in-memory caching:

```python
# Cache decorator
@cached(ttl=300, key_prefix="api")
def expensive_operation():
    return compute_result()

# Cache management
cache_manager = get_cache_manager()
cache_manager.set("key", "value", ttl=60)
```

**Key Features:**
- **TTL Support**: Time-to-live based expiration
- **LRU Eviction**: Least Recently Used eviction policy
- **Thread Safety**: Safe for concurrent access
- **Statistics**: Cache hit/miss statistics and monitoring

### 6. Monitoring System (`monitoring.py`)

Performance monitoring and health checks:

```python
# Performance monitoring
@monitor_performance
def api_endpoint():
    return process_request()

# Health checks
health_status = run_health_check("openapi_generation")
```

**Key Features:**
- **Response Time Tracking**: Detailed performance metrics
- **Health Checks**: Automated system health monitoring
- **Request Logging**: Comprehensive request/response logging
- **Statistics**: Throughput and error rate calculations

### 7. Server Information (`server_info.py`)

Runtime information and system status:

```python
# Server information
info = get_server_info_dict()
health = get_health_status()
metrics = get_metrics()
```

**Key Features:**
- **Runtime Info**: Python version, platform, architecture
- **Performance Metrics**: Uptime, request counts, error rates
- **Security Status**: Security features and configuration
- **Health Monitoring**: System health and component status

## 🔄 Data Flow

### 1. Function Registration

```
Function Definition → @openapi Decorator → Metadata Validation → Registry Storage
```

### 2. OpenAPI Generation

```
Registry → Schema Generation → Error Handling → Caching → JSON/YAML Output
```

### 3. Swagger UI Rendering

```
Request → Security Validation → HTML Generation → Security Headers → Response
```

### 4. Error Handling

```
Exception → Error Classification → Logging → Standardized Response → Client
```

## 🛡️ Security Architecture

### Input Validation Pipeline

```
User Input → Sanitization → Validation → Processing → Response
```

### Security Headers

- **CSP**: Content Security Policy for XSS protection
- **X-Frame-Options**: Clickjacking protection
- **X-XSS-Protection**: XSS filtering
- **X-Content-Type-Options**: MIME type sniffing protection

### Error Information Disclosure

- **Production**: Minimal error information
- **Development**: Detailed error information with stack traces
- **Logging**: Comprehensive server-side logging

## 📊 Performance Architecture

### Caching Strategy

```
Request → Cache Check → Cache Hit/Miss → Response/Computation → Cache Update
```

### Monitoring Pipeline

```
Request → Timing → Logging → Statistics → Health Checks → Alerts
```

## 🔧 Extension Points

### Custom Error Handlers

```python
def custom_error_handler(error: APIError) -> HttpResponse:
    # Custom error handling logic
    return create_error_response(error)
```

### Custom Health Checks

```python
def custom_health_check() -> bool:
    # Custom health check logic
    return True

register_health_check("custom_check", custom_health_check)
```

### Custom Cache Strategies

```python
class CustomCacheManager(CacheManager):
    def get(self, key: str) -> Optional[Any]:
        # Custom cache retrieval logic
        return super().get(key)
```

## 🚀 Deployment Architecture

### Azure Functions Integration

```
Azure Functions Runtime → Function App → OpenAPI Routes → Documentation
```

### CLI Tool Integration

```
CLI Commands → Library Functions → Azure Functions → OpenAPI Generation
```

## 📈 Scalability Considerations

### Memory Management

- **Cache Limits**: Configurable cache size limits
- **LRU Eviction**: Automatic cleanup of unused entries
- **TTL Expiration**: Time-based cache invalidation

### Performance Optimization

- **Lazy Loading**: On-demand schema generation
- **Caching**: Aggressive caching of expensive operations
- **Parallel Processing**: Concurrent request handling

### Monitoring and Alerting

- **Health Checks**: Automated system health monitoring
- **Performance Metrics**: Real-time performance tracking
- **Error Tracking**: Comprehensive error logging and analysis

## 🔮 Future Architecture Considerations

### Planned Enhancements

1. **Distributed Caching**: Redis/Memcached integration
2. **Advanced Monitoring**: Prometheus/Grafana integration
3. **API Gateway Integration**: Azure API Management support
4. **Authentication**: OAuth2/OpenID Connect support
5. **Rate Limiting**: Built-in rate limiting capabilities

### Extension Architecture

The library is designed with extensibility in mind:

- **Plugin System**: Custom decorators and processors
- **Middleware Support**: Request/response middleware
- **Custom Validators**: Extensible validation framework
- **Event System**: Hooks for custom processing