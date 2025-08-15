import os
from pathlib import Path
from typing import BinaryIO
from app.config.settings import settings

class LocalStorage:
    provider = "local"

    def __init__(self, base_dir: str | None = None, max_bytes: int | None = None):
        self.base_dir = Path(base_dir or settings.LOCAL_UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_bytes = max_bytes or settings.MAX_UPLOAD_MB * 1024 * 1024

    async def upload(self, *, key: str, body: BinaryIO, content_type: str) -> None:
        path = self.base_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        total = 0
        with open(path, "wb") as f:
            while True:
                chunk = body.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > self.max_bytes:
                    # cleanup partial file
                    try:
                        f.close()
                        path.unlink(missing_ok=True)
                    finally:
                        raise RuntimeError("FILE_TOO_LARGE")
                f.write(chunk)

    async def delete(self, *, key: str) -> None:
        path = self.base_dir / key
        if path.exists():
            path.unlink(missing_ok=True)

    def url(self, *, key: str, is_public: bool = False, ttl_seconds: int = 900) -> str:
        base = settings.PUBLIC_BASE_URL.rstrip("/")
        return f"{base}/{key}"
