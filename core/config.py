from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Prime Numbers Backend"

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://redis_server:6379/0",
        description="Redis broker URL"
    )
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TIMEZONE: str = "Asia/Kolkata"
    CELERY_BROKER_TRANSPORT_OPTIONS: dict = {
        "visibility_timeout": 3600
    }

    # OpenTelemetry
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://otel-collector:4318"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
