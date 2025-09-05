from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Use client-supplied request_id if present, else generate new
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request.state so routes/handlers can use it
        request.state.request_id = request_id

        # Continue processing request
        response = await call_next(request)

        # Attach request_id to response headers
        response.headers["X-Request-ID"] = request_id
        return response
