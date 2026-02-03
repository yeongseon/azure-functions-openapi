"""Integration tests for azure-functions-openapi components working together."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable
import time
from unittest import mock

import pytest

from azure_functions_openapi.cli import main, handle_generate, handle_validate
from azure_functions_openapi.monitoring import (
    get_performance_monitor,
    get_request_logger,
    monitor_performance,
    run_all_health_checks,
)
from azure_functions_openapi.openapi import get_openapi_json
from azure_functions_openapi.server_info import get_health_status, get_metrics, get_server_info_dict
from azure_functions_openapi.swagger_ui import render_swagger_ui


class TestOpenAPIGenerationIntegration:
    """Integration tests for OpenAPI generation across components."""

    def test_end_to_end_openapi_generation_and_validation(self) -> None:
        """Test complete flow: generate → validate → CLI integration."""
        # Generate OpenAPI spec
        args = mock.Mock()
        args.title = "Integration Test API"
        args.version = "1.0.0"
        args.format = "json"
        args.output = None
        args.pretty = False
        args.openapi_version = "3.0"

        with mock.patch("builtins.print") as mock_print:
            result = handle_generate(args)
            assert result == 0
            output = mock_print.call_args[0][0]
            spec = json.loads(output)

        # Validate the generated spec
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Integration Test API"
        assert spec["info"]["version"] == "1.0.0"
        assert "paths" in spec

        # Test validation with the same spec
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "openapi.json"
            spec_file.write_text(json.dumps(spec))

            validate_args = mock.Mock()
            validate_args.file = str(spec_file)
            validate_args.format = None

            result = handle_validate(validate_args)
            assert result == 0

    def test_openapi_version_3_1_generation_and_validation(self) -> None:
        """Test OpenAPI 3.1 generation and validation."""
        args = mock.Mock()
        args.title = "API 3.1 Integration"
        args.version = "1.0.0"
        args.format = "json"
        args.output = None
        args.pretty = False
        args.openapi_version = "3.1"

        with mock.patch("builtins.print") as mock_print:
            result = handle_generate(args)
            assert result == 0
            output = mock_print.call_args[0][0]
            spec = json.loads(output)

        # Validate 3.1 specific features
        assert spec["openapi"] == "3.1.0"


class TestMonitoringAndServerInfoIntegration:
    """Integration tests for monitoring and server info components."""

    def test_performance_monitoring_with_server_info(self) -> None:
        """Test that performance monitoring works with server info."""
        monitor = get_performance_monitor()
        initial_count = len(monitor._response_times)

        # Simulate some API calls through monitored functions
        @monitor_performance  # type: ignore[misc]
        def simulated_api_call() -> dict[str, str]:
            return {"status": "ok", "data": "test"}

        result = simulated_api_call()
        assert result["status"] == "ok"

        # Check that response time was recorded
        assert len(monitor._response_times) > initial_count

        # Check server info reflects the activity
        server_info = get_server_info_dict()
        stats = server_info["statistics"]
        assert stats["total_requests"] > 0

    def test_request_logging_with_server_metrics(self) -> None:
        """Test request logging integration with server metrics."""
        logger = get_request_logger()
        initial_log_count = len(logger._request_log)

        # Log some requests
        logger.log_request("GET", "/api/test", 200, 0.1)
        logger.log_request("POST", "/api/data", 201, 0.2)
        logger.log_request("GET", "/api/error", 500, 0.05)

        # Check logger statistics
        logger_stats = logger.get_request_stats()
        assert logger_stats["total_requests"] == 3
        assert logger_stats["status_codes"][200] == 1
        assert logger_stats["status_codes"][201] == 1
        assert logger_stats["status_codes"][500] == 1

    def test_health_checks_integration(self) -> None:
        """Test health checks integration with monitoring components."""
        # Run all health checks
        health_result = run_all_health_checks()

        assert "overall_status" in health_result
        assert "checks" in health_result
        assert "timestamp" in health_result

        # Check that individual health checks work
        for check_name, check_result in health_result["checks"].items():
            assert "status" in check_result
            assert "name" in check_result

    def test_server_info_and_monitoring_consistency(self) -> None:
        """Test that server info and monitoring components are consistent."""
        # Get server info
        server_info = get_server_info_dict()

        # Get health status
        health = get_health_status()

        # Get metrics
        metrics = get_metrics()

        # Verify consistency across components
        assert server_info["statistics"]["total_requests"] == metrics["requests"]["total"]
        assert server_info["statistics"]["total_errors"] == metrics["errors"]["total"]

        # Health status should reflect server info
        if health["status"] == "healthy":
            assert server_info["statistics"]["error_rate"] < 10.0


class TestCLIIntegration:
    """Integration tests for CLI with other components."""

    def test_cli_generate_with_output_file(self) -> None:
        """Test CLI generate command with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "generated_openapi.json"

            with mock.patch.object(
                sys,
                "argv",
                [
                    "azure-functions-openapi",
                    "generate",
                    "--title",
                    "CLI Integration Test",
                    "--version",
                    "2.0.0",
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            assert result == 0
            assert output_path.exists()

            # Verify the generated content
            content = output_path.read_text()
            spec = json.loads(content)
            assert spec["info"]["title"] == "CLI Integration Test"
            assert spec["info"]["version"] == "2.0.0"

    def test_cli_info_command_integration(self) -> None:
        """Test CLI info command integration with server info."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "info"]):
            with mock.patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        output = mock_print.call_args[0][0]
        info = json.loads(output)
        assert "server" in info
        assert "runtime" in info
        assert "statistics" in info

    def test_cli_health_command_integration(self) -> None:
        """Test CLI health command integration with monitoring."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "health"]):
            with mock.patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        output = mock_print.call_args[0][0]
        health = json.loads(output)
        assert "status" in health
        assert "timestamp" in health

    def test_cli_metrics_command_integration(self) -> None:
        """Test CLI metrics command integration with monitoring."""

        # Make some API calls to generate metrics
        @monitor_performance  # type: ignore[misc]
        def test_call() -> dict[str, str]:
            return {"test": "data"}

        test_call()

        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "metrics"]):
            with mock.patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        output = mock_print.call_args[0][0]
        metrics = json.loads(output)
        assert "requests" in metrics
        assert "errors" in metrics
        assert "uptime" in metrics


