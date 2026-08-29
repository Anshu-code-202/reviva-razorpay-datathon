from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.eligibility import EligibilityEvaluation


class EligibilityRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        incident_id: int,
        eligible: bool,
        reason: str,
        evaluated_by: str = "SYSTEM",
    ) -> EligibilityEvaluation:

        evaluation = EligibilityEvaluation(
            incident_id=incident_id,
            eligible=eligible,
            reason=reason,
            evaluated_by=evaluated_by,
        )

        self.session.add(evaluation)
        self.session.flush()

        return evaluation

    def get_latest_by_incident(
        self,
        incident_id: int,
    ) -> EligibilityEvaluation | None:

        statement = (
            select(EligibilityEvaluation)
            .where(
                EligibilityEvaluation.incident_id == incident_id
            )
            .order_by(
                EligibilityEvaluation.evaluated_at.desc()
            )
        )

        return self.session.scalars(statement).first()