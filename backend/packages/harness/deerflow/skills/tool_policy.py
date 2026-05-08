# 中文说明：技能工具策略，根据技能声明的 allowed-tools 过滤可用工具列表
import logging
from typing import Protocol

from deerflow.skills.types import Skill

logger = logging.getLogger(__name__)


# 中文说明：具名工具协议，要求实现 name 属性
class NamedTool(Protocol):
    name: str


# 中文说明：计算所有已加载技能声明的允许工具名称的并集
def allowed_tool_names_for_skills(skills: list[Skill]) -> set[str] | None:
    """Return the union of explicit skill allowed-tools declarations.

    None means legacy allow-all behavior. It is returned only when no loaded
    skill declares allowed-tools. Once any skill declares the field, legacy
    skills without the field contribute no tools instead of disabling the
    explicit restrictions from other skills.
    """
    if not skills:
        return None

    allowed: set[str] = set()
    has_explicit_declaration = False
    for skill in skills:
        if skill.allowed_tools is None:
            continue
        has_explicit_declaration = True
        if not skill.allowed_tools:
            logger.info("Skill %s declared empty allowed-tools", skill.name)
        allowed.update(skill.allowed_tools)

    if not has_explicit_declaration:
        return None
    return allowed


# 中文说明：根据技能的 allowed-tools 策略过滤工具列表
def filter_tools_by_skill_allowed_tools[ToolT: NamedTool](tools: list[ToolT], skills: list[Skill]) -> list[ToolT]:
    allowed = allowed_tool_names_for_skills(skills)
    if allowed is None:
        return tools

    return [tool for tool in tools if tool.name in allowed]
