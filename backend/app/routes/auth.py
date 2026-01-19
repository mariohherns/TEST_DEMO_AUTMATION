"""
Authentication routes for the API.

Responsibilities:
- Validate user credentials (username/password)
- Issue JWT access tokens for authenticated sessions

QE relevance:
- Enables security testing (auth required, invalid creds, lockouts, etc.)
- Supports role-based testing (admin vs viewer)
- Provides a deterministic way for automation suites to obtain tokens
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import TokenOut
from ..security import verify_password, create_access_token


# Router groups endpoints under /auth and labels them in API docs.
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return a JWT access token.

    Input:
    - OAuth2PasswordRequestForm provides `username` and `password` fields.
      This matches many standard OAuth2 flows and works well with Swagger UI.

    Output:
    - access_token: JWT token used in Authorization header
    - token_type: "bearer" (standard for OAuth2/JWT APIs)

    QE/SIT notes:
    - Primary entry point for obtaining tokens during automation
    - Supports negative/security testing (bad credentials, missing fields)
    - Token contains "role" claim used for authorization checks
    """

    # Query the user by username.
    # If user doesn't exist, return 401 to avoid revealing which usernames are valid.
    user = db.query(User).filter(User.username == form_data.username).first()

    # Verify password using secure hash comparison.
    # Never compare raw passwords directly; always verify against a stored hash.
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token with user identity + role.
    # The "role" claim supports role-based access control (admin endpoints).
    token = create_access_token(sub=user.username, role=user.role)

    # Standard OAuth2-style response (used by Swagger + client libraries)
    return {"access_token": token, "token_type": "bearer"}
