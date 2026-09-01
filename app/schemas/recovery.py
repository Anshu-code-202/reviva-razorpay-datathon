from datetime import datetime

from pydantic import BaseModel


class RecoveryRequest(BaseModel):
    idempotency_key: str


class RecoveryResponse(BaseModel):
    id: int
    incident_id: int
    approval_id: int
    resolution_type: str
    idempotency_key: str
    status: str
    result: str | None
    executed_at: datetime | None
    created_at: datetime