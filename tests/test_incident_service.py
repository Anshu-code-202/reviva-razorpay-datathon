from app.models.payment import Payment
from app.models.order import Order

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.incident_repository import IncidentRepository

from app.services.incident_detection import IncidentDetectionService
from app.services.incident_service import IncidentService


def create_services(session):
    payment_repository = PaymentRepository(session)
    order_repository = OrderRepository(session)
    incident_repository = IncidentRepository(session)

    detection_service = IncidentDetectionService(
        payment_repository=payment_repository,
        order_repository=order_repository,
        incident_repository=incident_repository,
    )

    incident_service = IncidentService(
        incident_repository=incident_repository,
    )

    return detection_service, incident_service


def test_get_incident(session):
    payment = Payment(
        payment_id="pay_service_001",
        merchant_id="merchant_service_001",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_service_001",
        merchant_id="merchant_service_001",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    detection_service, incident_service = create_services(session)

    incident = detection_service.detect(
        payment_id="pay_service_001",
        order_id="order_service_001",
    )

    assert incident is not None

    fetched = incident_service.get_incident(
        incident.incident_id
    )

    assert fetched is not None
    assert fetched.id == incident.id


def test_update_incident_status(session):
    payment = Payment(
        payment_id="pay_service_002",
        merchant_id="merchant_service_002",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_service_002",
        merchant_id="merchant_service_002",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    detection_service, incident_service = create_services(session)

    incident = detection_service.detect(
        payment_id="pay_service_002",
        order_id="order_service_002",
    )

    assert incident is not None
    assert incident.status == "DETECTED"

    updated = incident_service.update_status(
        incident_id=incident.incident_id,
        status="PROCESSING",
    )

    assert updated is not None
    assert updated.status == "PROCESSING"