from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_order_id(
        self,
        order_id: str,
    ) -> Order | None:
        statement = select(Order).where(
            Order.order_id == order_id
        )

        return self.session.scalar(statement)