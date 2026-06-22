"""LangGraph compatibility auth handler — shares JWT logic with Gateway.

The default DeerFlow runtime is embedded in the FastAPI Gateway; scripts and
Docker deployments do not load this module.  It is retained for LangGraph
tooling, Studio, or direct LangGraph Server compatibility through
``langgraph.json``'s ``auth.path``.

When that compatibility path is used, this module reuses the same JWT and CSRF
rules as Gateway so both modes validate sessions consistently.

Two layers:
  1. @auth.authenticate — validates JWT cookie, extracts user_id,
     and enforces CSRF on state-changing methods (POST/PUT/DELETE/PATCH)
  2. @auth.on — returns metadata filter so each user only sees own threads
"""

import secrets

from langgraph_sdk import Auth

from app.gateway.auth.errors import TokenError
from app.gateway.auth.jwt import decode_token
from app.gateway.auth_disabled import AUTH_DISABLED_USER_ID, is_auth_disabled
from app.gateway.deps import get_local_provider

auth = Auth()

# Methods that require CSRF validation (state-changing per RFC 7231).
_CSRF_METHODS = frozenset({"POST", "PUT", "DELETE", "PATCH"})


# 中文说明：对状态变更请求执行双重提交 Cookie CSRF 检查，与 Gateway 的 CSRFMiddleware 逻辑一致
def _check_csrf(request) -> None:
    """Enforce Double Submit Cookie CSRF check for state-changing requests.

    Mirrors Gateway's CSRFMiddleware logic so that LangGraph routes
    proxied directly by nginx have the same CSRF protection.
    """
    method = getattr(request, "method", "") or ""
    if method.upper() not in _CSRF_METHODS:
        return

    if is_auth_disabled():
        return

    cookie_token = request.cookies.get("csrf_token")
    header_token = request.headers.get("x-csrf-token")

    if not cookie_token or not header_token:
        raise Auth.exceptions.HTTPException(
            status_code=403,
            detail="CSRF token missing. Include X-CSRF-Token header.",
        )

    if not secrets.compare_digest(cookie_token, header_token):
        raise Auth.exceptions.HTTPException(
            status_code=403,
            detail="CSRF token mismatch.",
        )


# 中文说明：验证会话 Cookie、解码 JWT、校验 token_version，同时执行 CSRF 检查
@auth.authenticate
async def authenticate(request):
    """Validate the session cookie, decode JWT, and check token_version.

    Same validation chain as Gateway's get_current_user_from_request:
      cookie → decode JWT → DB lookup → token_version match
    Also enforces CSRF on state-changing methods.
    """
    # CSRF check before authentication so forged cross-site requests
    # are rejected early, even if the cookie carries a valid JWT.
    _check_csrf(request)

    if is_auth_disabled():
        return AUTH_DISABLED_USER_ID

    token = request.cookies.get("access_token")
    if not token:
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    payload = decode_token(token)
    if isinstance(payload, TokenError):
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = await get_local_provider().get_user(payload.sub)
    if user is None:
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail="User not found",
        )
    if user.token_version != payload.ver:
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail="Token revoked (password changed)",
        )

    return payload.sub


# 中文说明：写入时注入 user_id 元数据，读取时按 user_id 过滤，确保用户数据隔离
@auth.on
async def add_owner_filter(ctx: Auth.types.AuthContext, value: dict):
    """Inject user_id metadata on writes; filter by user_id on reads.

    Gateway stores thread ownership as ``metadata.user_id``.
    This handler ensures LangGraph Server enforces the same isolation.
    """
    # On create/update: stamp user_id into metadata
    metadata = value.setdefault("metadata", {})
    metadata["user_id"] = ctx.user.identity

    # Return filter dict — LangGraph applies it to search/read/delete
    return {"user_id": ctx.user.identity}
