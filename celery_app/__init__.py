from celery_app.app import celery_app
import celery_app.otel      # noqa
import celery_app.signals   # noqa

__all__ = ["celery_app"]
