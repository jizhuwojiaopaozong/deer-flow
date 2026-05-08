# 线程状态定义: 扩展 AgentState, 包含沙盒、线程数据、标题、制品、待办、上传文件、已查看图片

from typing import Annotated, NotRequired, TypedDict

from langchain.agents import AgentState


# 沙盒状态: 包含沙盒 ID
class SandboxState(TypedDict):
    sandbox_id: NotRequired[str | None]


# 线程数据状态: 包含工作区、上传、输出目录路径
class ThreadDataState(TypedDict):
    workspace_path: NotRequired[str | None]
    uploads_path: NotRequired[str | None]
    outputs_path: NotRequired[str | None]


# 已查看图片数据: 包含 base64 编码和 MIME 类型
class ViewedImageData(TypedDict):
    base64: str
    mime_type: str


# 制品列表 reducer: 合并并去重, 保持插入顺序
def merge_artifacts(existing: list[str] | None, new: list[str] | None) -> list[str]:
    """Reducer for artifacts list - merges and deduplicates artifacts."""
    if existing is None:
        return new or []
    if new is None:
        return existing
    # Use dict.fromkeys to deduplicate while preserving order
    return list(dict.fromkeys(existing + new))


# 已查看图片字典 reducer: 合并字典, 空字典表示清除所有图片
def merge_viewed_images(existing: dict[str, ViewedImageData] | None, new: dict[str, ViewedImageData] | None) -> dict[str, ViewedImageData]:
    """Reducer for viewed_images dict - merges image dictionaries.

    Special case: If new is an empty dict {}, it clears the existing images.
    This allows middlewares to clear the viewed_images state after processing.
    """
    if existing is None:
        return new or {}
    if new is None:
        return existing
    # Special case: empty dict means clear all viewed images
    if len(new) == 0:
        return {}
    # Merge dictionaries, new values override existing ones for same keys
    return {**existing, **new}


# 线程状态: 扩展 LangGraph 的 AgentState, 添加 DeerFlow 特有的状态字段
class ThreadState(AgentState):
    sandbox: NotRequired[SandboxState | None]
    thread_data: NotRequired[ThreadDataState | None]
    title: NotRequired[str | None]
    artifacts: Annotated[list[str], merge_artifacts]
    todos: NotRequired[list | None]
    uploaded_files: NotRequired[list[dict] | None]
    viewed_images: Annotated[dict[str, ViewedImageData], merge_viewed_images]  # image_path -> {base64, mime_type}
