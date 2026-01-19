from celery import Celery
from ..config import settings

celery = Celery(
    "refinery_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.task_routes = {"app.worker.tasks.*": {"queue": "refinery"}}