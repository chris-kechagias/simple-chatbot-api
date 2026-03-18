"""
Custom exceptions for the application,
providing structured error information for API responses.
Each exception includes a message, HTTP status code, error code, and optional details.

"""

# Standard Library Imports
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

# Third-Party Imports
from pydantic import BaseModel


class AppException(Exception):
    """Base exception for all application errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ConversationNotFoundException(AppException):
    def __init__(self, conversation_id: UUID):
        super().__init__(
            message=f"Conversation with ID {conversation_id} not found",
            status_code=404,
            error_code="CONVERSATION_NOT_FOUND",
        )
        self.conversation_id = conversation_id


class MessageNotFoundException(AppException):
    def __init__(self, message_id: UUID):
        super().__init__(
            message=f"Message with ID {message_id} not found",
            status_code=404,
            error_code="MESSAGE_NOT_FOUND",
        )
        self.message_id = message_id


class OpenAIServiceException(AppException):
    def __init__(
        self,
        message: str = "Error communicating with OpenAI service",
        status_code: int = 502,
        error_code: str = "OPENAI_SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details,
        )


class DatabaseException(AppException):
    def __init__(
        self, message: str = "Database error", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ErrorDetail(BaseModel):
    code: str
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
