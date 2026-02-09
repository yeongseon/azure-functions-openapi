# Performance Guide

This document covers performance optimization features and best practices for Azure Functions OpenAPI.

## KPIs and SLOs

The project tracks performance against clear KPIs to guide optimization and regression prevention.

### Key Performance Indicators (KPIs)

| KPI | Target | Notes |
| --- | --- | --- |
| OpenAPI spec generation | < 2 s | Typical path |
| Swagger UI render | < 200 ms | HTML response time |
| Error rate | < 1% | 4xx/5xx across monitored requests |

### Service Level Objectives (SLOs)

| SLO | Target |
| --- | --- |
| Availability (docs endpoints) | 99.9% |
| p95 response time (docs endpoints) | < 500 ms |
| p99 response time (docs endpoints) | < 1 s |

## Benchmarking and Regression Tests

Performance regression tests live in `./tests/performance` and focus on:

- OpenAPI spec generation latency

The tests are designed to be stable in CI by using generous thresholds and warmup passes.

### Measurement Method

- Runtime: local Python 3.9.6 on macOS
- Script: direct timing for `generate_openapi_spec()`
- Precision: `perf_counter_ns`
- Date: 2026-02-09

### Latest Snapshot

| Metric | Latest value | Notes |
| --- | --- | --- |
| OpenAPI generation average | 1.34 us | empty/minimal registry in local run |
| OpenAPI generation p95 | 1.38 us | same measurement batch |

## CI/CD Performance Profiling

The performance suite can be executed on demand and on a schedule to detect regressions early:

- Run `pytest tests/performance` locally
- Use the `performance.yml` workflow for scheduled runs

Results should be captured in CI logs and summarized in release notes when changes impact KPIs.

## Alerting and Production Monitoring

Monitor these signals in production deployments:

- Response time (p95, p99)
- Error rate (4xx/5xx)
- Memory usage (RSS, working set)
- CPU utilization

Recommended alert thresholds:

- p95 response time > 500 ms for 10 minutes
- Error rate > 1% for 10 minutes
- Memory usage > 80% of available limit
- CPU usage > 85% for 15 minutes

## Performance Features

### Caching

Caching is not built into this library. Apply caching at the application or
platform level if needed.

### Performance Monitoring

Use your platform observability tooling (e.g., Azure Monitor/Application Insights)
to track response times, throughput, and request logging.

## Performance Best Practices

### OpenAPI Generation

1. **Minimize changes**: Avoid frequent changes to function metadata
2. **Batch operations**: Group related operations together
3. **Optimize models**: Use efficient Pydantic models

### Memory Management

1. **Monitor memory**: Use platform monitoring to understand memory usage
2. **Limit metadata**: Keep models and descriptions lean

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

Configure monitoring settings via your platform configuration and
application logger.

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



### Quality Metrics

Track code quality alongside performance to prevent regressions:

- **Static analysis**: Ruff (lint), Mypy (type check)
- **Security checks**: Bandit
- **Test coverage**: Pytest + coverage (target 85%+)
- **Complexity/maintainability**: prefer small functions and clear interfaces

Suggested reporting cadence: every release and any significant performance change.

### Performance Targets

Recommended performance targets:

- **Response Time**: < 2s for spec generation
- **Throughput**: > 1000 requests/second
- **Error Rate**: < 1%

## Performance Troubleshooting

### Common Issues

1. **Slow Response Times**
   - Monitor memory usage
   - Review function complexity
   - Check external service latency

2. **High Memory Usage**
    - Check for memory leaks
    - Review data structures

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

Monitor key metrics during testing using your platform observability tools.

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
- [ ] Monitor memory usage
- [ ] Use async operations where appropriate
- [ ] Optimize database queries
- [ ] Monitor external service latency
