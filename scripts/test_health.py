def test_root_endpoint(client):
    """หน้าแรกคืนข้อมูลระบบ"""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "ZyntroAI Flask API" in data["service"]
    assert "version" in data
    assert data["status"] == "running"

def test_nonexistent_route(client):
    """เส้นทางไม่มีคืน 404"""
    resp = client.get("/api/v1/not-exist-really")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["success"] is False
    assert "ไม่พบ" in data["message"]
