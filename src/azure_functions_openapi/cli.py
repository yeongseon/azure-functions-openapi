# src/azure_functions_openapi/cli.py

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from azure_functions_openapi.openapi import generate_openapi_spec, get_openapi_json, get_openapi_yaml
from azure_functions_openapi.server_info import get_server_info_dict, get_health_status, get_metrics


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
  
  # Get server information
  azure-functions-openapi info
  
  # Check health status
  azure-functions-openapi health
  
  # Get metrics
  azure-functions-openapi metrics
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate OpenAPI specification")
    generate_parser.add_argument(
        "--title", 
        default="API", 
        help="API title (default: API)"
    )
    generate_parser.add_argument(
        "--version", 
        default="1.0.0", 
        help="API version (default: 1.0.0)"
    )
    generate_parser.add_argument(
        "--output", "-o", 
        help="Output file path"
    )
    generate_parser.add_argument(
        "--format", "-f", 
        choices=["json", "yaml"], 
        default="json", 
        help="Output format (default: json)"
    )
    generate_parser.add_argument(
        "--pretty", "-p", 
        action="store_true", 
        help="Pretty print output"
    )
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get server information")
    info_parser.add_argument(
        "--output", "-o", 
        help="Output file path"
    )
    info_parser.add_argument(
        "--format", "-f", 
        choices=["json", "yaml"], 
        default="json", 
        help="Output format (default: json)"
    )
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check health status")
    health_parser.add_argument(
        "--output", "-o", 
        help="Output file path"
    )
    health_parser.add_argument(
        "--format", "-f", 
        choices=["json", "yaml"], 
        default="json", 
        help="Output format (default: json)"
    )
    
    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Get performance metrics")
    metrics_parser.add_argument(
        "--output", "-o", 
        help="Output file path"
    )
    metrics_parser.add_argument(
        "--format", "-f", 
        choices=["json", "yaml"], 
        default="json", 
        help="Output format (default: json)"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate OpenAPI specification")
    validate_parser.add_argument(
        "file", 
        help="OpenAPI specification file to validate"
    )
    validate_parser.add_argument(
        "--format", "-f", 
        choices=["json", "yaml"], 
        help="File format (auto-detect if not specified)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "generate":
            return handle_generate(args)
        elif args.command == "info":
            return handle_info(args)
        elif args.command == "health":
            return handle_health(args)
        elif args.command == "metrics":
            return handle_metrics(args)
        elif args.command == "validate":
            return handle_validate(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_generate(args) -> int:
    """Handle generate command."""
    try:
        if args.format == "json":
            content = get_openapi_json(args.title, args.version)
        else:  # yaml
            content = get_openapi_yaml(args.title, args.version)
        
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


def handle_info(args) -> int:
    """Handle info command."""
    try:
        info = get_server_info_dict()
        
        if args.format == "json":
            content = json.dumps(info, indent=2 if args.pretty else None)
        else:  # yaml
            import yaml
            content = yaml.safe_dump(info, default_flow_style=False)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(content, encoding="utf-8")
            print(f"Server information written to {output_path}")
        else:
            print(content)
        
        return 0
    except Exception as e:
        print(f"Failed to get server information: {e}", file=sys.stderr)
        return 1


def handle_health(args) -> int:
    """Handle health command."""
    try:
        health = get_health_status()
        
        if args.format == "json":
            content = json.dumps(health, indent=2 if args.pretty else None)
        else:  # yaml
            import yaml
            content = yaml.safe_dump(health, default_flow_style=False)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(content, encoding="utf-8")
            print(f"Health status written to {output_path}")
        else:
            print(content)
        
        # Return non-zero exit code if unhealthy
        if health.get("status") == "unhealthy":
            return 1
        
        return 0
    except Exception as e:
        print(f"Failed to get health status: {e}", file=sys.stderr)
        return 1


def handle_metrics(args) -> int:
    """Handle metrics command."""
    try:
        metrics = get_metrics()
        
        if args.format == "json":
            content = json.dumps(metrics, indent=2 if args.pretty else None)
        else:  # yaml
            import yaml
            content = yaml.safe_dump(metrics, default_flow_style=False)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(content, encoding="utf-8")
            print(f"Metrics written to {output_path}")
        else:
            print(content)
        
        return 0
    except Exception as e:
        print(f"Failed to get metrics: {e}", file=sys.stderr)
        return 1


def handle_validate(args) -> int:
    """Handle validate command."""
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            return 1
        
        content = file_path.read_text(encoding="utf-8")
        
        # Auto-detect format if not specified
        if not args.format:
            if file_path.suffix.lower() in [".json"]:
                args.format = "json"
            elif file_path.suffix.lower() in [".yaml", ".yml"]:
                args.format = "yaml"
            else:
                # Try to parse as JSON first, then YAML
                try:
                    json.loads(content)
                    args.format = "json"
                except json.JSONDecodeError:
                    args.format = "yaml"
        
        # Parse the content
        if args.format == "json":
            spec = json.loads(content)
        else:  # yaml
            import yaml
            spec = yaml.safe_load(content)
        
        # Basic validation
        errors = validate_openapi_spec(spec)
        
        if errors:
            print("Validation errors found:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        else:
            print("OpenAPI specification is valid")
            return 0
            
    except Exception as e:
        print(f"Failed to validate OpenAPI specification: {e}", file=sys.stderr)
        return 1


def validate_openapi_spec(spec: dict) -> list:
    """Validate OpenAPI specification."""
    errors = []
    
    # Check required fields
    if "openapi" not in spec:
        errors.append("Missing required field: openapi")
    
    if "info" not in spec:
        errors.append("Missing required field: info")
    else:
        info = spec["info"]
        if "title" not in info:
            errors.append("Missing required field: info.title")
        if "version" not in info:
            errors.append("Missing required field: info.version")
    
    if "paths" not in spec:
        errors.append("Missing required field: paths")
    
    # Check OpenAPI version
    if "openapi" in spec:
        version = spec["openapi"]
        if not version.startswith("3."):
            errors.append(f"Unsupported OpenAPI version: {version}")
    
    # Check paths
    if "paths" in spec:
        paths = spec["paths"]
        if not isinstance(paths, dict):
            errors.append("paths must be an object")
        else:
            for path, path_item in paths.items():
                if not isinstance(path_item, dict):
                    errors.append(f"Path '{path}' must be an object")
                else:
                    # Check HTTP methods
                    valid_methods = ["get", "post", "put", "delete", "patch", "head", "options", "trace"]
                    for method in path_item.keys():
                        if method not in valid_methods and not method.startswith("x-"):
                            errors.append(f"Invalid HTTP method '{method}' in path '{path}'")
    
    return errors


if __name__ == "__main__":
    sys.exit(main())