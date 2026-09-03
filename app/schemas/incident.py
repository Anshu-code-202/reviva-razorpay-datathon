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
from decimal import Decimal

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


class IncidentClassificationResponse(BaseModel):
    incident_id: str
    recommendation: str


class PaymentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: str
    amount: Decimal
    currency: str
    status: str


class OrderDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: str
    amount: Decimal
    currency: str
    status: str


class IncidentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: str
    payment_id: int
    order_id: int
    type: str
    status: str
    detected_at: datetime
    created_at: datetime
    updated_at: datetime
    payment: PaymentDetailResponse
    order: OrderDetailResponse


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    event_type: str
    actor_type: str
    actor_id: str | None
    description: str
    created_at: datetime