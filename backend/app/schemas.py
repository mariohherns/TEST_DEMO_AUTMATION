from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    username: str
    password: str

class JobCreate(BaseModel):
    input_text: str

class JobOut(BaseModel):
    id: int
    created_at: datetime
    status: str
    submitted_by: str

    class Config:
        from_attributes = True

class ResultOut(BaseModel):
    job_id: int
    label: str
    confidence: float
    processed_at: datetime

    class Config:
        from_attributes = True

class AnalyticsOut(BaseModel):
    total_jobs: int
    done_jobs: int
    failed_jobs: int
    avg_confidence: Optional[float] = None
