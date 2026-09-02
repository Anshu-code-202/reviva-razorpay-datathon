"""API end-to-end acceptance test for REVIVA.

This test verifies that a client can use REVIVA through the public API
from incident detection through successful recovery.

Flow:

POST /incidents/detect
        ↓
incident_id
        ↓
POST /incidents/{incident_id}/eligibility
        ↓
eligible = true
        ↓
POST /incidents/{incident_id}/approval
        ↓
APPROVED
        ↓
POST /incidents/{incident_id}/recovery
        ↓
SUCCESS

This is a product-level acceptance test proving that the API,
domain services, database, eligibility, approval, recovery, and
idempotency boundaries work together.
"""

from app.models.audit import AuditEvent

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.order import Order
from app.models.payment import Payment


client = TestClient(app)


def test_api_end_to_end_recovery():
    session = SessionLocal()

    # Use unique identifiers for every test execution.
    # This prevents collisions with previous test data.
    run_id = uuid.uuid4().hex[:8]

    payment_id = f"pay_api_e2e_{run_id}"
    order_id = f"order_api_e2e_{run_id}"
    idempotency_key = f"idem_api_e2e_{run_id}"

    try:
        # ---------------------------------------------------------
        # 1. Arrange: create a captured payment
        # ---------------------------------------------------------

        payment = Payment(
            payment_id=payment_id,
            merchant_id="merchant_e2e_001",
            amount=Decimal("100.00"),
            currency="INR",
            status="CAPTURED",
            captured_at=datetime.now(timezone.utc),
        )

        session.add(payment)
        session.flush()

        # ---------------------------------------------------------
        # 2. Arrange: create a failed order linked to payment
        # ---------------------------------------------------------

        order = Order(
            order_id=order_id,
            merchant_id="merchant_e2e_001",
            payment_id=payment.id,
            amount=Decimal("100.00"),
            currency="INR",
            status="FAILED",
        )

        session.add(order)
        session.commit()

        # ---------------------------------------------------------
        # 3. Detect incident through the public API
        # ---------------------------------------------------------

        response = client.post(
            "/incidents/detect",
            json={
                "payment_id": payment_id,
                "order_id": order_id,
            },
        )

        assert response.status_code == 200

        incident = response.json()

        assert incident["payment_id"] == payment.id
        assert incident["order_id"] == order.id
        assert incident["type"] == "CAPTURED_PAYMENT_ORDER_FAILURE"
        assert incident["status"] == "DETECTED"

        incident_id = incident["incident_id"]

        # ---------------------------------------------------------
        # 4. Evaluate eligibility through the API
        # ---------------------------------------------------------

        response = client.post(
            f"/incidents/{incident_id}/eligibility"
        )

        assert response.status_code == 200

        eligibility = response.json()

        assert eligibility["eligible"] is True

        # ---------------------------------------------------------
        # 5. Approve recovery through the API
        # ---------------------------------------------------------

        response = client.post(
            f"/incidents/{incident_id}/approval",
            json={
                "approved_by": "ops_manager_e2e",
                "reason": "Approved for E2E recovery test",
            },
        )

        assert response.status_code == 200

        approval = response.json()

        assert approval["decision"] == "APPROVED"

        # ---------------------------------------------------------
        # 6. Execute recovery through the API
        # ---------------------------------------------------------

        response = client.post(
            f"/incidents/{incident_id}/recovery",
            json={
                "idempotency_key": idempotency_key,
            },
        )

        assert response.status_code == 200

        recovery = response.json()

        assert recovery["resolution_type"] == "REPROCESS_ORDER_CONFIRMATION"
        assert recovery["status"] == "SUCCESS"

    finally:
        session.rollback()
        session.close()

                # ---------------------------------------------------------
        # 7. Verify audit trail in the database
        # ---------------------------------------------------------

        audit_session = SessionLocal()

        try:
            audit_events = (
                audit_session.query(AuditEvent)
                .filter(AuditEvent.incident_id == incident["id"])
                .all()
            )

            assert len(audit_events) == 1

            audit_event = audit_events[0]

            assert audit_event.event_type == "RECOVERY_EXECUTED"
            assert audit_event.actor_type == "SYSTEM"
            assert audit_event.actor_id is None
            assert audit_event.incident_id == incident["id"]

            assert (
                "REPROCESS_ORDER_CONFIRMATION"
                in audit_event.description
            )

        finally:
            audit_session.close()