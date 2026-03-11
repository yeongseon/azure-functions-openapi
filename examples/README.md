# Examples

`azure-functions-openapi` ships three smoke-tested examples:

| Role | Path | Description |
| --- | --- | --- |
| Representative | `examples/hello` | Minimal HTTP trigger plus OpenAPI JSON, YAML, and Swagger UI routes. |
| Complex | `examples/todo_crud` | CRUD-style app with multiple operations, Pydantic models, and generated spec output. |
| Integration | `examples/with_validation` | Uses `@openapi` and `@validate_http` together with shared Pydantic models. |
