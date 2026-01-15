from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db import get_db
from ..models import Job, Result
from ..schemas import AnalyticsOut
from ..deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsOut)
def summary(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    total = db.query(func.count(Job.id)).scalar() or 0
    done = db.query(func.count(Job.id)).filter(Job.status == "DONE").scalar() or 0
    failed = db.query(func.count(Job.id)).filter(Job.status == "FAILED").scalar() or 0
    avg_conf = db.query(func.avg(Result.confidence)).scalar()
    return AnalyticsOut(total_jobs=total, done_jobs=done, failed_jobs=failed, avg_confidence=avg_conf)
