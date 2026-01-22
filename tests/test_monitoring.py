from __future__ import annotations

import time

import pytest

from azure_functions_openapi.monitoring import (
    HealthChecker,
    PerformanceMonitor,
    RequestLogger,
    get_health_checker,
    get_performance_monitor,
    get_request_logger,
    log_request,
    monitor_performance,
    run_all_health_checks,
    run_health_check,
)


class TestPerformanceMonitor:
    def test_init(self) -> None:
        monitor = PerformanceMonitor()
        assert monitor._response_times == []
        assert monitor._max_response_times == 1000

    def test_record_response_time(self) -> None:
        monitor = PerformanceMonitor()

        monitor.record_response_time(0.1)
        monitor.record_response_time(0.2)
        monitor.record_response_time(0.3)

        assert len(monitor._response_times) == 3
        assert 0.1 in monitor._response_times
        assert 0.2 in monitor._response_times
        assert 0.3 in monitor._response_times

    def test_record_response_time_truncates_old_entries(self) -> None:
        monitor = PerformanceMonitor()
        monitor._max_response_times = 5

        for i in range(10):
            monitor.record_response_time(float(i))

        assert len(monitor._response_times) == 5
        assert monitor._response_times == [5.0, 6.0, 7.0, 8.0, 9.0]

    def test_get_response_time_stats_empty(self) -> None:
        monitor = PerformanceMonitor()

        stats = monitor.get_response_time_stats()

        assert stats["min"] == 0.0
        assert stats["max"] == 0.0
        assert stats["avg"] == 0.0
        assert stats["count"] == 0

    def test_get_response_time_stats_with_data(self) -> None:
        monitor = PerformanceMonitor()
        for t in [0.1, 0.2, 0.3, 0.4, 0.5]:
            monitor.record_response_time(t)

        stats = monitor.get_response_time_stats()

        assert stats["min"] == 0.1
        assert stats["max"] == 0.5
        assert stats["count"] == 5
        assert 0.29 < stats["avg"] < 0.31

    def test_get_throughput_stats(self) -> None:
        monitor = PerformanceMonitor()
        monitor.record_response_time(0.1)
        monitor.record_response_time(0.2)

        stats = monitor.get_throughput_stats()

        assert "requests_per_second" in stats
        assert "requests_per_minute" in stats
        assert "requests_per_hour" in stats
        assert stats["total_requests"] == 2
        assert stats["uptime_seconds"] > 0


class TestRequestLogger:
    def test_init(self) -> None:
        logger = RequestLogger()
        assert logger._request_log == []
        assert logger._max_log_entries == 100

    def test_log_request(self) -> None:
        logger = RequestLogger()

        logger.log_request("GET", "/api/test", 200, 0.1)

        assert len(logger._request_log) == 1
        entry = logger._request_log[0]
        assert entry["method"] == "GET"
        assert entry["path"] == "/api/test"
        assert entry["status_code"] == 200
        assert entry["response_time"] == 0.1

    def test_log_request_with_optional_fields(self) -> None:
        logger = RequestLogger()

        logger.log_request(
            "POST",
            "/api/data",
            201,
            0.2,
            user_agent="TestAgent",
            ip_address="127.0.0.1",
        )

        entry = logger._request_log[0]
        assert entry["user_agent"] == "TestAgent"
        assert entry["ip_address"] == "127.0.0.1"

    def test_log_request_truncates_old_entries(self) -> None:
        logger = RequestLogger()
        logger._max_log_entries = 5

        for i in range(10):
            logger.log_request("GET", f"/api/{i}", 200, 0.1)

        assert len(logger._request_log) == 5
        assert logger._request_log[0]["path"] == "/api/5"

    def test_get_recent_requests_empty(self) -> None:
        logger = RequestLogger()

        result = logger.get_recent_requests()

        assert result == []

    def test_get_recent_requests_with_limit(self) -> None:
        logger = RequestLogger()
        for i in range(20):
            logger.log_request("GET", f"/api/{i}", 200, 0.1)

        result = logger.get_recent_requests(limit=5)

        assert len(result) == 5

    def test_get_request_stats_empty(self) -> None:
        logger = RequestLogger()

        stats = logger.get_request_stats()

        assert stats["total_requests"] == 0
        assert stats["status_codes"] == {}
        assert stats["methods"] == {}
        assert stats["avg_response_time"] == 0.0
        assert stats["error_rate"] == 0.0

    def test_get_request_stats_with_data(self) -> None:
        logger = RequestLogger()
        logger.log_request("GET", "/api/a", 200, 0.1)
        logger.log_request("POST", "/api/b", 201, 0.2)
        logger.log_request("GET", "/api/c", 404, 0.15)
        logger.log_request("GET", "/api/d", 500, 0.3)

        stats = logger.get_request_stats()

        assert stats["total_requests"] == 4
        assert stats["status_codes"][200] == 1
        assert stats["status_codes"][201] == 1
        assert stats["status_codes"][404] == 1
        assert stats["status_codes"][500] == 1
        assert stats["methods"]["GET"] == 3
        assert stats["methods"]["POST"] == 1
        assert stats["error_rate"] == 50.0


