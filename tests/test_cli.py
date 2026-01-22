# tests/test_cli.py
"""Tests for CLI module."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

import pytest

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
    """Tests for main() entry point."""

    def test_no_command_prints_help_and_returns_1(self) -> None:
        """Test that no command prints help and returns exit code 1."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi"]):
            result = main()
            assert result == 1

    def test_unknown_command_exits_with_error(self) -> None:
        """Test that unknown command exits with SystemExit (argparse behavior)."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "unknown"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # argparse exits with code 2 for errors


class TestHandleGenerate:
    """Tests for handle_generate() command."""

    def test_generate_json_default(self) -> None:
        """Test default JSON generation."""
        args = mock.Mock()
        args.title = "Test API"
        args.version = "1.0.0"
        args.format = "json"
        args.output = None
        args.pretty = False
        args.openapi_version = "3.0"

        with mock.patch("builtins.print") as mock_print:
            result = handle_generate(args)

        assert result == 0
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        spec = json.loads(output)
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "1.0.0"

    def test_generate_yaml_format(self) -> None:
        """Test YAML generation."""
        args = mock.Mock()
        args.title = "YAML API"
        args.version = "2.0.0"
        args.format = "yaml"
        args.output = None
        args.pretty = False
        args.openapi_version = "3.0"

        with mock.patch("builtins.print") as mock_print:
            result = handle_generate(args)

        assert result == 0
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        assert "openapi:" in output
        assert "YAML API" in output

    def test_generate_openapi_version_3_1(self) -> None:
        """Test OpenAPI 3.1 generation."""
        args = mock.Mock()
        args.title = "API 3.1"
        args.version = "1.0.0"
        args.format = "json"
        args.output = None
        args.pretty = False
        args.openapi_version = "3.1"

        with mock.patch("builtins.print") as mock_print:
            result = handle_generate(args)

        assert result == 0
        mock_print.assert_called_once()
        output = mock_print.call_args[0][0]
        spec = json.loads(output)
        assert spec["openapi"] == "3.1.0"
        assert spec["info"]["title"] == "API 3.1"

    def test_generate_openapi_version_3_0_explicit(self) -> None:
        """Test explicit OpenAPI 3.0 generation."""
        args = mock.Mock()
        args.title = "API 3.0"
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
        assert spec["openapi"] == "3.0.0"

    def test_generate_with_output_file(self) -> None:
        """Test generation with output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "openapi.json"

            args = mock.Mock()
            args.title = "File API"
            args.version = "1.0.0"
            args.format = "json"
            args.output = str(output_path)
            args.pretty = False
            args.openapi_version = "3.0"

            result = handle_generate(args)

            assert result == 0
            assert output_path.exists()
            content = output_path.read_text()
            spec = json.loads(content)
            assert spec["info"]["title"] == "File API"

    def test_generate_yaml_with_openapi_3_1(self) -> None:
        """Test YAML generation with OpenAPI 3.1."""
        args = mock.Mock()
        args.title = "YAML 3.1 API"
        args.version = "1.0.0"
        args.format = "yaml"
        args.output = None
        args.pretty = False
        args.openapi_version = "3.1"

        with mock.patch("builtins.print") as mock_print:
            result = handle_generate(args)

        assert result == 0
        output = mock_print.call_args[0][0]
        assert "openapi: 3.1.0" in output or "openapi: '3.1.0'" in output


class TestHandleInfo:
    """Tests for handle_info() command."""

    def test_info_json_format(self) -> None:
        """Test info command with JSON format."""
        args = mock.Mock()
        args.format = "json"
        args.output = None
        args.pretty = False

        with mock.patch("builtins.print") as mock_print:
            result = handle_info(args)

        assert result == 0
        mock_print.assert_called_once()


class TestHandleHealth:
    """Tests for handle_health() command."""

    def test_health_returns_0_when_healthy(self) -> None:
        """Test health command returns 0 when healthy."""
        args = mock.Mock()
        args.format = "json"
        args.output = None
        args.pretty = False

        with mock.patch("builtins.print"):
            result = handle_health(args)

        assert result == 0


class TestHandleMetrics:
    """Tests for handle_metrics() command."""

    def test_metrics_json_format(self) -> None:
        """Test metrics command with JSON format."""
        args = mock.Mock()
        args.format = "json"
        args.output = None
        args.pretty = False

        with mock.patch("builtins.print") as mock_print:
            result = handle_metrics(args)

        assert result == 0
        mock_print.assert_called_once()


