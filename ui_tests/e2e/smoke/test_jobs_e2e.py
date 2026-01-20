import pytest
from playwright.sync_api import Page, expect
from typing import Callable


@pytest.mark.smoke
@pytest.mark.parametrize(
    "job_text",
    ["selenium job", "crash", "queued"],
    ids=["success_submit", "failed_submit", "queued_submit"],
)
def test_submit_job_variants(
    page: Page,
    login_as: Callable[..., None],
    job_text: str,
) -> None:
    """
    E2E smoke: login + submit a job.

    Covers:
    - Login workflow
    - Job submission flow
    - Jobs table remains visible after submission
    """

    # Login using shared helper (defaults to viewer creds)
    login_as(page)

    # Submit a job
    page.locator("[data-testid='job-input']").fill(job_text)
    page.locator("[data-testid='submit-job']").click()

    # Validate table is still visible (basic smoke assertion)
    expect(page.locator("[data-testid='jobs-table']")).to_be_visible(timeout=20_000)


