from sqlalchemy import String, Integer, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.postgres import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)   # null for anonymous/system
    action: Mapped[str] = mapped_column(String(64), nullable=False)       # e.g., 'user.create'
    target_type: Mapped[str | None] = mapped_column(String(64), nullable=True)  # e.g., 'user','file'
    target_id: Mapped[str | None] = mapped_column(String(64), nullable=True)    # primary key as str
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