class TestSwaggerUIIntegration:
    """Integration tests for Swagger UI with other components."""

    def test_swagger_ui_with_openapi_spec(self) -> None:
        """Test Swagger UI integration with OpenAPI spec generation."""
        # Generate OpenAPI spec
        spec_json = get_openapi_json()
        spec = json.loads(spec_json)

        # Render Swagger UI
        response = render_swagger_ui()

        assert response.mimetype == "text/html"
        html_content = response.get_body().decode()
        assert "swagger-ui" in html_content.lower()
        assert spec["info"]["title"] in html_content


class TestErrorHandlingIntegration:
    """Integration tests for error handling across components."""

    def test_error_handling_in_monitoring(self) -> None:
        """Test that errors are properly handled and counted by monitoring."""
        server_info = get_server_info_dict()
        initial_errors = server_info["statistics"]["total_errors"]

        @monitor_performance  # type: ignore[misc]
        def failing_function() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        # Check that error was counted
        updated_info = get_server_info_dict()
        assert updated_info["statistics"]["total_errors"] > initial_errors

    def test_invalid_openapi_spec_validation(self) -> None:
        """Test validation of invalid OpenAPI specs."""
        invalid_spec = {
            "openapi": "3.0.0",
            # Missing required 'info' field
            "paths": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "invalid_openapi.json"
            spec_file.write_text(json.dumps(invalid_spec))

            args = mock.Mock()
            args.file = str(spec_file)
            args.format = None

            result = handle_validate(args)
            assert result == 1  # Should fail validation


class TestPerformanceIntegration:
    """Integration tests for performance across components."""

    def test_end_to_end_performance_measurement(self) -> None:
        """Test performance measurement across the entire stack."""
        start_time = time.time()

        # Simulate a complete API workflow
        @monitor_performance  # type: ignore[misc]
        def complete_workflow() -> dict[str, object]:
            # Generate OpenAPI spec
            spec_json = get_openapi_json()
            spec = json.loads(spec_json)

            # Get server info
            info = get_server_info_dict()

            # Log the request
            from azure_functions_openapi.monitoring import log_request

            log_request("GET", "/api/workflow", 200, time.time() - start_time)

            return {"spec": spec, "info": info}

        result = complete_workflow()

        # Verify all components worked
        assert "spec" in result
        assert "info" in result
        assert result["spec"]["openapi"] == "3.0.0"

        # Check that performance was monitored
        monitor = get_performance_monitor()
        assert len(monitor._response_times) > 0

    def test_concurrent_request_simulation(self) -> None:
        """Test handling of concurrent-like requests."""
        requests_completed = 0

        @monitor_performance  # type: ignore[misc]
        def simulate_request(request_id: int) -> dict[str, object]:
            nonlocal requests_completed
            requests_completed += 1

            # Simulate some work
            time.sleep(0.01)

            return {
                "request_id": request_id,
                "status": "completed",
                "server_info": get_server_info_dict(),
            }

        # Simulate multiple requests
        results = []
        for i in range(5):
            result = simulate_request(i)
            results.append(result)

        # Verify all requests completed
        assert len(results) == 5
        assert requests_completed == 5

        # Check that all were monitored
        monitor = get_performance_monitor()
        assert len(monitor._response_times) >= 5

        # Check server stats reflect the activity
        server_info = get_server_info_dict()
        assert server_info["statistics"]["total_requests"] >= 5
