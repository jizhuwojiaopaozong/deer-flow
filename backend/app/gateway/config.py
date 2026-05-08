# 中文说明：Gateway 配置模块，定义 API 网关的主机、端口、CORS 等配置项
import os

from pydantic import BaseModel, Field


# 中文说明：API 网关配置模型，包含主机地址、端口、CORS 来源、文档开关等字段
class GatewayConfig(BaseModel):
    """Configuration for the API Gateway."""

    host: str = Field(default="0.0.0.0", description="Host to bind the gateway server")
    port: int = Field(default=8001, description="Port to bind the gateway server")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"], description="Allowed CORS origins")
    enable_docs: bool = Field(default=True, description="Enable Swagger/ReDoc/OpenAPI endpoints")


_gateway_config: GatewayConfig | None = None


# 中文说明：获取全局网关配置单例，首次调用时从环境变量加载
def get_gateway_config() -> GatewayConfig:
    """Get gateway config, loading from environment if available."""
    global _gateway_config
    if _gateway_config is None:
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        _gateway_config = GatewayConfig(
            host=os.getenv("GATEWAY_HOST", "0.0.0.0"),
            port=int(os.getenv("GATEWAY_PORT", "8001")),
            cors_origins=cors_origins_str.split(","),
            enable_docs=os.getenv("GATEWAY_ENABLE_DOCS", "true").lower() == "true",
        )
    return _gateway_config
