# Custom OpenAPI Schema Example

Shows how to customize schemas using Pydantic models.

## Key Concepts

- Pydantic request/response models
- Schema defaults and field metadata

## Sample

```python
from pydantic import BaseModel, Field

class CreateTodoRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Todo title")
    priority: int = Field(1, ge=1, le=5, description="Priority from 1 to 5")


class CreateTodoResponse(BaseModel):
    id: str
    title: str
    priority: int
```

## Notes

- Field metadata is included in generated schemas.
- Use `Field` to enforce validation constraints.
