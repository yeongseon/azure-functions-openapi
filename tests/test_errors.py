# tests/test_errors.py

import json
import pytest
from typing import Any
from unittest.mock import patch
from azure.functions import HttpResponse

from azure_functions_openapi.errors import (
    APIError,
    ValidationError,
    NotFoundError,
    OpenAPIError,
    ErrorCode,
    create_error_response,
    handle_exception,
    validation_error,
    not_found_error,
    openapi_error,
)


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_error_code_values(self) -> None:
        """Test that error codes have expected values."""
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"


class TestAPIError:
    """Test APIError base class."""

    def test_api_error_creation(self) -> None:
        """Test APIError creation with all parameters."""
        error = APIError(
            message="Test error",
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details={"field": "test"},
            cause=ValueError("test cause"),
        )

        assert error.message == "Test error"
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.status_code == 400
        assert error.details == {"field": "test"}
        assert str(error.cause) == "test cause"

    def test_api_error_defaults(self) -> None:
        """Test APIError with default parameters."""
        error = APIError(message="Test error", error_code=ErrorCode.INTERNAL_ERROR)

        assert error.message == "Test error"
        assert error.error_code == ErrorCode.INTERNAL_ERROR
        assert error.status_code == 500
        assert error.details == {}
        assert error.cause is None


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_creation(self) -> None:
        """Test ValidationError creation."""
        error = ValidationError(
            message="Validation failed", details={"field": "test"}, cause=ValueError("test")
        )

        assert error.message == "Validation failed"
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.status_code == 400
        assert error.details == {"field": "test"}

    def test_validation_error_defaults(self) -> None:
        """Test ValidationError with defaults."""
        error = ValidationError()

        assert error.message == "Validation failed"
        assert error.error_code == ErrorCode.VALIDATION_ERROR
        assert error.status_code == 400


class TestNotFoundError:
    """Test NotFoundError class."""

    def test_not_found_error_creation(self) -> None:
        """Test NotFoundError creation."""
        error = NotFoundError(
            message="Resource not found", details={"resource": "test"}, cause=KeyError("test")
        )

        assert error.message == "Resource not found"
        assert error.error_code == ErrorCode.NOT_FOUND
        assert error.status_code == 404
        assert error.details == {"resource": "test"}

    def test_not_found_error_defaults(self) -> None:
        """Test NotFoundError with defaults."""
        error = NotFoundError()

        assert error.message == "Resource not found"
        assert error.error_code == ErrorCode.NOT_FOUND
        assert error.status_code == 404


class TestOpenAPIError:
    """Test OpenAPIError class."""

    def test_openapi_error_creation(self) -> None:
        """Test OpenAPIError creation."""
        error = OpenAPIError(
            message="OpenAPI generation failed",
            details={"operation": "test"},
            cause=RuntimeError("test"),
        )

        assert error.message == "OpenAPI generation failed"
        assert error.error_code == ErrorCode.OPENAPI_GENERATION_ERROR
        assert error.status_code == 500
        assert error.details == {"operation": "test"}

    def test_openapi_error_defaults(self) -> None:
        """Test OpenAPIError with defaults."""
        error = OpenAPIError()

        assert error.message == "OpenAPI generation failed"
        assert error.error_code == ErrorCode.OPENAPI_GENERATION_ERROR
        assert error.status_code == 500


class TestCreateErrorResponse:
    """Test create_error_response function."""

    def test_create_error_response_basic(self) -> None:
        """Test basic error response creation."""
        error = ValidationError("Test error", details={"field": "test"})
        response = create_error_response(error)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 400
        assert response.mimetype == "application/json"

        # Parse response body
        body = json.loads(response.get_body().decode())
        assert body["error"]["code"] == "VALIDATION_ERROR"
        assert body["error"]["message"] == "Test error"
        assert body["error"]["status_code"] == 400
        assert body["error"]["details"] == {"field": "test"}
        assert "timestamp" in body
        assert "request_id" in body

    def test_create_error_response_with_stack_trace(self) -> None:
        """Test error response with stack trace."""
        error = ValidationError("Test error", cause=ValueError("test cause"))
        response = create_error_response(error, include_stack_trace=True)

        body = json.loads(response.get_body().decode())
        assert "stack_trace" in body["error"]
        assert body["error"]["stack_trace"] == "test cause"

    def test_create_error_response_headers(self) -> None:
        """Test error response headers."""
        error = ValidationError("Test error")
        response = create_error_response(error)

        assert "X-Error-Code" in response.headers
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Error-Code"] == "VALIDATION_ERROR"


class TestHandleException:
    """Test handle_exception function."""

    def test_handle_api_error(self) -> None:
        """Test handling of APIError."""
        error = ValidationError("Test error")
        response = handle_exception(error)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 400

    def test_handle_generic_exception(self) -> None:
        """Test handling of generic exception."""
        error = ValueError("Test error")
        response = handle_exception(error)

        assert isinstance(response, HttpResponse)
        assert response.status_code == 500

        body = json.loads(response.get_body().decode())
        assert body["error"]["code"] == "INTERNAL_ERROR"
        assert "original_error" in body["error"]["details"]


class TestConvenienceFunctions:
    """Test convenience error creation functions."""

    def test_validation_error_function(self) -> None:
        """Test validation_error convenience function."""
        error = validation_error("Field is required", field="name", value="")

        assert isinstance(error, ValidationError)
        assert error.message == "Field is required"
        assert error.details["field"] == "name"
        assert error.details["value"] == ""

    def test_not_found_error_function(self) -> None:
        """Test not_found_error convenience function."""
        error = not_found_error("User", "123")

        assert isinstance(error, NotFoundError)
        assert error.message == "User not found (ID: 123)"
        assert error.details["resource_type"] == "User"
        assert error.details["resource_id"] == "123"

    def test_not_found_error_function_no_id(self) -> None:
        """Test not_found_error without resource ID."""
        error = not_found_error("User")

        assert isinstance(error, NotFoundError)
        assert error.message == "User not found"
        assert error.details["resource_type"] == "User"
        assert "resource_id" not in error.details

    def test_openapi_error_function(self) -> None:
        """Test openapi_error convenience function."""
        cause = RuntimeError("test cause")
        error = openapi_error("Generation failed", operation="test_op", cause=cause)

        assert isinstance(error, OpenAPIError)
        assert error.message == "Generation failed"
        assert error.details["operation"] == "test_op"
        assert error.cause == cause


@patch("azure_functions_openapi.errors.logger")
class TestLogging:
    """Test logging functionality."""

    def test_create_error_response_logging(self, mock_logger: Any) -> None:
        """Test that create_error_response logs errors."""
        error = ValidationError("Test error")
        create_error_response(error)

        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "API Error: VALIDATION_ERROR - Test error" in call_args[0][0]

    def test_handle_exception_logging(self, mock_logger: Any) -> None:
        """Test that handle_exception logs unexpected errors."""
        error = ValueError("Test error")
        handle_exception(error)

        mock_logger.error.assert_called()
        # Should log the original error and the conversion
        assert mock_logger.error.call_count >= 1
