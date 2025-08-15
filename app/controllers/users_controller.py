import math
from sqlalchemy.orm import Session
from fastapi import Request
from app.schemas.common import BaseResponse, Pagination
from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service
from app.services.audit_service import audit

def list_users_controller(db: Session, page: int, limit: int) -> BaseResponse:
    items, total = user_service.list_users(db, page, limit)
    pages = math.ceil(total / limit) if limit else 1
    data = [{"id": u.id, "email": u.email, "name": u.name} for u in items]
    return BaseResponse(success=True, message="Users fetched",
                        data=data, pagination=Pagination(page=page, limit=limit, total=total, pages=pages))

def create_user_controller(db: Session, payload: UserCreate, request: Request, actor_id: int | None) -> BaseResponse:
    try:
        u = user_service.create_user(db, email=payload.email, name=payload.name)
        audit(db, request=request, user_id=actor_id, action="user.create", target_type="user", target_id=str(u.id))
        return BaseResponse(success=True, message="User created",
                            data={"id": u.id, "email": u.email, "name": u.name})
    except ValueError as e:
        return BaseResponse(success=False, message=str(e),
                            error={"code": "USER_EXISTS", "details": {"email": payload.email}})

def get_user_controller(db: Session, user_id: int) -> BaseResponse:
    u = user_service.get_user(db, user_id)
    if not u:
        return BaseResponse(success=False, message="User not found",
                            error={"code": "NOT_FOUND", "details": {"id": user_id}})
    return BaseResponse(success=True, message="User fetched",
                        data={"id": u.id, "email": u.email, "name": u.name})

def update_user_controller(db: Session, user_id: int, payload: UserUpdate, request: Request, actor_id: int | None) -> BaseResponse:
    try:
        u = user_service.update_user(db, user_id, email=payload.email, name=payload.name)
        audit(db, request=request, user_id=actor_id, action="user.update", target_type="user", target_id=str(u.id))
        return BaseResponse(success=True, message="User updated",
                            data={"id": u.id, "email": u.email, "name": u.name})
    except LookupError:
        return BaseResponse(success=False, message="User not found",
                            error={"code": "NOT_FOUND", "details": {"id": user_id}})
    except ValueError as e:
        return BaseResponse(success=False, message=str(e),
                            error={"code": "USER_EXISTS", "details": {"email": payload.email}})

def delete_user_controller(db: Session, user_id: int, request: Request, actor_id: int | None) -> BaseResponse:
    try:
        user_service.delete_user(db, user_id)
        audit(db, request=request, user_id=actor_id, action="user.delete", target_type="user", target_id=str(user_id))
        return BaseResponse(success=True, message="User deleted")
    except LookupError:
        return BaseResponse(success=False, message="User not found",
                            error={"code": "NOT_FOUND", "details": {"id": user_id}})
