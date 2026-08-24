# incident_id
#     ↓
# Which incident was evaluated?

# eligible
#     ↓
# Can Reviva resolve it?

# reason
#     ↓
# Why?

# evaluated_by
#     ↓
# SYSTEM / HUMAN / AI

# evaluated_at
#     ↓
# When?

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EligibilityEvaluation(Base):
    __tablename__ = "eligibility_evaluations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    eligible: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evaluated_by: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="SYSTEM",
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    incident: Mapped["Incident"] = relationship(
        "Incident",
    )