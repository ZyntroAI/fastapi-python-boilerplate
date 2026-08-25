async def replay_failed_session(thread_id: str, checkpoint_id: str | None = None):
    config = {
        "configurable": {
            "thread_id": thread_id,
            **({"checkpoint_id": checkpoint_id} if checkpoint_id else {}),
        }
    }
    state = await graph.aget_state(config)
    print(f"Cost so far: ${state.values.get('cost_usd', 0):.4f}")
    
    # Re-run from that checkpoint
    result = await graph.ainvoke(None, config)
    return result
