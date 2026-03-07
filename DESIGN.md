# DESIGN.md

Design Principles for `azure-functions-openapi`

## Purpose

This document defines the architectural boundaries and design principles of the project.

## Design Goals

- Generate OpenAPI documents for Azure Functions Python v2 handlers.
- Keep the decorator model explicit and predictable.
- Preserve Azure Functions runtime behavior instead of abstracting it away.
- Provide Swagger UI and CLI tooling without turning the package into a framework.

## Non-Goals

This project does not aim to:

- Replace Azure Functions routing or hosting behavior
- Hide the `func.FunctionApp()` programming model
- Become a general web framework
- Own deployment, infrastructure, or application lifecycle concerns

## Design Principles

- Explicit metadata is preferred over magic inference.
- Decorators should collect metadata, not change core handler semantics.
- OpenAPI generation and UI rendering should remain separate concerns.
- Public APIs should evolve conservatively.
- Example applications should demonstrate supported patterns, not internal shortcuts.

## Integration Boundaries

- Runtime validation belongs to `azure-functions-validation`.
- Diagnostics belong to `azure-functions-doctor`.
- This repository owns OpenAPI metadata capture, document generation, and documentation UI helpers.

## Compatibility Policy

- Minimum supported Python version: `3.10`
- Supported runtime target: Azure Functions Python v2 programming model
- Public APIs follow semantic versioning expectations

## Change Discipline

- Changes to decorator behavior require strong regression coverage.
- Changes to generated spec defaults must be treated as user-facing behavior changes.
- Experimental APIs must be clearly labeled in code and docs.
