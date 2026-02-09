# tests/test_cli.py
"""Tests for CLI module."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

import pytest

from azure_functions_openapi.cli import handle_generate, main


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
