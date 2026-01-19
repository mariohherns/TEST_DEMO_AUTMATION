"""
FastAPI dependency functions for authentication and authorization.

Responsibilities:
- Extract JWT tokens from requests
- Decode and validate tokens
- Provide user context to endpoints
- Enforce role-based access control (RBAC)

QE relevance:
- Central enforcement point for security behavior
- Enables consistent negative-path testing
- Ensures unauthorized requests fail early and predictably
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from .security import decode_token


# OAuth2PasswordBearer automatically:
# - Reads the Authorization header
# - Extracts Bearer tokens
# - Returns 401 if header is missing
#
# tokenUrl is used by Swagger UI to know where to obtain tokens.
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2)) -> dict:
    """
    Dependency that validates the JWT token and returns user context.

    Flow:
    1. Extract token from Authorization header
    2. Decode and validate JWT signature + expiration
    3. Return minimal user identity to endpoint

    Returns:
    - dict with username and role

    QE/SIT notes:
    - Used by nearly all protected endpoints
    - Central place to test invalid, expired, or tampered tokens
    """

    try:
        # Decode token (verifies signature + exp claim)
        payload = decode_token(token)

        # Extract required fields from token
        # KeyError will be raised if expected fields are missing
        return {
            "username": payload["sub"],
            "role": payload.get("role", "viewer"),
        }

    except (JWTError, KeyError):
        # Do not leak details about why token failed
        # Prevents attackers from inferring token structure
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that enforces admin-only access.

    Used by:
    - Admin endpoints (e.g. /admin/health)

    QE/SIT notes:
    - Enables role-based testing
    - Ensures consistent 403 responses for unauthorized users
    """

    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only",
        )

    # Return user context so endpoints can still access it if needed
    return user
