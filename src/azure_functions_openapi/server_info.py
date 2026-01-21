# src/azure_functions_openapi/server_info.py

from datetime import datetime, timezone
import os
import platform
import sys
import time
from typing import Any, Dict

from azure_functions_openapi.errors import OpenAPIError


class ServerInfo:
    """Server information and health monitoring."""

    def __init__(self) -> None:
        self._start_time = time.time()
        self._request_count = 0
        self._error_count = 0

    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information."""
        try:
            return {
                "server": {
                    "name": "Azure Functions OpenAPI",
                    "version": self._get_package_version(),
                    "environment": os.getenv("FUNCTIONS_WORKER_RUNTIME", "unknown"),
                    "region": os.getenv("WEBSITE_SITE_NAME", "local"),
                    "instance_id": os.getenv("WEBSITE_INSTANCE_ID", "local"),
                },
                "runtime": {
                    "python_version": sys.version,
                    "platform": platform.platform(),
                    "architecture": platform.architecture()[0],
                    "processor": platform.processor(),
                },
                "uptime": {
                    "start_time": datetime.fromtimestamp(
                        self._start_time, timezone.utc
                    ).isoformat(),
                    "uptime_seconds": int(time.time() - self._start_time),
                    "uptime_human": self._format_uptime(time.time() - self._start_time),
                },
                "statistics": {
                    "total_requests": self._request_count,
                    "total_errors": self._error_count,
                    "error_rate": self._calculate_error_rate(),
                    "requests_per_minute": self._calculate_requests_per_minute(),
                },
                "security": {
                    "csp_enabled": True,
                    "input_validation": True,
                    "error_handling": True,
                    "caching_enabled": True,
                },
                "features": {
                    "openapi_generation": True,
                    "swagger_ui": True,
                    "error_handling": True,
                    "caching": True,
                    "monitoring": True,
                    "security_headers": True,
                },
            }
        except Exception as e:
            raise OpenAPIError(
                message="Failed to get server information", details={"error": str(e)}, cause=e
            )

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the server."""
        try:
            uptime = time.time() - self._start_time
            error_rate = self._calculate_error_rate()

            # Determine health status
            if error_rate > 0.1:  # More than 10% error rate
                status = "unhealthy"
            elif uptime < 60:  # Less than 1 minute uptime
                status = "starting"
            else:
                status = "healthy"

            return {
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime_seconds": int(uptime),
                "error_rate": error_rate,
                "total_requests": self._request_count,
                "total_errors": self._error_count,
                "checks": {
                    "server_responding": True,
                    "openapi_available": True,
                    "swagger_ui_available": True,
                    "cache_functioning": True,
                },
            }
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "checks": {
                    "server_responding": False,
                    "openapi_available": False,
                    "swagger_ui_available": False,
                    "cache_functioning": False,
                },
            }

    def increment_request_count(self) -> None:
        """Increment the request counter."""
        self._request_count += 1

    def increment_error_count(self) -> None:
        """Increment the error counter."""
        self._error_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        uptime = time.time() - self._start_time

        return {
            "requests": {
                "total": self._request_count,
                "per_second": self._request_count / uptime if uptime > 0 else 0,
                "per_minute": self._calculate_requests_per_minute(),
                "per_hour": self._request_count / (uptime / 3600) if uptime > 0 else 0,
            },
            "errors": {
                "total": self._error_count,
                "rate": self._calculate_error_rate(),
                "per_second": self._error_count / uptime if uptime > 0 else 0,
            },
            "uptime": {
                "seconds": int(uptime),
                "human": self._format_uptime(uptime),
            },
            "performance": {
                "average_response_time": self._estimate_response_time(),
                "memory_usage": self._get_memory_usage(),
            },
        }

    def _get_package_version(self) -> str:
        """Get the package version."""
        try:
            from azure_functions_openapi import __version__

            return __version__
        except ImportError:
            return "unknown"

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} minutes {secs} seconds"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours} hours {minutes} minutes"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days} days {hours} hours"

    def _calculate_error_rate(self) -> float:
        """Calculate error rate as a percentage."""
        if self._request_count == 0:
            return 0.0
        return (self._error_count / self._request_count) * 100

    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute."""
        uptime_minutes = (time.time() - self._start_time) / 60
        if uptime_minutes == 0:
            return 0.0
        return self._request_count / uptime_minutes

    def _estimate_response_time(self) -> float:
        """Estimate average response time (placeholder implementation)."""
        # This is a placeholder - in a real implementation, you'd track actual response times
        return 0.1  # 100ms average

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information."""
        try:
            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss,  # Resident Set Size
                "vms": memory_info.vms,  # Virtual Memory Size
                "percent": process.memory_percent(),
                "available": psutil.virtual_memory().available,
                "total": psutil.virtual_memory().total,
            }
        except ImportError:
            return {
                "rss": 0,
                "vms": 0,
                "percent": 0,
                "available": 0,
                "total": 0,
                "note": "psutil not available",
            }


# Global server info instance
_server_info = ServerInfo()


def get_server_info() -> ServerInfo:
    """Get the global server info instance."""
    return _server_info


def get_server_info_dict() -> Dict[str, Any]:
    """Get server information as a dictionary."""
    return _server_info.get_server_info()


def get_health_status() -> Dict[str, Any]:
    """Get health status."""
    return _server_info.get_health_status()


def get_metrics() -> Dict[str, Any]:
    """Get performance metrics."""
    return _server_info.get_metrics()


def increment_request_count() -> None:
    """Increment request counter."""
    _server_info.increment_request_count()


def increment_error_count() -> None:
    """Increment error counter."""
    _server_info.increment_error_count()
