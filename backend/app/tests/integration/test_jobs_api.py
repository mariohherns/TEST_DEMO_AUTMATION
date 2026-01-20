import httpx
import pytest


@pytest.mark.regression
@pytest.mark.sit
@pytest.mark.parametrize(
    "input_text,expected_terminal,expect_result",
    [
        ("hello world", {"DONE"}, True),
        ("please crash", {"FAILED"}, False),
    ],
    ids=["happy-path", "failure-injection"],
)
def test_job_lifecycle_parametrized(
    api_base,
    viewer_headers,
    poll_job_status,
    input_text,
    expected_terminal,
    expect_result,
):
    """
    Parametrized SIT test for the job lifecycle.

    Covers:
    - Job creation via API
    - Polling until terminal state
    - Result retrieval behavior depending on terminal outcome
    """

    # Create job
    r = httpx.post(
        f"{api_base}/jobs",
        json={"input_text": input_text},
        headers=viewer_headers,
        timeout=10,
    )
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    # Wait for completion (shared helper from conftest)
    status = poll_job_status(
        job_id=job_id,
        api_base=api_base,
        headers=viewer_headers,
        max_attempts=25,
        sleep_s=1.0,
    )
    assert status in expected_terminal

    # Validate result behavior
    result_resp = httpx.get(
        f"{api_base}/jobs/{job_id}/result",
        headers=viewer_headers,
        timeout=10,
    )

    if expect_result and status == "DONE":
        assert result_resp.status_code == 200, result_resp.text
        body = result_resp.json()
        assert "label" in body
        assert "confidence" in body
        assert 0.0 <= body["confidence"] <= 1.0
    else:
        assert result_resp.status_code in (404, 422), result_resp.text
