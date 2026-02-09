# Tutorials

Step-by-step walkthroughs for common scenarios.

## Tutorial 1: Minimal HTTP Function with OpenAPI

1. Create a new Azure Functions project.
2. Add a function with `@openapi` metadata.
3. Add `/openapi.json` and `/docs` endpoints.
4. Run locally with `func start`.

## Tutorial 2: CRUD API with Pydantic Models

1. Define request/response models in Pydantic.
2. Use `request_model` and `response_model` in `@openapi`.
3. Validate and return typed responses.

## Tutorial 3: Production Readiness

1. Review performance targets in `docs/PERFORMANCE.md`.
2. Configure platform monitoring (e.g., Application Insights).
