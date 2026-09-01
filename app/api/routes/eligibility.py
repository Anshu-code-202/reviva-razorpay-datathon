from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.eligibility_repository import EligibilityRepository
from app.repositories.incident_repository import IncidentRepository
from app.schemas.eligibility import EligibilityEvaluationResponse
from app.services.eligibility_service import EligibilityService


router = APIRouter(
    prefix="/incidents",
    tags=["Eligibility"],
)


def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@router.post(
    "/{incident_id}/eligibility",
    response_model=EligibilityEvaluationResponse,
)
def evaluate_eligibility(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident_repository = IncidentRepository(session)

    incident = incident_repository.get_by_incident_id(
        incident_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    service = EligibilityService(
        eligibility_repository=EligibilityRepository(session),
    )

    evaluation = service.evaluate(incident)

    session.commit()

    return evaluation