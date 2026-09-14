"""
Graph Nodes — Pure Functions: State → State
Node 1: Context Guard (40-60% + Re-Injection)
Node 2: LLM Call
Node 3: Post-Process / Output
"""
from typing import Dict, Any
from app.core.context_guard import get_context_guard

# --------------------------
# 🛡️ NODE 1: Context Guard
# --------------------------
def context_guard_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIRST NODE: Process messages through 40-60% Rule
    Returns cleaned/compacted messages + guard metrics
    """
    guard = get_context_guard()
    messages = state.get("messages", [])
    
    # ✅ Apply Guard Logic
    cleaned_messages = guard.process(messages)
    
    # ✅ Return metrics for observability
    return {
        "messages": cleaned_messages,
        "context_guard": {
            "status": guard.status(),
            "applied": True,
            "original_count": len(messages),
            "cleaned_count": len(cleaned_messages)
        }
    }

# --------------------------
# 🤖 NODE 2: LLM Generation
# --------------------------
def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    SECOND NODE: Call LLM with Guard-Protected Messages
    """
    messages = state.get("messages", [])
    
    # ✅ Pass protected messages to LLM
    from app.services.llm_service import call_llm  # Your existing LLM service
    response = call_llm(messages)
    
    return {
        "response": response,
        "metadata": {
            "llm_called": True,
            "input_message_count": len(messages)
        }
    }

# --------------------------
# ✅ NODE 3: Finalize Output
# --------------------------
def output_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    FINAL NODE: Format response + attach guard info
    """
    return {
        "messages": state.get("messages", []),  # Preserve protected history
        "response": state.get("response"),
        "context_guard": state.get("context_guard", {}),
        "success": state.get("error") is None
    }
