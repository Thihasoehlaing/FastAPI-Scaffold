from fastapi import APIRouter, UploadFile, File, Query, Path, Depends, Body, Request
from sqlalchemy.orm import Session
from app.deps.db import get_db
from app.deps.storage import get_storage
from app.deps.auth import require_permission, get_current_user
from app.controllers.files_controller import (
    upload_file_controller,
    get_file_controller,
    get_file_url_controller,
    delete_file_controller,
    presign_upload_controller,
)
from app.schemas.file import PresignRequest

router = APIRouter(prefix="/files", tags=["files"])

@router.post("", summary="Upload a file", dependencies=[Depends(require_permission("files.write"))])
async def upload_file(
    upload: UploadFile = File(...),
    is_public: bool = Query(False),
    request: Request = None,
    db: Session = Depends(get_db),
    storage = Depends(get_storage),
    actor = Depends(get_current_user),
):
    return await upload_file_controller(db, storage, upload, is_public, request, actor.id)

@router.post("/presign", summary="Create presigned upload", dependencies=[Depends(require_permission("files.write"))])
def presign_upload(payload: PresignRequest = Body(...), storage = Depends(get_storage)):
    return presign_upload_controller(storage, payload)

@router.get("/{file_id}", summary="Get file metadata", dependencies=[Depends(require_permission("files.read"))])
def get_file(file_id: int = Path(..., ge=1), db: Session = Depends(get_db)):
    return get_file_controller(db, file_id)

@router.get("/{file_id}/url", summary="Get access URL", dependencies=[Depends(require_permission("files.read"))])
def get_file_url(
    file_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    storage = Depends(get_storage),
):
    return get_file_url_controller(db, storage, file_id)

@router.delete("/{file_id}", summary="Delete file", dependencies=[Depends(require_permission("files.delete"))])
def delete_file(
    file_id: int = Path(..., ge=1),
    request: Request = None,
    db: Session = Depends(get_db),
    storage = Depends(get_storage),
    actor = Depends(get_current_user),
):
    return delete_file_controller(db, storage, file_id, request, actor.id)
