"""
Pydantic models defining the API request and response contracts.

Responsibilities:
- Validate incoming API payloads
- Control what data is exposed in responses
- Convert ORM objects into JSON-safe structures

QE relevance:
- Provides stable response shapes for automation
- Prevents accidental exposure of internal fields
- Enables strong contract testing (API schemas)
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TokenOut(BaseModel):
    """
    Response schema for authentication token issuance.

    Returned by:
    - POST /auth/login

    QE/Security notes:
    - token_type is fixed to "bearer" for OAuth2 compatibility
    - access_token is consumed by UI and test automation
    """
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    """
    Input schema for login requests (JSON-based).

    Note:
    - Not used when OAuth2PasswordRequestForm is enabled
    - Useful for alternative auth flows or future extensions

    QE notes:
    - Provides explicit validation for auth-related inputs
    """
    username: str
    password: str


class JobCreate(BaseModel):
    """
    Input schema for creating a new job.

    Used by:
    - POST /jobs

    QE/SIT notes:
    - Ensures input_text is always present
    - Prevents malformed job submissions
    """
    input_texts: str


class JobOut(BaseModel):
    """
    Output schema representing a job summary.

    Used by:
    - POST /jobs
    - GET /jobs
    - GET /jobs/{id}

    QE/SIT notes:
    - Stable structure for polling and UI rendering
    - Excludes internal DB fields
    """
    id: int
    created_at: datetime
    status: str
    submitted_by: str

    class Config:
        # Allows conversion directly from SQLAlchemy ORM objects
        # without manual field mapping.
        from_attributes = True


class ResultOut(BaseModel):
    """
    Output schema representing a job's processing result.

    Used by:
    - GET /jobs/{id}/result

    QE/SIT notes:
    - Enables validation of async processing outcomes
    - Confidence values can be range-tested (0.0–1.0)
    """
    job_id: int
    label: str
    confidence: float
    processed_at: datetime

    class Config:
        # Enables ORM → schema conversion
        from_attributes = True


class AnalyticsOut(BaseModel):
    """
    Output schema for analytics dashboard summaries.

    Used by:
    - GET /analytics/summary

    QE/SIT notes:
    - Aggregated values are ideal for KPI validation
    - Optional avg_confidence supports empty datasets
    """
    total_jobs: int
    done_jobs: int
    failed_jobs: int
    avg_confidence: Optional[float] = None
