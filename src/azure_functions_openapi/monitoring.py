# src/azure_functions_openapi/monitoring.py

import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timezone

from azure_functions_openapi.errors import OpenAPIError
from azure_functions_openapi.server_info import increment_request_count, increment_error_count


logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        self._response_times: list = []
        self._max_response_times = 1000  # Keep last 1000 response times
        self._start_time = time.time()
    
    def record_response_time(self, response_time: float) -> None:
        """Record a response time."""
        self._response_times.append(response_time)
        
        # Keep only the last N response times
        if len(self._response_times) > self._max_response_times:
            self._response_times = self._response_times[-self._max_response_times:]
    
    def get_response_time_stats(self) -> Dict[str, float]:
        """Get response time statistics."""
        if not self._response_times:
            return {
                "min": 0.0,
                "max": 0.0,
                "avg": 0.0,
                "median": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "count": 0
            }
        
        sorted_times = sorted(self._response_times)
        count = len(sorted_times)
        
        return {
            "min": min(sorted_times),
            "max": max(sorted_times),
            "avg": sum(sorted_times) / count,
            "median": sorted_times[count // 2],
            "p95": sorted_times[int(count * 0.95)],
            "p99": sorted_times[int(count * 0.99)],
            "count": count
        }
    
    def get_throughput_stats(self) -> Dict[str, float]:
        """Get throughput statistics."""
        uptime = time.time() - self._start_time
        total_requests = len(self._response_times)
        
        return {
            "requests_per_second": total_requests / uptime if uptime > 0 else 0.0,
            "requests_per_minute": (total_requests / uptime) * 60 if uptime > 0 else 0.0,
            "requests_per_hour": (total_requests / uptime) * 3600 if uptime > 0 else 0.0,
            "total_requests": total_requests,
            "uptime_seconds": uptime
        }


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return _performance_monitor


def monitor_performance(func: Callable) -> Callable:
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        increment_request_count()
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            increment_error_count()
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            _performance_monitor.record_response_time(response_time)
            
            # Log performance metrics
            logger.debug(f"Function {func.__name__} executed in {response_time:.3f}s")
    
    return wrapper


class RequestLogger:
    """Request logging and monitoring."""
    
    def __init__(self):
        self._request_log: list = []
        self._max_log_entries = 100  # Keep last 100 requests
    
    def log_request(
        self, 
        method: str, 
        path: str, 
        status_code: int, 
        response_time: float,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Log a request."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time": response_time,
            "user_agent": user_agent,
            "ip_address": ip_address
        }
        
        self._request_log.append(log_entry)
        
        # Keep only the last N entries
        if len(self._request_log) > self._max_log_entries:
            self._request_log = self._request_log[-self._max_log_entries:]
        
        # Log to application logger
        logger.info(
            f"{method} {path} {status_code} {response_time:.3f}s",
            extra=log_entry
        )
    
    def get_recent_requests(self, limit: int = 10) -> list:
        """Get recent request log entries."""
        return self._request_log[-limit:] if self._request_log else []
    
    def get_request_stats(self) -> Dict[str, Any]:
        """Get request statistics."""
        if not self._request_log:
            return {
                "total_requests": 0,
                "status_codes": {},
                "methods": {},
                "avg_response_time": 0.0,
                "error_rate": 0.0
            }
        
        total_requests = len(self._request_log)
        status_codes = {}
        methods = {}
        response_times = []
        error_count = 0
        
        for entry in self._request_log:
            # Status codes
            status = entry["status_code"]
            status_codes[status] = status_codes.get(status, 0) + 1
            
            # Methods
            method = entry["method"]
            methods[method] = methods.get(method, 0) + 1
            
            # Response times
            response_times.append(entry["response_time"])
            
            # Error count (4xx and 5xx)
            if status >= 400:
                error_count += 1
        
        return {
            "total_requests": total_requests,
            "status_codes": status_codes,
            "methods": methods,
            "avg_response_time": sum(response_times) / len(response_times),
            "error_rate": (error_count / total_requests) * 100 if total_requests > 0 else 0.0
        }


# Global request logger instance
_request_logger = RequestLogger()


def get_request_logger() -> RequestLogger:
    """Get the global request logger instance."""
    return _request_logger


def log_request(
    method: str, 
    path: str, 
    status_code: int, 
    response_time: float,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None
) -> None:
    """Log a request."""
    _request_logger.log_request(method, path, status_code, response_time, user_agent, ip_address)


class HealthChecker:
    """Health check functionality."""
    
    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}
        self._last_check_times: Dict[str, float] = {}
        self._check_intervals: Dict[str, float] = {}
    
    def register_check(self, name: str, check_func: Callable[[], bool], interval: float = 60.0) -> None:
        """Register a health check."""
        self._checks[name] = check_func
        self._check_intervals[name] = interval
        self._last_check_times[name] = 0.0
    
    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check."""
        if name not in self._checks:
            return {
                "name": name,
                "status": "unknown",
                "error": f"Check '{name}' not found"
            }
        
        try:
            start_time = time.time()
            result = self._checks[name]()
            end_time = time.time()
            
            self._last_check_times[name] = end_time
            
            return {
                "name": name,
                "status": "healthy" if result else "unhealthy",
                "duration": end_time - start_time,
                "last_check": datetime.fromtimestamp(end_time, timezone.utc).isoformat()
            }
        except Exception as e:
            self._last_check_times[name] = time.time()
            return {
                "name": name,
                "status": "error",
                "error": str(e),
                "last_check": datetime.fromtimestamp(time.time(), timezone.utc).isoformat()
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_status = "healthy"
        
        for name in self._checks:
            result = self.run_check(name)
            results[name] = result
            
            if result["status"] != "healthy":
                overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": results
        }
    
    def get_check_status(self, name: str) -> Dict[str, Any]:
        """Get the status of a specific check."""
        if name not in self._checks:
            return {
                "name": name,
                "status": "unknown",
                "error": f"Check '{name}' not found"
            }
        
        last_check = self._last_check_times.get(name, 0.0)
        interval = self._check_intervals.get(name, 60.0)
        
        # Check if we need to run the check
        if time.time() - last_check > interval:
            return self.run_check(name)
        else:
            return {
                "name": name,
                "status": "cached",
                "last_check": datetime.fromtimestamp(last_check, timezone.utc).isoformat(),
                "next_check": datetime.fromtimestamp(last_check + interval, timezone.utc).isoformat()
            }


# Global health checker instance
_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    return _health_checker


def register_health_check(name: str, check_func: Callable[[], bool], interval: float = 60.0) -> None:
    """Register a health check."""
    _health_checker.register_check(name, check_func, interval)


def run_health_check(name: str) -> Dict[str, Any]:
    """Run a health check."""
    return _health_checker.run_check(name)


def run_all_health_checks() -> Dict[str, Any]:
    """Run all health checks."""
    return _health_checker.run_all_checks()


# Default health checks
def _check_openapi_generation() -> bool:
    """Check if OpenAPI generation is working."""
    try:
        from azure_functions_openapi.openapi import generate_openapi_spec
        spec = generate_openapi_spec()
        return "openapi" in spec and "info" in spec and "paths" in spec
    except Exception:
        return False


def _check_swagger_ui() -> bool:
    """Check if Swagger UI rendering is working."""
    try:
        from azure_functions_openapi.swagger_ui import render_swagger_ui
        response = render_swagger_ui()
        return response.mimetype == "text/html" and len(response.get_body()) > 0
    except Exception:
        return False


def _check_cache_functionality() -> bool:
    """Check if caching is working."""
    try:
        from azure_functions_openapi.cache import get_cache_manager
        cache = get_cache_manager()
        cache.set("health_check", "test", ttl=1)
        result = cache.get("health_check")
        return result == "test"
    except Exception:
        return False


# Register default health checks
register_health_check("openapi_generation", _check_openapi_generation)
register_health_check("swagger_ui", _check_swagger_ui)
register_health_check("cache_functionality", _check_cache_functionality)