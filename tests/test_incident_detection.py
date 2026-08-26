from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.order import Order

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.incident_repository import IncidentRepository

from app.services.incident_detection import IncidentDetectionService


DATABASE_URL = "postgresql+psycopg://postgres:MyNewPassword123%21@localhost:5432/reviva"


def main():
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:

        # Create test payment
        payment = Payment(
            payment_id="pay_incident_test_001",
            merchant_id="merchant_test_001",
            amount=500,
            currency="INR",
            status="CAPTURED",
        )

        session.add(payment)
        session.flush()

        # Create failed order linked to the payment
        order = Order(
            order_id="order_incident_test_001",
            merchant_id="merchant_test_001",
            payment_id=payment.id,
            amount=500,
            currency="INR",
            status="FAILED",
        )

        session.add(order)
        session.flush()

        # Create repositories
        payment_repository = PaymentRepository(session)
        order_repository = OrderRepository(session)
        incident_repository = IncidentRepository(session)

        # Create service
        service = IncidentDetectionService(
            payment_repository=payment_repository,
            order_repository=order_repository,
            incident_repository=incident_repository,
        )

        # First detection
        incident = service.detect(
            payment_id="pay_incident_test_001",
            order_id="order_incident_test_001",
        )

        assert incident is not None

        print("First detection:")
        print("Incident ID:", incident.incident_id)
        print("Incident Type:", incident.type)

        # Second detection - idempotency test
        same_incident = service.detect(
            payment_id="pay_incident_test_001",
            order_id="order_incident_test_001",
        )

        assert same_incident is not None
        assert incident.id == same_incident.id

        print("\nSecond detection:")
        print("Incident ID:", same_incident.incident_id)

        session.commit()

        print("\nINCIDENT DETECTION TEST PASSED")
        print("Idempotency verified")


if __name__ == "__main__":
    main()