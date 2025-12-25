import enum
from uuid import uuid4
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Enum as SQLEnum,
)
from db.base import Base

class PrimeNumberRequestStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    FAILED = "FAILED"

def generate_uuid():
    return str(uuid4())

class PrimeNumberRequest(Base):
    __tablename__ = "prime_number_requests"

    request_id = Column(
        String(255),
        primary_key=True,
        default=generate_uuid,
        index=True,
    )

    no_of_primes = Column(Integer, nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    status = Column(
        SQLEnum(PrimeNumberRequestStatus, name="prime_number_request_status"),
        nullable=False,
        default=PrimeNumberRequestStatus.QUEUED,
    )
    completed_at = Column(DateTime, nullable=True)
    result = Column(Text, default="{}", nullable=False)

    # Monitoring fields
    celery_req_id = Column(String(255), nullable=True)
