import pytest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.order import Order
from app.models.incident import Incident

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.incident_repository import IncidentRepository

from app.services.incident_detection import IncidentDetectionService

DATABASE_URL = "postgresql+psycopg://postgres:MyNewPassword123%21@localhost:5432/reviva"


def create_service(session):
    return IncidentDetectionService(
        payment_repository=PaymentRepository(session),
        order_repository=OrderRepository(session),
        incident_repository=IncidentRepository(session),
    )


def test_captured_failed_match(session):
    payment = Payment(
        payment_id="pay_case_001",
        merchant_id="merchant_case_001",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_case_001",
        merchant_id="merchant_case_001",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_001",
        order_id="order_case_001",
    )

    assert incident is not None
    assert incident.type == "CAPTURED_PAYMENT_ORDER_FAILURE"

    print("PASS: CAPTURED + FAILED + MATCH -> CREATE")


def test_failed_failed_match(session):
    payment = Payment(
        payment_id="pay_case_002",
        merchant_id="merchant_case_002",
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_case_002",
        merchant_id="merchant_case_002",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_002",
        order_id="order_case_002",
    )

    assert incident is None

    print("PASS: FAILED + FAILED + MATCH -> NO INCIDENT")


def test_captured_confirmed(session):
    payment = Payment(
        payment_id="pay_case_003",
        merchant_id="merchant_case_003",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_case_003",
        merchant_id="merchant_case_003",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="CONFIRMED",
    )

    session.add(order)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_003",
        order_id="order_case_003",
    )

    assert incident is None

    print("PASS: CAPTURED + CONFIRMED -> NO INCIDENT")


def test_captured_failed_mismatch(session):
    payment_a = Payment(
        payment_id="pay_case_004_a",
        merchant_id="merchant_case_004",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    payment_b = Payment(
        payment_id="pay_case_004_b",
        merchant_id="merchant_case_004",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add_all([payment_a, payment_b])
    session.flush()

    order = Order(
        order_id="order_case_004",
        merchant_id="merchant_case_004",
        payment_id=payment_b.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_004_a",
        order_id="order_case_004",
    )

    assert incident is None

    print("PASS: CAPTURED + FAILED + MISMATCH -> NO INCIDENT")


def test_missing_payment(session):
    order_payment = Payment(
        payment_id="pay_case_005_real",
        merchant_id="merchant_case_005",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(order_payment)
    session.flush()

    order = Order(
        order_id="order_case_005",
        merchant_id="merchant_case_005",
        payment_id=order_payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_005_missing",
        order_id="order_case_005",
    )

    assert incident is None

    print("PASS: MISSING PAYMENT -> NO INCIDENT")


def test_missing_order(session):
    payment = Payment(
        payment_id="pay_case_006",
        merchant_id="merchant_case_006",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_006",
        order_id="order_case_006_missing",
    )

    assert incident is None

    print("PASS: MISSING ORDER -> NO INCIDENT")


def main():
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        test_captured_failed_match(session)
        session.rollback()

    with Session(engine) as session:
        test_failed_failed_match(session)
        session.rollback()

    with Session(engine) as session:
        test_captured_confirmed(session)
        session.rollback()

    with Session(engine) as session:
        test_captured_failed_mismatch(session)
        session.rollback()

    with Session(engine) as session:
        test_missing_payment(session)
        session.rollback()

    with Session(engine) as session:
        test_missing_order(session)
        session.rollback()

    print("\nALL INCIDENT DETECTION CASES PASSED")

def test_database_prevents_duplicate_incident(session):
    payment = Payment(
        payment_id="pay_db_constraint_001",
        merchant_id="merchant_db_constraint_001",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_db_constraint_001",
        merchant_id="merchant_db_constraint_001",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    incident_1 = Incident(
        incident_id="INC-db-001",
        payment_id=payment.id,
        order_id=order.id,
        type="CAPTURED_PAYMENT_ORDER_FAILURE",
    )

    session.add(incident_1)
    session.flush()

    # Same payment + order + type.
    # Different incident_id, so the failure must come
    # from the new database-level unique constraint.
    incident_2 = Incident(
        incident_id="INC-db-002",
        payment_id=payment.id,
        order_id=order.id,
        type="CAPTURED_PAYMENT_ORDER_FAILURE",
    )

    session.add(incident_2)

    with pytest.raises(IntegrityError):
        session.flush()

    session.rollback()

    print("PASS: DATABASE PREVENTS DUPLICATE INCIDENT")

def test_detected_at_is_set_per_incident(session):#Is the timestamp generated when each incident is created, rather than once when the Python module is imported?
    payment = Payment(
        payment_id="pay_case_timestamp",
        merchant_id="merchant_timestamp",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_case_timestamp",
        merchant_id="merchant_timestamp",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    service = create_service(session)

    incident = service.detect(
        payment_id="pay_case_timestamp",
        order_id="order_case_timestamp",
    )

    assert incident is not None
    assert incident.detected_at is not None

    print("PASS: detected_at is generated per incident")


if __name__ == "__main__":
    main()