import pytest

class TestAuthLogin:
    def test_login_success(self, client, test_user):
        """ล็อกอินสำเร็จ — ได้ Token ทั้งคู่"""
        resp = client.post("/api/v1/auth/login", json={
            "email": "test@zyntroai.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["email"] == "test@zyntroai.com"

    def test_login_wrong_password(self, client, test_user):
        """รหัสผ่านผิด — 401"""
        resp = client.post("/api/v1/auth/login", json={
            "email": "test@zyntroai.com",
            "password": "WrongPass!",
        })
        assert resp.status_code == 401
        assert resp.get_json()["success"] is False

    def test_login_invalid_email_format(self, client):
        """รูปแบบอีเมลผิด — 400"""
        resp = client.post("/api/v1/auth/login", json={
            "email": "not-an-email",
            "password": "anything",
        })
        assert resp.status_code == 400

    def test_login_missing_fields(self, client):
        """ไม่ส่งฟิลด์จำเป็น — 400"""
        resp = client.post("/api/v1/auth/login", json={"email": "a@b.com"})
        assert resp.status_code == 400

class TestAuthRefresh:
    def test_refresh_token_success(self, client, test_user):
        """ใช้ Refresh Token ขอ Access Token ใหม่"""
        login_resp = client.post("/api/v1/auth/login", json={
            "email": "test@zyntroai.com",
            "password": "TestPass123!",
        })
        refresh_token = login_resp.get_json()["data"]["refresh_token"]

        resp = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        assert resp.status_code == 200
        assert "access_token" in resp.get_json()["data"]

    def test_refresh_needs_token(self, client):
        """ไม่ส่ง Token — 401"""
        resp = client.post("/api/v1/auth/refresh")
        assert resp.status_code in (401, 422)
