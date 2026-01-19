"""
Analytics and reporting endpoints.

Responsibilities:
- Aggregate job and result data
- Provide high-level metrics for dashboards and reporting
- Support quality trend analysis and operational insights

QE relevance:
- Enables quality metrics tracking (pass/fail rates)
- Supports defect trend monitoring
- Provides KPIs for system integration validation
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from ..models import Job, Result
from ..schemas import AnalyticsOut
from ..deps import get_current_user


# Router groups analytics-related endpoints under /analytics
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsOut)
def summary(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Return a high-level summary of job processing outcomes.

    Metrics returned:
    - total_jobs: total number of jobs submitted
    - done_jobs: jobs successfully completed
    - failed_jobs: jobs that failed processing
    - avg_confidence: average confidence score across results

    QE/SIT notes:
    - Used to validate end-to-end processing health
    - Supports regression analysis across test runs
    - Can be compared across environments (QA vs prod)
    """

    # Count all jobs (fallback to 0 if table is empty)
    total = db.query(func.count(Job.id)).scalar() or 0

    # Count successfully completed jobs
    done = (
        db.query(func.count(Job.id))
        .filter(Job.status == "DONE")
        .scalar()
        or 0
    )

    # Count failed jobs (defect indicator)
    failed = (
        db.query(func.count(Job.id))
        .filter(Job.status == "FAILED")
        .scalar()
        or 0
    )

    # Average confidence across all results.
    # Returns None if no results exist (handled by schema).
    avg_conf = db.query(func.avg(Result.confidence)).scalar()

    return AnalyticsOut(
        total_jobs=total,
        done_jobs=done,
        failed_jobs=failed,
        avg_confidence=avg_conf,
    )

