from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from azure_functions_openapi.cli import (
    handle_generate,
    handle_health,
    handle_info,
    handle_metrics,
    handle_validate,
    main,
    validate_openapi_spec,
)


class TestMain:
    def test_main_no_command_returns_1(self) -> None:
        with patch.object(sys, "argv", ["azure-functions-openapi"]):
            result = main()
        assert result == 1

    def test_main_unknown_command_returns_1(self) -> None:
        with patch.object(sys, "argv", ["azure-functions-openapi", "unknown"]):
            with patch("azure_functions_openapi.cli.argparse.ArgumentParser.parse_args") as mock:
                mock.return_value = argparse.Namespace(command="unknown_cmd")
                result = main()
        assert result == 1

    def test_main_generate_command(self) -> None:
        with patch.object(sys, "argv", ["azure-functions-openapi", "generate"]):
            with patch("azure_functions_openapi.cli.handle_generate", return_value=0) as mock:
                result = main()
        assert mock.called or result == 0

    def test_main_info_command(self) -> None:
        with patch.object(sys, "argv", ["azure-functions-openapi", "info"]):
            with patch("azure_functions_openapi.cli.handle_info", return_value=0) as mock:
                result = main()
        assert mock.called or result == 0

    def test_main_health_command(self) -> None:
        with patch.object(sys, "argv", ["azure-functions-openapi", "health"]):
            with patch("azure_functions_openapi.cli.handle_health", return_value=0) as mock:
                result = main()
        assert mock.called or result == 0

    def test_main_metrics_command(self) -> None:
        with patch.object(sys, "argv", ["azure-functions-openapi", "metrics"]):
            with patch("azure_functions_openapi.cli.handle_metrics", return_value=0) as mock:
                result = main()
        assert mock.called or result == 0


class TestHandleGenerate:
    def test_handle_generate_json(self) -> None:
        args = argparse.Namespace(
            format="json",
            title="Test API",
            version="1.0.0",
            output=None,
            pretty=False,
        )

        with patch("azure_functions_openapi.cli.get_openapi_json", return_value="{}"):
            result = handle_generate(args)

        assert result == 0

    def test_handle_generate_yaml(self) -> None:
        args = argparse.Namespace(
            format="yaml",
            title="Test API",
            version="1.0.0",
            output=None,
            pretty=False,
        )

        with patch("azure_functions_openapi.cli.get_openapi_yaml", return_value="openapi: 3.0.0"):
            result = handle_generate(args)

        assert result == 0

    def test_handle_generate_with_output_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            output_path = f.name

        args = argparse.Namespace(
            format="json",
            title="Test API",
            version="1.0.0",
            output=output_path,
            pretty=False,
        )

        with patch("azure_functions_openapi.cli.get_openapi_json", return_value='{"test": true}'):
            result = handle_generate(args)

        assert result == 0
        assert Path(output_path).exists()
        Path(output_path).unlink()

    def test_handle_generate_error(self) -> None:
        args = argparse.Namespace(
            format="json",
            title="Test API",
            version="1.0.0",
            output=None,
            pretty=False,
        )

        with patch("azure_functions_openapi.cli.get_openapi_json", side_effect=Exception("Error")):
            result = handle_generate(args)

        assert result == 1


class TestHandleInfo:
    def test_handle_info_json(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_server_info_dict",
            return_value={"server": "test"},
        ):
            result = handle_info(args)

        assert result == 0

    def test_handle_info_yaml(self) -> None:
        args = argparse.Namespace(format="yaml", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_server_info_dict",
            return_value={"server": "test"},
        ):
            result = handle_info(args)

        assert result == 0

    def test_handle_info_error(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_server_info_dict",
            side_effect=Exception("Error"),
        ):
            result = handle_info(args)

        assert result == 1


class TestHandleHealth:
    def test_handle_health_healthy(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_health_status",
            return_value={"status": "healthy"},
        ):
            result = handle_health(args)

        assert result == 0

    def test_handle_health_unhealthy(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_health_status",
            return_value={"status": "unhealthy"},
        ):
            result = handle_health(args)

        assert result == 1

    def test_handle_health_error(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_health_status",
            side_effect=Exception("Error"),
        ):
            result = handle_health(args)

        assert result == 1


