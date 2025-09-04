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

### Server Information

Get server information:

```bash
# Get server info as JSON
azure-functions-openapi info

# Get server info as YAML
azure-functions-openapi info --format yaml

# Save to file
azure-functions-openapi info --output server-info.json
```

#### Server Information Includes

- Server details (name, version, environment)
- Runtime information (Python version, platform)
- Uptime statistics
- Request/error statistics
- Security features status
- Available features

### Health Status

Check health status:

```bash
# Check health status
azure-functions-openapi health

# Save health status to file
azure-functions-openapi health --output health.json

# Get health status as YAML
azure-functions-openapi health --format yaml
```

#### Health Status Information

- Overall health status (healthy/unhealthy/starting/error)
- Individual health checks
- Timestamp
- Uptime
- Error rate
- Request statistics

### Performance Metrics

Get performance metrics:

```bash
# Get metrics
azure-functions-openapi metrics

# Save metrics to file
azure-functions-openapi metrics --output metrics.json

# Get metrics as YAML
azure-functions-openapi metrics --format yaml
```

#### Metrics Include

- Request statistics (total, per second, per minute, per hour)
- Error statistics (total, rate, per second)
- Uptime information
- Performance metrics (response time, memory usage)

### Validate OpenAPI Specification

Validate an OpenAPI specification file:

```bash
# Validate JSON file
azure-functions-openapi validate openapi.json

# Validate YAML file
azure-functions-openapi validate openapi.yaml

# Specify format explicitly
azure-functions-openapi validate spec.json --format json
```

#### Validation Checks

- Required fields (openapi, info, paths)
- OpenAPI version compatibility
- Path structure validation
- HTTP method validation
- Parameter structure validation

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

### Health Check Script

```bash
#!/bin/bash
# health-check.sh

# Check health status
if azure-functions-openapi health --format json | jq -r '.status' | grep -q "healthy"; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is unhealthy"
    exit 1
fi
```

### Monitoring Script

```bash
#!/bin/bash
# monitor.sh

# Get metrics and save to file with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
azure-functions-openapi metrics --output "metrics_${TIMESTAMP}.json"

# Check if error rate is too high
ERROR_RATE=$(azure-functions-openapi metrics --format json | jq -r '.errors.rate')
if (( $(echo "$ERROR_RATE > 5" | bc -l) )); then
    echo "⚠️  High error rate: ${ERROR_RATE}%"
fi
```

### CI/CD Integration

```yaml
# .github/workflows/api-validation.yml
name: API Validation

on: [push, pull_request]

jobs:
  validate-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install azure-functions-openapi
      - name: Generate OpenAPI spec
        run: |
          azure-functions-openapi generate --output openapi.json
      - name: Validate OpenAPI spec
        run: |
          azure-functions-openapi validate openapi.json
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
- `3`: File not found
- `4`: Validation error

## Error Handling

The CLI tool provides clear error messages:

```bash
# Invalid command
$ azure-functions-openapi invalid-command
Error: Unknown command: invalid-command

# File not found
$ azure-functions-openapi validate nonexistent.json
Error: File not found: nonexistent.json

# Validation error
$ azure-functions-openapi validate invalid.json
Validation errors found:
  - Missing required field: openapi
  - Missing required field: info
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
# Get only the status from health check
azure-functions-openapi health | jq -r '.status'

# Get error rate from metrics
azure-functions-openapi metrics | jq -r '.errors.rate'

# Filter server info
azure-functions-openapi info | jq '.server'
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
FROM python:3.9-slim

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
   azure-functions-openapi validate your-file.json
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