# 中文说明：运行状态和断开模式枚举定义
"""Run status and disconnect mode enums."""

from enum import StrEnum


# 中文说明：运行生命周期状态枚举（待处理/运行中/成功/错误/超时/中断）
class RunStatus(StrEnum):
    """Lifecycle status of a single run."""

    pending = "pending"
    running = "running"
    success = "success"
    error = "error"
    timeout = "timeout"
    interrupted = "interrupted"


# 中文说明：SSE 消费者断开时的行为模式（取消或继续）
class DisconnectMode(StrEnum):
    """Behaviour when the SSE consumer disconnects."""

    cancel = "cancel"
    continue_ = "continue"
