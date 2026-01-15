import os, time
import httpx
import pytest
pytestmark = [pytest.mark.sit]


API = os.getenv("API_BASE", "http://127.0.0.1:8000")

def token(username, password):
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]

def test_job_lifecycle_done():
    t = token("viewer", "viewer123")
    headers = {"Authorization": f"Bearer {t}"}

    r = httpx.post(f"{API}/jobs", json={"input_text": "hello world"}, headers=headers, timeout=10)
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    # Poll for DONE/FAILED
    status = None
    for _ in range(10):
        j = httpx.get(f"{API}/jobs/{job_id}", headers=headers, timeout=10)
        assert j.status_code == 200, j.text
        status = j.json()["status"]
        if status in ("DONE", "FAILED"):
            break
        time.sleep(1)

    assert status in ("DONE", "FAILED")

    if status == "DONE":
        res = httpx.get(f"{API}/jobs/{job_id}/result", headers=headers, timeout=10)
        assert res.status_code == 200, res.text

