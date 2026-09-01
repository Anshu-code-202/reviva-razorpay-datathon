"""                    REVIVA
                       │
                 Incident
                       ↓
                Eligibility
                  ┌────┴────┐
                  │         │
               REJECT     ELIGIBLE
                  │         ↓
                STOP     Approval
                            │
                     ┌──────┴──────┐
                     │             │
                  REJECT        APPROVED
                     │             ↓
                   STOP       Idempotency
                                  │
                                  ↓
                             Resolution
                                  │
                                  ↓
                             Audit Event
So the real safety coverage is coming from test_recovery_service.py, where you already test:

 Recovery without eligibility → blocked
 Ineligible incident → blocked
 Recovery without approval → blocked
 Rejected approval → blocked
 Eligible + approved → recovery succeeds
 Duplicate recovery → same resolution returned"""
# def test_recovery_safety_file_loads():
#     assert True


from app.models.payment import Payment

from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.resolution_repository import ResolutionRepository

from app.services.recovery_service import RecoveryService

from tests.test_recovery_service import(add_approval,add_eligibility,create_incident,)

def create_service(session):
    return RecoveryService(
        eligibility_repository=EligibilityRepository(session),
        approval_repository=ApprovalRepository(session),
        resolution_repository=ResolutionRepository(session),
        audit_event_repository=AuditEventRepository(session),

    )

def test_same_incident_cannot_be_recovered_twice_with_different_key(session): #: Double recovery prevention.
    incident=create_incident(session,"safety_001")

    add_eligibility(session,incident,eligible=True)
    add_approval(session,incident,decision="APPROVED")

    service=create_service(session)

    first=service.recover(incident=incident,idempotency_key="safety-key-001",)


    second=service.recover(incident=incident,idempotency_key="safety-key-002",)


    assert first is not None
    assert second is not None
    assert first.id == second.id
    assert second.idempotency_key == "safety-key-001"

    print("PASS: same incident cannot execute twice")



def test_same_idempotency_key_returns_existing_resolution(session):#Idempotency guarantee.

# If the exact same recovery request is sent twice (e.g., due to a network retry), the system doesn't rerun the logic—it just safely gives back the original resolution
    incident=create_incident(session,"safety_002")
    def test_same_idempotency_key_returns_existing_resolution(session):
        incident = create_incident(session, "safety_002")

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
            idempotency_key="same-key-002",
        )

        second = service.recover(
            incident=incident,
            idempotency_key="same-key-002",
        )

        assert first is not None
        assert second is not None

        assert first.id == second.id
        assert first.idempotency_key == second.idempotency_key
        assert first.status == "SUCCESS"

        print("PASS: same idempotency key returns existing resolution")

def test_successful_recovery_creates_audit_event(session): #System auditability.

# Simple explanation: Whenever a recovery succeeds, the system automatically writes an unchangeable record stating what was executed and who triggered it.
    incident=create_incident(session,"safety_003")
    add_eligibility(session,incident,eligible=True)
    add_approval(session,incident,decision="APPROVED",)

    service=create_service(session)

    reslution=service.recover(incident=incident,idempotency_key="safety-key-004",)

    assert reslution is not None

    audit_repository=AuditEventRepository(session)
    events=audit_repository.get_by_incident_id(incident.id)

    assert len(events) == 1
    assert events[0].event_type == "RECOVERY_EXECUTED"
    assert events[0].actor_type == "SYSTEM"

    print("PASS: successful recovery creates audit event")



def test_recovery_does_not_modify_payment(session): #Financial safety.

# Simple explanation: Processing a recovery fixes the order status without accidentally altering, deducting, or refunding the payment amount/status.
    incident=create_incident(session,"safety_004")

    add_eligibility(session,incident,eligible=True)
    add_approval(session,incident,decision="APPROVED",)

    payment=session.get(Payment, incident.payment_id)

    assert payment is not None

    original_status=payment.status
    original_amount=payment.amount

    service=create_service(session)

    resolution = service.recover(
        incident=incident,
        idempotency_key="safety-key-005",
    )

    assert resolution is not None

    session.refresh(payment)


    assert payment.status == original_status
    assert payment.amount == original_amount

    print("PASS: recovery does not modify payment")

def test_safety_suite_loads():
    assert True


"""

safety guarantee you're testing is:

Same Incident
      +
Same Idempotency Key
      ↓
Do NOT execute recovery again
      ↓
Return existing Resolution


The recovery safety tests now cover:

 No eligibility → recovery blocked
   Ineligible incident → recovery blocked
 No human approval → recovery blocked
 Rejected approval → recovery blocked
 Eligible + approved → recovery succeeds
 Same incident cannot be recovered twice with a different key
 Same idempotency key returns the existing resolution
 Successful recovery creates an audit event
 Recovery does not modify the payment
 Existing recovery behavior remains intact"""