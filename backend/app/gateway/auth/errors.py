# 中文说明：认证模块的类型化错误定义，包含错误码枚举、令牌错误枚举和结构化错误响应
"""Typed error definitions for auth module.

AuthErrorCode: exhaustive enum of all auth failure conditions.
TokenError: exhaustive enum of JWT decode failures.
AuthErrorResponse: structured error payload for HTTP responses.
"""

from enum import StrEnum

from pydantic import BaseModel


# 中文说明：认证错误码枚举，穷举所有认证失败条件
class AuthErrorCode(StrEnum):
    """Exhaustive list of auth error conditions."""

    INVALID_CREDENTIALS = "invalid_credentials"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    USER_NOT_FOUND = "user_not_found"
    EMAIL_ALREADY_EXISTS = "email_already_exists"
    PROVIDER_NOT_FOUND = "provider_not_found"
    NOT_AUTHENTICATED = "not_authenticated"
    SYSTEM_ALREADY_INITIALIZED = "system_already_initialized"


# 中文说明：JWT 解码失败原因枚举
class TokenError(StrEnum):
    """Exhaustive list of JWT decode failure reasons."""

    EXPIRED = "expired"
    INVALID_SIGNATURE = "invalid_signature"
    MALFORMED = "malformed"


# 中文说明：结构化错误响应模型，替代裸字符串 detail
class AuthErrorResponse(BaseModel):
    """Structured error response — replaces bare `detail` strings."""

    code: AuthErrorCode
    message: str


# 中文说明：将 TokenError 映射到 AuthErrorCode 的单一真相来源
def token_error_to_code(err: TokenError) -> AuthErrorCode:
    """Map TokenError to AuthErrorCode — single source of truth."""
    if err == TokenError.EXPIRED:
        return AuthErrorCode.TOKEN_EXPIRED
    return AuthErrorCode.TOKEN_INVALID
