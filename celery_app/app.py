from celery import Celery
from core.config import settings

celery_app = Celery("prime_numbers")

celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    result_backend=settings.CELERY_RESULT_BACKEND,
    timezone=settings.CELERY_TIMEZONE,
    broker_transport_options={
        "visibility_timeout": 3600
    },
)

celery_app.autodiscover_tasks(["tasks"])
