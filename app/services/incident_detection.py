# IncidentDetectionService answers:

# Should an incident exist?
# This is the brain of deterministic incident detection.

# # It answers:"""Payment
#    +
# Order
#    ↓
# Business rules
#    ↓
# Should REVIVA create an incident?
#    ↓
# YES → create incident
# NO  → no incident"""

# "Does this payment/order combination represent an incident?"
    #              IncidentDetectionService
    #                        │
    #          ┌─────────────┴─────────────┐
    #          ↓                           ↓
    # PaymentRepository             OrderRepository
    #          ↓                           ↓
    #       Payment                     Order
    #          └─────────────┬─────────────┘
    #                        ↓
    #                 Business Rules
    #                        ↓
    #               IncidentRepository
    #                        ↓
    #                    PostgreSQL
from app.models.incident import Incident
from app.repositories.incident_repository import IncidentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository


CAPTURED_PAYMENT_ORDER_FAILURE = "CAPTURED_PAYMENT_ORDER_FAILURE"


class IncidentDetectionService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        order_repository: OrderRepository,
        incident_repository: IncidentRepository,
    ):
        self.payment_repository = payment_repository
        self.order_repository = order_repository
        self.incident_repository = incident_repository

    def detect(
        self,
        payment_id: str,
        order_id: str,
    ) -> Incident | None:

        # Fetch payment
        payment = self.payment_repository.get_by_payment(payment_id)

        if payment is None:
            return None

        # Fetch order
        order = self.order_repository.get_by_order_id(order_id)

        if order is None:
            return None

        # Rule 1:
        # Payment must be captured.
        if payment.status != "CAPTURED":
            return None

        # Rule 2:
        # Order must be failed.
        if order.status != "FAILED":
            return None

        # Rule 3:
        # Payment and order must belong to the same payment.
        if order.payment_id != payment.id:
            return None

        # Idempotency:
        # Do not create the same incident twice.
        existing_incident = self.incident_repository.find_existing(
            payment_id=payment.id,
            order_id=order.id,
            incident_type=CAPTURED_PAYMENT_ORDER_FAILURE,
        )

        if existing_incident is not None:
            return existing_incident

        # Deterministic incident ID.
        incident_id = (
            f"INC-{payment.payment_id}-{order.order_id}"
        )

        return self.incident_repository.create(
            incident_id=incident_id,
            payment_id=payment.id,
            order_id=order.id,
            incident_type=CAPTURED_PAYMENT_ORDER_FAILURE,
        )

#     The service answers one deterministic question:

# "Does this payment/order pair satisfy the canonical REVIVA incident definition?"