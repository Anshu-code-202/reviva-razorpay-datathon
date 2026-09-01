from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EligibilityEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    incident_id:int
    eligible:bool
    reason:str
    evaluated_by:str
    evaluated_at:datetime