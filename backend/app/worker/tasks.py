"""
Worker task logic to process a submitted Job and produce a Result.

Responsibilities:
- Update job status through lifecycle states
- Simulate AI inference latency
- Generate deterministic failure conditions for negative-path testing
- Persist results to the database

QE/SIT relevance:
- Enables system integration testing of async pipelines
- Provides controlled failure paths ("crash") for defect validation
- Supports regression testing for status transitions and data integrity
"""

import random
import time
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Job, Result


# Possible output labels from the simulated model
LABELS = ["PASS", "REVIEW", "FAIL"]


def process_job(job_id: int) -> dict:
    """
    Process a job and store its result.

    Args:
        job_id: Primary key of the Job to process.

    Returns:
        dict: A small status payload used for debugging/local runs.
              Example:
              {"ok": True, "label": "PASS", "confidence": 0.82}
              or
              {"ok": False, "reason": "Simulated model crash"}

    Flow:
    1) Fetch job by ID
    2) Mark job PROCESSING
    3) Simulate AI latency
    4) If input contains "crash" -> mark FAILED and exit
    5) Else generate label/confidence, store Result, mark DONE

    QE notes:
    - Status transitions are testable checkpoints for SIT automation.
    - Failure injection via "crash" is intentional to test error handling.
    """

    # Create a new DB session for this worker execution.
    # This is separate from API request sessions and prevents session-sharing bugs.
    db: Session = SessionLocal()

    try:
        # Retrieve the Job record
        job = db.get(Job, job_id)
        if not job:
            # Controlled failure response (helps troubleshooting / automation diagnostics)
            return {"ok": False, "reason": "Job not found"}

        # Mark job as processing early so UI/tests can observe lifecycle transition
        job.status = "PROCESSING"
        db.commit()

        # Simulated "AI inference" latency
        # In real systems, this might be a call to an ML model or external service.
        time.sleep(1.5)

        # Failure injection mechanism for negative testing.
        # This lets QE validate FAILED status, defect flows, and resilience.
        if "crash" in job.input_text.lower():
            job.status = "FAILED"
            db.commit()
            return {"ok": False, "reason": "Simulated model crash"}

        # Simulated model output
        label = random.choice(LABELS)
        confidence = round(random.uniform(0.50, 0.99), 2)

        # Create and persist the Result row
        res = Result(job_id=job_id, label=label, confidence=confidence)
        db.add(res)

        # Mark job as completed only after result is persisted successfully
        job.status = "DONE"
        db.commit()

        return {"ok": True, "label": label, "confidence": confidence}

    finally:
        # Always close DB session to prevent connection leaks
        db.close()
