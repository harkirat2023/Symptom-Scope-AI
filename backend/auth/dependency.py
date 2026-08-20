import logging
import time

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils.settings import settings

logger = logging.getLogger("symptomscope.auth")

security = HTTPBearer(auto_error=False)

JWKS_CACHE: dict[str, tuple[float, list[dict]]] = {}
JWKS_CACHE_TTL: int = 3600


async def _fetch_jwks_keys(jwks_url: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(jwks_url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("keys", [])


async def _get_jwks_client() -> list[dict]:
    jwks_url = settings.clerk_jwks_url
    issuer = settings.clerk_issuer
    if not jwks_url and issuer:
        jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    if not jwks_url:
        return []
    now = time.time()
    cached = JWKS_CACHE.get(jwks_url)
    if cached and (now - cached[0]) < JWKS_CACHE_TTL:
        return cached[1]
    try:
        keys = await _fetch_jwks_keys(jwks_url)
        JWKS_CACHE[jwks_url] = (now, keys)
        return keys
    except Exception as exc:
        logger.warning("Clerk JWKS fetch failed (%s) — falling back to dev auth", exc)
        return []


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None and settings.dev_mode:
        return "dev-user-id"
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    token = credentials.credentials
    jwks_keys = await _get_jwks_client()
    if not jwks_keys:
        if settings.dev_mode:
            return "dev-user-id"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWKS configuration missing",
        )
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing kid",
        )
    signing_key = None
    for key in jwks_keys:
        if key.get("kid") == kid:
            signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
            break
    if signing_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: key not found",
        )
    issuer = settings.clerk_issuer
    try:
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_exp": True, "require": ["exp"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
        )
    return user_id
