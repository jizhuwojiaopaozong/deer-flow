# 中文说明：技能演化配置，控制代理是否可以创建和修改技能
from pydantic import BaseModel, Field


# 中文说明：技能演化配置类，支持启用/禁用和审核模型设置
class SkillEvolutionConfig(BaseModel):
    """Configuration for agent-managed skill evolution."""

    enabled: bool = Field(
        default=False,
        description="Whether the agent can create and modify skills under skills/custom.",
    )
    moderation_model_name: str | None = Field(
        default=None,
        description="Optional model name for skill security moderation. Defaults to the primary chat model.",
    )
    security_fail_closed: bool = Field(
        default=True,
        description=("When the moderation model is unavailable, block skill writes if True (fail-closed). If False, non-executable content is allowed with a warning while executable content is still blocked."),
    )
