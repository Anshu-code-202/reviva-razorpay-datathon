# ADR-002 — REVIVA MVP Incident Definition

* **Status:** Accepted
* **Date:** August 22, 2026
* **Decision Type:** Product Scope / Incident Model
* **Related Artifacts:** `prd.md`, `ADR-001-reviva-product-boundary.md`

---

## 1. Context

REVIVA requires a narrowly defined incident type for the MVP.

The product is not intended to investigate every possible payment failure or merchant operational issue.

The MVP must demonstrate one complete and controlled incident lifecycle from detection through safe resolution.

The selected flagship incident is:

> **Payment captured + merchant order failed**

This represents a cross-system state inconsistency where the payment system indicates successful capture while the merchant's business/order system indicates failure.

---

## 2. Decision

The REVIVA MVP will support **one primary incident type**:

> **CAPTURED_PAYMENT_ORDER_FAILED**

The incident is created when the required deterministic correlation and state conditions are satisfied.

The canonical condition is:

```text
Payment = CAPTURED
Order   = FAILED
```

The incident must involve the same relevant merchant and payment/order relationship.

Incident creation must be deterministic and must not depend on an LLM.

---

## 3. Why This Incident

This incident was selected because it provides a complete demonstration of REVIVA's core product capability.

It requires the system to:

1. ingest payment information
2. ingest merchant order information
3. correlate events
4. compare states
5. detect an inconsistency
6. create an incident
7. collect evidence
8. reconstruct a timeline
9. investigate the cause
10. recommend a resolution
11. evaluate policy
12. evaluate guardrails
13. obtain approval where required
14. execute a controlled resolution
15. guarantee idempotency
16. record an audit trail

Therefore, one incident type is sufficient to exercise the complete MVP architecture.

---

## 4. Canonical Incident

The canonical MVP incident is:

```text
Payment Event
    payment_status = CAPTURED
          │
          │ correlation
          ▼
Merchant Order Event
    order_status = FAILED
          │
          ▼
State Mismatch
          │
          ▼
REVIVA Incident
```

The incident should retain the identifiers and evidence required to explain why it was created.

---

## 5. Incident Eligibility

An incident is eligible for creation only when the required deterministic conditions are satisfied.

At minimum:

* merchant context matches
* payment and order relationship can be established
* payment state is `CAPTURED`
* merchant order state is `FAILED`
* relevant event information is available
* correlation is deterministic

If the required relationship cannot be established, REVIVA must not create the flagship incident merely because two unrelated events have conflicting states.

---

## 6. Incident Identity

The incident must have a stable identity.

The identity must allow REVIVA to:

* uniquely identify the incident
* associate evidence with the incident
* associate investigation results with the incident
* associate recommendations with the incident
* associate approvals with the incident
* associate resolution actions with the incident
* associate audit events with the incident

Duplicate source events must not unintentionally create duplicate logical incidents.

---

## 7. Incident Lifecycle

The MVP incident lifecycle is:

```text
DETECTED
    ↓
INVESTIGATING
    ↓
RECOMMENDATION_READY
    ↓
AWAITING_APPROVAL
    ↓
APPROVED
    ↓
RESOLUTION_IN_PROGRESS
    ↓
RESOLVED
```

Additional failure/blocking states are:

```text
BLOCKED
REJECTED
FAILED
```

These states represent operational outcomes and must not be treated as equivalent to successful resolution.

---

## 8. State Transition Rules

### DETECTED → INVESTIGATING

The incident has been created and investigation begins.

### INVESTIGATING → RECOMMENDATION_READY

Required evidence and investigation processing have completed sufficiently to produce a resolution recommendation.

### RECOMMENDATION_READY → AWAITING_APPROVAL

The proposed resolution requires human approval according to policy.

### RECOMMENDATION_READY → RESOLUTION_IN_PROGRESS

Only when policy and guardrails determine that approval is not required and execution is permitted.

### AWAITING_APPROVAL → APPROVED

An authorized actor approves the proposed resolution.

### AWAITING_APPROVAL → REJECTED

An authorized actor rejects the proposed resolution.

### APPROVED → RESOLUTION_IN_PROGRESS

The approved resolution is submitted for execution.

### RESOLUTION_IN_PROGRESS → RESOLVED

The mock resolution provider successfully completes the required business-state change.

### RESOLUTION_IN_PROGRESS → FAILED

Resolution execution fails and the incident cannot currently be completed.

### Any Applicable State → BLOCKED

The incident cannot safely proceed because a policy, guardrail, authorization, or required condition prevents execution.

---

## 9. Investigation Model

Investigation must occur in two layers.

### Layer 1 — Deterministic Investigation

REVIVA evaluates known conditions and rules without AI.

This includes:

* event relationships
* state comparisons
* timestamps
* identifiers
* known processing information
* policy-relevant conditions
* deterministic guardrails

### Layer 2 — AI-Assisted Investigation

AI may be invoked only when deterministic investigation does not sufficiently explain an ambiguous incident.

