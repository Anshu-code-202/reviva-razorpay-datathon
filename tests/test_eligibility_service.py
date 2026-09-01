from app.models.incident import Incident
from app.models.payment import Payment
from app.models.order import Order

from app.repositories.eligibility_repository import EligibilityRepository
from app.services.eligibility_service import EligibilityService

def create_service(session):
    return EligibilityService(
eligibility_repository=EligibilityRepository(session),
)

def test_eligible_captured_payment_order_failure(session):
# Create isolated test payment
    payment = Payment(
    payment_id="pay_eligibility_001",
    merchant_id="merchant_eligibility_001",
    amount=500,
    currency="INR",
    status="CAPTURED",
    )


    session.add(payment)
    session.flush()

# Create isolated test order
    order = Order(
        order_id="order_eligibility_001",
        merchant_id="merchant_eligibility_001",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    # Create isolated test incident
    incident = Incident(
        incident_id="INC-eligibility-001",
        payment_id=payment.id,
        order_id=order.id,
        type="CAPTURED_PAYMENT_ORDER_FAILURE",
        status="DETECTED",
    )

    session.add(incident)
    session.flush()

    service = create_service(session)

    evaluation = service.evaluate(incident)

    assert evaluation is not None
    assert evaluation.eligible is True
    assert evaluation.reason == (
        "Incident satisfies MVP recovery eligibility rules."
    )
    assert evaluation.evaluated_by == "SYSTEM"

print("PASS: DETECTED + CAPTURED_PAYMENT_ORDER_FAILURE -> ELIGIBLE")


def test_ineligible_non_detected_incident(session):
    payment = Payment(
    payment_id="pay_eligibility_002",
    merchant_id="merchant_eligibility_002",
    amount=500,
    currency="INR",
    status="CAPTURED",
    )


    session.add(payment)
    session.flush()

    order = Order(
        order_id="order_eligibility_002",
        merchant_id="merchant_eligibility_002",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    incident = Incident(
        incident_id="INC-eligibility-002",
        payment_id=payment.id,
        order_id=order.id,
        type="CAPTURED_PAYMENT_ORDER_FAILURE",
        status="PROCESSING",
    )

    session.add(incident)
    session.flush()

    service = create_service(session)

    evaluation = service.evaluate(incident)

    assert evaluation is not None
    assert evaluation.eligible is False
    assert evaluation.reason == (
        "Incident is not in DETECTED state."
    )
    assert evaluation.evaluated_by == "SYSTEM"

print("PASS: NON-DETECTED incident -> NOT ELIGIBLE")

