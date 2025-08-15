from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def write_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    request_id: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    extra: dict | None = None,
) -> AuditLog:
    row = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        request_id=request_id,
        ip=ip,
        user_agent=user_agent,
        extra=extra or None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
