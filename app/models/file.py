from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.postgres import Base
from app.db.mixins import TimestampMixin, SoftDeleteMixin

class File(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="local")
    bucket: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
