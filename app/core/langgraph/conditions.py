"""
Conditional Routing — Decide Next Step Based on Guard Status
Flow:
  After Guard → IF Compacted → Skip Summary Node → LLM
             → IF Safe → Direct → LLM
             → IF Too Large → Compact First → Retry
"""
from typing import Dict, Any, Literal

def after_guard_route(state: Dict[str, Any]) -> Literal["llm_generate", "recompact"]:
    """
    🧭 Decision Node
    Returns next node name
    """
    guard_info = state.get("context_guard", {})
    pct = float(guard_info.get("status", {}).get("usage", "0%").replace("%",""))

    if pct >= 75:
        return "recompact"       # Too large → force recompact
    elif guard_info.get("applied"):
        return "llm_generate"    # Compacted → proceed to LLM
    else:
        return "llm_generate"    # Safe → proceed normally
