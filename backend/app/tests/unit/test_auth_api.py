import os
import httpx
import pytest

pytestmark = [pytest.mark.smoke, pytest.mark.security]

API = os.getenv("API_BASE", "http://127.0.0.1:8000")

@pytest.mark.parametrize(
    "username,password,expected_status,expect_token",
    [
        ("admin", "admin123", 200, True),
        ("viewer", "viewer123", 200, True),
        ("wrong", "wrong123", 401, False),
        ("admin", "wrongpass", 401, False),
    ],
    ids=[
        "valid-admin-login",
        "valid-viewer-login",
        "invalid-username",
        "invalid-password",
    ],
)
def test_login_parametrized(username, password, expected_status, expect_token):
    """
    Parametrized login test covering both valid and invalid credentials.

    QE notes:
    - Reduces duplicated test logic
    - Makes it easy to add more auth scenarios
    - Improves CI visibility with readable test IDs
    """

    response = httpx.post(
        f"{API}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    assert response.status_code == expected_status, response.text

    body = response.json()

    if expect_token:
        assert "access_token" in body
        assert body.get("token_type") == "bearer"
    else:
        # For invalid logins, we assert error detail instead
        assert "detail" in body
