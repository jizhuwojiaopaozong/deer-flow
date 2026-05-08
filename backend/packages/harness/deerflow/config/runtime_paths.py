# 中文说明：运行时路径解析模块，为独立 harness 使用提供项目根目录和状态目录定位
"""Runtime path resolution for standalone harness usage."""

import os
from pathlib import Path


# 中文说明：返回调用方项目根目录，用于定位运行时文件
def project_root() -> Path:
    """Return the caller project root for runtime-owned files."""
    if env_root := os.getenv("DEER_FLOW_PROJECT_ROOT"):
        root = Path(env_root).resolve()
        if not root.exists():
            raise ValueError(f"DEER_FLOW_PROJECT_ROOT is set to '{env_root}', but the resolved path '{root}' does not exist.")
        if not root.is_dir():
            raise ValueError(f"DEER_FLOW_PROJECT_ROOT is set to '{env_root}', but the resolved path '{root}' is not a directory.")
        return root
    return Path.cwd().resolve()


# 中文说明：返回可写的 DeerFlow 状态目录
def runtime_home() -> Path:
    """Return the writable DeerFlow state directory."""
    if env_home := os.getenv("DEER_FLOW_HOME"):
        return Path(env_home).resolve()
    return project_root() / ".deer-flow"


def resolve_path(value: str | os.PathLike[str], *, base: Path | None = None) -> Path:
    """Resolve absolute paths as-is and relative paths against the project root."""
    path = Path(value)
    if not path.is_absolute():
        path = (base or project_root()) / path
    return path.resolve()


def existing_project_file(names: tuple[str, ...]) -> Path | None:
    """Return the first existing named file under the project root."""
    root = project_root()
    for name in names:
        candidate = root / name
        if candidate.is_file():
            return candidate
    return None
