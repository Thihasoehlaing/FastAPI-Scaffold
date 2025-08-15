from sqlalchemy.orm import Session
from fastapi import UploadFile, Request
from app.schemas.common import BaseResponse
from app.schemas.file import FileOut, FileUrlOut, FileDeleteOut, PresignRequest, PresignOut
from app.services import file_service
from app.services.file_service import build_object_key
from app.services.audit_service import audit

async def upload_file_controller(db: Session, storage, upload: UploadFile, is_public: bool, request: Request, actor_id: int | None) -> BaseResponse:
    try:
        rec = await file_service.upload_file(db, storage, upload, is_public=is_public)
        audit(db, request=request, user_id=actor_id, action="file.upload", target_type="file", target_id=str(rec.id),
              extra={"key": rec.key, "name": rec.original_name})
        return BaseResponse(
            success=True,
            message="File uploaded",
            data=FileOut(
                id=rec.id,
                original_name=rec.original_name,
                key=rec.key,
                content_type=rec.content_type,
                size_bytes=rec.size_bytes,
                provider=rec.provider,
                is_public=rec.is_public,
            ).model_dump()
        )
    except ValueError as e:
        if str(e) == "UNSUPPORTED_TYPE":
            return BaseResponse(success=False, message="Unsupported file type",
                                error={"code": "UNSUPPORTED_TYPE", "details": None})
        raise
    except RuntimeError as e:
        if str(e) == "FILE_TOO_LARGE":
            return BaseResponse(success=False, message="File too large",
                                error={"code": "FILE_TOO_LARGE", "details": None})
        raise

def get_file_controller(db: Session, file_id: int) -> BaseResponse:
    f = file_service.get_file(db, file_id)
    if not f:
        return BaseResponse(success=False, message="File not found",
                            error={"code": "NOT_FOUND", "details": {"id": file_id}})
    return BaseResponse(success=True, message="File",
                        data=FileOut(
                            id=f.id, original_name=f.original_name, key=f.key,
                            content_type=f.content_type, size_bytes=f.size_bytes,
                            provider=f.provider, is_public=f.is_public
                        ).model_dump())

def get_file_url_controller(db: Session, storage, file_id: int) -> BaseResponse:
    f = file_service.get_file(db, file_id)
    if not f:
        return BaseResponse(success=False, message="File not found",
                            error={"code": "NOT_FOUND", "details": {"id": file_id}})
    url = storage.url(key=f.key, is_public=f.is_public, ttl_seconds=900)
    return BaseResponse(success=True, message="URL generated", data=FileUrlOut(url=url).model_dump())

def delete_file_controller(db: Session, storage, file_id: int, request: Request, actor_id: int | None) -> BaseResponse:
    f = file_service.delete_file(db, storage, file_id)
    if not f:
        return BaseResponse(success=False, message="File not found",
                            error={"code": "NOT_FOUND", "details": {"id": file_id}})
    audit(db, request=request, user_id=actor_id, action="file.delete", target_type="file", target_id=str(file_id))
    return BaseResponse(success=True, message="File deleted", data=FileDeleteOut(deleted=True).model_dump())

def presign_upload_controller(storage, payload: PresignRequest) -> BaseResponse:
    key = build_object_key(payload.filename)
    try:
        # Prefer POST style if available (S3)
        if hasattr(storage, "presign_post"):
            data = storage.presign_post(
                key=key,
                content_type=payload.content_type,
                is_public=payload.is_public,
                expires_in=payload.expires_in,
            )
        else:
            raise AttributeError
    except AttributeError:
        # Fallback to PUT style (Azure SAS)
        if hasattr(storage, "presign_put"):
            data = storage.presign_put(
                key=key,
                content_type=payload.content_type,
                is_public=payload.is_public,
                expires_in=payload.expires_in,
            )
        else:
            return BaseResponse(
                success=False,
                message="Presign not supported for current storage driver",
                error={"code": "NOT_SUPPORTED", "details": {"driver": getattr(storage, 'provider', 'unknown')}},
            )

    out = PresignOut(
        url=data["url"],
        fields=data.get("fields", {}),
        key=key,
        provider=getattr(storage, "provider", "unknown"),
        expires_in=payload.expires_in,
    )
    return BaseResponse(success=True, message="Presign generated", data=out.model_dump())