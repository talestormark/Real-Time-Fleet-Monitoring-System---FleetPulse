from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "fleetpulse",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "detect-incidents-every-minute": {
            "task": "app.worker.tasks.detect_incidents",
            "schedule": 60.0,  # Run every 60 seconds
        },
        "update-device-status-every-minute": {
            "task": "app.worker.tasks.update_device_status",
            "schedule": 60.0,
        },
    },
)
