# 中文说明：IM 渠道抽象基类模块，定义所有渠道实现的公共接口
"""Abstract base class for IM channels."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.channels.message_bus import InboundMessage, InboundMessageType, MessageBus, OutboundMessage, ResolvedAttachment

logger = logging.getLogger(__name__)


# 中文说明：所有 IM 渠道实现的抽象基类，子类必须实现 start、stop 和 send 方法
class Channel(ABC):
    """Base class for all IM channel implementations.

    Each channel connects to an external messaging platform and:
    1. Receives messages, wraps them as InboundMessage, publishes to the bus.
    2. Subscribes to outbound messages and sends replies back to the platform.

    Subclasses must implement ``start``, ``stop``, and ``send``.
    """

    def __init__(self, name: str, bus: MessageBus, config: dict[str, Any]) -> None:
        self.name = name
        self.bus = bus
        self.config = config
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def supports_streaming(self) -> bool:
        return False

    # -- lifecycle ---------------------------------------------------------

    @abstractmethod
    async def start(self) -> None:
        """Start listening for messages from the external platform."""

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully stop the channel."""

    # -- outbound ----------------------------------------------------------

    @abstractmethod
    async def send(self, msg: OutboundMessage) -> None:
        """Send a message back to the external platform.

        The implementation should use ``msg.chat_id`` and ``msg.thread_ts``
        to route the reply to the correct conversation/thread.
        """

    # 中文说明：上传单个文件附件到平台，默认不支持，子类可覆盖
    async def send_file(self, msg: OutboundMessage, attachment: ResolvedAttachment) -> bool:
        """Upload a single file attachment to the platform.

        Returns True if the upload succeeded, False otherwise.
        Default implementation returns False (no file upload support).
        """
        return False

    # -- helpers -----------------------------------------------------------

    # 中文说明：便捷工厂方法，用于创建 InboundMessage 实例
    def _make_inbound(
        self,
        chat_id: str,
        user_id: str,
        text: str,
        *,
        msg_type: InboundMessageType = InboundMessageType.CHAT,
        thread_ts: str | None = None,
        files: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InboundMessage:
        """Convenience factory for creating InboundMessage instances."""
        return InboundMessage(
            channel_name=self.name,
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            msg_type=msg_type,
            thread_ts=thread_ts,
            files=files or [],
            metadata=metadata or {},
        )

    # 中文说明：出站消息回调，仅转发目标为当前渠道的消息，先发送文本再上传附件
    async def _on_outbound(self, msg: OutboundMessage) -> None:
        """Outbound callback registered with the bus.

        Only forwards messages targeted at this channel.
        Sends the text message first, then uploads any file attachments.
        File uploads are skipped entirely when the text send fails to avoid
        partial deliveries (files without accompanying text).
        """
        if msg.channel_name == self.name:
            try:
                await self.send(msg)
            except Exception:
                logger.exception("Failed to send outbound message on channel %s", self.name)
                return  # Do not attempt file uploads when the text message failed

            for attachment in msg.attachments:
                try:
                    success = await self.send_file(msg, attachment)
                    if not success:
                        logger.warning("[%s] file upload skipped for %s", self.name, attachment.filename)
                except Exception:
                    logger.exception("[%s] failed to upload file %s", self.name, attachment.filename)

    # 中文说明：可选地处理入站文件附件，子类可覆盖以下载文件到沙盒目录
    async def receive_file(self, msg: InboundMessage, thread_id: str) -> InboundMessage:
        """
        Optionally process and materialize inbound file attachments for this channel.

        By default, this method does nothing and simply returns the original message.
        Subclasses (e.g. FeishuChannel) may override this to download files (images, documents, etc)
        referenced in msg.files, save them to the sandbox, and update msg.text to include
        the sandbox file paths for downstream model consumption.

        Args:
            msg: The inbound message, possibly containing file metadata in msg.files.
            thread_id: The resolved DeerFlow thread ID for sandbox path context.

        Returns:
            The (possibly modified) InboundMessage, with text and/or files updated as needed.
        """
        return msg
