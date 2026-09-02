# # This defines the shape of data entering/leaving the service/API.For example:

# IncidentResponse
# ----------------
# id
# payment_id
# order_id
# type
# status
# created_at
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentDetectionRequest(BaseModel):
    payment_id: str
    order_id: str


class IncidentDetectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: str
    payment_id: int
    order_id: int
    type: str
    status: str
    created_at: datetime
