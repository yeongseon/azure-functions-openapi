# CLI Guide

`azure-functions-openapi` ships with a CLI entry point for generating OpenAPI output from decorated handlers.

## Install

```bash
pip install azure-functions-openapi
```

Then verify:

```bash
azure-functions-openapi --help
```

## Command overview

Current command set:

- `generate`: build OpenAPI spec in JSON or YAML

## `generate` command

### Basic usage

```bash
azure-functions-openapi generate
```

By default this prints JSON to stdout using:

- title: `API`
- version: `1.0.0`
- OpenAPI version: `3.0.0`

### Common examples

Generate JSON to stdout:

```bash
azure-functions-openapi generate --title "Todo API" --version "1.2.0"
```

Generate YAML to stdout:

```bash
azure-functions-openapi generate --format yaml --title "Todo API"
```

Write JSON to file:

```bash
azure-functions-openapi generate --output openapi.json --format json
```

Write YAML to file:

```bash
azure-functions-openapi generate --output openapi.yaml --format yaml
```

Generate OpenAPI 3.1 output:

```bash
azure-functions-openapi generate --openapi-version 3.1 --output openapi-3.1.json
```

### Options reference

| Option | Alias | Values | Default | Description |
| --- | --- | --- | --- | --- |
| `--title` | - | any string | `API` | OpenAPI `info.title` |
| `--version` | - | any string | `1.0.0` | OpenAPI `info.version` |
| `--output` | `-o` | file path | stdout | Write generated content to file |
| `--format` | `-f` | `json`, `yaml` | `json` | Output serialization format |
| `--openapi-version` | - | `3.0`, `3.1` | `3.0` | OpenAPI schema version |
| `--pretty` | `-p` | flag | `false` | Compatibility flag (accepted; output is already formatted) |

!!! note
    `--pretty` is currently accepted by the CLI parser but does not alter rendering behavior. JSON output is already pretty-printed.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Runtime or generation error |
| `2` | Invalid CLI arguments (argparse parse error) |

## Validate generated output

Use a validator in local checks and CI:

```bash
pip install openapi-spec-validator
openapi-spec-validator openapi.json
```

For YAML:

```bash
openapi-spec-validator openapi.yaml
```

## CI example

```yaml
name: OpenAPI Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install tools
        run: pip install azure-functions-openapi openapi-spec-validator
      - name: Generate spec
        run: azure-functions-openapi generate --openapi-version 3.1 --output openapi.json
      - name: Validate spec
        run: openapi-spec-validator openapi.json
```

## Troubleshooting

### `command not found`

- Confirm package installed in active environment
- Use `python -m azure_functions_openapi.cli --help` as fallback

### Empty `paths` in output

- Ensure app handlers are decorated with `@openapi`
- Ensure decorated modules are imported before running generation

### Unsupported version error

- Use only `--openapi-version 3.0` or `--openapi-version 3.1`

## Related docs

- [Usage](usage.md)
- [Configuration](configuration.md)
- [API Reference](api.md)
- [Troubleshooting](troubleshooting.md)
