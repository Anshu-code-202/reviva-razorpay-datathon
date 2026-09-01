# seeding refers to populating a database with an initial set of data.
from app.db.session import SessionLocal
from app.models.payment import Payment
from app.models.order import Order


def main():
    session = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Get or create test payment
        # ---------------------------------------------------------
        payment = (
            session.query(Payment)
            .filter(Payment.payment_id == "pay_test_001")
            .first()
        )

        if payment is None:
            payment = Payment(
                payment_id="pay_test_001",
                merchant_id="merchant_test_001",
                amount=500,
                currency="INR",
                status="CAPTURED",
            )

            session.add(payment)
            session.flush()

            print("Created test payment.")
        else:
            print("Test payment already exists. Reusing it.")

        # ---------------------------------------------------------
        # 2. Get or create test order
        # ---------------------------------------------------------
        order = (
            session.query(Order)
            .filter(Order.order_id == "order_test_001")
            .first()
        )

        if order is None:
            order = Order(
                order_id="order_test_001",
                merchant_id="merchant_test_001",
                payment_id=payment.id,
                amount=500,
                currency="INR",
                status="FAILED",
            )

            session.add(order)
            session.flush()

            print("Created test order.")
        else:
            print("Test order already exists. Reusing it.")

        session.commit()

        print("\nREVIVA test data ready.")
        print(f"payment_id   = {payment.payment_id}")
        print(f"payment DB id = {payment.id}")
        print(f"payment status = {payment.status}")
        print(f"order_id     = {order.order_id}")
        print(f"order DB id   = {order.id}")
        print(f"order status  = {order.status}")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
