from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.repositories import file_repo
from app.utils.filename import build_key
from app.utils.mime import guess_mime, parse_allowed_mime, is_mime_allowed
from app.config.settings import settings

async def upload_file(db: Session, storage, file: UploadFile, *, is_public: bool = False):
    allowed = parse_allowed_mime(settings.ALLOWED_MIME)
    header_ct = (file.content_type or "").lower()
    name_ct = guess_mime(file.filename)

    # MIME guard: header must be allowed OR filename-guess allowed
    if not (is_mime_allowed(header_ct, allowed) or is_mime_allowed(name_ct, allowed)):
        raise ValueError("UNSUPPORTED_TYPE")

    key = build_key(file.filename, ext_fallback="")
    content_type = header_ct or name_ct

    # stream & size guard handled by storage; may raise RuntimeError("FILE_TOO_LARGE")
    await storage.upload(key=key, body=file.file, content_type=content_type)

    rec = file_repo.create(
        db,
        original_name=file.filename,
        key=key,
        provider=storage.provider,
        bucket=None,
        content_type=content_type,
        size_bytes=0,     # set 0; measure separately if you need exact size
        checksum=None,
        is_public=is_public,
    )
    return rec

def get_file(db: Session, file_id: int):
    return file_repo.get(db, file_id)

def delete_file(db: Session, storage, file_id: int):
    f = file_repo.get(db, file_id)
    if not f:
        return None
    # delete from storage first
    import anyio
    anyio.run(storage.delete, key=f.key)  # run async from sync context
    file_repo.delete(db, f)
    return f

def build_object_key(filename: str) -> str:
    return build_key(filename, ext_fallback="")