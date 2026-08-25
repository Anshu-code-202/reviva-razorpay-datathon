from decimal import Decimal
from datetime import datetime,timezone

from app.db.session import SessionLocal
from app.models import Payment

db=SessionLocal()

try:
    payment=Payment(
        payment_id="pay_test_001",
        merchant_id="merchant_test_001",
        amount=Decimal("999.00"),
        currency="INR",
        status="CAPTURED",
        captured_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    print("INSERT OK")
    print("Payment ID:",payment.id)
    print("Payment:",payment.payment_id)

finally:
    db.close()