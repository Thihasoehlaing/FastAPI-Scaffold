from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.models.user import User


def list_users(db: Session, page: int, limit: int):
    return user_repo.list_users(db, page, limit)


def create_user(db: Session, *, email: str, name: str) -> User:
    if user_repo.get_by_email(db, email):
        raise ValueError("Email already exists")
    return user_repo.create(db, email=email, name=name)


def get_user(db: Session, user_id: int) -> User | None:
    return user_repo.get_by_id(db, user_id)


def update_user(db: Session, user_id: int, *, email: str | None, name: str | None) -> User:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise LookupError("User not found")
    if email and (other := user_repo.get_by_email(db, email)) and other.id != user.id:
        raise ValueError("Email already exists")
    return user_repo.update(db, user, email=email, name=name)


def delete_user(db: Session, user_id: int) -> None:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise LookupError("User not found")
    user_repo.delete(db, user)
