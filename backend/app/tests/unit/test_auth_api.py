import httpx
import pytest


@pytest.mark.security
@pytest.mark.smoke
@pytest.mark.parametrize(
    "username,password,expected_status,expect_token",
    [
        ("admin", "admin123", 200, True),
        ("viewer", "viewer123", 200, True),
        ("wrong", "wrong123", 401, False),
        ("admin", "wrongpass", 401, False),
    ],
    ids=[
        "valid-admin-login",
        "valid-viewer-login",
        "invalid-username",
        "invalid-password",
    ],
)
def test_login_parametrized(
    api_base: str,
    username: str,
    password: str,
    expected_status: int,
    expect_token: bool,
) -> None:
    """
    Parametrized login smoke test covering valid and invalid credentials.

    QE notes:
    - Validates OAuth2 password flow
    - Covers both success and failure paths
    - Fast enough for PR smoke gates
    """

    # Call login endpoint directly (do NOT reuse token fixtures here)
    response = httpx.post(
        f"{api_base}/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    # Verify HTTP status
    assert response.status_code == expected_status, response.text

    body = response.json()

    if expect_token:
        # Successful login should return a bearer token
        assert "access_token" in body, body
        assert body.get("token_type") == "bearer", body
    else:
        # Invalid login should return an error payload
        assert "detail" in body, body
