# Hello OpenAPI Example

The `hello_openapi` example demonstrates the most minimal usage of the `@openapi` decorator.

### File

- `examples/hello_openapi/function_app.py`

### Key Concepts

- One route
- No request model
- Returns a simple greeting response

### Sample

```python
@app.route(route="hello", ...)
@openapi(summary="Hello", description="Returns a greeting.", response_model=HelloResponse)
def hello(req: HttpRequest) -> HttpResponse:
    ...
```
