# Performance Guide

This document covers performance optimization features and best practices for Azure Functions OpenAPI.

## Performance Features

### Caching System

The library includes a comprehensive caching system to improve performance:

#### In-Memory Cache

- **TTL-based expiration**: Automatic cleanup of expired entries
- **LRU eviction**: Least Recently Used eviction when cache is full
- **Thread-safe operations**: Safe for concurrent access
- **Configurable TTL**: Default 5 minutes, customizable per operation

#### Cached Operations

The following operations are automatically cached:

- **OpenAPI spec generation**: 10-minute TTL
- **JSON serialization**: 5-minute TTL
- **YAML serialization**: 5-minute TTL

#### Cache Management

```python
from azure_functions_openapi.cache import (
    get_cache_manager,
    invalidate_cache,
    clear_all_cache,
    get_cache_stats
)

# Get cache statistics
stats = get_cache_stats()
print(f"Active entries: {stats['active_entries']}")

# Invalidate specific cache entries
invalidated = invalidate_cache("openapi_spec")

# Clear all cache
clear_all_cache()
```

### Performance Monitoring

#### Response Time Tracking

The library tracks response times for all operations:

```python
from azure_functions_openapi.monitoring import get_performance_monitor

monitor = get_performance_monitor()
stats = monitor.get_response_time_stats()

print(f"Average response time: {stats['avg']:.3f}s")
print(f"95th percentile: {stats['p95']:.3f}s")
```

#### Throughput Metrics

Monitor requests per second, minute, and hour:

```python
throughput = monitor.get_throughput_stats()
print(f"Requests per second: {throughput['requests_per_second']:.2f}")
```

#### Request Logging

Track individual requests with detailed metrics:

```python
from azure_functions_openapi.monitoring import log_request

log_request(
    method="GET",
    path="/api/users",
    status_code=200,
    response_time=0.150,
    user_agent="Mozilla/5.0...",
    ip_address="192.168.1.1"
)
```

### Performance Decorators

Use the `@monitor_performance` decorator to automatically track function performance:

```python
from azure_functions_openapi.monitoring import monitor_performance

@monitor_performance
def my_api_function():
    # Your function code
    return {"result": "success"}
```

## Performance Best Practices

### OpenAPI Generation

1. **Use caching**: The library automatically caches generated specs
2. **Minimize changes**: Avoid frequent changes to function metadata
3. **Batch operations**: Group related operations together
4. **Optimize models**: Use efficient Pydantic models

### Memory Management

1. **Monitor cache size**: Use `get_cache_stats()` to monitor memory usage
2. **Clear cache periodically**: Use `clear_all_cache()` in maintenance windows
3. **Limit cache entries**: The cache automatically limits entries to prevent memory issues

### Response Optimization

1. **Minimize data**: Only include necessary information in responses
2. **Use compression**: Enable gzip compression in Azure Functions
3. **Optimize serialization**: Use efficient JSON serialization
4. **Cache responses**: Cache frequently accessed data

### Database and External Services

1. **Connection pooling**: Use connection pooling for database connections
2. **Async operations**: Use async/await for I/O operations
3. **Timeout configuration**: Set appropriate timeouts
4. **Retry logic**: Implement exponential backoff for retries

## Performance Configuration

### Cache Configuration

Configure cache behavior:

```python
from azure_functions_openapi.cache import get_cache_manager

cache = get_cache_manager()
cache.default_ttl = 600  # 10 minutes
```

### Monitoring Configuration

Configure monitoring settings:

```python
from azure_functions_openapi.monitoring import get_performance_monitor

monitor = get_performance_monitor()
monitor._max_response_times = 2000  # Keep more response times
```

### Logging Configuration

Configure logging for performance monitoring:

```python
import logging

# Set up performance logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('azure_functions_openapi.monitoring')
logger.setLevel(logging.DEBUG)
```

## Performance Metrics

### Key Metrics to Monitor

1. **Response Time**
   - Average response time
   - 95th percentile response time
   - 99th percentile response time
   - Maximum response time

2. **Throughput**
   - Requests per second
   - Requests per minute
   - Requests per hour
   - Total requests

3. **Error Rate**
   - Error percentage
   - Error count
   - Error types

4. **Cache Performance**
   - Cache hit rate
   - Cache miss rate
   - Cache size
   - Cache evictions

### Performance Targets

Recommended performance targets:

- **Response Time**: < 100ms for cached operations
- **Throughput**: > 1000 requests/second
- **Error Rate**: < 1%
- **Cache Hit Rate**: > 90%

## Performance Troubleshooting

### Common Issues

1. **Slow Response Times**
   - Check cache hit rates
   - Monitor memory usage
   - Review function complexity
   - Check external service latency

2. **High Memory Usage**
   - Monitor cache size
   - Check for memory leaks
   - Review data structures
   - Clear cache if needed

3. **High Error Rates**
   - Check input validation
   - Review error handling
   - Monitor external services
   - Check resource limits

### Performance Profiling

Use Python profiling tools:

```python
import cProfile
import pstats

# Profile your function
profiler = cProfile.Profile()
profiler.enable()

# Your code here
generate_openapi_spec()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Memory Profiling

Use memory profiling tools:

```python
from memory_profiler import profile

@profile
def my_function():
    # Your code here
    pass
```

## Performance Testing

### Load Testing

Use tools like Apache Bench or wrk for load testing:

```bash
# Test with 100 concurrent users for 30 seconds
ab -n 1000 -c 100 -t 30 http://localhost:7071/api/openapi.json
```

### Stress Testing

Test system limits:

```bash
# Test with high concurrency
ab -n 10000 -c 500 http://localhost:7071/api/openapi.json
```

### Monitoring During Tests

Monitor key metrics during testing:

```python
from azure_functions_openapi.monitoring import get_performance_monitor

monitor = get_performance_monitor()

# Before test
initial_stats = monitor.get_response_time_stats()

# Run your test
# ...

# After test
final_stats = monitor.get_response_time_stats()
print(f"Performance change: {final_stats['avg'] - initial_stats['avg']:.3f}s")
```

## Performance Optimization Checklist

- [ ] Enable caching for all operations
- [ ] Monitor response times and throughput
- [ ] Optimize Pydantic models
- [ ] Use efficient serialization
- [ ] Implement proper error handling
- [ ] Monitor memory usage
- [ ] Configure appropriate timeouts
- [ ] Use connection pooling
- [ ] Implement retry logic
- [ ] Regular performance testing
- [ ] Monitor cache hit rates
- [ ] Clear cache when needed
- [ ] Use async operations where appropriate
- [ ] Optimize database queries
- [ ] Monitor external service latency