from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError

from app.errors import api_error
from app.settings import get_settings

bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=4)
def signing_keys(issuer: str) -> PyJWKClient:
    # URL comes only from server settings, never from the token's jku/iss headers.
    return PyJWKClient(f"{issuer}/.well-known/jwks.json", lifespan=300, timeout=5)


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> UUID:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise api_error(401, "UNAUTHENTICATED", "Vui lòng đăng nhập để truy cập chuyến đi.")
    settings = get_settings()
    if not settings.supabase_url:
        raise api_error(503, "AUTH_NOT_CONFIGURED", "Tính năng đăng nhập chưa được cấu hình.")
    issuer = f"{str(settings.supabase_url).rstrip('/')}/auth/v1"
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        if header.get("alg") not in ("RS256", "ES256") or not header.get("kid"):
            raise jwt.InvalidTokenError("Unsupported signing key")
        key = signing_keys(issuer).get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
            issuer=issuer,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
        )
        if claims.get("role") != "authenticated" or claims.get("is_anonymous") is True:
            raise jwt.InvalidTokenError("Not an authenticated user")
        return UUID(claims["sub"])
    except PyJWKClientConnectionError as exc:
        raise api_error(503, "AUTH_UNAVAILABLE", "Chưa xác minh được phiên đăng nhập.") from exc
    except (jwt.PyJWTError, ValueError, TypeError) as exc:
        raise api_error(
            401, "INVALID_SESSION", "Phiên đăng nhập không hợp lệ hoặc đã hết hạn."
        ) from exc


UserId = Annotated[UUID, Depends(current_user)]


def current_admin(user_id: UserId) -> UUID:
    # Server-controlled allowlist; never trust user_metadata or a client-supplied role.
    if user_id not in get_settings().admin_user_ids:
        raise api_error(403, "ADMIN_REQUIRED", "Tài khoản không có quyền quản trị.")
    return user_id


AdminId = Annotated[UUID, Depends(current_admin)]
