"""                    REVIVA
                       │
        ┌──────────────┴──────────────┐
        ↓                             ↓
 Payment/Order                  AI Classification
        │                             │
        ↓                             ↓
 Incident Detection             Bounded Enum
        │                             │
        ↓                             │
 Eligibility ◄────────────────────────┘
        │
        ↓
 Human Approval
        │
        ↓
 Guardrails + Idempotency
        │
        ↓
 Recovery
        │
        ↓
 Audit"""
from enum import Enum

from app.models.incident import Incident
from app.models.order import Order
from app.models.payment import Payment

class RecoveryRecommendation(str,Enum):
    REPROCESS_ORDER_CONFIRMATION_CANDIDATE=(
        "REPROCESS_ORDER_CONFIRMATION_CANDIDATE"
    )
    NO_ACTION_ALREADY_RESOLVED="NO_ACTION_ALREADY_RESOLVED"
    MANUAL_REVIEW="MANUAL_REVIEW"
    REQUEST_MISSING_EVIDENCE="REQUEST_MISSING_EVIDENCE"

class IncidentClassifier:
    """classifies an incident into a bounded recovery recommendation.
    
    The classifier does NOT:
    -  execute recovery
    -  approve recovery
    -  determine final eligibility
    -  move money
      
    
    It only produces a bounded recommendation.
        """
    def classify(self,incident:Incident,payment:Payment | None,order:Order | None,)->RecoveryRecommendation:

         # Missing evidence must never result in an automated recovery recommendation.
        if payment is None or order is None:
            return RecoveryRecommendation.REQUEST_MISSING_EVIDENCE

        # payment is no longer captured
        if payment.status != "CAPTURED":
            return RecoveryRecommendation.NO_ACTION_ALREADY_RESOLVED

        # the order has already progressed successfully
        if order.status in  {"CONFIRMED","FULFILLED"}:
            return RecoveryRecommendation.NO_ACTION_ALREADY_RESOLVED

        # The canonical REVIVA incident:
        # captured payment + failed order.

        if (incident.type == "CAPTURED_PAYMENT_ORDER_FAILURE"
            and order.status == "FAILED"):

            return (RecoveryRecommendation.REPROCESS_ORDER_CONFIRMATION_CANDIDATE)

        #anything ambiguous goes to manual review.
        return RecoveryRecommendation.MANUAL_REVIEW


    # keep the LLM boundary explicit: in prompts.py
    
