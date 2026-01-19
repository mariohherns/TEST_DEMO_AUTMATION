"""
Security utilities for authentication and authorization.

Responsibilities:
- Securely hash and verify user passwords
- Create and decode JWT access tokens
- Centralize cryptographic configuration

QE relevance:
- Enables security, regression, and role-based testing
- Prevents credential leaks and authentication flaws
- Ensures consistent token behavior across environments
"""

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone

from .config import settings


# -------------------------------------------------
# Password hashing configuration
# -------------------------------------------------
# CryptContext allows algorithm upgrades over time.
# bcrypt is a secure, adaptive hashing algorithm suitable for passwords.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# JWT signing algorithm
# HS256 is symmetric (shared secret) and sufficient for internal services.
ALGO = "HS256"


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Why:
    - Plaintext passwords must never be stored
    - bcrypt is slow by design, mitigating brute-force attacks

    QE/security notes:
    - Hash output is non-deterministic (salted)
    - Tests should verify `verify_password`, not hash equality
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Returns:
    - True if password matches
    - False otherwise

    QE/security notes:
    - Safe against timing attacks
    - Used during login validation
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(sub: str, role: str) -> str:
    """
    Create a timezone-aware JWT access token.

    Token contents:
    - sub: subject (unique user identifier, e.g. username)
    - role: user role (admin/viewer)
    - exp: expiration timestamp (UTC-aware)

    Why timezone-aware datetimes:
    - Avoids naive datetime bugs
    - Prevents inconsistent expiration across services
    - Required for correct JWT validation in distributed systems

    QE relevance:
    - Predictable expiration enables token-expiry testing
    - Role claim supports authorization test scenarios
    """

    # Use timezone-aware UTC datetime (modern Python best practice)
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MIN
    )

    # JWT payload
    payload = {
        "sub": sub,     # Who the user is
        "role": role,   # What the user can do
        "exp": exp,     # When the token expires
    }

    # Sign and encode the token
    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=ALGO,
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Validation performed:
    - Signature verification using JWT_SECRET
    - Expiration check (exp claim)
    - Algorithm enforcement

    Raises:
    - jose.JWTError on invalid or expired tokens

    QE relevance:
    - Central point for negative testing:
      * expired token
      * tampered token
      * wrong signing key
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[ALGO],
    )
