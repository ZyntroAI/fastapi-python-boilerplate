"""
Persistent Checkpoint Manager
- Save/Resume conversation state
- Auto-recovery after compaction
- Per-Session Isolation
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from langgraph.checkpoint.memory import MemorySaver
import json

# Global Memory Store (replace with Redis/DB in production)
checkpointer = MemorySaver()

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, session_id: str, metadata: Dict = None) -> Dict:
        """Register new session"""
        self.sessions[session_id] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": [],
            "context_guard_history": [],
            "metadata": metadata or {},
            "checkpoint_available": False
        }
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve session"""
        return self.sessions.get(session_id)

    def save_to_session(self, session_id: str, messages: list, guard_metrics: Dict):
        """Save progress + guard metrics"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        self.sessions[session_id]["messages"] = messages
        self.sessions[session_id]["context_guard_history"].append({
            **guard_metrics,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.sessions[session_id]["checkpoint_available"] = True

    def resume_session(self, session_id: str) -> Optional[list]:
        """Restore messages from last checkpoint"""
        session = self.get_session(session_id)
        return session["messages"] if session and session["checkpoint_available"] else None

session_manager = SessionManager()
