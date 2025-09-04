# src/azure_functions_openapi/errors.py

from enum import Enum
import logging
from typing import Any, Dict, Optional

from azure.functions import HttpResponse

logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standard error codes for API responses."""

    # Validation errors (400-499)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"

    # Authentication/Authorization errors (401-403)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"  # nosec B105

    # Not found errors (404)
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"

    # Server errors (500-599)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"

    # OpenAPI specific errors
    OPENAPI_GENERATION_ERROR = "OPENAPI_GENERATION_ERROR"
    INVALID_OPERATION_ID = "INVALID_OPERATION_ID"
    INVALID_ROUTE_PATH = "INVALID_ROUTE_PATH"


class APIError(Exception):
    """Base exception class for API errors."""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.cause = cause
        super().__init__(self.message)


class ValidationError(APIError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=details,
            cause=cause,
        )


class NotFoundError(APIError):
    """Raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details,
            cause=cause,
        )


class OpenAPIError(APIError):
    """Raised when OpenAPI generation fails."""

    def __init__(
        self,
        message: str = "OpenAPI generation failed",
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.OPENAPI_GENERATION_ERROR,
            status_code=500,
            details=details,
            cause=cause,
        )


def create_error_response(error: APIError, include_stack_trace: bool = False) -> HttpResponse:
    """
    Create a standardized error response.

    Parameters:
        error: The APIError instance
        include_stack_trace: Whether to include stack trace in response (for debugging)

    Returns:
        HttpResponse with error details
    """
    error_response = {
        "error": {
            "code": error.error_code.value,
            "message": error.message,
            "status_code": error.status_code,
            "details": error.details,
        },
        "timestamp": _get_timestamp(),
        "request_id": _generate_request_id(),
    }

    # Include stack trace in development/debugging mode
    if include_stack_trace and error.cause:
        error_response["error"]["stack_trace"] = str(error.cause)  # type: ignore

    # Log the error
    logger.error(
        f"API Error: {error.error_code.value} - {error.message}",
        extra={
            "error_code": error.error_code.value,
            "status_code": error.status_code,
            "details": error.details,
            "cause": str(error.cause) if error.cause else None,
        },
    )

    return HttpResponse(
        body=_serialize_error_response(error_response),
        status_code=error.status_code,
        mimetype="application/json",
        headers={
            "Content-Type": "application/json",
            "X-Error-Code": error.error_code.value,
            "X-Request-ID": error_response["request_id"],
        },
    )


def handle_exception(exception: Exception, include_stack_trace: bool = False) -> HttpResponse:
    """
    Handle unexpected exceptions and convert them to standardized error responses.

    Parameters:
        exception: The exception to handle
        include_stack_trace: Whether to include stack trace in response

    Returns:
        HttpResponse with error details
    """
    if isinstance(exception, APIError):
        return create_error_response(exception, include_stack_trace)

    # Convert unexpected exceptions to internal server errors
    api_error = APIError(
        message="An unexpected error occurred",
        error_code=ErrorCode.INTERNAL_ERROR,
        status_code=500,
        details={"original_error": str(exception)},
        cause=exception,
    )

    return create_error_response(api_error, include_stack_trace)


def _serialize_error_response(error_response: Dict[str, Any]) -> str:
    """Serialize error response to JSON string."""
    import json

    return json.dumps(error_response, indent=2, ensure_ascii=False)


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_request_id() -> str:
    """Generate a unique request ID."""
    import uuid

    return str(uuid.uuid4())


# Convenience functions for common error scenarios
def validation_error(
    message: str, field: Optional[str] = None, value: Optional[Any] = None
) -> ValidationError:
    """Create a validation error with field-specific details."""
    details = {}
    if field:
        details["field"] = field
    if value is not None:
        details["value"] = str(value)

    return ValidationError(message=message, details=details)


def not_found_error(resource_type: str, resource_id: Optional[str] = None) -> NotFoundError:
    """Create a not found error with resource details."""
    details = {"resource_type": resource_type}
    if resource_id:
        details["resource_id"] = resource_id

    message = f"{resource_type} not found"
    if resource_id:
        message += f" (ID: {resource_id})"

    return NotFoundError(message=message, details=details)


def openapi_error(
    message: str, operation: Optional[str] = None, cause: Optional[Exception] = None
) -> OpenAPIError:
    """Create an OpenAPI generation error."""
    details = {}
    if operation:
        details["operation"] = operation

    return OpenAPIError(message=message, details=details, cause=cause)
