# 中文说明：工具和工具组配置，定义工具的名称、分组和实现路径
from pydantic import BaseModel, ConfigDict, Field


# 中文说明：工具组配置，用于逻辑分组管理工具
class ToolGroupConfig(BaseModel):
    """Config section for a tool group"""

    name: str = Field(..., description="Unique name for the tool group")
    model_config = ConfigDict(extra="allow")


# 中文说明：单个工具的配置，指定工具名称、所属组和实现类路径
class ToolConfig(BaseModel):
    """Config section for a tool"""

    name: str = Field(..., description="Unique name for the tool")
    group: str = Field(..., description="Group name for the tool")
    use: str = Field(
        ...,
        description="Variable name of the tool provider(e.g. deerflow.sandbox.tools:bash_tool)",
    )
    model_config = ConfigDict(extra="allow")
