from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import Base, engine, SessionLocal
from .seed import seed_users
from .routes import auth, jobs, analytics, admin
import logging
logging.basicConfig(level=logging.INFO)


app = FastAPI(title="AI Refinery QA Lab")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()

app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(analytics.router)
app.include_router(admin.router)
