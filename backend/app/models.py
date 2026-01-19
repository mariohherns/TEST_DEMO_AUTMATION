"""
SQLAlchemy ORM models representing the database schema.

Responsibilities:
- Define persistent entities (User, Job, Result)
- Enforce data integrity via constraints (unique keys, foreign keys)
- Provide relationships for convenient ORM navigation

QE/SIT relevance:
- Data model consistency is essential for system integration testing:
  UI/API/worker must agree on how data is stored and linked.
- Constraints create testable guarantees (e.g., one Result per Job).
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class User(Base):
    """
    Represents an authenticated user in the system.

    Fields:
    - username: unique identifier used during login
    - password_hash: bcrypt-hashed password (never store plaintext)
    - role: supports role-based access control (RBAC)
      e.g. "admin" can access admin endpoints; "viewer" cannot

    QE relevance:
    - Supports security testing (auth success/failure)
    - Supports RBAC testing (403 vs 200 outcomes)
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # unique=True ensures no duplicate usernames can exist
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # store hash only; never store raw password
    password_hash: Mapped[str] = mapped_column(String(255))

    # simple role model; can be expanded later (permissions table, etc.)
    role: Mapped[str] = mapped_column(String(50), default="viewer")  # admin | viewer


class Job(Base):
    """
    Represents a submitted job (work item) to be processed by the worker.

    Lifecycle:
    - QUEUED: created and waiting for processing
    - PROCESSING: worker started processing
    - DONE: worker finished and wrote Result
    - FAILED: worker encountered an error (no Result or partial data)

    QE relevance:
    - SIT validates status transitions and timestamps
    - Regression tests ensure API/worker keep lifecycle consistent
    """
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # created_at default uses server time at insert
    # Note: datetime.utcnow() is naive; timezone-aware UTC is better in production.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )

    # status used for polling from UI and automation tests
    status: Mapped[str] = mapped_column(
        String(30),
        default="QUEUED",
    )  # QUEUED|PROCESSING|DONE|FAILED

    # who submitted the job (ties back to JWT "sub")
    submitted_by: Mapped[str] = mapped_column(String(100))

    # job payload / request input
    input_text: Mapped[str] = mapped_column(Text)

    # One-to-one relationship: a job produces a single result.
    # cascade="all,delete" means if job is deleted, delete its result too.
    result = relationship(
        "Result",
        back_populates="job",
        uselist=False,          # one-to-one, not one-to-many
        cascade="all,delete",
    )


class Result(Base):
    """
    Represents the processing output of a job.

    Fields:
    - job_id: foreign key ensures results cannot exist without a job
    - label/confidence: simulated inference output
    - processed_at: timestamp to help analytics and debugging

    QE relevance:
    - Used to validate async completion
    - Confidence supports boundary testing (0.0 <= confidence <= 1.0)
    """
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # unique=True enforces "one result per job"
    # ForeignKey enforces referential integrity with jobs table.
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), unique=True)

    label: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)

    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # back reference to the Job (ORM navigation)
    job = relationship("Job", back_populates="result")
