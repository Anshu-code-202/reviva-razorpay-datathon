from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

from app.repositories.approval_repository import ApprovalRepository
from app.repositories.audit_event_repository import AuditEventRepository
from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.resolution_repository import ResolutionRepository

from app.schemas.recovery import RecoveryRequest,RecoveryResponse

from app.services.recovery_service import RecoveryService

router=APIRouter(prefix="/incidents",tags=["Recovery"],)

def get_db():
    db=SessionLocal()

    try:
        yield db

    finally:
        db.close()

@router.post("/{incident_id}/recovery",
             response_model=RecoveryResponse,)


def recover_incident(
    incident_id:str,
    request:RecoveryRequest,
    db:Session=Depends(get_db),
):
    incident_repository=IncidentRepository(db)
    incident=incident_repository.get_by_incident_id(
        incident_id

    )

    if incident is None:
        raise HTTPException(status_code=404,
                            detail="INCIDENT not found.",
                            )

    service=RecoveryService(
        eligibility_repository=EligibilityRepository(db),
        approval_repository=ApprovalRepository(db),
        resolution_repository=ResolutionRepository(db),
        audit_event_repository=AuditEventRepository(db),
    )

    resolution=service.recover(
        incident=incident,
        idempotency_key=request.idempotency_key,
    )

    if resolution is None:
        db.rollback()
        raise HTTPException(status_code=400,
                            detail=("Incident is not eligible for recovery,"
                                    "or required approval is missing."
                                    ),)

    db.commit()

    return resolution

@router.get(
    "/{incident_id}/recovery",
    response_model=RecoveryResponse,
)
def get_recovery(
    incident_id: str,
    db: Session = Depends(get_db),
):
    incident_repository = IncidentRepository(db)

    incident = incident_repository.get_by_incident_id(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    resolution_repository = ResolutionRepository(db)

    resolution = resolution_repository.get_by_incident_id(
        incident.id
    )

    if resolution is None:
        raise HTTPException(
            status_code=404,
            detail="No recovery found for this incident.",
        )

    return resolution