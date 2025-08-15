from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.controllers.auth_controller import register_controller, login_controller, me_controller
from app.schemas.auth import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", summary="Register")
def register(payload: RegisterRequest = Body(...), db: Session = Depends(get_db)):
    return register_controller(db, payload)

@router.post("/login", summary="Login")
def login(payload: LoginRequest = Body(...), db: Session = Depends(get_db)):
    return login_controller(db, payload)

@router.get("/me", summary="Current user")
def me(user = Depends(get_current_user)):
    return me_controller(user)