class TestHandleValidate:
    """Tests for handle_validate() command."""

    def test_validate_valid_json_spec(self) -> None:
        """Test validation of valid JSON OpenAPI spec."""
        valid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "openapi.json"
            spec_file.write_text(json.dumps(valid_spec))

            args = mock.Mock()
            args.file = str(spec_file)
            args.format = None

            result = handle_validate(args)

        assert result == 0

    def test_validate_file_not_found(self) -> None:
        """Test validation with non-existent file."""
        args = mock.Mock()
        args.file = "/nonexistent/file.json"
        args.format = None

        result = handle_validate(args)

        assert result == 1

    def test_validate_invalid_spec_missing_openapi(self) -> None:
        """Test validation fails when openapi field is missing."""
        invalid_spec = {
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "openapi.json"
            spec_file.write_text(json.dumps(invalid_spec))

            args = mock.Mock()
            args.file = str(spec_file)
            args.format = None

            result = handle_validate(args)

        assert result == 1


class TestValidateOpenapiSpec:
    """Tests for validate_openapi_spec() function."""

    def test_valid_spec_returns_empty_list(self) -> None:
        """Test valid spec returns no errors."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert errors == []

    def test_valid_spec_3_1_returns_empty_list(self) -> None:
        """Test valid 3.1 spec returns no errors."""
        spec = {
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert errors == []

    def test_missing_openapi_field(self) -> None:
        """Test missing openapi field returns error."""
        spec = {
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert "Missing required field: openapi" in errors

    def test_missing_info_field(self) -> None:
        """Test missing info field returns error."""
        spec = {
            "openapi": "3.0.0",
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert "Missing required field: info" in errors

    def test_missing_info_title(self) -> None:
        """Test missing info.title returns error."""
        spec = {
            "openapi": "3.0.0",
            "info": {"version": "1.0.0"},
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert "Missing required field: info.title" in errors

    def test_missing_info_version(self) -> None:
        """Test missing info.version returns error."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test"},
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert "Missing required field: info.version" in errors

    def test_missing_paths_field(self) -> None:
        """Test missing paths field returns error."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
        }
        errors = validate_openapi_spec(spec)
        assert "Missing required field: paths" in errors

    def test_unsupported_openapi_version(self) -> None:
        """Test unsupported OpenAPI version returns error."""
        spec = {
            "openapi": "2.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        errors = validate_openapi_spec(spec)
        assert "Unsupported OpenAPI version: 2.0" in errors

    def test_invalid_paths_type(self) -> None:
        """Test invalid paths type returns error."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": "invalid",
        }
        errors = validate_openapi_spec(spec)
        assert "paths must be an object" in errors

    def test_invalid_http_method(self) -> None:
        """Test invalid HTTP method returns error."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/test": {"invalid_method": {}}},
        }
        errors = validate_openapi_spec(spec)
        assert "Invalid HTTP method 'invalid_method' in path '/test'" in errors

    def test_extension_fields_are_allowed(self) -> None:
        """Test x- extension fields are allowed in paths."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/test": {"get": {}, "x-custom": "value"}},
        }
        errors = validate_openapi_spec(spec)
        assert errors == []


class TestCLIIntegration:
    """Integration tests for CLI commands via sys.argv."""

    def test_generate_command_via_main(self) -> None:
        """Test generate command through main()."""
        with mock.patch.object(
            sys, "argv", ["azure-functions-openapi", "generate", "--title", "CLI Test"]
        ):
            with mock.patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        output = mock_print.call_args[0][0]
        spec = json.loads(output)
        assert spec["info"]["title"] == "CLI Test"

    def test_generate_with_openapi_version_flag(self) -> None:
        """Test generate command with --openapi-version flag."""
        with mock.patch.object(
            sys,
            "argv",
            ["azure-functions-openapi", "generate", "--openapi-version", "3.1"],
        ):
            with mock.patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        output = mock_print.call_args[0][0]
        spec = json.loads(output)
        assert spec["openapi"] == "3.1.0"

    def test_generate_with_all_options(self) -> None:
        """Test generate command with all options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "spec.json"

            with mock.patch.object(
                sys,
                "argv",
                [
                    "azure-functions-openapi",
                    "generate",
                    "--title",
                    "Full Test",
                    "--version",
                    "2.0.0",
                    "--openapi-version",
                    "3.1",
                    "--format",
                    "json",
                    "--output",
                    str(output_path),
                ],
            ):
                result = main()

            assert result == 0
            assert output_path.exists()
            spec = json.loads(output_path.read_text())
            assert spec["openapi"] == "3.1.0"
            assert spec["info"]["title"] == "Full Test"
            assert spec["info"]["version"] == "2.0.0"

    def test_info_command_via_main(self) -> None:
        """Test info command through main()."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "info"]):
            with mock.patch("builtins.print"):
                result = main()

        assert result == 0

    def test_health_command_via_main(self) -> None:
        """Test health command through main()."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "health"]):
            with mock.patch("builtins.print"):
                result = main()

        assert result == 0

    def test_metrics_command_via_main(self) -> None:
        """Test metrics command through main()."""
        with mock.patch.object(sys, "argv", ["azure-functions-openapi", "metrics"]):
            with mock.patch("builtins.print"):
                result = main()

        assert result == 0

    def test_validate_command_via_main(self) -> None:
        """Test validate command through main()."""
        valid_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "spec.json"
            spec_file.write_text(json.dumps(valid_spec))

            with mock.patch.object(
                sys, "argv", ["azure-functions-openapi", "validate", str(spec_file)]
            ):
                with mock.patch("builtins.print"):
                    result = main()

        assert result == 0