class TestHandleMetrics:
    def test_handle_metrics_json(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_metrics",
            return_value={"requests": 100},
        ):
            result = handle_metrics(args)

        assert result == 0

    def test_handle_metrics_error(self) -> None:
        args = argparse.Namespace(format="json", output=None, pretty=False)

        with patch(
            "azure_functions_openapi.cli.get_metrics",
            side_effect=Exception("Error"),
        ):
            result = handle_metrics(args)

        assert result == 1


class TestHandleValidate:
    def test_handle_validate_valid_json(self) -> None:
        valid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_spec, f)
            file_path = f.name

        args = argparse.Namespace(file=file_path, format=None)
        result = handle_validate(args)

        assert result == 0
        Path(file_path).unlink()

    def test_handle_validate_invalid_spec(self) -> None:
        invalid_spec = {"invalid": "spec"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(invalid_spec, f)
            file_path = f.name

        args = argparse.Namespace(file=file_path, format=None)
        result = handle_validate(args)

        assert result == 1
        Path(file_path).unlink()

    def test_handle_validate_file_not_found(self) -> None:
        args = argparse.Namespace(file="/nonexistent/file.json", format=None)
        result = handle_validate(args)

        assert result == 1

    def test_handle_validate_yaml(self) -> None:
        valid_spec = "openapi: '3.0.0'\ninfo:\n  title: Test\n  version: '1.0.0'\npaths: {}"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(valid_spec)
            file_path = f.name

        args = argparse.Namespace(file=file_path, format=None)
        result = handle_validate(args)

        assert result == 0
        Path(file_path).unlink()


class TestValidateOpenapiSpec:
    def test_validate_openapi_spec_valid(self) -> None:
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        errors = validate_openapi_spec(spec)

        assert errors == []

    def test_validate_openapi_spec_missing_openapi(self) -> None:
        spec = {"info": {"title": "Test", "version": "1.0.0"}, "paths": {}}

        errors = validate_openapi_spec(spec)

        assert any("openapi" in e for e in errors)

    def test_validate_openapi_spec_missing_info(self) -> None:
        spec = {"openapi": "3.0.0", "paths": {}}

        errors = validate_openapi_spec(spec)

        assert any("info" in e for e in errors)

    def test_validate_openapi_spec_missing_info_title(self) -> None:
        spec = {"openapi": "3.0.0", "info": {"version": "1.0.0"}, "paths": {}}

        errors = validate_openapi_spec(spec)

        assert any("title" in e for e in errors)

    def test_validate_openapi_spec_missing_info_version(self) -> None:
        spec = {"openapi": "3.0.0", "info": {"title": "Test"}, "paths": {}}

        errors = validate_openapi_spec(spec)

        assert any("version" in e for e in errors)

    def test_validate_openapi_spec_missing_paths(self) -> None:
        spec = {"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}}

        errors = validate_openapi_spec(spec)

        assert any("paths" in e for e in errors)

    def test_validate_openapi_spec_invalid_version(self) -> None:
        spec = {
            "openapi": "2.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        errors = validate_openapi_spec(spec)

        assert any("Unsupported" in e for e in errors)

    def test_validate_openapi_spec_invalid_path_item(self) -> None:
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/test": "invalid"},
        }

        errors = validate_openapi_spec(spec)

        assert any("must be an object" in e for e in errors)

    def test_validate_openapi_spec_invalid_http_method(self) -> None:
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/test": {"invalid_method": {}}},
        }

        errors = validate_openapi_spec(spec)

        assert any("Invalid HTTP method" in e for e in errors)

    def test_validate_openapi_spec_extension_allowed(self) -> None:
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/test": {"x-custom": "value", "get": {}}},
        }

        errors = validate_openapi_spec(spec)

        assert not any("x-custom" in e for e in errors)
