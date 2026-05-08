# 中文说明：Token 使用量追踪配置
from pydantic import BaseModel, Field


# 中文说明：Token 使用量配置类，控制是否启用使用量追踪中间件
class TokenUsageConfig(BaseModel):
    """Configuration for token usage tracking."""

    enabled: bool = Field(default=False, description="Enable token usage tracking middleware")
