"""LangGraph time-travel recovery (lazy langgraph import).

Provides a standard validator->approver->execute graph with an in-memory
checkpointer, plus rollback_and_fix(): replay from a prior checkpoint with new
data. langgraph is imported lazily so the rest of the suite works without it.
"""
from __future__ import annotations

from typing import Any, Dict


def build_graph():
    """Build the standard graph. Raises ImportError if langgraph is missing."""
    from langgraph.graph import StateGraph
    from langgraph.checkpoint.memory import MemorySaver

    builder = StateGraph(dict)
    builder.add_node("validator", lambda s: s)
    builder.add_node("approver", lambda s: s)
    builder.add_node("execute", lambda s: s)
    builder.set_entry_point("validator")
    builder.add_edge("validator", "approver")
    builder.add_edge("approver", "execute")
    return builder.compile(checkpointer=MemorySaver())


_GRAPH = None


def get_graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


def rollback_and_fix(thread_id: str, error_cp: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Replay from the checkpoint before ``error_cp`` using ``new_data``."""
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    history = list(graph.get_state_history(config))
    prev_state = None
    for s in history:
        if s.checkpoint_id == error_cp:
            break
        prev_state = s
    if prev_state is None:
        return {"result": "checkpoint_not_found"}
    try:
        from langgraph.types import StateUpdate
        graph.update_state(config, StateUpdate(values=new_data,
                                               checkpoint_id=prev_state.checkpoint_id),
                           as_node="validator")
    except Exception:  # older langgraph: pass values directly
        graph.update_state(config, new_data, as_node="validator")
    result = graph.invoke(None, config)
    return {"result": "recovered", "new_state": result}
