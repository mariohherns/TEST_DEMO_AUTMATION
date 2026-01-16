import os
import httpx
import pytest
pytestmark = [pytest.mark.smoke, pytest.mark.security]


API = os.getenv("API_BASE", "http://127.0.0.1:8000")

def test_login_admin():
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "access_token" in body
    assert body.get("token_type") == "bearer"

def test_login_invalid_credentials():
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": "wrong", "password": "wrong123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 401
