from datetime import datetime, timezone

from app.models.audit import AuditEvent
from app.models.incident import Incident
from app.models.resolution import Resolution

from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.resolution_repository import ResolutionRepository
from app.repositories.audit_event_repository import AuditEventRepository


class RecoveryService:
    """
    Orchestrates the safe MVP recovery workflow.

    Flow:

    Incident
        ↓
    Verify eligibility
        ↓
    Verify human approval
        ↓
    Check idempotency
        ↓
    Create Resolution
        ↓
    Create AuditEvent
    """

    def __init__(
        self,
        eligibility_repository: EligibilityRepository,
        approval_repository: ApprovalRepository,
        resolution_repository: ResolutionRepository,
        audit_event_repository: AuditEventRepository,
    ):
        self.eligibility_repository = eligibility_repository
        self.approval_repository = approval_repository
        self.resolution_repository = resolution_repository
        self.audit_event_repository = audit_event_repository

    def recover(
        self,
        incident: Incident,
        idempotency_key: str,
    ) -> Resolution | None:

        # ---------------------------------------------------------
        # 1. Verify eligibility
        # ---------------------------------------------------------

        evaluation = (
            self.eligibility_repository.get_latest_by_incident(
                incident.id
            )
        )

        if evaluation is None:
            return None

        if evaluation.eligible is not True:
            return None

        # ---------------------------------------------------------
        # 2. Verify human approval
        # ---------------------------------------------------------

        approval = (
            self.approval_repository.get_latest_by_incident(
                incident.id
            )
        )

        if approval is None:
            return None

        if approval.decision != "APPROVED":
            return None

        # ---------------------------------------------------------
        # 3. Check idempotency
        # ---------------------------------------------------------

        existing_resolution = (
            self.resolution_repository.get_by_idempotency_key(
                idempotency_key
            )
        )

        if existing_resolution is not None:
            return existing_resolution

        # Also prevent multiple resolutions for the same incident.
        existing_incident_resolution = (
            self.resolution_repository.get_by_incident_id(
                incident.id
            )
        )

        if existing_incident_resolution is not None:
            return existing_incident_resolution

        # ---------------------------------------------------------
        # 4. Create Resolution
        # ---------------------------------------------------------

        resolution = self.resolution_repository.create(
            incident_id=incident.id,
            approval_id=approval.id,
            resolution_type="REPROCESS_ORDER_CONFIRMATION",
            idempotency_key=idempotency_key,
        )

        resolution.status = "SUCCESS"
        resolution.result = (
            "Order confirmation workflow reprocessed successfully."
        )
        resolution.executed_at = datetime.now(timezone.utc)

        self.resolution_repository.session.flush()

        # ---------------------------------------------------------
        # 5. Create AuditEvent
        # ---------------------------------------------------------

        self.audit_event_repository.create(
            incident_id=incident.id,
            event_type="RECOVERY_EXECUTED",
            actor_type="SYSTEM",
            actor_id=None,
            description=(
                "REVIVA executed the approved "
                "REPROCESS_ORDER_CONFIRMATION recovery."
            ),
        )

        return resolution