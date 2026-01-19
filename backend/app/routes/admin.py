"""

Administrative and operational endpoints.

Responsibilities:
- Expose health and admin-only operations
- Enforce role-based access control (RBAC)

QE relevance:
- Validates authorization behavior (403 vs 401)
- Provides operational readiness checks
- Supports CI/CD and monitoring workflows
"""

from fastapi import APIRouter, Depends
from ..deps import require_admin

# Router groups admin-only endpoints under /admin
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/health")
def health(_: dict = Depends(require_admin)):
    """
    Admin-only health check endpoint.

    Returns:
    - {"status": "ok"} if service is healthy and caller is authorized

    QE/SIT notes:
    - Used to validate RBAC enforcement
    - Useful for smoke tests and deployment validation
    - Ensures only privileged users can access operational endpoints
    """

    # The underscore (_) indicates we intentionally do not use
    # the returned user object, only enforce admin access.
    return {"status": "ok"}
