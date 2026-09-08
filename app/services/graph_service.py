"""
Graph Service — ZyntroAI FastAPI Boilerplate
Encapsulates LangGraph + Context Guard 40-60% + Persistent Memory
Flow: Resume → Guard → Route → LLM → Save → Return
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.core.langgraph.graph import graph
from app.core.langgraph.memory import session_manager
from app.core.context_guard import get_context_guard

# ═══════════════════════════════════════════════════════════
# SERVICE CLASS
# ═══════════════════════════════════════════════════════════
class GraphService:
    # ────────────────────────────────────────────────────────
    # Main Entry: Protected Chat Endpoint
    # ────────────────────────────────────────────────────────
    @staticmethod
    async def run_chat(
        messages: List[Dict[str, Any]],
        session_id: Optional[str] = None,
        resume: bool = False
    ) -> Dict[str, Any]:
        """
        🛡️ Full Protected Chat Flow
        
        Args:
            messages: New conversation messages
            session_id: Persistent session identifier (auto-saves history)
            resume: If True → restore from last checkpoint
        
        Returns:
            Complete response with guard metrics + session info
        """
        try:
            # ── Step 1: Resume from Checkpoint (if requested) ──
            if resume and session_id:
                saved_messages = session_manager.resume_session(session_id)
                if saved_messages:
                    # Append new messages to restored history
                    messages = saved_messages + messages

            # ── Step 2: Prepare Thread Config for Checkpointing ──
            config = {
                "configurable": {
                    "thread_id": session_id or "default-session"
                }
            }

            # ── Step 3: Execute Graph → Guard → Route → LLM → Save ──
            result = await graph.ainvoke(
                input={
                    "messages": messages,
                    "metadata": {
                        "session_id": session_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                },
                config=config
            )

            # ── Step 4: Extract Guard Metrics ──
            guard_info = result.get("context_guard", {})
            guard_status = guard_info.get("status", {})

            # ── Step 5: Save Progress to Session ──
            if session_id:
                session_manager.save_to_session(
                    session_id=session_id,
                    messages=result.get("messages", messages),
                    guard_metrics={
                        **guard_status,
                        "applied": guard_info.get("applied", False),
                        "aggressive_compact": guard_info.get("aggressive_compact", False)
                    }
                )

            # ── Step 6: Return Standardized Response ──
            return {
                "success": True,
                "response": result.get("response"),
                "messages": result.get("messages", []),
                "context_guard": {
                    "usage_pct": guard_status.get("usage", "N/A"),
                    "tokens": guard_status.get("tokens", "N/A"),
                    "phase": guard_status.get("phase", "SAFE"),
                    "compactions": guard_status.get("compactions", 0),
                    "applied": guard_info.get("applied", False),
                    "aggressive_compact": guard_info.get("aggressive_compact", False)
                },
                "session": {
                    "id": session_id,
                    "resumed": resume and bool(saved_messages) if session_id else False
                }
            }

        # ── Error Handling ──
        except Exception as error:
            return {
                "success": False,
                "error": str(error),
                "context_guard": get_context_guard().status(),
                "session": {"id": session_id, "resumed": False}
            }

    # ────────────────────────────────────────────────────────
    # Session History & Status
    # ────────────────────────────────────────────────────────
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full session info: message count, compaction logs, status"""
        session = session_manager.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "created_at": session.get("created_at"),
            "message_count": len(session.get("messages", [])),
            "checkpoint_available": session.get("checkpoint_available", False),
            "compactions_total": len(session.get("context_guard_history", [])),
            "recent_events": session.get("context_guard_history", [])[-5:],
            "metadata": session.get("metadata", {})
        }

    # ────────────────────────────────────────────────────────
    # System Health Check
    # ────────────────────────────────────────────────────────
    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Verify Guard + Graph are operational"""
        return {
            "graph_ready": True,
            "context_guard": get_context_guard().status(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════
# Singleton Instance (Import this in routes)
# ═══════════════════════════════════════════════════════════
graph_service = GraphService()
