from fastapi.testclient import TestClient


def test_order_invalid_quantity_returns_rfc7807(monkeypatch):
    # ป้องกันไม่ให้เรียก RabbitMQ จริงตอนเทสต์ validation ของ order endpoint
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    from services.order_service.app import main as order_main if False else __import__(
        "sys"
    )
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "order_main", root / "services/order-service/app/main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = TestClient(module.app)
    response = client.post("/api/v1/orders", params={"item_id": "sku-01", "quantity": 0})

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")

    body = response.json()
    assert body["type"] == "https://api.zyntroai.com/errors/invalid-quantity"
    assert body["title"] == "Invalid Order Quantity"
    assert body["status"] == 400
    assert "quantity" in body["detail"].lower()
    assert body["instance"] == "/api/v1/orders"


def test_request_validation_error_returns_rfc7807():
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "order_main_val", root / "services/order-service/app/main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = TestClient(module.app)
    # ส่ง quantity เป็น string ที่แปลงเป็น int ไม่ได้เพื่อกระตุ้น RequestValidationError (422)
    response = client.post(
        "/api/v1/orders", params={"item_id": "sku-01", "quantity": "not-an-int"}
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")

    body = response.json()
    assert body["type"] == "https://api.zyntroai.com/errors/validation-error"
    assert body["title"] == "Unprocessable Entity"
    assert body["status"] == 422
    assert body["instance"] == "/api/v1/orders"
    assert isinstance(body.get("invalid_params"), list)
    assert len(body["invalid_params"]) >= 1
