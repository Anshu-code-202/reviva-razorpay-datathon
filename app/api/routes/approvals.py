
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.approval_repository import ApprovalRepository
from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.incident_repository import IncidentRepository
from app.schemas.approval import ApprovalRequest, ApprovalResponse
from app.services.approval_service import ApprovalService


router = APIRouter(
    prefix="/incidents",
    tags=["Approvals"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/{incident_id}/approval",
    response_model=ApprovalResponse,
)
def approve_incident(
    incident_id: str,
    request: ApprovalRequest,
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

    service = ApprovalService(
        approval_repository=ApprovalRepository(db),
        eligibility_repository=EligibilityRepository(db),
    )

    try:
        approval = service.approve(
            incident=incident,
            approved_by=request.approved_by,
            reason=request.reason,
        )

        db.commit()

        return approval

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@router.get(
    "/{incident_id}/approval",
    response_model=ApprovalResponse,
)
def get_approval(
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

    approval_repository = ApprovalRepository(db)

    approval = approval_repository.get_latest_by_incident(
        incident.id
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="No approval found for this incident.",
        )

    return approval