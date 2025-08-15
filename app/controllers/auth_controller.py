from sqlalchemy.orm import Session
from app.schemas.common import BaseResponse
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services import auth_service

def register_controller(db: Session, payload: RegisterRequest) -> BaseResponse:
    try:
        u = auth_service.register(db, email=payload.email, name=payload.name, password=payload.password)
        return BaseResponse(success=True, message="Registered",
                            data={"id": u.id, "email": u.email, "name": u.name})
    except ValueError as e:
        return BaseResponse(success=False, message=str(e),
                            error={"code": "USER_EXISTS", "details": {"email": payload.email}})

def login_controller(db: Session, payload: LoginRequest) -> BaseResponse:
    try:
        token = auth_service.login(db, email=payload.email, password=payload.password)
        return BaseResponse(success=True, message="Authenticated", data={"access_token": token, "token_type": "bearer"})
    except PermissionError:
        return BaseResponse(success=False, message="Invalid credentials",
                            error={"code": "INVALID_CREDENTIALS", "details": None})

def me_controller(user) -> BaseResponse:
    return BaseResponse(success=True, message="Me",
                        data={"id": user.id, "email": user.email, "name": user.name})
