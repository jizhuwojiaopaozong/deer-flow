# 工具系统模块: 提供工具加载、注册和技能管理功能
from .tools import get_available_tools

__all__ = ["get_available_tools", "skill_manage_tool"]


# 延迟加载技能管理工具: 避免模块级别的循环导入
def __getattr__(name: str):
    if name == "skill_manage_tool":
        from .skill_manage_tool import skill_manage_tool

        return skill_manage_tool
    raise AttributeError(name)
