"""
API routes related to Job lifecycle management.

Responsibilities:
- Accept job submissions from authenticated users
- Persist jobs in the database
- Trigger asynchronous processing (AI/worker simulation)
- Expose job status and results for UI and automation

QE relevance:
- Central entry point for SIT and regression testing
- Exercises async workflows, DB integration, and security
- Provides deterministic endpoints for automation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Job, Result
from ..schemas import JobCreate, JobOut, ResultOut
from ..deps import get_current_user
from ..worker.tasks import process_job


# Router definition:
# - prefix="/jobs" means all routes start with /jobs
# - tags=["jobs"] groups endpoints in OpenAPI docs
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobOut)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Create a new job and trigger processing.

    Flow:
    1. Validate request payload (JobCreate schema)
    2. Persist job in DB with initial QUEUED status
    3. Trigger async processing (worker)
    4. Return job metadata immediately (non-blocking)

    QE/SIT notes:
    - Verifies API → DB integration
    - Enables async lifecycle testing
    - Allows regression tests to validate status transitions
    """

    # Create a new Job ORM object
    # submitted_by comes from the JWT-authenticated user
    job = Job(
        input_text=data.input_text,
        submitted_by=user["username"],
        status="QUEUED",
    )

    # Persist job to the database
    db.add(job)
    db.commit()
    db.refresh(job)  # ensures job.id is available

    # Trigger processing:
    # For local development, we run inline to simplify debugging.
    # In real deployments, this would be queued asynchronously
    # using Celery/RQ: process_job.delay(job.id)
    process_job(job.id)

    return job


@router.get("", response_model=list[JobOut])
def list_jobs(
    status: str | None = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    List jobs with optional status filtering.

    Parameters:
    - status (optional): filter jobs by lifecycle state

    QE/SIT notes:
    - Used by UI polling and dashboards
    - Enables validation of filtering logic
    - Supports regression testing for data consistency
    """

    # Base query: all jobs
    q = db.query(Job)

    # Optional filter by job status
    if status:
        q = q.filter(Job.status == status)
    
   
    # Order newest first and cap results to avoid large payloads
    return q.order_by(Job.created_at.desc()).limit(100).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Retrieve a single job by ID.

    QE/SIT notes:
    - Used for polling job status
    - Validates correct 404 handling
    - Ensures authorization is enforced consistently
    """

    job = db.get(Job, job_id)

    # Explicit 404 if job does not exist
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job

@router.get("/{job_id}/result", response_model=ResultOut)
def get_result(
    job_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Retrieve the processing result for a completed job.

    QE/SIT notes:
    - Validates async completion behavior
    - Supports negative testing (result not ready)
    - Used heavily in E2E automation
    """

    # Query result table by job_id
    res = db.query(Result).filter(Result.job_id == job_id).first()

    # If processing is not complete, result may not exist yet
    if not res:
        raise HTTPException(status_code=404, detail="Result not available")

    return res
