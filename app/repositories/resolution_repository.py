from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resolution import Resolution


class ResolutionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        incident_id: int,
        approval_id: int,
        resolution_type: str,
        idempotency_key: str,
    ) -> Resolution:

        resolution = Resolution(
            incident_id=incident_id,
            approval_id=approval_id,
            resolution_type=resolution_type,
            idempotency_key=idempotency_key,
        )

        self.session.add(resolution)
        self.session.flush()

        return resolution

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Resolution | None:

        statement = select(Resolution).where(
            Resolution.idempotency_key == idempotency_key
        )

        return self.session.scalar(statement)

    def get_by_incident_id(
        self,
        incident_id: int,
    ) -> Resolution | None:

        statement = select(Resolution).where(
            Resolution.incident_id == incident_id
        )

        return self.session.scalar(statement)
    