import logging
import os
import socket

from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import Resource

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def init_fastapi_otel(app):
    """
    Initialize OpenTelemetry for FastAPI.
    Call this ONCE during app startup.
    """

    resource = Resource.create({
        "service.name": "fastapi-server",
        "service.instance.id": f"{socket.gethostname()}-{os.getpid()}",
    })

    # Traces
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="http://otel-collector:4318/v1/traces"
            )
        )
    )
    trace.set_tracer_provider(trace_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint="http://otel-collector:4318/v1/metrics"
        ),
        export_interval_millis=10_000,
    )
    metrics.set_meter_provider(
        MeterProvider(resource=resource, metric_readers=[metric_reader])
    )

    # Logs
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(
                endpoint="http://otel-collector:4318/v1/logs"
            )
        )
    )

    handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider,
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    LoggingInstrumentor().instrument(set_logging_format=True)

    # FastAPI instrumentation
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace_provider,
    )
