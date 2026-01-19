"""
FastAPI application bootstrap using Lifespan events (modern replacement
for deprecated @app.on_event startup/shutdown handlers).

Responsibilities:
- Configure middleware (CORS)
- Initialize application resources on startup (DB schema, seed data)
- Optionally clean up resources on shutdown
- Register API routers
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import Base, engine, SessionLocal
from .seed import seed_users
from .routes import auth, jobs, analytics, admin


# -------------------------------------------------
# Logging configuration
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -------------------------------------------------
# Lifespan event handler (startup + shutdown)
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    This replaces deprecated @app.on_event("startup") and ("shutdown").

    Startup responsibilities:
    - Create database tables (demo-safe, idempotent)
    - Seed baseline users for authentication testing

    Shutdown responsibilities:
    - Log shutdown event
    - Close or release shared resources if applicable

    Why this matters for QE:
    - Ensures deterministic startup state for SIT and automation
    - Supports stable, repeatable environments
    - Centralized lifecycle control
    """
    logger.info("Lifespan startup: initializing application resources...")

    # Initialize database schema
    Base.metadata.create_all(bind=engine)

    # Seed initial data (admin/viewer users)
    db = SessionLocal()
    try:
        seed_users(db)
        logger.info("Lifespan startup: database seeded successfully.")
    except Exception as exc:
        logger.exception("Startup failed during DB initialization: %s", exc)
        raise
    finally:
         # Always close the session to avoid leaks.
        db.close()

    # Yield control back to FastAPI (app starts accepting requests here)
    yield

    # Shutdown logic (optional but important for real systems)
    logger.info("Lifespan shutdown: application is shutting down.")


# -------------------------------------------------
# FastAPI application instance
# -------------------------------------------------
app = FastAPI(
    title="QA Lab",
    lifespan=lifespan,  
)


# -------------------------------------------------
# Middleware
# -------------------------------------------------
# CORS allows the browser-based UI (Next.js) to call the API.
# For demos you can allow "*", but for real production you should restrict.
#
# "allow_headers" must include Authorization for JWT auth.
#
# "allow_credentials=True" means cookies/credentials allowed;
# only use it with explicit allow_origins (not "*") in strict production setups
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # demo-friendly; production: settings.cors_list()
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # needed for Authorization header (JWT)
)

# -------------------------------------------------
# Router registration
# -------------------------------------------------
# Each router corresponds to a cohesive API area:
# - auth: login + token issuance
# - jobs: job submission + lifecycle status + results
# - analytics: rollups for dashboards
# - admin: restricted endpoints (health, metrics)
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(analytics.router)
app.include_router(admin.router)
