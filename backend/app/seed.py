"""
seed.py

Database seed utilities.

Responsibilities:
- Populate baseline data required for the application to function
- Ensure predictable test users exist across environments

QE relevance:
- Enables repeatable authentication and authorization testing
- Eliminates manual setup steps for SIT and regression automation
"""

from sqlalchemy.orm import Session
from .models import User
from .security import hash_password

def seed_users(db: Session) -> None:
    """
    Seed baseline users into the database.

    This function is idempotent:
    - If users already exist, it exits without modifying data.
    - If no users exist, it inserts predefined test users.

    Seeded users:
    - admin / admin123  (role: admin)
    - viewer / viewer123 (role: viewer)

    QE/SIT notes:
    - Provides known credentials for automation
    - Enables role-based access testing
    - Ensures consistent startup state across environments
    """

    # Idempotency check:
    # If any users already exist, assume seeding has already occurred.
    # This prevents duplicate users when the app restarts.
    if db.query(User).count() > 0:
        return

    # Create admin user with hashed password
    db.add(
        User(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
        )
    )

    # Create standard viewer user
    db.add(
        User(
            username="viewer",
            password_hash=hash_password("viewer123"),
            role="viewer",
        )
    )

    # Commit both inserts as a single transaction
    db.commit()

