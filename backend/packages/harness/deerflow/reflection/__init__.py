# 中文说明：反射模块，提供通过模块路径动态加载变量和类的功能
from .resolvers import resolve_class, resolve_variable

__all__ = ["resolve_class", "resolve_variable"]
