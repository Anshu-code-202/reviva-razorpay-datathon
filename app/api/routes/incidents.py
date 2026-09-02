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


from app.ai.classifier import IncidentClassifier

from app.db.session import SessionLocal
from app.repositories.incident_repository import IncidentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.incident import (
    IncidentClassificationResponse,
    IncidentDetectionRequest,
    IncidentDetectionResponse,
)
from app.repositories.audit_event_repository import AuditEventRepository
from app.schemas.incident import (
    AuditEventResponse,
    IncidentDetailResponse,
)


from app.services.incident_detection import IncidentDetectionService
from app.services.incident_service import IncidentService

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

 
@router.post(
    "/{incident_id}/classify",
    response_model=IncidentClassificationResponse,
)



def classify_incident(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident_repository = IncidentRepository(session)

    incident_service = IncidentService(
        incident_repository=incident_repository,
    )

    incident=incident_service.get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404,detail="Incident not found.",)

    classifier=IncidentClassifier()

    recommendation=classifier.classify(
        incident=incident,
        payment=incident.payment,
        order=incident.order,
    )

    return IncidentClassificationResponse(
        incident_id=incident.incident_id,
        recommendation=recommendation.value,
    )




@router.get(
    "/{incident_id}",
    response_model=IncidentDetailResponse,
)
def get_incident(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident_repository = IncidentRepository(session)

    incident = incident_repository.get_by_incident_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    return incident


@router.get(
    "/{incident_id}/audit",
    response_model=list[AuditEventResponse],
)
def get_incident_audit(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident_repository = IncidentRepository(session)

    incident = incident_repository.get_by_incident_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    audit_repository = AuditEventRepository(session)

    return audit_repository.get_by_incident_id(incident.id)



"""                    REVIVA API
                        │
              ┌─────────┴─────────┐
              │                   │
           WRITE                 READ
              │                   │
       ┌──────┴──────┐       ┌────┴─────┐
       │             │       │          │
     Detect       Classify  Incident   Audit
       │             │       │          │
       └──────┬──────┘       └────┬─────┘
              │                   │
         Eligibility              │
              │                   │
           Approval               │
              │                   │
           Recovery ──────────────┘"""