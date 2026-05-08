# 中文说明：子代理系统包，导出配置、执行器和注册表等核心组件
from .config import SubagentConfig
from .executor import SubagentExecutor, SubagentResult
from .registry import get_available_subagent_names, get_subagent_config, list_subagents

__all__ = [
    "SubagentConfig",
    "SubagentExecutor",
    "SubagentResult",
    "get_available_subagent_names",
    "get_subagent_config",
    "list_subagents",
]
