# Maintenance Guide

This document outlines scheduled maintenance tasks and automation points.

## Scheduled Automation

- Dependency updates: Dependabot (weekly)
- Stale issues and branches: `stale.yml` (daily)
- Maintenance checks: `maintenance.yml` (weekly)

## Manual Tasks

- Run formatting and linting: `make lint`
- Update changelog: `make changelog`
- Review deprecated APIs and remove them on major releases

## Documentation from Docstrings

If you add public APIs, include clear docstrings. The docs build can be extended to
extract API docs via MkDocs plugins if needed.

## Health Checks

Use your platform observability tooling (e.g., Azure Monitor/Application Insights)
to validate production readiness and health.
