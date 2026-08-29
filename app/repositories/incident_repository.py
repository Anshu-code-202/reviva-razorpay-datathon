# # Keeps database operations separate from business logic./IncidentDetectionService
#         ↓
# IncidentRepository
#         ↓
# SQLAlchemy
#         ↓
# PostgreSQL

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import Incident

class IncidentRepository:
    def __init__(self,session:Session):     #here repositroy recieves a SQLAlechemy database session
    
        self.session=session

    def find_existing( 
            self,payment_id:int,
            order_id:int,
            incident_type:str,
  )->Incident| None:
        statement=select(Incident).where( #first piece of idempotency.It asks PostgreSQL:

# "Does this exact incident already exist?"
            Incident.payment_id==payment_id,
            Incident.order_id==order_id,
            Incident.type==incident_type,)
        return self.session.scalar(statement)

 
# If incident does not exist earler then do create Incident
    def create(self,incident_id:str,  #creates the actual database object:
               payment_id:int,
               order_id:int,
               incident_type:str,
    )->Incident:
        incident=Incident(
            incident_id=incident_id,payment_id=payment_id,order_id=order_id,
            type=incident_type,
        )

        


        self.session.add(incident) #puts it into SQLAlchemy's pending transaction.
        self.session.flush() #sends the INSERT to PostgreSQL without committing the entire transaction yet
        
        return incident


#     So IncidentService cannot yet retrieve an incident by its public incident_id or update its status cleanly.

# 1. Extend IncidentRepository
    def get_by_incident_id(self,incident_id:str)->Incident|None:
        statement=select(Incident) .where(
            Incident.incident_id==incident_id)
        return self.session.scalars(statement).first()

    def update_status( #So the repository becomes responsible for database operations, while the service will decide whether a status transition is allowed.
            self,incident:Incident,status:str,
    )->Incident:
        incident.status=status
        self.session.flush()

        return incident