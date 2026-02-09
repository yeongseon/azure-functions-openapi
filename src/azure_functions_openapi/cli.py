# src/azure_functions_openapi/cli.py
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from azure_functions_openapi.openapi import (
    OPENAPI_VERSION_3_0,
    OPENAPI_VERSION_3_1,
    get_openapi_json,
    get_openapi_yaml,
)


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Azure Functions OpenAPI CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate OpenAPI spec
  azure-functions-openapi generate --title "My API" --version "1.0.0"
  
  # Generate and save to file
  azure-functions-openapi generate --output openapi.json --format json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate OpenAPI specification")
    generate_parser.add_argument("--title", default="API", help="API title (default: API)")
    generate_parser.add_argument("--version", default="1.0.0", help="API version (default: 1.0.0)")
    generate_parser.add_argument("--output", "-o", help="Output file path")
    generate_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "yaml"],
        default="json",
        help="Output format (default: json)",
    )
    generate_parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print output")
    generate_parser.add_argument(
        "--openapi-version",
        choices=["3.0", "3.1"],
        default="3.0",
        help="OpenAPI version (default: 3.0)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "generate":
            return handle_generate(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_generate(args: argparse.Namespace) -> int:
    """Handle generate command."""
    try:
        openapi_version = (
            OPENAPI_VERSION_3_1 if args.openapi_version == "3.1" else OPENAPI_VERSION_3_0
        )

        if args.format == "json":
            content = get_openapi_json(args.title, args.version, openapi_version)
        else:
            content = get_openapi_yaml(args.title, args.version, openapi_version)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(content, encoding="utf-8")
            print(f"OpenAPI specification written to {output_path}")
        else:
            print(content)

        return 0
    except Exception as e:
        print(f"Failed to generate OpenAPI specification: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
