# API Reference

## @openapi Decorator

This library provides an `@openapi` decorator that adds OpenAPI metadata to Azure Function routes.

### Parameters

| Name            | Type         | Description                                    |
|-----------------|--------------|------------------------------------------------|
| summary         | str          | Short summary shown in Swagger UI              |
| description     | str          | Long description in Markdown                   |
| request_model   | BaseModel    | Pydantic model for request body                |
| response_model  | BaseModel    | Pydantic model for response body               |
| tags            | List[str]    | Tags for grouping endpoints                    |
| operation_id    | str          | Unique identifier for the operation            |

Example usage:

```python
@openapi(
    summary="Create a new item",
    description="Creates a new item and returns it.",
    request_model=ItemRequest,
    response_model=ItemResponse,
    tags=["Items"]
)
```
