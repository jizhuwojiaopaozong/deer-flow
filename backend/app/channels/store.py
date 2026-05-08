# 中文说明：渠道存储模块，持久化 IM 聊天与 DeerFlow 线程的映射关系
"""ChannelStore — persists IM chat-to-DeerFlow thread mappings."""

from __future__ import annotations

import json
import logging
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# 中文说明：基于 JSON 文件的存储类，管理 IM 会话到 DeerFlow 线程的映射
class ChannelStore:
    """JSON-file-backed store that maps IM conversations to DeerFlow threads.

    Data layout (on disk)::

        {
            "<channel_name>:<chat_id>": {
                "thread_id": "<uuid>",
                "user_id": "<platform_user>",
                "created_at": 1700000000.0,
                "updated_at": 1700000000.0
            },
            ...
        }

    The store is intentionally simple — a single JSON file that is atomically
    rewritten on every mutation. For production workloads with high concurrency,
    this can be swapped for a proper database backend.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        if path is None:
            from deerflow.config.paths import get_paths

            path = Path(get_paths().base_dir) / "channels" / "store.json"
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, dict[str, Any]] = self._load()
        self._lock = threading.Lock()

    # -- persistence -------------------------------------------------------

    def _load(self) -> dict[str, dict[str, Any]]:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                logger.warning("Corrupt channel store at %s, starting fresh", self._path)
        return {}

    def _save(self) -> None:
        fd = tempfile.NamedTemporaryFile(
            mode="w",
            dir=self._path.parent,
            suffix=".tmp",
            delete=False,
        )
        try:
            json.dump(self._data, fd, indent=2)
            fd.close()
            Path(fd.name).replace(self._path)
        except BaseException:
            fd.close()
            Path(fd.name).unlink(missing_ok=True)
            raise

    # -- key helpers -------------------------------------------------------

    @staticmethod
    def _key(channel_name: str, chat_id: str, topic_id: str | None = None) -> str:
        if topic_id:
            return f"{channel_name}:{chat_id}:{topic_id}"
        return f"{channel_name}:{chat_id}"

    # -- public API --------------------------------------------------------

    # 中文说明：根据渠道名和聊天ID查找对应的 DeerFlow 线程ID
    def get_thread_id(self, channel_name: str, chat_id: str, topic_id: str | None = None) -> str | None:
        """Look up the DeerFlow thread_id for a given IM conversation/topic."""
        entry = self._data.get(self._key(channel_name, chat_id, topic_id))
        return entry["thread_id"] if entry else None

    # 中文说明：创建或更新 IM 会话到 DeerFlow 线程的映射
    def set_thread_id(
        self,
        channel_name: str,
        chat_id: str,
        thread_id: str,
        *,
        topic_id: str | None = None,
        user_id: str = "",
    ) -> None:
        """Create or update the mapping for an IM conversation/topic."""
        with self._lock:
            key = self._key(channel_name, chat_id, topic_id)
            now = time.time()
            existing = self._data.get(key)
            self._data[key] = {
                "thread_id": thread_id,
                "user_id": user_id,
                "created_at": existing["created_at"] if existing else now,
                "updated_at": now,
            }
            self._save()

    # 中文说明：移除指定的映射关系，可按 topic 精确删除或批量删除
    def remove(self, channel_name: str, chat_id: str, topic_id: str | None = None) -> bool:
        """Remove a mapping.

        If ``topic_id`` is provided, only that specific conversation/topic mapping is removed.
        If ``topic_id`` is omitted, all mappings whose key starts with
        ``"<channel_name>:<chat_id>"`` (including topic-specific ones) are removed.

        Returns True if at least one mapping was removed.
        """
        with self._lock:
            # Remove a specific conversation/topic mapping.
            if topic_id is not None:
                key = self._key(channel_name, chat_id, topic_id)
                if key in self._data:
                    del self._data[key]
                    self._save()
                    return True
                return False

            # Remove all mappings for this channel/chat_id (base and any topic-specific keys).
            prefix = self._key(channel_name, chat_id)
            keys_to_delete = [k for k in self._data if k == prefix or k.startswith(prefix + ":")]
            if not keys_to_delete:
                return False

            for k in keys_to_delete:
                del self._data[k]
            self._save()
            return True

    # 中文说明：列出所有存储的映射，可按渠道名过滤
    def list_entries(self, channel_name: str | None = None) -> list[dict[str, Any]]:
        """List all stored mappings, optionally filtered by channel."""
        results = []
        for key, entry in self._data.items():
            parts = key.split(":", 2)
            ch = parts[0]
            chat = parts[1] if len(parts) > 1 else ""
            topic = parts[2] if len(parts) > 2 else None
            if channel_name and ch != channel_name:
                continue
            item: dict[str, Any] = {"channel_name": ch, "chat_id": chat, **entry}
            if topic is not None:
                item["topic_id"] = topic
            results.append(item)
        return results
