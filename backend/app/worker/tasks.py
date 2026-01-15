import random
import time
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Job, Result

LABELS = ["PASS", "REVIEW", "FAIL"]


def process_job(job_id: int):
    db: Session = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return {"ok": False, "reason": "Job not found"}

        job.status = "PROCESSING"
        db.commit()

        # Simulated AI latency
        time.sleep(1.5)

        if "crash" in job.input_text.lower():
            job.status = "FAILED"
            db.commit()
            return {"ok": False, "reason": "Simulated model crash"}

        label = random.choice(LABELS)
        confidence = round(random.uniform(0.50, 0.99), 2)

        res = Result(job_id=job_id, label=label, confidence=confidence)
        db.add(res)
        job.status = "DONE"
        db.commit()

        return {"ok": True, "label": label, "confidence": confidence}
    finally:
        db.close()
