from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.file import File

def create(db: Session, **kwargs) -> File:
    f = File(**kwargs); db.add(f); db.commit(); db.refresh(f); return f

def get(db: Session, file_id: int) -> File | None:
    return db.execute(select(File).where(File.id == file_id, File.is_deleted.is_(False))).scalar_one_or_none()

def delete(db: Session, f: File) -> None:
    f.is_deleted = True
    db.commit()

def list_files(db: Session, page: int, limit: int):
    offset = (page - 1) * limit
    q = select(File).where(File.is_deleted.is_(False)).offset(offset).limit(limit)
    items = db.execute(q).scalars().all()
    total = db.execute(select(func.count()).select_from(select(File).where(File.is_deleted.is_(False)).subquery())).scalar_one()
    return items, total
