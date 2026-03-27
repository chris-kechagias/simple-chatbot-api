"""
This module defines the error handling logic for the application.
It includes custom exception handlers for our `AppException` class,
as well as a generic handler for unexpected exceptions and a specific handler for validation errors from FastAPI/Pydantic.
Each handler logs the error with relevant context and returns a standardized JSON response containing the error code,
message, timestamp, and any additional details.

"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from . import AppException, ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def create_error_response(exception: AppException) -> Dict[str, Any]:
    """Helper function to create a standardized error response from an AppException."""
    response = ErrorResponse(
        error=ErrorDetail(
            code=exception.error_code,
            message=exception.message,
            timestamp=datetime.now(timezone.utc),
            details=exception.details,
        )
    )

    return response.model_dump(mode="json")


async def app_exception_handler(request, exception: AppException):
    """Handle all custom application exceptions"""

    # Log the error with context and return JSONResponse
    logger.warning(
        f"Application error:{exception.error_code} - {exception.message}",
        extra={
            "error_code": exception.error_code,
            "status_code": exception.status_code,
            "path": request.url.path,
            "method": request.method,
            "details": exception.details,
        },
    )
    return JSONResponse(
        status_code=exception.status_code,
        content=create_error_response(exception),
    )


async def generic_exception_handler(request, exception: Exception):
    """Catch-all handler for unexpected exceptions"""

    # Log the error with context and return a generic JSONResponse
    logger.error(
        "Unexpected error",
        exc_info=exception,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            AppException(
                message="An unexpected error occurred",
                status_code=500,
                error_code="UNEXPECTED_ERROR",
            )
        ),
    )


async def validation_exception_handler(request, exception: RequestValidationError):
    """Handle Pydantic/FastAPI validation exceptions"""

    # log + return JSONResponse
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exception.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            AppException(
                message="Validation error",
                status_code=422,
                error_code="VALIDATION_ERROR",
                details={"errors": exception.errors()},
            )
        ),
    )
