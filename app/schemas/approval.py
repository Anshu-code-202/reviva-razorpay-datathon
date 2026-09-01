from datetime import datetime

from pydantic import BaseModel


class ApprovalRequest(BaseModel):
    approved_by:str
    reason:str | None=None

class ApprovalResponse(BaseModel):
    id: int
    incident_id: int
    decision: str
    approved_by: str
    reason: str | None
    decided_at: datetime