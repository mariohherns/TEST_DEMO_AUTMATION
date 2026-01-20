import os
import re
import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "http://127.0.0.1:3000")


@pytest.fixture(scope="session")
def viewer_creds() -> tuple[str, str]:
    # Keep credentials centralized (matches your API tests approach)
    return ("viewer", "viewer123")


@pytest.fixture
def login_as(base_url: str, viewer_creds: tuple[str, str]):
    """
    UI login helper for Playwright tests.

    Usage:
        login_as(page)  # logs in as viewer
        login_as(page, "admin", "admin123")
    """
    def _login(page: Page, username: str | None = None, password: str | None = None) -> None:
        u, p = viewer_creds
        username = username or u
        password = password or p

        # Start clean each time to isolate tests
        page.context.clear_cookies()
        page.goto(f"{base_url}/login", wait_until="domcontentloaded")
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        page.reload(wait_until="domcontentloaded")

        # Fill and submit login form
        page.locator("[data-testid='username']").fill(username)
        page.locator("[data-testid='password']").fill(password)
        page.locator("[data-testid='login-btn']").click()

        # Assert navigation and page readiness
        expect(page).to_have_url(re.compile(r".*/jobs(?:\?.*)?$"), timeout=20_000)
        expect(page.locator("[data-testid='job-input']")).to_be_visible(timeout=20_000)
        expect(page.locator("[data-testid='jobs-table']")).to_be_visible(timeout=20_000)

    return _login

