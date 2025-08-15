import re
import uuid
from pathlib import Path

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")

def sanitize_filename(name: str) -> str:
    name = name.replace(" ", "_")
    name = _SAFE.sub("", name)
    return name[:200] or uuid.uuid4().hex  # cap length; fallback to uuid

def build_key(original_name: str, ext_fallback: str = "") -> str:
    safe = sanitize_filename(original_name)
    # yyyy/mm/dd/uuid_safeName
    from datetime import datetime
    d = datetime.utcnow()
    ext = Path(safe).suffix or ext_fallback
    stem = Path(safe).stem[:80]
    return f"{d:%Y/%m/%d}/{uuid.uuid4().hex}_{stem}{ext}"
