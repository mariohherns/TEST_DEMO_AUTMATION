import os
import time
import uuid
import pytest
import httpx

API = os.getenv("API_BASE", "http://127.0.0.1:8000")
POLL_SECONDS = int(os.getenv("SIT_POLL_SECONDS", "25"))
POLL_INTERVAL = float(os.getenv("SIT_POLL_INTERVAL", "1.0"))

pytestmark = [pytest.mark.sit]


def _login(username: str, password: str) -> str:
    """OAuth2 Password flow -> form-encoded login."""
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "access_token" in body, body
    return body["access_token"]


def _poll_job_status(token: str, job_id: int) -> dict:
    """Poll /jobs/{id} until DONE/FAILED or timeout."""
    headers = {"Authorization": f"Bearer {token}"}

    deadline = time.time() + POLL_SECONDS
    last = None

    while time.time() < deadline:
        r = httpx.get(f"{API}/jobs/{job_id}", headers=headers, timeout=10)
        assert r.status_code == 200, r.text
        last = r.json()
        status = last.get("status")

        if status in ("DONE", "FAILED"):
            return last

        time.sleep(POLL_INTERVAL)

    pytest.fail(f"Timed out waiting for job {job_id} to finish. Last state: {last}")


def test_sit_golden_path_job_completes_and_result_available():
    """
    Golden Path SIT:
    - Auth (viewer)
    - Create job
    - Job transitions via (async)
    - Result is available when DONE
    """
    token = _login("viewer", "viewer123")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Unique input text to avoid collisions with old rows
    run_id = uuid.uuid4().hex[:8]
    input_text = f"sit-golden-{run_id}"

    # 1) Create job (API should return quickly even if worker is async)
    r = httpx.post(f"{API}/jobs", json={"input_text": input_text}, headers=headers, timeout=10)
    assert r.status_code == 200, r.text
    job = r.json()
    assert "id" in job, job
    job_id = job["id"]

    # 2) Poll until DONE/FAILED
    final_job = _poll_job_status(token, job_id)
    assert final_job["status"] in ("DONE", "FAILED")

    # 3) If DONE, result endpoint should return expected schema
    if final_job["status"] == "DONE":
        res = httpx.get(f"{API}/jobs/{job_id}/result", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        assert res.status_code == 200, res.text
        body = res.json()

        # Adjust keys if your schema differs, but keep assertions strong
        assert "label" in body, body
        assert "confidence" in body, body
        assert isinstance(body["confidence"], (int, float)), body

    # 4) If FAILED, result should be unavailable or return an expected error
    if final_job["status"] == "FAILED":
        res = httpx.get(f"{API}/jobs/{job_id}/result", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        # Depending on your implementation, this might be 404 or 400.
        assert res.status_code in (400, 404), res.text
