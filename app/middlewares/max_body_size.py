from starlette.types import ASGIApp, Receive, Scope, Send, Message
from starlette.responses import JSONResponse
from app.config.settings import settings

class MaxBodySizeMiddleware:
    def __init__(self, app: ASGIApp, max_bytes: int | None = None):
        self.app = app
        self.max_bytes = max_bytes or settings.MAX_UPLOAD_MB * 1024 * 1024

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        consumed = 0

        async def limited_receive() -> Message:
            nonlocal consumed
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                consumed += len(body or b"")
                if consumed > self.max_bytes:
                    resp = JSONResponse(
                        status_code=413,
                        content={
                            "success": False,
                            "message": "Payload too large",
                            "error": {"code": "FILE_TOO_LARGE", "details": {"max_mb": settings.MAX_UPLOAD_MB}},
                        },
                    )
                    await resp(scope, receive, send)
                    return {"type": "http.disconnect"}
            return message

        await self.app(scope, limited_receive, send)
