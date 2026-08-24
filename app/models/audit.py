# Incident
#    ↓
# Eligibility
#    ↓
# Approval
#    ↓
# Resolution
#    ↓
# AuditEvent
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    actor_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    incident: Mapped["Incident"] = relationship(
        "Incident",
    )