import mimetypes
from typing import Iterable

def guess_mime(filename: str, default: str = "application/octet-stream") -> str:
    mt, _ = mimetypes.guess_type(filename)
    return mt or default

def parse_allowed_mime(csv: str) -> list[str]:
    return [x.strip().lower() for x in csv.split(",") if x.strip()]

def is_mime_allowed(candidate: str, allowed: Iterable[str]) -> bool:
    c = (candidate or "").lower()
    return any(
        c == a or (a.endswith("/*") and c.startswith(a.split("/")[0] + "/"))
        for a in allowed
    )
