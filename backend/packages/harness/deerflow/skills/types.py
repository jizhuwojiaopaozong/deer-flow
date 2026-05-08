# 中文说明：技能类型定义，包含技能分类枚举和技能数据类
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

SKILL_MD_FILE = "SKILL.md"


# 中文说明：技能来源分类枚举，区分内置技能和用户自定义技能
class SkillCategory(StrEnum):
    """Source category for a skill.

    - ``PUBLIC``: built-in skill bundled with the platform, read-only.
    - ``CUSTOM``: user-authored skill that can be edited or deleted.
    """

    PUBLIC = "public"
    CUSTOM = "custom"


@dataclass
# 中文说明：技能数据类，包含名称、描述、路径和分类等元信息
class Skill:
    """Represents a skill with its metadata and file path"""

    name: str
    description: str
    license: str | None
    skill_dir: Path
    skill_file: Path
    relative_path: Path  # Relative path from category root to skill directory
    category: SkillCategory  # 'public' or 'custom'
    allowed_tools: list[str] | None = None
    enabled: bool = False  # Whether this skill is enabled

    # 中文说明：返回技能相对于分类根目录的路径
    @property
    def skill_path(self) -> str:
        """Returns the relative path from the category root (skills/{category}) to this skill's directory"""
        path = self.relative_path.as_posix()
        return "" if path == "." else path

    # 中文说明：获取技能在容器中的完整挂载路径
    def get_container_path(self, container_base_path: str = "/mnt/skills") -> str:
        """
        Get the full path to this skill in the container.

        Args:
            container_base_path: Base path where skills are mounted in the container

        Returns:
            Full container path to the skill directory
        """
        category_base = f"{container_base_path}/{self.category}"
        skill_path = self.skill_path
        if skill_path:
            return f"{category_base}/{skill_path}"
        return category_base

    # 中文说明：获取技能主文件 SKILL.md 在容器中的完整路径
    def get_container_file_path(self, container_base_path: str = "/mnt/skills") -> str:
        """
        Get the full path to this skill's main file (SKILL.md) in the container.

        Args:
            container_base_path: Base path where skills are mounted in the container

        Returns:
            Full container path to the skill's SKILL.md file
        """
        return f"{self.get_container_path(container_base_path)}/SKILL.md"

    def __repr__(self) -> str:
        return f"Skill(name={self.name!r}, description={self.description!r}, category={self.category!r})"
