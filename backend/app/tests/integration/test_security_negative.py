import os
import httpx
import pytest

pytestmark = [pytest.mark.security, pytest.mark.rbac]

API = os.getenv("API_BASE", "http://127.0.0.1:8000")

def login_token(username: str, password: str) -> str:
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.mark.parametrize(
    "username,password,expected_status",
    [
        ("admin", "admin123", 200),
        ("viewer", "viewer123", 403),
    ],
    ids=["admin-allowed", "viewer-forbidden"],
)


def test_admin_health_rbac(username, password, expected_status):
    """
    RBAC test for /admin/health.

    - Admin should succeed (200)
    - Viewer should be forbidden (403)
    """
    token = login_token(username, password)
    headers = {"Authorization": f"Bearer {token}"}

    resp = httpx.get(f"{API}/admin/health", headers=headers, timeout=10)
    assert resp.status_code == expected_status, resp.text

