from decimal import Decimal
from app.ai.classifier import (IncidentClassifier,RecoveryRecommendation,)

from app.models.incident import Incident
from app.models.payment import Payment
from app.models.order import Order

def make_payment(status="CAPTURED"):
    return Payment(
        payment_id="pay_ai_test",
        merchant_id="merchant_ai",
        amount=Decimal("100.00"),
        currency="INR",
        status=status,
    )

def make_order(status="FAILED"):
    return Order(
        order_id="order_ai_test",
        merchant_id="merchant_ai",
        payment_id=1,
        amount=Decimal("100.00"),
        currency="INR",
        status=status,
    )


def make_incident(incident_type="CAPTURED_PAYMENT_ORDER_FAILURE"):
    return Incident(
        incident_id="INC-AI-TEST",
        payment_id=1,
        order_id=1,
        type=incident_type,
        status="DETECTED",
    )

def test_captured_payment_failed_order_is_recovery_candidate():

    classifier=IncidentClassifier()

    result=classifier.classify(
        make_incident(),make_payment("CAPTURED"),make_order("FAILED"),

    )

    assert (result == RecoveryRecommendation.REPROCESS_ORDER_CONFIRMATION_CANDIDATE
    )


def test_confirmed_order_requires_no_action():
    classifier=IncidentClassifier()

    result=classifier.classify(
        make_incident(),make_payment("CAPTURED"),make_order("CONFIRMED"),
    )

    assert result == RecoveryRecommendation.NO_ACTION_ALREADY_RESOLVED


def test_non_captured_payment_requires_no_action():
    classifier=IncidentClassifier()
    result=classifier.classify(
        make_incident(),make_order("FAILED"),make_payment("FAILED"),
    )

    assert result == RecoveryRecommendation.NO_ACTION_ALREADY_RESOLVED



def test_missing_payment_or_order_requests_missing_evidence():
    classifier=IncidentClassifier()
    result = classifier.classify(
        make_incident,None,make_order("FAILED"),
    )

    assert result == RecoveryRecommendation.REQUEST_MISSING_EVIDENCE

def test_ambiguous_incident_requires_manual_review():
    classifier=IncidentClassifier()
    result = classifier.classify(
        make_incident("UNKOWN_INCIDENT"),
        make_payment("CAPTURED"),
        make_order("FAILED"),   )

    assert result == RecoveryRecommendation.MANUAL_REVIEW
