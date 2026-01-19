import os
import time
import httpx
import pytest

pytestmark = [pytest.mark.sit]

API = os.getenv("API_BASE", "http://127.0.0.1:8000")


def login_token(username: str, password: str) -> str:
    """Login and return a bearer token for authenticated API calls."""
    r = httpx.post(
        f"{API}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def viewer_token() -> str:
    """
    Session-scoped token fixture.
    Reduces repeated logins across SIT tests.
    """
    return login_token("viewer", "viewer123")


@pytest.fixture
def auth_headers(viewer_token: str) -> dict:
    """Reusable Authorization header for authenticated requests."""
    return {"Authorization": f"Bearer {viewer_token}"}


def poll_job_status(job_id: int, headers: dict, max_attempts: int = 10, sleep_s: float = 1.0) -> str:
    """
    Poll job status until it reaches a terminal state or timeout.

    Terminal states:
    - DONE
    - FAILED
    """
    last_status = None
    for _ in range(max_attempts):
        r = httpx.get(f"{API}/jobs/{job_id}", headers=headers, timeout=10)
        assert r.status_code == 200, r.text

        last_status = r.json()["status"]
        if last_status in ("DONE", "FAILED"):
            return last_status

        time.sleep(sleep_s)

    # If we exit the loop, we timed out waiting for completion.
    pytest.fail(f"Job {job_id} did not reach DONE/FAILED within {max_attempts * sleep_s:.1f}s. Last status={last_status}")


@pytest.mark.parametrize(
    "input_text,expected_terminal,expect_result",
    [
        ("hello world", {"DONE"}, True),      # normally DONE, but allow FAILED if env is unstable
        ("please crash", {"FAILED"}, False),            # deterministic failure path
    ],
    ids=["happy-path", "failure-injection"],
)
def test_job_lifecycle_parametrized(auth_headers, input_text, expected_terminal, expect_result):
    """
    Parametrized SIT test for the job lifecycle.

    Covers:
    - Job creation via API
    - Polling until terminal state
    - Result retrieval behavior depending on terminal outcome
    """

    # Create job
    r = httpx.post(
        f"{API}/jobs",
        json={"input_text": input_text},
        headers=auth_headers,
        timeout=10,
    )
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    # Wait for completion
    status = poll_job_status(job_id, auth_headers)
    assert status in expected_terminal

    # Validate result behavior
    result_resp = httpx.get(f"{API}/jobs/{job_id}/result", headers=auth_headers, timeout=10)

    if expect_result and status == "DONE":
        assert result_resp.status_code == 200, result_resp.text
        body = result_resp.json()
        assert "label" in body
        assert "confidence" in body
        # Basic sanity: confidence is in the simulated range
        assert 0.0 <= body["confidence"] <= 1.0
    else:
        # When FAILED (or not done), result should not be available
        assert result_resp.status_code in (404, 422), result_resp.text
