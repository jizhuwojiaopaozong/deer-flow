# 中文说明：运行事件存储子包，根据配置创建内存/数据库/JSONL 存储
from deerflow.runtime.events.store.base import RunEventStore
from deerflow.runtime.events.store.memory import MemoryRunEventStore


# 中文说明：根据配置创建运行事件存储实例
def make_run_event_store(config=None) -> RunEventStore:
    """Create a RunEventStore based on run_events.backend configuration."""
    if config is None or config.backend == "memory":
        return MemoryRunEventStore()
    if config.backend == "db":
        from deerflow.persistence.engine import get_session_factory

        sf = get_session_factory()
        if sf is None:
            # database.backend=memory but run_events.backend=db -> fallback
            return MemoryRunEventStore()
        from deerflow.runtime.events.store.db import DbRunEventStore

        return DbRunEventStore(sf, max_trace_content=config.max_trace_content)
    if config.backend == "jsonl":
        from deerflow.runtime.events.store.jsonl import JsonlRunEventStore

        return JsonlRunEventStore()
    raise ValueError(f"Unknown run_events backend: {config.backend!r}")


__all__ = ["MemoryRunEventStore", "RunEventStore", "make_run_event_store"]
