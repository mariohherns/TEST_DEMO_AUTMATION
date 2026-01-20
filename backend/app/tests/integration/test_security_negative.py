import httpx
import pytest


@pytest.mark.security
@pytest.mark.rbac
@pytest.mark.regression
@pytest.mark.sit
@pytest.mark.parametrize(
    "who,expected_status",
    [
        ("admin", 200),
        ("viewer", 403),
    ],
    ids=["admin-allowed", "viewer-forbidden"],
)
def test_admin_health_rbac(
    api_base, admin_headers, viewer_headers, who, expected_status
):
    """
    RBAC test for /admin/health.

    - Admin should succeed (200)
    - Viewer should be forbidden (403)
    """

    # Select the correct Authorization header based on role
    headers = admin_headers if who == "admin" else viewer_headers

    # Call protected admin endpoint
    resp = httpx.get(
        f"{api_base}/admin/health",
        headers=headers,
        timeout=10,
    )

    # Validate RBAC behavior
    assert resp.status_code == expected_status, resp.text
