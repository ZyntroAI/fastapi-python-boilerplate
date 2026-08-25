from langgraph.types import interrupt

def sensitive_action_node(state: State):
    # Snapshot what needs approval
    proposed_action = {
        "action": "send_email",
        "to": state["recipient"],
        "subject": state["subject"],
        "body": state["draft"]
    }
    
    # Pause here — UI shows the proposed action for approval
    approval = interrupt(proposed_action)
    
    if approval["approved"]:
        return {"result": send_email(approval)}
    else:
        return {"result": "Action rejected by user"}
