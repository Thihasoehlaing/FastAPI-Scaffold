from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User

def list_users(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    q = select(User).where(User.is_deleted.is_(False)).offset(offset).limit(limit)
    items = db.execute(q).scalars().all()

    total = db.execute(select(func.count()).select_from(select(User).where(User.is_deleted.is_(False)).subquery())).scalar_one()
    return items, total

def get_by_id(db: Session, user_id: int) -> User | None:
    return db.execute(select(User).where(User.id == user_id, User.is_deleted.is_(False))).scalar_one_or_none()

def get_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email, User.is_deleted.is_(False))).scalar_one_or_none()

def create(db: Session, *, email: str, name: str, password_hash: str) -> User:
    user = User(email=email, name=name, password_hash=password_hash)
    db.add(user); db.commit(); db.refresh(user)
    return user

def update(db: Session, user: User, *, email: str | None, name: str | None) -> User:
    if email is not None: user.email = email
    if name is not None: user.name = name
    db.commit(); db.refresh(user)
    return user

def delete(db: Session, user: User) -> None:
    user.is_deleted = True
    db.commit()
