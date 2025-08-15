from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
