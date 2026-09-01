"""We want to see whether the complete chain works:
The E2E test proves that the pieces work together in the correct order.

What we proved with test_end_to_end_recovery.py

Your existing tests already proved things like:

Incident detection works.
Eligibility rules work.
Approval requires eligibility.
Recovery requires approval.
Recovery is idempotent.
Payment isn't modified.
Audit event can be created.

But we hadn't yet proved this single real workflow:


CAPTURED payment
      ↓
FAILED order
      ↓
DETECTED incident
      ↓
ELIGIBLE
      ↓
APPROVED
      ↓
SUCCESS resolution
      ↓
RECOVERY_EXECUTED audit
      ↓
payment unchanged
      ↓
second execution blocked"""
from decimal import Decimal

from sqlalchemy import select

from app.models.payment import Payment
from app.models.order import Order
from app.models.incident import Incident
from app.models.eligibility import EligibilityEvaluation
from app.models.approval import Approval
from app.models.resolution import Resolution
from app.models.audit import AuditEvent

from app.repositories.payment_repository import PaymentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.resolution_repository import ResolutionRepository
from app.repositories.audit_event_repository import AuditEventRepository

from app.services.incident_detection import IncidentDetectionService
from app.services.eligibility_service import EligibilityService
from app.services.approval_service import ApprovalService
from app.services.recovery_service import RecoveryService


