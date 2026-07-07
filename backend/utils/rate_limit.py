from fastapi import Request
from slowapi import Limiter
from utils.settings import settings


def _rate_limit_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    ip = forwarded.split(",")[0].strip() or request.client.host if request.client else "unknown"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return f"user:{ip}"
    return f"ip:{ip}"


storage_uri = settings.redis_url or None
limiter = Limiter(key_func=_rate_limit_key, storage_uri=storage_uri)
