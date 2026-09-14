"""
Graph Definition — Linear Flow with Guard First
[Input] → [Context Guard] → [LLM] → [Output] → [END]
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
from .state import AgentState
from .nodes import context_guard_node, llm_node, output_node

def build_graph() -> StateGraph:
    """
    Build Compiled Graph — Ready to Invoke
    Flow:
    1. Context Guard ALWAYS runs FIRST (protects LLM)
    2. Then LLM receives clean/compacted messages
    3. Return formatted output
    """
    # Initialize Graph with shared state
    graph = StateGraph(AgentState)

    # ✅ Register Nodes
    graph.add_node("context_guard", context_guard_node)
    graph.add_node("llm_generate", llm_node)
    graph.add_node("format_output", output_node)

    # ✅ Define Flow (Guard → LLM → Output → END)
    graph.set_entry_point("context_guard")
    graph.add_edge("context_guard", "llm_generate")
    graph.add_edge("llm_generate", "format_output")
    graph.add_edge("format_output", END)

    # ✅ Compile & Return
    return graph.compile()

# Singleton Instance
graph = build_graph()
