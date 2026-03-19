# Standard Library Imports
import logging
from datetime import datetime, timezone
from typing import Any, Dict

# Third-Party Imports
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Local/First-Party Imports
from ..utils.errors import AppException

logger = logging.getLogger(__name__)


def create_error_response(exception: AppException) -> Dict[str, Any]:
    """Helper function to create a standardized error response from an AppException."""
    response = {
        "success": False,
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }

    if exception.details:
        response["error"]["details"] = exception.details

    return response


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
