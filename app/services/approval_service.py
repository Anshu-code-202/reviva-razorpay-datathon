from app.models.approval import Approval
from app.models.incident import Incident
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.eligibility_repository import EligibilityRepository


class ApprovalService:
    def __init__(
        self,
        approval_repository: ApprovalRepository,
        eligibility_repository: EligibilityRepository,
    ):
        self.approval_repository = approval_repository
        self.eligibility_repository = eligibility_repository

    def approve(
        self,
        incident: Incident,
        approved_by: str,
        reason: str | None = None,
    ) -> Approval:

        evaluation = (
            self.eligibility_repository.get_latest_by_incident(
                incident.id
            )
        )

        if evaluation is None:
            raise ValueError(
                "Incident has not been evaluated for eligibility."
            )

        if evaluation.eligible is not True:
            raise ValueError(
                "Incident is not eligible for recovery."
            )

        if not approved_by.strip():
            raise ValueError(
                "Approver identity is required."
            )

        return self.approval_repository.create(
            incident_id=incident.id,
            decision="APPROVED",
            approved_by=approved_by,
            reason=reason,
        )