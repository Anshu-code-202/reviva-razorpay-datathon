from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment

class PaymentRepository:
    def __init__(self,session:Session):
        self.session=session

    def get_by_payment(self,
        payment_id:str)->Payment|None:

        statement=select(Payment).where(
            Payment.payment_id==payment_id
        )
        return self.session.scalar(statement)