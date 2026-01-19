"""
Database configuration and session management.

Responsibilities:
- Initialize SQLAlchemy engine
- Provide a session factory for DB access
- Expose a FastAPI dependency for safe session lifecycle handling

QE relevance:
- Ensures each request uses an isolated DB session
- Prevents connection leaks during regression and load testing
- Enables reliable, repeatable system integration testing
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings


# -------------------------------------------------
# SQLAlchemy engine
# -------------------------------------------------
# create_engine creates a pool of DB connections.
# pool_pre_ping=True ensures connections are validated before use,
# which prevents errors from stale or dropped connections.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


# -------------------------------------------------
# Session factory
# -------------------------------------------------
# SessionLocal is NOT a session itself.
# It is a factory that creates a new session per request.
#
# autocommit=False:
#   - Explicit commits improve transaction control and safety.
#
# autoflush=False:
#   - Prevents unexpected writes before we explicitly commit.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# -------------------------------------------------
# Declarative base class
# -------------------------------------------------
# All ORM models inherit from Base.
# This allows SQLAlchemy to discover table metadata.
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    QE/SIT notes:
    - Centralizes schema metadata
    - Enables automated schema creation during startup
    """
    pass


# -------------------------------------------------
# FastAPI dependency for DB sessions
# -------------------------------------------------
def get_db():
    """
    Yield a database session for the duration of a request.

    Usage:
        db: Session = Depends(get_db)

    Flow:
    - Create a new DB session
    - Yield it to the endpoint
    - Ensure the session is closed after request completion

    QE/SIT relevance:
    - Prevents connection leaks during test runs
    - Guarantees clean DB state per request
    - Critical for stability under concurrent testing
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Always close the session, even if an exception occurs
        db.close()
