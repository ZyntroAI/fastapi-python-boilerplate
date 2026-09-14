import os

def update_status(state: str, blocker: dict = None):
    """Post status to project board"""
    payload = {
        "state": state,
        "blocker": blocker,
        "updated_at": __import__("datetime").datetime.utcnow().isoformat()
    }
    endpoint = os.getenv("PROJECT_BOARD_WEBHOOK")
    if endpoint:
        import requests
        requests.post(endpoint, json=payload, timeout=10)
    print(f"📊 Board Updated: {state}")
    return payload
