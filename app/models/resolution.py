# Why idempotency_key is critical

# This is one of the most important fields in your whole project:

# idempotency_key
#         ↓
# Same resolution request twice
#         ↓
# Same key
#         ↓
# Do NOT execute twice
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Resolution(Base):
    __tablename__ = "resolutions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    approval_id: Mapped[int] = mapped_column(
        ForeignKey("approvals.id"),
        nullable=False,
        index=True,
    )

    resolution_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    incident: Mapped["Incident"] = relationship(
        "Incident",
    )

    approval: Mapped["Approval"] = relationship(
        "Approval",
    )