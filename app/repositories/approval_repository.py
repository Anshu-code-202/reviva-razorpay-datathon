from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import Approval

class ApprovalRepository:
    def __init__(self,session:Session):
        self.session=session

    def create(self,incident_id:int,decision:str,approved_by:str,reason:str|None=None,
               )->Approval:

        approval=Approval(incident_id=incident_id,
                 decision=decision,
                 approved_by=approved_by,
                 reason=reason,)
        self.session.add(approval)
        self.session.flush()

        return approval

    def get_latest_by_incident(self,incident_id:int,)->Approval|None:
        statement=(select(Approval)
                   .where(Approval.incident_id==incident_id)
                   .order_by(Approval.decided_at.desc()
                    )
                    )

        return self.session.scalars(statement).first()
        