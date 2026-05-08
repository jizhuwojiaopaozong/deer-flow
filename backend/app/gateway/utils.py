# 中文说明：Gateway 层共享工具函数，提供日志参数消毒等安全辅助
"""Shared utility helpers for the Gateway layer."""


# 中文说明：去除字符串中的控制字符，防止日志注入攻击
def sanitize_log_param(value: str) -> str:
    """Strip control characters to prevent log injection."""
    return value.replace("\n", "").replace("\r", "").replace("\x00", "")
