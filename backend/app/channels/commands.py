# 中文说明：所有渠道实现共享的命令定义模块
"""Shared command definitions used by all channel implementations.

Keeping the authoritative command set in one place ensures that channel
parsers (e.g. Feishu) and the ChannelManager dispatcher stay in sync
automatically — adding or removing a command here is the single edit
required.
"""

from __future__ import annotations

# 中文说明：所有渠道已知的命令集合，确保各渠道解析器和调度器保持同步
KNOWN_CHANNEL_COMMANDS: frozenset[str] = frozenset(
    {
        "/bootstrap",
        "/new",
        "/status",
        "/models",
        "/memory",
        "/help",
    }
)
