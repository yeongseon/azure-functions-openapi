# Testing Guide

This project targets **85%+ total coverage** for core modules.

## Test Structure

- `tests/`: unit and integration-oriented test modules
- `tests/performance/`: performance regression checks

## Run Tests

```bash
make test
make cov
```

## Coverage Policy

- CI runs tests on Python `3.10` to `3.14`.
- Coverage report is generated as `coverage.xml`.
- Codecov upload runs in CI for Python `3.10` jobs.

## Adding New Tests

When adding a feature:

1. Add happy-path tests.
2. Add error and validation edge cases.
3. Add regression tests for fixed bugs.
4. Keep tests isolated and deterministic.

## Performance Checks

Use `tests/performance/test_performance_regression.py` for simple performance guardrails.
