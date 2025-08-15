import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        # Attach to state for logs/controllers
        request.state.request_id = req_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = req_id
        return response
