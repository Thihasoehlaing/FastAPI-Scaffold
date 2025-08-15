from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError

from app.schemas.common import BaseResponse


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except ValidationError as ve:
            return JSONResponse(
                status_code=422,
                content=BaseResponse(
                    success=False,
                    message="Validation error",
                    error={"code": "VALIDATION_ERROR", "details": ve.errors()},
                ).model_dump(),
            )

        except PermissionError as pe:
            return JSONResponse(
                status_code=403,
                content=BaseResponse(
                    success=False,
                    message=str(pe) or "Forbidden",
                    error={"code": "FORBIDDEN", "details": None},
                ).model_dump(),
            )

        except KeyError as ke:
            return JSONResponse(
                status_code=400,
                content=BaseResponse(
                    success=False,
                    message=f"Missing key: {ke}",
                    error={"code": "BAD_REQUEST", "details": {"key": str(ke)}},
                ).model_dump(),
            )

        except Exception as e:
            # Last-resort handler; avoid leaking internals
            return JSONResponse(
                status_code=500,
                content=BaseResponse(
                    success=False,
                    message="Internal server error",
                    error={"code": "INTERNAL_ERROR", "details": None},
                ).model_dump(),
            )
