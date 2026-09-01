# Frontend / Postman / API Client
#              │
#              ▼
#         FastAPI API
#              │
#       ┌──────┴───────┐
#       ▼              ▼
#  Incident API    Recovery API
#       │              │
#       └──────┬───────┘
#              ▼
#         Service Layer
#              │
#         Repositories
#              │
#         PostgreSQL
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.incident_repository import IncidentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.incident import (
    IncidentDetectionRequest,
    IncidentDetectionResponse,
)
from app.services.incident_detection import IncidentDetectionService


router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@router.post(
    "/detect",
    response_model=IncidentDetectionResponse,
)
def detect_incident(
    request: IncidentDetectionRequest,
    session: Session = Depends(get_session),
):
    service = IncidentDetectionService(
        payment_repository=PaymentRepository(session),
        order_repository=OrderRepository(session),
        incident_repository=IncidentRepository(session),
    )

    incident = service.detect(
        payment_id=request.payment_id,
        order_id=request.order_id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="No matching REVIVA incident detected.",
        )

    session.commit()

    return incident 

    
