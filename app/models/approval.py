# Why Approval exists separately

# This is important for your project.

# We don't want:

# AI → automatically refund payment

# We want:

# AI/System
#    ↓
# Recommendation
#    ↓
# Eligibility
#    ↓
# Human Approval
#    ↓
# Resolution

# So Approval becomes a permanent record of:

# what decision was made
# who made it
# why
# when

from datetime import datetime,timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    decision: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    approved_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda:datetime.now(timezone.utc),
    )

    incident: Mapped["Incident"] = relationship(
        "Incident",
    )