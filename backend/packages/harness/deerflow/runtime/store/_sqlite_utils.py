# 中文说明：SQLite 连接工具函数，为存储和检查点提供路径解析
"""Shared SQLite connection utilities for store and checkpointer providers."""

from __future__ import annotations

import pathlib

from deerflow.config.paths import resolve_path


# 中文说明：解析 SQLite 连接字符串，将相对路径转为绝对路径
def resolve_sqlite_conn_str(raw: str) -> str:
    """Return a SQLite connection string ready for use with store/checkpointer backends.

    SQLite special strings (``":memory:"`` and ``file:`` URIs) are returned
    unchanged.  Plain filesystem paths — relative or absolute — are resolved
    to an absolute string via :func:`resolve_path`.
    """
    if raw == ":memory:" or raw.startswith("file:"):
        return raw
    return str(resolve_path(raw))


# 中文说明：确保 SQLite 文件的父目录存在
def ensure_sqlite_parent_dir(conn_str: str) -> None:
    """Create parent directory for a SQLite filesystem path.

    No-op for in-memory databases (``":memory:"``) and ``file:`` URIs.
    """
    if conn_str != ":memory:" and not conn_str.startswith("file:"):
        pathlib.Path(conn_str).parent.mkdir(parents=True, exist_ok=True)
