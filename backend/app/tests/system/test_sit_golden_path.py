import uuid
import pytest
import httpx
from typing import Callable, Dict

@pytest.mark.sit
@pytest.mark.regression
@pytest.mark.parametrize(
    "input_prefix",
    [
        "sit-golden",
        "sit-unicode-ñá漢字",
        "sit-long-" + ("x" * 50),
    ],
    ids=["normal", "unicode", "long"],
)
def test_sit_job_completes_and_result_behaves(
    api_base: str,
    viewer_headers: Dict[str, str],
    poll_job_status: Callable[..., str],
    input_prefix: str,
) -> None:
    """
    Parametrized SIT regression:
    - Create a job with different input text variants
    - Job reaches a terminal state (DONE/FAILED)
    - If DONE -> result schema is valid
    - If FAILED -> result endpoint returns expected error (400/404)
    """

    # Unique input text to avoid collisions with old rows
    run_id = uuid.uuid4().hex[:8]
    input_text = f"{input_prefix}-{run_id}"

    # 1) Create job (API should return quickly even if worker is async)
    r = httpx.post(
        f"{api_base}/jobs",
        json={"input_text": input_text},
        headers=viewer_headers,
        timeout=10,
    )
    assert r.status_code == 200, r.text

    job = r.json()
    assert "id" in job, job
    job_id = job["id"]

    # 2) Poll until DONE/FAILED (shared helper from conftest)
    status = poll_job_status(
        job_id=job_id,
        api_base=api_base,
        headers=viewer_headers,
        max_attempts=25,
        sleep_s=1.0,
    )
    assert status in ("DONE", "FAILED")

    # 3) If DONE, result endpoint should return expected schema
    if status == "DONE":
        res = httpx.get(
            f"{api_base}/jobs/{job_id}/result",
            headers=viewer_headers,
            timeout=10,
        )
        assert res.status_code == 200, res.text
        body = res.json()

        assert "label" in body, body
        assert "confidence" in body, body
        assert isinstance(body["confidence"], (int, float)), body

    # 4) If FAILED, result should be unavailable or return an expected error
    if status == "FAILED":
        res = httpx.get(
            f"{api_base}/jobs/{job_id}/result",
            headers=viewer_headers,
            timeout=10,
        )
        assert res.status_code in (400, 404), res.text
