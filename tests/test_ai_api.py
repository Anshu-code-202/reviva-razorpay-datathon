
from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.order import Order


client = TestClient(app)


def test_ai_classification_api_returns_recommendation():
    payment_id = f"pay_ai_api_{uuid4().hex}"
    order_id = f"order_ai_api_{uuid4().hex}"

    session = SessionLocal()

    try:
        payment = Payment(
            payment_id=payment_id,
            merchant_id="merchant_ai_api",
            amount=Decimal("500.00"),
            currency="INR",
            status="CAPTURED",
        )

        session.add(payment)
        session.flush()

        order = Order(
            order_id=order_id,
            merchant_id="merchant_ai_api",
            payment_id=payment.id,
            amount=Decimal("500.00"),
            currency="INR",
            status="FAILED",
        )

        session.add(order)
        session.commit()

    finally:
        session.close()

    detect_response = client.post(
        "/incidents/detect",
        json={
            "payment_id": payment_id,
            "order_id": order_id,
        },
    )

    assert detect_response.status_code == 200

    incident = detect_response.json()
    incident_id = incident["incident_id"]

    classify_response = client.post(
        f"/incidents/{incident_id}/classify"
    )

    assert classify_response.status_code == 200

    result = classify_response.json()

    assert result["incident_id"] == incident_id
    assert (
        result["recommendation"]
        == "REPROCESS_ORDER_CONFIRMATION_CANDIDATE"
    )

