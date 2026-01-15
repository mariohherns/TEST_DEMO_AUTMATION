import os
import httpx

API = os.getenv("API_BASE", "http://127.0.0.1:8000")

def test_admin_health_requires_admin():
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": "viewer", "password": "viewer123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    t = r.json()["access_token"]

    headers = {"Authorization": f"Bearer {t}"}
    h = httpx.get(f"{API}/admin/health", headers=headers, timeout=10)
    assert h.status_code == 403

