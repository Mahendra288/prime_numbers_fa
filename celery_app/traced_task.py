from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.context import get_current

from celery_app.app import celery_app

propagator = TraceContextTextMapPropagator()


class TracedTask(celery_app.Task):
    abstract = True

    def apply_async(self, args=None, kwargs=None, **options):
        carrier = {}
        propagator.inject(carrier, context=get_current())

        headers = options.get("headers") or {}
        headers["tracing"] = carrier
        options["headers"] = headers

        return super().apply_async(args, kwargs, **options)
