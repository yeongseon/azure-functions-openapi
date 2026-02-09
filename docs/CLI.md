# CLI Tool Guide

The Azure Functions OpenAPI CLI tool provides command-line access to various features of the library.

## Installation

The CLI tool is automatically installed when you install the package:

```bash
pip install azure-functions-openapi
```

## Usage

### Basic Commands

```bash
# Show help
azure-functions-openapi --help

# Show command-specific help
azure-functions-openapi generate --help
```

### Generate OpenAPI Specification

Generate an OpenAPI specification:

```bash
# Generate JSON specification
azure-functions-openapi generate --title "My API" --version "1.0.0"

# Generate YAML specification
azure-functions-openapi generate --format yaml --title "My API" --version "1.0.0"

# Save to file
azure-functions-openapi generate --output openapi.json --title "My API" --version "1.0.0"

# Pretty print output
azure-functions-openapi generate --pretty --title "My API" --version "1.0.0"
```

#### Generate Command Options

- `--title`: API title (default: "API")
- `--version`: API version (default: "1.0.0")
- `--output, -o`: Output file path
- `--format, -f`: Output format (json or yaml, default: json)
- `--pretty, -p`: Pretty print output

### Validate OpenAPI Specification

Use external validators to check generated specs:

```bash
openapi-spec-validator openapi.json
```

## Examples

### Generate API Documentation

```bash
# Generate comprehensive API documentation
azure-functions-openapi generate \
  --title "User Management API" \
  --version "2.1.0" \
  --output docs/api-spec.json \
  --format json \
  --pretty
```

The CLI tool provides one primary command:

- `generate`: Create OpenAPI JSON/YAML output

### CI/CD Integration

```yaml
# .github/workflows/api-validation.yml
name: API Validation

on: [push, pull_request]

jobs:
  validate-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install azure-functions-openapi openapi-spec-validator
      - name: Generate OpenAPI spec
        run: |
          azure-functions-openapi generate --output openapi.json
      - name: Validate OpenAPI spec
        run: |
          openapi-spec-validator openapi.json
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: openapi-spec
          path: openapi.json
```

## Exit Codes

The CLI tool uses standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid arguments

## Error Handling

The CLI tool provides clear error messages:

```bash
# Invalid command
$ azure-functions-openapi invalid-command
Error: Unknown command: invalid-command

# Validation error
$ openapi-spec-validator invalid.json
```

## Configuration

### Environment Variables

You can configure the CLI tool using environment variables:

```bash
# Set default output format
export AZURE_FUNCTIONS_OPENAPI_DEFAULT_FORMAT=yaml

# Set default output directory
export AZURE_FUNCTIONS_OPENAPI_OUTPUT_DIR=./docs
```

### Configuration File

Create a configuration file at `~/.azure-functions-openapi/config.json`:

```json
{
  "default_format": "json",
  "default_output_dir": "./docs",
  "pretty_print": true,
  "cache_ttl": 300
}
```

## Integration with Other Tools

### jq Integration

Use jq to process JSON output:

```bash
# Filter OpenAPI info
azure-functions-openapi generate --format json | jq '.info'
```

### curl Integration

Use curl to send generated specs to other services:

```bash
# Generate spec and send to API gateway
azure-functions-openapi generate --format json | \
  curl -X POST -H "Content-Type: application/json" \
  -d @- https://api-gateway.example.com/specs
```

### Docker Integration

Use the CLI tool in Docker containers:

```dockerfile
FROM python:3.10-slim

# Install the package
RUN pip install azure-functions-openapi

# Copy your application
COPY . /app
WORKDIR /app

# Use the CLI tool
CMD ["azure-functions-openapi", "generate", "--output", "/app/openapi.json"]
```

## Troubleshooting

### Common Issues

1. **Command not found**
   ```bash
   # Make sure the package is installed
   pip install azure-functions-openapi
   
   # Check if the command is in PATH
   which azure-functions-openapi
   ```

2. **Permission denied**
   ```bash
   # Make sure you have write permissions for output files
   chmod 755 /path/to/output/directory
   ```

3. **Invalid JSON/YAML**
   ```bash
   # Validate your input files
   openapi-spec-validator your-file.json
   ```

### Debug Mode

Enable debug mode for more verbose output:

```bash
# Set debug environment variable
export AZURE_FUNCTIONS_OPENAPI_DEBUG=1

# Run command with debug output
azure-functions-openapi generate --title "Debug API"
```

### Log Files

The CLI tool logs to:
- Console output (stdout/stderr)
- System logs (when available)
- Debug files (when debug mode is enabled)
