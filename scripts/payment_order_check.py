from decimal import Decimal

from app.db.session import SessionLocal
from app.models import Payment, Order

db=SessionLocal()

try:
    payment=db.query(Payment).filter_by(
        payment_id="pay_test_001"
    ).first()

    if not payment:
        raise RuntimeError("Test payment not found")

    order=Order(
        order_id="order_test_001",
        merchant_id=payment.merchant_id,
        payment_id=payment.id,
        amount=Decimal("999.00"),
        currency="INR",
        status="FAILED",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    print("ORDER INSERT OK")
    print("Order ID:",order.id)

    print("Order:",order.order_id)

     # Test Order → Payment
    print("Order Payment:", order.payment.payment_id)

    # Test Payment → Order
    print("Payment Order:",payment.order.order_id)


finally:
    db.close()