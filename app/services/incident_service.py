#IncidentService answers:How do we retrieve and manage an existing incident? # We first need to check your existing status conventions and repository capabilities so we don't introduce inconsistent lifecycle rules.Step 1: IncidentService

# Our first responsibility is incident retrieval and lifecycle status updates.

# The repository currently only knows how to:

# find_existing()
# create()

# So IncidentService cannot yet retrieve an incident by its public incident_id or update its status cleanly.


'''The important architecture principle remains:

Services contain business logic. Repositories contain persistence logic.

IncidentDetectionService
        │
        │ detects
        ▼
IncidentRepository
        │
        ▼
     Incident
        ▲
        │
IncidentService
        │
        ├── get_incident()
        └── update_status()
        IncidentDetectionService
        │
        │ detects
        ▼
IncidentRepository
        │
        ▼
     Incident
        ▲
        │
IncidentService
        │
        ├── get_incident()
        └── update_status()'''

from app.models.incident import Incident 
from app.repositories.incident_repository import IncidentRepository

class IncidentService:
    def __init__(self,incident_repository: IncidentRepository):
        self.incident_repository = incident_repository


    def get_incident(self,incident_id:str,)->Incident|None:
        return self.incident_repository.get_by_incident_id(
            incident_id
        )

    def update_status(self,incident_id:str,status:str,)->Incident | None:
        incident=self.incident_repository.get_by_incident_id(incident_id)

        if incident is None:
            return None

        return self.incident_repository.update_status(incident=incident,status=status,)
        