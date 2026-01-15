from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Job, Result
from ..schemas import JobCreate, JobOut, ResultOut
from ..deps import get_current_user
from ..worker.tasks import process_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobOut)
def create_job(data: JobCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    job = Job(input_text=data.input_text, submitted_by=user["username"], status="QUEUED")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Queue async processing
    process_job(job.id)  # run inline for local dev
    # process_job.delay(job.id)

    # process_job.delay(job.id)
    return job

@router.get("", response_model=list[JobOut])
def list_jobs(status: str | None = None, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    return q.order_by(Job.created_at.desc()).limit(100).all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@router.get("/{job_id}/result", response_model=ResultOut)
def get_result(job_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    res = db.query(Result).filter(Result.job_id == job_id).first()
    if not res:
        raise HTTPException(404, "Result not available")
    return res
