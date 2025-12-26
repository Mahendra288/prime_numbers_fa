import json
import logging
from enum import Enum
from typing import List

from fastapi import APIRouter, Query, HTTPException
from sqlalchemy.orm import Session
from opentelemetry import trace

from db.session import SessionLocal
from models.prime_number_request import PrimeNumberRequest, PrimeNumberRequestStatus

router = APIRouter()
tracer = trace.get_tracer(__name__)

from pydantic import BaseModel

class FetchPrimesResponseModel(BaseModel):
    request_id: str

class PrimesRequestStatusResponseModel(BaseModel):
    request_id: str
    status: PrimeNumberRequestStatus
    result: List[int]


@router.get("/primes/fetch/v1/", response_model=FetchPrimesResponseModel)
def start_prime_request(no_of_primes: int = Query(..., gt=0)):
    from find_primes.tasks.prime_calculation import find_n_primes

    db: Session = SessionLocal()
    try:
        prime_request = PrimeNumberRequest(
            no_of_primes=no_of_primes,
            status=PrimeNumberRequestStatus.QUEUED
        )
        db.add(prime_request)
        db.commit()
        db.refresh(prime_request)

        with tracer.start_as_current_span("fastapi-server.find-primes-api") as span:
            async_task = find_n_primes.delay(
                no_of_primes=no_of_primes,
                request_id=prime_request.request_id
            )

            # update celery task id in DB
            prime_request.celery_req_id = async_task.id
            db.add(prime_request)
            db.commit()

            # OpenTelemetry span attributes
            span.set_attribute("celery_req_id", async_task.id)
            span.set_attribute("prime_number_request_id", prime_request.request_id)
            span.add_event(f"Pushed to Celery queue: {async_task.id}")

        response = {"request_id": prime_request.request_id}
        logging.info(f"API Response: {json.dumps(response)}")
        return response

    finally:
        db.close()

@router.get("/primes_request/status/v1/", response_model=PrimesRequestStatusResponseModel)
def get_prime_request_status(request_id: str = Query(...)):
    db: Session = SessionLocal()
    try:
        prime_request = db.query(PrimeNumberRequest).filter(
            PrimeNumberRequest.request_id == request_id
        ).first()

        if not prime_request:
            raise HTTPException(status_code=404, detail="Request ID not found")

        result_dict = json.loads(prime_request.result) if prime_request.result else {}
        primes = result_dict.get("primes", [])

        response = {
            "request_id": prime_request.request_id,
            "status": prime_request.status.value if isinstance(prime_request.status, Enum) else prime_request.status,
            "result": primes
        }

        logging.info(f"API Response: {json.dumps(response)}")
        return response

    finally:
        db.close()
