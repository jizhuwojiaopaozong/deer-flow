# 中文说明：认证提供者抽象基类，定义认证和用户查询的接口
"""Auth provider abstraction."""

from abc import ABC, abstractmethod


# 中文说明：认证提供者抽象基类
class AuthProvider(ABC):
    """Abstract base class for authentication providers."""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> "User | None":
        """Authenticate user with given credentials.

        Returns User if authentication succeeds, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: str) -> "User | None":
        """Retrieve user by ID."""
        raise NotImplementedError


# Import User at runtime to avoid circular imports
from app.gateway.auth.models import User  # noqa: E402
