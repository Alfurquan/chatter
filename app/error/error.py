from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from enum import Enum

class ErrorCode(str, Enum):
    """
    Enumeration of possible error codes.
    """
    INVALID_REQUEST = "invalid_request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    CONVERSATION_CREATION_FAILED = "conversation_creation_failed"
    CONVERSATION_FETCH_FAILED = "conversation_fetch_failed"
    USER_NOT_FOUND = "user_not_found"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MESSAGE_FETCH_FAILED = "message_fetch_failed"

class ErrorResponse(BaseModel):
    """
    Error response model for structured error messages.
    """
    code: str
    message: str
    details: dict | None = None
    request_id: str | None = None

class APIException(Exception):
    """
    Custom exception class for API errors.
    Includes an error code, message, and optional details.
    """
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code

async def api_exception_handler(request: Request, exc: APIException):
    """
    Exception handler for APIException.
    Returns a structured JSON response with error details.
    """
    error = ErrorResponse(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        request_id=request.headers.get("X-Request-ID", str(uuid.uuid4()))
    )
    return JSONResponse(status_code=exc.status_code, content={"error": error.dict()})