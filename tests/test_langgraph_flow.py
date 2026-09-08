"""
Test Full Flow: Input → Guard → Compact → Re-Inject → LLM
"""
import pytest
from app.core.langgraph.graph import graph
from app.core.context_guard import GuardSettings, init_guard

@pytest.mark.asyncio
async def test_guard_runs_first():
    # Initialize Guard
    init_guard(GuardSettings(
        max_tokens=1000,
        threshold_compact=0.6,
        rules=["Test Rule A", "Test Rule B"],
        goals=["Test Goal X"]
    ))

    # Simulate long conversation
    messages = [
        {"role": "user", "content": f"Message {i}"}
        for i in range(30)  # Trigger compaction
    ]

    # Run through Graph
    result = await graph.ainvoke({"messages": messages})

    # ✅ Guard ran
    assert result["context_guard"]["applied"] is True
    # ✅ Messages were compacted
    assert len(result["messages"]) < len(messages)
    # ✅ Response exists
    assert "response" in result
