from datetime import datetime
from sqlalchemy.orm import Session
import json
from models.prime_number_request import (
    PrimeNumberRequest,
    PrimeNumberRequestStatus,
)

def lock_request(db: Session, request_id: str) -> type[PrimeNumberRequest]:
    return (
        db.query(PrimeNumberRequest)
        .filter(PrimeNumberRequest.request_id == request_id)
        .with_for_update()
        .one()
    )


def mark_running(db: Session, request_id: str) -> None:
    with db.begin():
        req = lock_request(db, request_id)
        req.status = PrimeNumberRequestStatus.RUNNING


def mark_finished(db: Session, request_id: str, result: dict) -> None:
    with db.begin():
        req = lock_request(db, request_id)
        req.status = PrimeNumberRequestStatus.FINISHED
        req.completed_at = datetime.utcnow()
        req.result = json.dumps(result)


def mark_failed(db: Session, request_id: str) -> None:
    with db.begin():
        req = lock_request(db, request_id)
        req.status = PrimeNumberRequestStatus.FAILED
        req.completed_at = datetime.utcnow()


def is_prime_number(number: int) -> bool:
    if number < 2:
        return False
    for factor in range(2, int(number ** 0.5) + 1):
        if number % factor == 0:
            return False
    return True


def find_primes(n: int) -> list[int]:
    primes = []
    number = 2

    while len(primes) < n:
        if is_prime_number(number):
            primes.append(number)
        number += 1

    return primes
