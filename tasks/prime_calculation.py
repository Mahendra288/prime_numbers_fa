import json
from opentelemetry import trace
from sqlalchemy.orm import Session

from celery_app.app import celery_app
from celery_app.traced_task import TracedTask
from db.session import SessionLocal
from business_logic import primes_calculation
tracer = trace.get_tracer(__name__)


@celery_app.task(base=TracedTask, bind=True)
def find_n_primes(self, no_of_primes: int, request_id: str):
    db: Session = SessionLocal()

    try:
        primes_calculation.mark_running(db, request_id)

        with tracer.start_as_current_span(
            "celery-worker.find-primes-core-logic"
        ) as span:
            span.set_attribute("no_of_primes", no_of_primes)
            span.set_attribute("request_id", request_id)

            primes = primes_calculation.find_primes(no_of_primes)
            result = {"primes": primes}

            span.add_event("prime numbers calculation completed")

        primes_calculation.mark_finished(db, request_id, result)
        return json.dumps(result)

    except Exception:
        primes_calculation.mark_failed(db, request_id)
        raise

    finally:
        db.close()
