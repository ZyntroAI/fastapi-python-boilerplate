from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text
    assert "FastAPI" in response.text  # ตรวจสอบว่ามีข้อความที่คาดหวัง

def test_static_css():
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "body" in response.text  # ตรวจสอบว่าไฟล์ CSS ถูก serve

def test_spa_route():
    response = client.get("/app")
    assert response.status_code == 200
    assert "<div id=\"root\"" in response.text  # ตรวจสอบว่า React/Vue mount point ถูกต้อง
