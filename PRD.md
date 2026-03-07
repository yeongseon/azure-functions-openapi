# PRD - azure-functions-openapi

## Overview

`azure-functions-openapi` provides OpenAPI document generation and Swagger UI support for the
Azure Functions Python v2 programming model.

It is intended for decorator-based `func.FunctionApp()` applications that want lightweight API
documentation without adopting a full web framework.

## Problem Statement

Azure Functions Python applications often expose HTTP APIs without a consistent way to:

- define endpoint documentation close to handler code
- generate OpenAPI documents from that metadata
- render Swagger UI for local or hosted inspection

This leads to duplicated documentation, drift between implementation and docs, and inconsistent
developer experience across projects.

## Goals

- Provide a small decorator-first API for endpoint metadata.
- Generate OpenAPI JSON and YAML from registered handlers.
- Render Swagger UI from generated specifications.
- Stay aligned with Azure Functions Python v2 and companion libraries in this ecosystem.

## Non-Goals

- Building a full routing framework
- Replacing Azure Functions runtime concepts
- Owning request validation or response validation at runtime
- Supporting the legacy `function.json`-based Python v1 model

## Primary Users

- Maintainers of Azure Functions Python HTTP APIs
- Teams that want OpenAPI output without leaving the Azure Functions model
- Users pairing this package with `azure-functions-validation`

## Core Use Cases

- Annotate a handler with OpenAPI metadata
- Generate `/openapi.json` and `/openapi.yaml`
- Serve Swagger UI for the same application
- Produce spec artifacts via CLI or automation

## Success Criteria

- Supported examples generate valid OpenAPI output in CI
- Representative examples render correctly in Swagger UI
- Documentation and generated output stay aligned through smoke tests
