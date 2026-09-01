            #       REVIVA
            #            │
            #  ┌─────────▼─────────┐
            #  │ Incident Detection│
            #  └─────────┬─────────┘
            #            ↓
            #  ┌───────────────────┐
            #  │ Incident Service  │
            #  └─────────┬─────────┘
            #            ↓
            #  ┌───────────────────┐
            #  │ Eligibility       │
            #  │ Deterministic     │
            #  └─────────┬─────────┘
            #            ↓
            #  ┌───────────────────┐
            #  │ Human Approval    │
            #  └─────────┬─────────┘
            #            ↓
            #  ┌───────────────────┐
            #  │ Recovery Service  │
            #  │ • eligibility     │
            #  │ • approval        │
            #  │ • idempotency     │
            #  └─────────┬─────────┘
            #            ↓
            #  ┌───────────────────┐
            #  │ Resolution        │
            #  └─────────┬─────────┘
            #            ↓
            #  ┌───────────────────┐
            #  │ Audit Event       │
            #  └───────────────────┘

                
from app.models.approval import Approval
from app.models.incident import Incident
from app.models.eligibility import EligibilityEvaluation
from app.models.payment import Payment
from app.models.order import Order

from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.resolution_repository import ResolutionRepository
from app.repositories.audit_event_repository import AuditEventRepository

from app.services.recovery_service import RecoveryService


def create_service(session):
    return RecoveryService(
        eligibility_repository=EligibilityRepository(session),
        approval_repository=ApprovalRepository(session),
        resolution_repository=ResolutionRepository(session),
        audit_event_repository=AuditEventRepository(session),
    )


def create_incident(session, suffix="001"):
    payment = Payment(
        payment_id=f"pay_recovery_{suffix}",
        merchant_id=f"merchant_recovery_{suffix}",
        amount=500,
        currency="INR",
        status="CAPTURED",
    )

    session.add(payment)
    session.flush()

    order = Order(
        order_id=f"order_recovery_{suffix}",
        merchant_id=f"merchant_recovery_{suffix}",
        payment_id=payment.id,
        amount=500,
        currency="INR",
        status="FAILED",
    )

    session.add(order)
    session.flush()

    incident = Incident(
        incident_id=f"INC-recovery-{suffix}",
        payment_id=payment.id,
        order_id=order.id,
        type="CAPTURED_PAYMENT_ORDER_FAILURE",
        status="DETECTED",
    )

    session.add(incident)
    session.flush()

    return incident


def add_eligibility(session, incident, eligible=True):
    evaluation = EligibilityEvaluation(
        incident_id=incident.id,
        eligible=eligible,
        reason=(
            "Incident satisfies MVP recovery eligibility rules."
            if eligible
            else "Incident is not eligible for recovery."
        ),
        evaluated_by="SYSTEM",
    )

    session.add(evaluation)
    session.flush()

    return evaluation


def add_approval(session, incident, decision="APPROVED"):
    approval = Approval(
        incident_id=incident.id,
        decision=decision,
        approved_by="operations_manager_001",
        reason="Approved for MVP recovery.",
    )

    session.add(approval)
    session.flush()

    return approval
def test_recovery_requires_eligibility(session):
    incident = create_incident(session, "001")

    service = create_service(session)

    resolution = service.recover(
        incident=incident,
        idempotency_key="recovery-key-001",
    )

    assert resolution is None

    print("PASS: recovery requires eligibility")


def test_recovery_rejects_ineligible_incident(session):
    incident = create_incident(session, "002")

    add_eligibility(
        session,
        incident,
        eligible=False,
    )

    add_approval(
        session,
        incident,
        decision="APPROVED",
    )

    service = create_service(session)

    resolution = service.recover(
        incident=incident,
        idempotency_key="recovery-key-002",
    )

    assert resolution is None

    print("PASS: ineligible incident cannot recover")


def test_recovery_requires_approval(session):
    incident = create_incident(session, "003")

    add_eligibility(
        session,
        incident,
        eligible=True,
    )

    service = create_service(session)

    resolution = service.recover(
        incident=incident,
        idempotency_key="recovery-key-003",
    )

    assert resolution is None

    print("PASS: recovery requires human approval")


def test_recovery_rejects_non_approved_decision(session):
    incident = create_incident(session, "004")

    add_eligibility(
        session,
        incident,
        eligible=True,
    )

    add_approval(
        session,
        incident,
        decision="REJECTED",
    )

    service = create_service(session)

    resolution = service.recover(
        incident=incident,
        idempotency_key="recovery-key-004",
    )

    assert resolution is None

    print("PASS: rejected approval cannot recover")


def test_successful_recovery(session):
    incident = create_incident(session, "005")

    add_eligibility(
        session,
        incident,
        eligible=True,
    )

    approval = add_approval(
        session,
        incident,
        decision="APPROVED",
    )

    service = create_service(session)

    resolution = service.recover(
        incident=incident,
        idempotency_key="recovery-key-005",
    )

    assert resolution is not None
    assert resolution.incident_id == incident.id
    assert resolution.approval_id == approval.id
    assert resolution.resolution_type == (
        "REPROCESS_ORDER_CONFIRMATION"
    )
    assert resolution.idempotency_key == "recovery-key-005"
    assert resolution.status == "SUCCESS"
    assert resolution.result == (
        "Order confirmation workflow reprocessed successfully."
    )
    assert resolution.executed_at is not None

    print("PASS: eligible + approved -> recovery SUCCESS")


def test_recovery_is_idempotent(session):
    incident = create_incident(session, "006")

    add_eligibility(
        session,
        incident,
        eligible=True,
    )

    add_approval(
        session,
        incident,
        decision="APPROVED",
    )

    service = create_service(session)

    first = service.recover(
        incident=incident,
        idempotency_key="recovery-key-006",
    )

    second = service.recover(
        incident=incident,
        idempotency_key="recovery-key-006",
    )

    assert first is not None
    assert second is not None

    assert first.id == second.id
    assert first.idempotency_key == second.idempotency_key

    print("PASS: duplicate recovery request is idempotent")

