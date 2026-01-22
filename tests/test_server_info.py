from __future__ import annotations

import time
from unittest.mock import patch

from azure_functions_openapi.server_info import (
    ServerInfo,
    get_health_status,
    get_metrics,
    get_server_info,
    get_server_info_dict,
    increment_error_count,
    increment_request_count,
)


class TestServerInfo:
    def test_get_server_info_returns_dict(self) -> None:
        server_info = ServerInfo()
        info = server_info.get_server_info()

        assert isinstance(info, dict)
        assert "server" in info
        assert "runtime" in info
        assert "uptime" in info
        assert "statistics" in info
        assert "security" in info
        assert "features" in info

    def test_get_server_info_server_section(self) -> None:
        server_info = ServerInfo()
        info = server_info.get_server_info()

        server = info["server"]
        assert "name" in server
        assert server["name"] == "Azure Functions OpenAPI"
        assert "version" in server
        assert "environment" in server
        assert "region" in server
        assert "instance_id" in server

    def test_get_server_info_runtime_section(self) -> None:
        server_info = ServerInfo()
        info = server_info.get_server_info()

        runtime = info["runtime"]
        assert "python_version" in runtime
        assert "platform" in runtime
        assert "architecture" in runtime
        assert "processor" in runtime

    def test_get_server_info_uptime_section(self) -> None:
        server_info = ServerInfo()
        time.sleep(0.1)
        info = server_info.get_server_info()

        uptime = info["uptime"]
        assert "start_time" in uptime
        assert "uptime_seconds" in uptime
        assert "uptime_human" in uptime
        assert uptime["uptime_seconds"] >= 0

    def test_get_server_info_statistics_section(self) -> None:
        server_info = ServerInfo()
        info = server_info.get_server_info()

        stats = info["statistics"]
        assert "total_requests" in stats
        assert "total_errors" in stats
        assert "error_rate" in stats
        assert "requests_per_minute" in stats

    def test_get_health_status_healthy(self) -> None:
        server_info = ServerInfo()
        server_info._start_time = time.time() - 120

        health = server_info.get_health_status()

        assert isinstance(health, dict)
        assert "status" in health
        assert health["status"] == "healthy"
        assert "timestamp" in health
        assert "uptime_seconds" in health
        assert "checks" in health

    def test_get_health_status_starting(self) -> None:
        server_info = ServerInfo()

        health = server_info.get_health_status()

        assert health["status"] == "starting"

    def test_get_health_status_unhealthy_high_error_rate(self) -> None:
        server_info = ServerInfo()
        server_info._start_time = time.time() - 120
        server_info._request_count = 100
        server_info._error_count = 50

        health = server_info.get_health_status()

        assert health["status"] == "unhealthy"

    def test_increment_request_count(self) -> None:
        server_info = ServerInfo()
        initial = server_info._request_count

        server_info.increment_request_count()

        assert server_info._request_count == initial + 1

    def test_increment_error_count(self) -> None:
        server_info = ServerInfo()
        initial = server_info._error_count

        server_info.increment_error_count()

        assert server_info._error_count == initial + 1

    def test_get_metrics(self) -> None:
        server_info = ServerInfo()
        server_info._request_count = 10
        server_info._error_count = 2

        metrics = server_info.get_metrics()

        assert isinstance(metrics, dict)
        assert "requests" in metrics
        assert "errors" in metrics
        assert "uptime" in metrics
        assert "performance" in metrics

        assert metrics["requests"]["total"] == 10
        assert metrics["errors"]["total"] == 2

    def test_format_uptime_seconds(self) -> None:
        server_info = ServerInfo()

        assert server_info._format_uptime(30) == "30 seconds"

    def test_format_uptime_minutes(self) -> None:
        server_info = ServerInfo()

        result = server_info._format_uptime(150)
        assert "2 minutes" in result

    def test_format_uptime_hours(self) -> None:
        server_info = ServerInfo()

        result = server_info._format_uptime(7200)
        assert "2 hours" in result

    def test_format_uptime_days(self) -> None:
        server_info = ServerInfo()

        result = server_info._format_uptime(172800)
        assert "2 days" in result

    def test_calculate_error_rate_no_requests(self) -> None:
        server_info = ServerInfo()

        assert server_info._calculate_error_rate() == 0.0

    def test_calculate_error_rate_with_errors(self) -> None:
        server_info = ServerInfo()
        server_info._request_count = 100
        server_info._error_count = 10

        assert server_info._calculate_error_rate() == 10.0

    def test_get_memory_usage_without_psutil(self) -> None:
        server_info = ServerInfo()

        with patch.dict("sys.modules", {"psutil": None}):
            memory = server_info._get_memory_usage()
            assert isinstance(memory, dict)


class TestGlobalFunctions:
    def test_get_server_info_returns_instance(self) -> None:
        result = get_server_info()
        assert isinstance(result, ServerInfo)

    def test_get_server_info_dict_returns_dict(self) -> None:
        result = get_server_info_dict()
        assert isinstance(result, dict)
        assert "server" in result

    def test_get_health_status_returns_dict(self) -> None:
        result = get_health_status()
        assert isinstance(result, dict)
        assert "status" in result

    def test_get_metrics_returns_dict(self) -> None:
        result = get_metrics()
        assert isinstance(result, dict)
        assert "requests" in result

    def test_increment_request_count_increments(self) -> None:
        server = get_server_info()
        initial = server._request_count

        increment_request_count()

        assert server._request_count == initial + 1

    def test_increment_error_count_increments(self) -> None:
        server = get_server_info()
        initial = server._error_count

        increment_error_count()

        assert server._error_count == initial + 1
