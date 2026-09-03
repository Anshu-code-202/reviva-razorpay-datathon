from decimal import Decimal
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.payment import Payment
from app.models.order import Order

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.incident_repository import IncidentRepository

from app.services.incident_detection import IncidentDetectionService


router = APIRouter(
    prefix="/simulator",
    tags=["Simulator"],
)


class DemoScenarioRequest(BaseModel):
    payment_id: str = "pay_test_001"
    order_id: str = "order_test_001"
    merchant_id: str = "merchant_test_001"
    amount: Decimal = Decimal("500.00")
    currency: str = "INR"


@router.post("/create-scenario")
def create_demo_scenario(
    payload: DemoScenarioRequest,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Create CAPTURED payment
    # ---------------------------------------------------------

    payment = (
        db.query(Payment)
        .filter(Payment.payment_id == payload.payment_id)
        .first()
    )

    if payment is not None:
        raise HTTPException(
            status_code=409,
            detail="Payment already exists",
        )

    payment = Payment(
        payment_id=payload.payment_id,
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        currency=payload.currency,
        status="CAPTURED",
        captured_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.flush()

    # ---------------------------------------------------------
    # 2. Create FAILED order
    # ---------------------------------------------------------

    order = (
        db.query(Order)
        .filter(Order.order_id == payload.order_id)
        .first()
    )

    if order is not None:
        raise HTTPException(
            status_code=409,
            detail="Order already exists",
        )

    order = Order(
        order_id=payload.order_id,
        merchant_id=payload.merchant_id,
        payment_id=payment.id,
        amount=payload.amount,
        currency=payload.currency,
        status="FAILED",
    )

    db.add(order)
    db.flush()

    # ---------------------------------------------------------
    # 3. Run EXISTING REVIVA incident detection
    # ---------------------------------------------------------

    detection_service = IncidentDetectionService(
        payment_repository=PaymentRepository(db),
        order_repository=OrderRepository(db),
        incident_repository=IncidentRepository(db),
    )

    incident = detection_service.detect(
        payment_id=payment.payment_id,
        order_id=order.order_id,
    )

    if incident is None:
        db.rollback()

        raise HTTPException(
            status_code=422,
            detail="REVIVA could not detect an incident",
        )

    db.commit()
    db.refresh(incident)

    return {
        "status": "scenario_created",
        "payment": {
            "payment_id": payment.payment_id,
            "status": payment.status,
            "amount": str(payment.amount),
            "currency": payment.currency,
        },
        "order": {
            "order_id": order.order_id,
            "status": order.status,
        },
        "incident": {
            "incident_id": incident.incident_id,
            "type": incident.type,
            "status": incident.status,
        },
    }