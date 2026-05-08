# 中文说明：内置守卫提供者，包含基于白名单/黑名单的授权实现
"""Built-in guardrail providers that ship with DeerFlow."""

from deerflow.guardrails.provider import GuardrailDecision, GuardrailReason, GuardrailRequest


# 中文说明：白名单/黑名单授权提供者，无需外部依赖
class AllowlistProvider:
    """Simple allowlist/denylist provider. No external dependencies."""

    name = "allowlist"

    def __init__(self, *, allowed_tools: list[str] | None = None, denied_tools: list[str] | None = None):
        self._allowed = set(allowed_tools) if allowed_tools else None
        self._denied = set(denied_tools) if denied_tools else set()

    # 中文说明：评估工具调用是否允许执行
    def evaluate(self, request: GuardrailRequest) -> GuardrailDecision:
        if self._allowed is not None and request.tool_name not in self._allowed:
            return GuardrailDecision(allow=False, reasons=[GuardrailReason(code="oap.tool_not_allowed", message=f"tool '{request.tool_name}' not in allowlist")])
        if request.tool_name in self._denied:
            return GuardrailDecision(allow=False, reasons=[GuardrailReason(code="oap.tool_not_allowed", message=f"tool '{request.tool_name}' is denied")])
        return GuardrailDecision(allow=True, reasons=[GuardrailReason(code="oap.allowed")])

    async def aevaluate(self, request: GuardrailRequest) -> GuardrailDecision:
        return self.evaluate(request)
