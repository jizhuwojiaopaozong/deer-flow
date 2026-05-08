# 中文说明：Gateway 内部调用方的进程本地认证模块，用于同进程内的可信内部调用
"""Process-local authentication for Gateway internal callers."""

from __future__ import annotations

import secrets
from types import SimpleNamespace

from deerflow.runtime.user_context import DEFAULT_USER_ID

INTERNAL_AUTH_HEADER_NAME = "X-DeerFlow-Internal-Token"
_INTERNAL_AUTH_TOKEN = secrets.token_urlsafe(32)


# 中文说明：生成同进程 Gateway 内部调用的认证请求头
def create_internal_auth_headers() -> dict[str, str]:
    """Return headers that authenticate same-process Gateway internal calls."""
    return {INTERNAL_AUTH_HEADER_NAME: _INTERNAL_AUTH_TOKEN}


# 中文说明：验证令牌是否匹配进程本地内部令牌（使用常量时间比较防止时序攻击）
def is_valid_internal_auth_token(token: str | None) -> bool:
    """Return True when *token* matches the process-local internal token."""
    return bool(token) and secrets.compare_digest(token, _INTERNAL_AUTH_TOKEN)


# 中文说明：返回可信内部渠道调用使用的合成用户对象
def get_internal_user():
    """Return the synthetic user used for trusted internal channel calls."""
    return SimpleNamespace(id=DEFAULT_USER_ID, system_role="internal")
