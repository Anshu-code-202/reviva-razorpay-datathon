from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


class AuditEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        incident_id: int,
        event_type: str,
        actor_type: str,
        description: str,
        actor_id: str | None = None,
    ) -> AuditEvent:

        event = AuditEvent(
            incident_id=incident_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            description=description,
        )

        self.session.add(event)
        self.session.flush()

        return event

    def get_by_incident_id(
        self,
        incident_id: int,
    ) -> list[AuditEvent]:

        statement = (
            select(AuditEvent)
            .where(
                AuditEvent.incident_id == incident_id
            )
            .order_by(
                AuditEvent.created_at.asc()
            )
        )

        return list(self.session.scalars(statement).all())