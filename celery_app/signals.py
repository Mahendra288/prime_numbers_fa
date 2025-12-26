from celery.signals import task_prerun, task_postrun, task_failure
from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

tracer = trace.get_tracer(__name__)
propagator = TraceContextTextMapPropagator()


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, **kwargs):
    headers = task.request.get("headers", {})

    context = propagator.extract(headers)
    token = attach(context)
    task.request.otel_token = token

    span = tracer.start_span(
        name=f"celery.task.{task.name}",
        context=context,
    )
    span.set_attribute("celery.task_id", task_id)
    task.request.otel_span = span


@task_postrun.connect
def task_postrun_handler(task=None, **kwargs):
    if hasattr(task.request, "otel_span"):
        task.request.otel_span.set_attribute("celery.status", "success")
        task.request.otel_span.end()

    if hasattr(task.request, "otel_token"):
        detach(task.request.otel_token)


@task_failure.connect
def task_failure_handler(task=None, exception=None, **kwargs):
    if hasattr(task.request, "otel_span"):
        task.request.otel_span.set_attribute("celery.status", "failed")
        task.request.otel_span.record_exception(exception)
        task.request.otel_span.end()

    if hasattr(task.request, "otel_token"):
        detach(task.request.otel_token)
