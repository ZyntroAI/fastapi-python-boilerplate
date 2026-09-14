"""Token Budget — hard cap / soft truncate / usage metrics"""
from __future__ import annotations

import logging
from typing import Dict

from app import metrics
from app.context_compiler import estimate_tokens

logger = logging.getLogger("token_budget")

MODEL_LIMITS = {
    "default": 128000,
    "gpt-4o": 128000,
    "claude-3-opus": 200000,
    "gemini": 1000000,
    "mini": 32000,
}


class TokenBudget:
    """บังคับวงเงิน token ต่อ model + กัน payload เกิน"""

    def __init__(self, model: str = "default") -> None:
        self.model = model
        self.max = MODEL_LIMITS.get(model, MODEL_LIMITS["default"])

    def check(self, estimated: int) -> bool:
        """Hard check: เกิน → reject เร็ว (ไม่เรียก provider)"""
        return estimated <= self.max

    def truncate(self, context: Dict) -> Dict:
        """Soft: ตัด message เก่าออกทีละตัวจนไม่เกิน budget"""
        ctx = {**context, "messages": list(context["messages"]), "system": context["system"]}
        while ctx["estimated_tokens"] > self.max and ctx["messages"]:
            removed = ctx["messages"].pop(0)
            # เก็บเฉพาะ tokens ที่ตัดจริง (ถ้าเกิน budget)
            over = ctx["estimated_tokens"] - self.max
            saved = min(over, estimate_tokens(removed.get("content", "")))
            if saved > 0:
                metrics.TOKEN_SAVED.inc(saved)
            ctx["estimated_tokens"] = estimate_tokens(ctx["system"]) + sum(
                estimate_tokens(m.get("content", "")) for m in ctx["messages"]
            )
        metrics.TOKEN_TOTAL.labels(self.model).inc(ctx["estimated_tokens"])
        return ctx

    def reject_reason(self, estimated: int) -> str:
        return f"estimated {estimated} exceeds model limit {self.max}"
