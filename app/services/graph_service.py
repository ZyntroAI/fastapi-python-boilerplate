"""
Graph Service — Wraps LangGraph for API Use
Handles invocation, streaming, and error handling
"""
from typing import List, Dict, Any, Optional
from app.core.langgraph.graph import graph
from app.core.context_guard import get_context_guard

class GraphService:
    @staticmethod
    async def run_chat(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute Full Guarded Flow"""
        try:
            result = await graph.ainvoke({
                "messages": messages,
                "metadata": {
                    "timestamp": __import__("datetime").datetime.utcnow().isoformat()
                }
            })
            return {
                "success": True,
                "response": result.get("response"),
                "messages": result.get("messages", []),
                "context_guard": result.get("context_guard", {})
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "context_guard": get_context_guard().status()
            }

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Return Guard + Graph Health"""
        return {
            "graph_ready": True,
            "context_guard": get_context_guard().status()
        }

graph_service = GraphService()
