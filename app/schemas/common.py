from pydantic import BaseModel
from typing import Any, Optional


class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class ErrorObj(BaseModel):
    code: str
    details: Any | None = None


class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Any | None = None
    pagination: Optional[Pagination] = None
    error: Optional[ErrorObj] = None
