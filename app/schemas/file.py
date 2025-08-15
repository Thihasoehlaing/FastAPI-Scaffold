from pydantic import BaseModel
from typing import Optional, Dict, Any

class FileOut(BaseModel):
    id: int
    original_name: str
    key: str
    content_type: str
    size_bytes: int
    provider: str
    is_public: bool

class FileUrlOut(BaseModel):
    url: str
    expires_in: Optional[int] = None

class FileDeleteOut(BaseModel):
    deleted: bool

class PresignRequest(BaseModel):
    filename: str
    content_type: str
    is_public: bool = False
    expires_in: int = 900

class PresignOut(BaseModel):
    url: str
    fields: Dict[str, Any]
    key: str
    provider: str
    expires_in: int
