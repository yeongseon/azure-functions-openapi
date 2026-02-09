# Architecture Guide

This document provides an overview of the azure-functions-openapi library architecture, design decisions, and internal components.

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Functions App                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                                        │
│  │   @openapi      │                                        │
│  │   Decorator     │                                        │
│  └─────────────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              OpenAPI Registry                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              OpenAPI Generation                         │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │   JSON      │  │   YAML      │  │   Swagger UI    │ │ │
│  │  │   Spec      │  │   Spec      │  │   Rendering     │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Decorator System (`decorator.py`)

The `@openapi` decorator is the heart of the system:

```python
@openapi(
    summary="API endpoint",
    description="Detailed description",
    tags=["API"],
    request_model=RequestModel,
    response_model=ResponseModel
)
def my_function(req: func.HttpRequest) -> func.HttpResponse:
    # Function implementation
```

**Key Features:**
- **Metadata Collection**: Stores OpenAPI metadata in a global registry
- **Input Validation**: Validates and sanitizes all decorator parameters
- **Type Safety**: Full type hints and validation

### 2. OpenAPI Generation (`openapi.py`)

Converts registered metadata into OpenAPI 3.0 specifications:

```python
# Generate OpenAPI spec
spec = generate_openapi_spec(title="My API", version="1.0.0")

# Get JSON/YAML formats
json_spec = get_openapi_json()
yaml_spec = get_openapi_yaml()
```

**Key Features:**
- **Schema Generation**: Automatic Pydantic model to JSON Schema conversion
- **Error Resilience**: Graceful handling of schema generation failures
- **Validation**: Comprehensive input validation

### 3. Swagger UI (`swagger_ui.py`)

Renders interactive API documentation:

```python
# Render Swagger UI with enhanced security
response = render_swagger_ui(
    title="API Documentation",
    openapi_url="/api/openapi.json",
    custom_csp="custom-csp-policy"
)
```

**Key Features:**
- **Security Headers**: CSP, X-Frame-Options, X-XSS-Protection
- **Input Sanitization**: XSS protection and content validation
- **Customization**: Configurable CSP policies and UI options

### 4. Operational Concerns

This library focuses on OpenAPI generation and documentation rendering.

## 🔄 Data Flow

### 1. Function Registration

```
Function Definition → @openapi Decorator → Metadata Validation → Registry Storage
```

### 2. OpenAPI Generation

```
Registry → Schema Generation → JSON/YAML Output
```

### 3. Swagger UI Rendering

```
Request → Security Validation → HTML Generation → Security Headers → Response
```

## 🛡️ Security Architecture

### Input Validation Pipeline

```
User Input → Sanitization → Validation → Processing → Response
```

### Security Headers

- **CSP**: Content Security Policy for XSS protection
- **X-Frame-Options**: Clickjacking protection
- **X-XSS-Protection**: XSS filtering
- **X-Content-Type-Options**: MIME type sniffing protection

## 🔧 Extension Points

## 🚀 Deployment Architecture

### Azure Functions Integration

```
Azure Functions Runtime → Function App → OpenAPI Routes → Documentation
```
