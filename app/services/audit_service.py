from sqlalchemy.orm import Session
from fastapi import Request
from app.repositories.audit_repo import write_log

def audit(
    db: Session,
    *,
    request: Request | None,
    user_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    extra: dict | None = None,
):
    req_id = getattr(getattr(request, "state", None), "request_id", None) if request else None
    ip = None
    ua = None
    if request:
        ip = request.headers.get("x-forwarded-for") or request.client.host if request.client else None
        ua = request.headers.get("user-agent")
    return write_log(
        db,
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        request_id=req_id,
        ip=ip,
        user_agent=ua,
        extra=extra,
    )
