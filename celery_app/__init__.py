from celery_app.app import celery_app
import app.celery_app.otel      # noqa
import app.celery_app.signals   # noqa

__all__ = ["celery_app"]
