'''The service receives an existing Incident:

Incident
   ↓
EligibilityService.evaluate()
   ↓
Check rules
   ↓
ELIGIBLE / NOT ELIGIBLE
   ↓
EligibilityRepository
   ↓
EligibilityEvaluation'''

from app.models.eligibility import EligibilityEvaluation
from app.models.incident import Incident
from app.repositories.eligibility_repository import EligibilityRepository


class EligibilityService:
    def __init__(
        self,
        eligibility_repository: EligibilityRepository,
    ):
        self.eligibility_repository = eligibility_repository

    def evaluate(
        self,
        incident: Incident,
    ) -> EligibilityEvaluation:

        # Rule 1:
        # Incident must be in DETECTED state.
        if incident.status != "DETECTED":
            return self.eligibility_repository.create(
                incident_id=incident.id,
                eligible=False,
                reason="Incident is not in DETECTED state.",
                evaluated_by="SYSTEM",
            )

        # Rule 2:
        # MVP recovery is only allowed for the
        # canonical captured-payment/order-failure incident.
        if incident.type != "CAPTURED_PAYMENT_ORDER_FAILURE":
            return self.eligibility_repository.create(
                incident_id=incident.id,
                eligible=False,
                reason="Incident type is not eligible for MVP recovery.",
                evaluated_by="SYSTEM",
            )

        # All deterministic eligibility checks passed.
        return self.eligibility_repository.create(
            incident_id=incident.id,
            eligible=True,
            reason="Incident satisfies MVP recovery eligibility rules.",
            evaluated_by="SYSTEM",
        )
    