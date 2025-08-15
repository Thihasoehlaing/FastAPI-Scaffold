from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt_tools import create_access_token
from app.models.user import User

def register(db: Session, *, email: str, name: str, password: str) -> User:
    if user_repo.get_by_email(db, email):
        raise ValueError("Email already exists")
    user = user_repo.create(db, email=email, name=name, password_hash=hash_password(password))
    return user

def login(db: Session, *, email: str, password: str) -> str:
    user = user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash) or not user.is_active:
        raise PermissionError("Invalid credentials")
    return create_access_token(sub=str(user.id))
