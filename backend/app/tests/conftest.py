import os
import time
import httpx
import pytest

API = os.getenv("API_BASE", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def api_base() -> str:
    return API


@pytest.fixture(scope="session")
def login_token(api_base: str):
    """
    Session-scoped helper to get a bearer token.
    Usage: token = login_token("viewer", "viewer123")
    """
    def _login(username: str, password: str) -> str:
        r = httpx.post(
            f"{api_base}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        assert r.status_code == 200, r.text
        return r.json()["access_token"]
    return _login


@pytest.fixture(scope="session")
def viewer_token(login_token) -> str:
    return login_token("viewer", "viewer123")


@pytest.fixture(scope="session")
def admin_token(login_token) -> str:
    return login_token("admin", "admin123")


@pytest.fixture
def viewer_headers(viewer_token: str) -> dict:
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}



@pytest.fixture(scope="session")
def poll_job_status():
    """
    Reusable helper to poll job status until DONE or FAILED.

    Returns the final status string.
    """

    def _poll(
        job_id: int,
        api_base: str,
        headers: dict,
        max_attempts: int = 10,
        sleep_s: float = 1.0,
    ) -> str:
        last_status = None

        for _ in range(max_attempts):
            r = httpx.get(
                f"{api_base}/jobs/{job_id}",
                headers=headers,
                timeout=10,
            )
            assert r.status_code == 200, r.text

            last_status = r.json()["status"]
            if last_status in ("DONE", "FAILED"):
                return last_status

            time.sleep(sleep_s)

        pytest.fail(
            f"Job {job_id} did not reach DONE/FAILED within "
            f"{max_attempts * sleep_s:.1f}s. Last status={last_status}"
        )

    return _poll

