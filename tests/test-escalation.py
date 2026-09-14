from ..request_builder import build_request

def test_request_includes_approval_flag():
    req = build_request("github", "workflows", "fix SHA pins", "repo", "agent")
    assert req["permission_request"]["approval_required"] is True
