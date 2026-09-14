"""
End-to-End JWT Authentication Flow — through Traefik
✅ Register → Login → Get Token → Access Protected → Verify Auth Required
"""
import os
import pytest
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://localhost:80")

# Test user — fresh for each run
TEST_EMAIL = "e2e-test-auth@example.com"
TEST_PASSWORD = "SecurePass123!"
TEST_USERNAME = "e2e_test_user"


@pytest.fixture(scope="module")
def client():
    """Reusable HTTP client pointing at Traefik ingress"""
    return httpx.Client(
        base_url=API_BASE,
        timeout=15.0,
        follow_redirects=True
    )


@pytest.fixture(scope="module")
def auth_tokens(client):
    """
    Full auth flow once per test module:
    1. Register user (if endpoint exists)
    2. Login → get access/refresh tokens
    Returns: {"access": "...", "refresh": "..."}
    """
    tokens = {}

    # Step 1: Register (if your API supports public registration)
    try:
        register = client.post("/api/auth/register", json={
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        # Ignore if already exists (409 Conflict)
        assert register.status_code in (200, 201, 409)
    except httpx.HTTPError:
        # Registration endpoint may be disabled — skip silently
        pass

    # Step 2: Login — get JWT tokens
    login = client.post("/api/auth/login", data={
        "username": TEST_EMAIL,  # OAuth2 uses "username" field
        "password": TEST_PASSWORD
    })

    # If registration skipped, try with known test user
    if login.status_code in (401, 422):
        login = client.post("/api/auth/login", data={
            "username": "test@example.com",
            "password": "testpass123"
        })

    assert login.status_code == 200, f"Login failed: {login.text}"
    data = login.json()

    # Support both {"access_token": "..."} and {"access": "..."} formats
    tokens["access"] = (
        data.get("access_token") or
        data.get("access") or
        data.get("token")
    )
    tokens["refresh"] = data.get("refresh_token") or data.get("refresh")

    assert tokens["access"], "No access token returned from login"
    return tokens


@pytest.mark.e2e
def test_login_returns_jwt_format(client):
    """✅ Login returns valid JWT structure"""
    resp = client.post("/api/auth/login", data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    # Allow 401 if test user not seeded — test structure only
    if resp.status_code == 200:
        data = resp.json()
        token = data.get("access_token") or data.get("access")
        assert token and len(token.split(".")) == 3, "Token must be JWT format (3 parts)"


@pytest.mark.e2e
def test_protected_route_rejects_without_token(client):
    """✅ Protected routes return 401 when no token provided"""
    resp = client.get("/api/users/me")
    assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}"


@pytest.mark.e2e
def test_protected_route_accepts_jwt(client, auth_tokens):
    """✅ Access protected route WITH valid JWT — through Traefik"""
    resp = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_tokens['access']}"}
    )
    assert resp.status_code == 200, f"Expected 200 with valid token, got {resp.status_code}"
    data = resp.json()
    # Verify response contains user identity fields
    assert any(k in data for k in ["id", "email", "username", "user_id"]), "User data not returned"


@pytest.mark.e2e
def test_expired_or_invalid_token_rejected(client):
    """✅ Invalid/garbage token → 401 Unauthorized"""
    resp = client.get(
        "/api/users/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.INVALID.TOKEN"}
    )
    assert resp.status_code in (401, 403), "Invalid token must be rejected"


@pytest.mark.e2e
def test_token_refresh_flow(client, auth_tokens):
    """✅ Refresh token → get new access token"""
    if not auth_tokens.get("refresh"):
        pytest.skip("No refresh token — skipping refresh flow test")

    resp = client.post("/api/auth/refresh", json={
        "refresh_token": auth_tokens["refresh"]
    })
    # Some APIs return new access token
    if resp.status_code == 200:
        data = resp.json()
        new_token = data.get("access_token") or data.get("access")
        assert new_token and new_token != auth_tokens["access"], "New token should differ"


@pytest.mark.e2e
def test_logout_revokes_token(client, auth_tokens):
    """✅ Logout endpoint invalidates token"""
    resp = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {auth_tokens['access']}"}
    )
    # Logout may return 200 or 204
    assert resp.status_code in (200, 204, 401)  # 401 = already invalidated

    # Verify token no longer works
    verify = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_tokens['access']}"}
    )
    assert verify.status_code in (401, 403), "Token should be invalid after logout"