def test_end_to_end_recovery_workflow(session):
    """
    Deterministic REVIVA happy-path workflow:

    detect
        -> eligibility
        -> approval
        -> recovery
        -> audit

    The test verifies the persisted PostgreSQL state.
    """

    # ---------------------------------------------------------
    # 1. CREATE CAPTURED PAYMENT
    # ---------------------------------------------------------

    payment = Payment(
        payment_id="pay_e2e_001",
        merchant_id="merchant_e2e_001",
        amount=Decimal("500.00"),
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    original_payment_status = payment.status
    original_payment_amount = payment.amount

    # ---------------------------------------------------------
    # 2. CREATE FAILED ORDER
    # ---------------------------------------------------------

    order = Order(
        order_id="order_e2e_001",
        merchant_id="merchant_e2e_001",
        payment_id=payment.id,
        amount=Decimal("500.00"),
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    # ---------------------------------------------------------
    # 3. DETECT INCIDENT
    # ---------------------------------------------------------

    incident_detection_service = IncidentDetectionService(
        payment_repository=PaymentRepository(session),
        order_repository=OrderRepository(session),
        incident_repository=IncidentRepository(session),
    )

    incident = incident_detection_service.detect(
        payment_id="pay_e2e_001",
        order_id="order_e2e_001",
    )

    assert incident is not None
    assert incident.type == "CAPTURED_PAYMENT_ORDER_FAILURE"
    assert incident.status == "DETECTED"

    # Verify incident persisted in PostgreSQL.
    persisted_incident = session.scalar(
        select(Incident).where(
            Incident.incident_id == "INC-pay_e2e_001-order_e2e_001"
        )
    )

    assert persisted_incident is not None
    assert persisted_incident.id == incident.id
    assert persisted_incident.status == "DETECTED"

    # ---------------------------------------------------------
    # 4. EVALUATE ELIGIBILITY
    # ---------------------------------------------------------

    eligibility_repository = EligibilityRepository(session)

    eligibility_service = EligibilityService(
        eligibility_repository=eligibility_repository,
    )

    evaluation = eligibility_service.evaluate(incident)

    assert evaluation is not None
    assert evaluation.eligible is True
    assert evaluation.evaluated_by == "SYSTEM"

    # Verify eligibility evaluation persisted.
    persisted_evaluation = session.scalar(
        select(EligibilityEvaluation)
        .where(
            EligibilityEvaluation.incident_id == incident.id
        )
        .order_by(
            EligibilityEvaluation.evaluated_at.desc()
        )
    )

    assert persisted_evaluation is not None
    assert persisted_evaluation.eligible is True

    # ---------------------------------------------------------
    # 5. HUMAN APPROVAL
    # ---------------------------------------------------------

    approval_repository = ApprovalRepository(session)

    approval_service = ApprovalService(
        approval_repository=approval_repository,
        eligibility_repository=eligibility_repository,
    )

    approval = approval_service.approve(
        incident=incident,
        approved_by="ops-manager-e2e",
        reason="Approved for deterministic MVP recovery test.",
    )

    assert approval is not None
    assert approval.decision == "APPROVED"
    assert approval.approved_by == "ops-manager-e2e"

    # Verify approval persisted.
    persisted_approval = session.scalar(
        select(Approval)
        .where(
            Approval.incident_id == incident.id
        )
        .order_by(
            Approval.decided_at.desc()
        )
    )

    assert persisted_approval is not None
    assert persisted_approval.decision == "APPROVED"
    assert persisted_approval.approved_by == "ops-manager-e2e"

    # ---------------------------------------------------------
    # 6. EXECUTE RECOVERY
    # ---------------------------------------------------------

    resolution_repository = ResolutionRepository(session)

    audit_event_repository = AuditEventRepository(session)

    recovery_service = RecoveryService(
        eligibility_repository=eligibility_repository,
        approval_repository=approval_repository,
        resolution_repository=resolution_repository,
        audit_event_repository=audit_event_repository,
    )

    idempotency_key = "e2e-recovery-pay_e2e_001"

    resolution = recovery_service.recover(
        incident=incident,
        idempotency_key=idempotency_key,
    )

    assert resolution is not None
    assert resolution.status == "SUCCESS"
    assert resolution.resolution_type == (
        "REPROCESS_ORDER_CONFIRMATION"
    )
    assert resolution.idempotency_key == idempotency_key
    assert resolution.executed_at is not None

    # ---------------------------------------------------------
    # 7. VERIFY RESOLUTION IN DATABASE
    # ---------------------------------------------------------

    persisted_resolution = session.scalar(
        select(Resolution).where(
            Resolution.idempotency_key == idempotency_key
        )
    )

    assert persisted_resolution is not None
    assert persisted_resolution.incident_id == incident.id
    assert persisted_resolution.approval_id == approval.id
    assert persisted_resolution.status == "SUCCESS"

    # ---------------------------------------------------------
    # 8. VERIFY AUDIT EVENT
    # ---------------------------------------------------------

    audit_events = list(
        session.scalars(
            select(AuditEvent).where(
                AuditEvent.incident_id == incident.id
            )
        ).all()
    )

    assert len(audit_events) == 1

    audit_event = audit_events[0]

    assert audit_event.event_type == "RECOVERY_EXECUTED"
    assert audit_event.actor_type == "SYSTEM"
    assert audit_event.actor_id is None
    assert "REPROCESS_ORDER_CONFIRMATION" in (
        audit_event.description
    )

    # ---------------------------------------------------------
    # 9. VERIFY PAYMENT WAS NOT MUTATED
    # ---------------------------------------------------------

    session.refresh(payment)

    assert payment.status == original_payment_status
    assert payment.amount == original_payment_amount

    # ---------------------------------------------------------
    # 10. VERIFY IDEMPOTENCY
    # ---------------------------------------------------------

    second_resolution = recovery_service.recover(
        incident=incident,
        idempotency_key=idempotency_key,
    )

    assert second_resolution is not None
    assert second_resolution.id == resolution.id

    # There must still be exactly one resolution.
    resolution_count = len(
        list(
            session.scalars(
                select(Resolution).where(
                    Resolution.incident_id == incident.id
                )
            ).all()
        )
    )

    assert resolution_count == 1

    # There must still be exactly one recovery audit event.
    audit_count = len(
        list(
            session.scalars(
                select(AuditEvent).where(
                    AuditEvent.incident_id == incident.id,
                    AuditEvent.event_type == "RECOVERY_EXECUTED",
                )
            ).all()
        )
    )

    assert audit_count == 1