# 目录遍历工具: 递归列出目录结构, 支持深度限制和忽略规则
from pathlib import Path

from deerflow.sandbox.search import should_ignore_name


# 列出目录内容: 递归遍历指定深度, 过滤忽略项和符号链接越界
def list_dir(path: str, max_depth: int = 2) -> list[str]:
    """
    List files and directories up to max_depth levels deep.

    Args:
        path: The root directory path to list.
        max_depth: Maximum depth to traverse (default: 2).
                   1 = only direct children, 2 = children + grandchildren, etc.

    Returns:
        A list of absolute paths for files and directories,
        excluding items matching IGNORE_PATTERNS.
    """
    result: list[str] = []
    root_path = Path(path).resolve()

    if not root_path.is_dir():
        return result

    # 检查路径是否在根目录内: 防止符号链接逃逸
    def _is_within_root(candidate: Path) -> bool:
        try:
            candidate.relative_to(root_path)
            return True
        except ValueError:
            return False

    # 递归遍历目录: 逐层深入到最大深度, 处理符号链接和权限错误
    def _traverse(current_path: Path, current_depth: int) -> None:
        """Recursively traverse directories up to max_depth."""
        if current_depth > max_depth:
            return

        try:
            for item in current_path.iterdir():
                if should_ignore_name(item.name):
                    continue

                if item.is_symlink():
                    try:
                        item_resolved = item.resolve()
                        if not _is_within_root(item_resolved):
                            continue
                    except OSError:
                        continue
                    post_fix = "/" if item_resolved.is_dir() else ""
                    result.append(str(item_resolved) + post_fix)
                    continue

                item_resolved = item.resolve()
                if not _is_within_root(item_resolved):
                    continue

                post_fix = "/" if item.is_dir() else ""
                result.append(str(item_resolved) + post_fix)

                # Recurse into subdirectories if not at max depth
                if item.is_dir() and current_depth < max_depth:
                    _traverse(item, current_depth + 1)
        except PermissionError:
            pass

    _traverse(root_path, 1)

    return sorted(result)
