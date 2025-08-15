from fastapi import APIRouter, Query, Path, Body, Depends, Request
from sqlalchemy.orm import Session
from app.deps.db import get_db
from app.deps.auth import require_permission, get_current_user
from app.schemas.user import UserCreate, UserUpdate
from app.controllers.users_controller import (
    list_users_controller,
    create_user_controller,
    get_user_controller,
    update_user_controller,
    delete_user_controller,
)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", summary="List users")
def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_users_controller(db, page=page, limit=limit)

@router.post("", summary="Create user", dependencies=[Depends(require_permission("users.write"))])
def create_user(
    payload: UserCreate = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    actor = Depends(get_current_user),
):
    return create_user_controller(db, payload, request, actor.id)

@router.get("/{user_id}", summary="Get user by id", dependencies=[Depends(require_permission("users.read"))])
def get_user(user_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return get_user_controller(db, user_id)

@router.patch("/{user_id}", summary="Update user", dependencies=[Depends(require_permission("users.write"))])
def update_user(
    user_id: int = Path(..., ge=1),
    payload: UserUpdate = Body(...),
    request: Request = None,
    db: Session = Depends(get_db),
    actor = Depends(get_current_user),
):
    return update_user_controller(db, user_id, payload, request, actor.id)

@router.delete("/{user_id}", summary="Delete user", dependencies=[Depends(require_permission("users.delete"))])
def delete_user(
    user_id: int = Path(..., ge=1),
    request: Request = None,
    db: Session = Depends(get_db),
    actor = Depends(get_current_user),
):
    return delete_user_controller(db, user_id, request, actor.id)
