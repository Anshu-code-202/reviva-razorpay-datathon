# this is more directly connected to REVIVA's investigation process.
# Payment event
# Order event
#         ↓
#      Evidence
#         ↓
#      Incident
#         ↓
# Eligibility
# This is particularly important because REVIVA is supposed to correlate scattered payment/order events,
#  rather than letting an LLM simply guess the cause.

# it fits directly into REVIVA's event → evidence → incident investigation flow.

# Evidence
# --------------------------
# source_system
# source_event_id
# event_type
# occurred_at
# payload / details

from datetime import datetime,timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    evidence_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    source_system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_event_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    payload_details: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

#     Why these fields?

# Think about an actual REVIVA event:

# Evidence
# ------------------------------------
# evidence_id     = ev_123
# source_system   = PAYMENT_SYSTEM
# source_event_id = payment_event_456
# event_type      = PAYMENT_CAPTURED
# occurred_at     = 2026-08-25 10:30
# payload_details = {...}

# This gives REVIVA the raw facts it can use when investigating an incident.