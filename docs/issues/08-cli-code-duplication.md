# Issue #8: Refactor CLI Output Formatting Code Duplication

## Priority
🟡 **MEDIUM**

## Category
Code Quality / Refactoring

## Description
The CLI module has significant code duplication in the `handle_info()`, `handle_health()`, and `handle_metrics()` functions. All three functions repeat identical logic for JSON/YAML output formatting and file writing.

## Current Behavior
```python
# Lines 161-237 in cli.py

def handle_info(args: argparse.Namespace) -> int:
    # ... get data ...
    if args.output == "json":
        output = json.dumps(info, indent=2)
    else:
        output = yaml.dump(info, default_flow_style=False)
    
    if args.file:
        with open(args.file, "w") as f:
            f.write(output)
    else:
        print(output)
    return 0

def handle_health(args: argparse.Namespace) -> int:
    # ... get data ...
    # ❌ Duplicate code - same as above
    if args.output == "json":
        output = json.dumps(health, indent=2)
    else:
        output = yaml.dump(health, default_flow_style=False)
    
    if args.file:
        with open(args.file, "w") as f:
            f.write(output)
    else:
        print(output)
    return 0

def handle_metrics(args: argparse.Namespace) -> int:
    # ... get data ...
    # ❌ Duplicate code - same as above
    if args.output == "json":
        output = json.dumps(metrics, indent=2)
    else:
        output = yaml.dump(metrics, default_flow_style=False)
    
    if args.file:
        with open(args.file, "w") as f:
            f.write(output)
    else:
        print(output)
    return 0
```

## Problems
1. **Maintenance Burden**: Changes to output logic must be made in 3 places
2. **Bug Risk**: Easy to update one function but forget the others
3. **Code Smell**: Violates DRY (Don't Repeat Yourself) principle
4. **Testing**: Requires duplicate test cases for identical logic

## Expected Behavior
Extract common functionality into a shared helper function that all three handlers can use.

## Affected Files
- `src/azure_functions_openapi/cli.py` (Lines 161-237)

## Proposed Solution

### Create Shared Helper Function
```python
def _write_output(
    data: Any,
    args: argparse.Namespace,
    description: str = "data"
) -> int:
    """Write data as JSON or YAML to file or stdout.
    
    Args:
        data: Data to output (must be serializable to JSON/YAML)
        args: Parsed command-line arguments containing:
            - output: Format ('json' or 'yaml')
            - file: Optional output file path
        description: Description of data for logging
        
    Returns:
        Exit code (0 for success, 1 for error)
        
    Raises:
        None - errors are logged and returned as exit code
    """
    try:
        # Format data based on output type
        if args.output == "json":
            output = json.dumps(data, indent=2)
        else:  # yaml
            output = yaml.dump(data, default_flow_style=False)
        
        # Write to file or stdout
        if args.file:
            with open(args.file, "w", encoding="utf-8") as f:
                f.write(output)
            logger.info(f"Wrote {description} to {args.file}")
        else:
            print(output)
        
        return 0
        
    except (OSError, IOError) as e:
        logger.error(f"Failed to write {description}: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error writing {description}: {e}")
        return 1
```

### Refactored Handler Functions
```python
def handle_info(args: argparse.Namespace) -> int:
    """Handle 'info' command."""
    try:
        info = get_server_info().to_dict()
        return _write_output(info, args, "server information")
    except Exception as e:
        logger.error(f"Failed to get server info: {e}")
        return 1


def handle_health(args: argparse.Namespace) -> int:
    """Handle 'health' command."""
    try:
        health = check_health()
        return _write_output(health, args, "health status")
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        return 1


def handle_metrics(args: argparse.Namespace) -> int:
    """Handle 'metrics' command."""
    try:
        metrics = get_performance_metrics()
        return _write_output(metrics, args, "performance metrics")
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return 1
```

## Benefits
- ✅ **Reduces code duplication** by ~60 lines
- ✅ **Single source of truth** for output formatting
- ✅ **Easier maintenance** - changes in one place
- ✅ **Better error handling** - centralized error messages
- ✅ **Improved testability** - test helper function once
- ✅ **Consistent behavior** across all commands

## Impact
- **User-facing**: No changes to CLI behavior
- **Internal**: Cleaner, more maintainable code
- **Testing**: Easier to test and maintain

## Additional Improvements
While refactoring, consider:
1. Add UTF-8 encoding to file writes (done in solution above)
2. Add logging for file write operations
3. Add specific error handling for file I/O
4. Improve error messages

## Test Cases
```python
def test_write_output_json_stdout(capsys):
    """Test JSON output to stdout."""
    args = argparse.Namespace(output="json", file=None)
    data = {"status": "ok", "count": 42}
    
    result = _write_output(data, args, "test data")
    
    assert result == 0
    captured = capsys.readouterr()
    assert '"status": "ok"' in captured.out
    assert '"count": 42' in captured.out


def test_write_output_yaml_file(tmp_path):
    """Test YAML output to file."""
    output_file = tmp_path / "output.yaml"
    args = argparse.Namespace(output="yaml", file=str(output_file))
    data = {"status": "ok", "count": 42}
    
    result = _write_output(data, args, "test data")
    
    assert result == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "status: ok" in content
    assert "count: 42" in content


def test_write_output_file_error(tmp_path):
    """Test error handling for file write failures."""
    # Try to write to directory (will fail)
    args = argparse.Namespace(output="json", file=str(tmp_path))
    data = {"status": "ok"}
    
    result = _write_output(data, args, "test data")
    
    assert result == 1  # Error exit code


def test_handlers_use_shared_function(mocker):
    """Test that all handlers use the shared output function."""
    mock_write = mocker.patch("azure_functions_openapi.cli._write_output")
    mock_write.return_value = 0
    
    args = argparse.Namespace(output="json", file=None)
    
    # All handlers should call _write_output
    handle_info(args)
    handle_health(args)
    handle_metrics(args)
    
    assert mock_write.call_count == 3
```

## Related Issues
- Issue #9 (Missing Type Validation) - Both improve CLI robustness

## Estimated Effort
🕐 Medium (2-3 hours including comprehensive testing)

## Labels
- refactoring
- code-quality
- technical-debt
- cli
- medium-priority
- good-first-issue