class TestHealthChecker:
    def test_init(self) -> None:
        checker = HealthChecker()
        assert checker._checks == {}

    def test_register_check(self) -> None:
        checker = HealthChecker()

        checker.register_check("test", lambda: True)

        assert "test" in checker._checks

    def test_run_check_not_found(self) -> None:
        checker = HealthChecker()

        result = checker.run_check("nonexistent")

        assert result["status"] == "unknown"
        assert "not found" in result["error"]

    def test_run_check_healthy(self) -> None:
        checker = HealthChecker()
        checker.register_check("healthy_check", lambda: True)

        result = checker.run_check("healthy_check")

        assert result["status"] == "healthy"
        assert "duration" in result
        assert "last_check" in result

    def test_run_check_unhealthy(self) -> None:
        checker = HealthChecker()
        checker.register_check("unhealthy_check", lambda: False)

        result = checker.run_check("unhealthy_check")

        assert result["status"] == "unhealthy"

    def test_run_check_error(self) -> None:
        checker = HealthChecker()

        def failing_check() -> bool:
            raise ValueError("Check failed")

        checker.register_check("error_check", failing_check)

        result = checker.run_check("error_check")

        assert result["status"] == "error"
        assert "Check failed" in result["error"]

    def test_run_all_checks_all_healthy(self) -> None:
        checker = HealthChecker()
        checker.register_check("check1", lambda: True)
        checker.register_check("check2", lambda: True)

        result = checker.run_all_checks()

        assert result["overall_status"] == "healthy"
        assert len(result["checks"]) == 2

    def test_run_all_checks_one_unhealthy(self) -> None:
        checker = HealthChecker()
        checker.register_check("healthy", lambda: True)
        checker.register_check("unhealthy", lambda: False)

        result = checker.run_all_checks()

        assert result["overall_status"] == "unhealthy"

    def test_get_check_status_not_found(self) -> None:
        checker = HealthChecker()

        result = checker.get_check_status("nonexistent")

        assert result["status"] == "unknown"

    def test_get_check_status_runs_if_stale(self) -> None:
        checker = HealthChecker()
        checker.register_check("test", lambda: True, interval=0.1)

        result = checker.get_check_status("test")

        assert result["status"] == "healthy"


class TestMonitorPerformanceDecorator:
    def test_decorator_calls_function(self) -> None:
        @monitor_performance
        def sample_function() -> str:
            return "result"

        result = sample_function()

        assert result == "result"

    def test_decorator_records_response_time(self) -> None:
        monitor = get_performance_monitor()
        initial_count = len(monitor._response_times)

        @monitor_performance
        def sample_function() -> str:
            time.sleep(0.01)
            return "result"

        sample_function()

        assert len(monitor._response_times) > initial_count

    def test_decorator_increments_error_count_on_exception(self) -> None:
        @monitor_performance
        def failing_function() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()


class TestGlobalFunctions:
    def test_get_performance_monitor(self) -> None:
        monitor = get_performance_monitor()
        assert isinstance(monitor, PerformanceMonitor)

    def test_get_request_logger(self) -> None:
        logger = get_request_logger()
        assert isinstance(logger, RequestLogger)

    def test_get_health_checker(self) -> None:
        checker = get_health_checker()
        assert isinstance(checker, HealthChecker)

    def test_log_request_function(self) -> None:
        logger = get_request_logger()
        initial_count = len(logger._request_log)

        log_request("GET", "/test", 200, 0.1)

        assert len(logger._request_log) > initial_count

    def test_run_health_check_function(self) -> None:
        checker = get_health_checker()
        checker.register_check("global_test", lambda: True)

        result = run_health_check("global_test")

        assert result["status"] == "healthy"

    def test_run_all_health_checks_function(self) -> None:
        result = run_all_health_checks()

        assert "overall_status" in result
        assert "checks" in result