AI may:

* summarize the incident
* interpret complex event sequences
* identify likely causes
* explain inconsistencies
* identify supporting evidence
* recommend the MVP resolution

AI remains outside the authority boundary.

---

## 10. Resolution for the Incident

The primary MVP resolution for this incident is:

> **Mock order-confirmation reprocess**

The intended state transition is:

```text
Payment = CAPTURED
Order   = FAILED
       ↓
Investigation
       ↓
Recommendation
       ↓
Policy
       ↓
Guardrails
       ↓
Approval
       ↓
Mock Resolution
       ↓
Order = CONFIRMED
```

No real money movement occurs.

---

## 11. Duplicate Incident Handling

REVIVA must protect against duplicate source events.

If the same logical payment/order state mismatch is observed multiple times, the system must not blindly create multiple logical incidents.

Correlation and incident identity must provide deterministic protection against duplicate incident creation.

Duplicate events should instead become additional evidence or be recognized as already associated with the existing incident, depending on the event's relationship to the incident.

---

## 12. Failure Handling

The incident must fail safely.

### LLM Timeout

```text
LLM unavailable
      ↓
No unsafe action
      ↓
Continue deterministic/manual path
```

### Invalid AI Output

```text
AI output
    ↓
Schema validation
    ↓
Invalid
    ↓
Reject AI result
    ↓
No execution
```

### Unauthorized Resolution

```text
Resolution request
      ↓
Authorization check
      ↓
Denied
      ↓
No business-state change
      ↓
Audit
```

### Worker Failure

```text
Resolution execution
      ↓
Failure
      ↓
Record failure
      ↓
Retry/recovery when permitted
      ↓
Idempotency protection
```

---

## 13. Incident Evidence

The incident must retain relevant evidence used during investigation.

Evidence may include:

* payment events
* order events
* event IDs
* timestamps
* correlation information
* webhook/processing information
* deterministic findings
* AI findings where applicable
* policy evaluation
* guardrail evaluation
* approval information
* resolution result

The incident should be explainable from its associated evidence.

---

## 14. Incident Timeline

REVIVA shall reconstruct a chronological timeline for the incident.

The timeline must help an operator answer:

```text
What happened first?
What happened next?
Where did the states diverge?
What evidence proves the mismatch?
What did REVIVA determine?
What resolution was proposed?
What controls were applied?
What action was taken?
What was the final result?
```

---

## 15. Audit Requirements

All consequential incident actions must be auditable.

The audit trail should capture:

* incident creation
* investigation
* AI recommendation where applicable
* policy evaluation
* guardrail evaluation
* approval requirement
* approval/rejection
* resolution request
* resolution execution
* final resolution result
* failures and blocked actions

The audit history must not be modifiable by AI.

---

## 16. Explicit MVP Exclusions

The following incident types are outside the MVP:

* payment declined
* payment failed before capture
* refund mismatch
* partial payment mismatch
* duplicate payment investigation
* fraud investigation
* chargeback/dispute investigation
* bank settlement reconciliation
* payment retry optimization
* real payment recovery
* real-money refund
* multi-step financial recovery workflows

These may be considered in future product versions but are not part of the current MVP.

---

## 17. Consequences

### Positive Consequences

* Extremely clear MVP scope
* One complete end-to-end workflow
* Easy deterministic testing
* Easy failure injection
* Clear AI boundary
* Clear database/domain requirements
* Strong buildathon demonstration
* Reduced implementation risk

### Negative Consequences

* MVP does not represent every real payment incident.
* The investigation engine will initially have limited incident coverage.
* Future incident types will require explicit product and architecture decisions.
* Some real-world edge cases remain outside the initial system.

These limitations are intentional.

---

## 18. Decision Rule for Future Incident Types

A new incident type must not be added simply because it is technically possible.

Before adding another incident type, the team must determine:

1. Does it represent a meaningful merchant operations problem?
2. Can the incident be detected deterministically?
3. Can the evidence be reconstructed?
4. Can the resolution be governed by deterministic policy?
5. Can the resolution be safely executed?
6. Can the complete lifecycle be audited?
7. Does adding it justify the additional MVP complexity?

If these conditions are not satisfied, the incident type remains outside MVP scope.

---

## 19. Decision Outcome

**Accepted.**

REVIVA MVP will focus on:

> **One controlled incident: Payment captured + merchant order failed.**

The complete MVP success loop is:

```text
Payment Captured
      ↓
Order Failed
      ↓
Deterministic Correlation
      ↓
Mismatch Detected
      ↓
Incident Created
      ↓
Evidence Collected
      ↓
Timeline Reconstructed
      ↓
Deterministic Investigation
      ↓
Optional AI Explanation
      ↓
Resolution Recommendation
      ↓
Policy + Guardrails
      ↓
Human Approval When Required
      ↓
Idempotent Mock Resolution
      ↓
Order Confirmed
      ↓
Audit Recorded
```

This decision is binding for the MVP unless superseded by a later ADR.
