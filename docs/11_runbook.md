# REVIVA — Product Requirements Document (PRD) v0.1

**Date:** August 22, 2026
**Project:** REVIVA
**Target:** Razorpay AI Buildathon 2026 + 2027 Placements
**Status:** Draft for Day 0 Review

---

## 1. Product Summary

**REVIVA** is an AI-assisted cross-system payment incident investigation and resolution platform.

Reviva helps merchant operations teams investigate situations where payment-system state and merchant-owned business-system state become inconsistent.

The MVP focuses on one controlled incident:

> **Payment captured + merchant order failed**

Reviva correlates events, reconstructs an evidence timeline, investigates the incident, optionally uses AI to explain ambiguous evidence, evaluates a resolution through deterministic policies and guardrails, obtains approval when required, executes one idempotent mock resolution, and records the complete audit trail.

---

## 2. Problem Statement

A payment being successfully captured does not necessarily mean that the merchant's business process completed successfully.

For example:

```text
Payment system
    Payment = CAPTURED
          +
Merchant order system
    Order = FAILED
```

The customer may see a successful payment while the merchant's order remains unsuccessful.

The evidence needed to understand the incident may exist across payment events, order events, webhook information, timestamps, and merchant-side processing information.

The operations team therefore needs to determine:

1. What happened?
2. Which events are related?
3. Where did the state transition diverge?
4. What evidence supports the conclusion?
5. Is a resolution possible?
6. Is the resolution permitted?
7. Does it require approval?
8. Was the resolution executed safely?
9. What happened afterward?

Reviva addresses this investigation and controlled-resolution workflow.

---

## 3. Product Positioning

Reviva is **not** intended to replace payment processing, payment retry systems, or existing payment-side reconciliation capabilities.

Its focus is the boundary between:

```text
Payment System
      +
Merchant-Owned Business System
      ↓
Cross-System Correlation
      ↓
State Mismatch
      ↓
Incident Investigation
      ↓
Safe Resolution
```

The product hypothesis is:

> Reviva helps merchant operations teams investigate payment/business-state inconsistencies across systems, reconstruct what happened from distributed evidence, explain ambiguous incidents, and safely execute eligible resolutions under deterministic policies and audit controls.

---

## 4. Target Users

### Primary User

**Merchant Operations Operator**

Responsible for investigating customer/payment incidents and determining the appropriate operational response.

### Secondary User

**Authorized Manager / Approver**

Reviews and approves business-state-changing resolutions when policy requires human approval.

### Not Primary Users

* End customers
* Banks
* Payment processors
* Developers as the primary workflow actor
* General consumers

---

## 5. Core MVP User Journey

```text
Payment captured
      ↓
Merchant order failed
      ↓
Reviva receives/correlates events
      ↓
State mismatch detected
      ↓
Incident created
      ↓
Evidence collected
      ↓
Timeline reconstructed
      ↓
Deterministic investigation
      ↓
AI investigation if ambiguity remains
      ↓
Resolution recommended
      ↓
Policy + guardrails evaluated
      ↓
Approval required?
      ↓
Human approval
      ↓
Idempotent resolution execution
      ↓
Order confirmed in mock merchant system
      ↓
Audit trail recorded
```

---

# 6. Functional Requirements

## FR-01 — Merchant Representation

The system shall represent a merchant context for incoming payment and business events.

The merchant context must allow Reviva to associate events and incidents with the correct merchant.

---

## FR-02 — Payment Event Ingestion

Reviva shall accept simulated payment events containing relevant identifiers and state information.

Minimum information:

* merchant ID
* payment ID
* order/reference ID
* amount
* currency
* payment status
* event ID
* event type
* event timestamp
* received timestamp

---

## FR-03 — Merchant Order Event Ingestion

Reviva shall accept simulated merchant order/business events.

Minimum information:

* merchant ID
* order ID
* payment/reference ID
* amount
* order status
* event ID
* event type
* event timestamp
* received timestamp

---

## FR-04 — Event Correlation

Reviva shall correlate payment and merchant-order events using deterministic identifiers and relationships.

Correlation must not depend on an LLM.

---

## FR-05 — State Comparison

Reviva shall compare correlated payment and order states.

For the flagship MVP scenario:

```text
Payment = CAPTURED
Order   = FAILED
```

This shall be recognized as a state inconsistency when the relevant correlation conditions are satisfied.

---

## FR-06 — Incident Creation

When an eligible state mismatch is detected, Reviva shall create an incident.

The incident shall maintain its lifecycle and associated evidence.

---

## FR-07 — Incident Lifecycle

The MVP shall support:

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

Failure/blocking states shall also be represented where applicable:

* BLOCKED
* REJECTED
* FAILED

---

## FR-08 — Evidence Collection

Reviva shall collect relevant evidence associated with an incident.

Evidence may include:

* payment events
* order events
* event identifiers
* timestamps
* correlation information
* webhook/processing information
* deterministic investigation findings

---

## FR-09 — Timeline Reconstruction

Reviva shall reconstruct a chronological timeline of relevant incident events.

The timeline shall allow an operator to understand the sequence of events leading to the mismatch.

---

## FR-10 — Deterministic Investigation

Reviva shall perform deterministic investigation before invoking AI.

Known conditions and rules shall be evaluated without relying on an LLM.

---

## FR-11 — AI-Assisted Investigation

Reviva may invoke an LLM when deterministic investigation cannot sufficiently explain an ambiguous incident.

AI may:

* summarize the incident
* interpret complex event sequences
* identify likely causes
* explain state inconsistencies
* identify relevant evidence
* recommend a resolution

AI output shall be structured and validated.

---

## FR-12 — AI Safety Boundary

AI shall **not**:

* execute financial actions
* authorize itself
* bypass policy
* bypass approval
* change monetary amounts
* override limits
* modify audit history
* directly control financial state
* directly control merchant business state

AI output shall be treated as untrusted input.

---

## FR-13 — Resolution Recommendation

Reviva shall generate a resolution recommendation after investigation.

For the MVP, the primary recommendation is:

> **Reprocess the failed merchant order confirmation.**

The recommendation itself does not execute the action.

---

## FR-14 — Policy Evaluation

Reviva shall evaluate whether a proposed resolution is eligible according to merchant-defined policies.

Possible outcomes include:

* eligible
* blocked
* approval required

---

## FR-15 — Deterministic Guardrails

Guardrails shall independently evaluate the proposed resolution.

AI output must not bypass deterministic safety controls.

---

## FR-16 — Human Approval

Business-state-changing resolution shall require approval where the applicable policy requires it.

Approval shall be associated with an authorized actor.

---

## FR-17 — Resolution Execution

Reviva shall execute the approved MVP resolution through a simulated/mock merchant order-resolution provider.

The MVP shall not move real money.

---

## FR-18 — Idempotent Resolution

Resolution execution shall be idempotent.

Repeated requests using the same resolution/idempotency key shall not create duplicate business effects.

---

## FR-19 — Audit Trail

Reviva shall record consequential system actions and decisions.

The audit trail should allow the system to answer:

```text
What happened?
What evidence was found?
What did the system conclude?
What did AI recommend?
What policy was applied?
What guardrail was evaluated?
Was approval required?
Who approved?
What action occurred?
What was the final result?
```

---

## FR-20 — Dashboard

The MVP dashboard shall provide enough information for an operator to:

* view incidents
* open an incident
* inspect the timeline
* inspect evidence
* view the investigation
* view AI explanation where available
* view recommended resolution
* inspect guardrail results
* approve/review where authorized
* inspect resolution status
* inspect audit history

The dashboard is an operational interface, not a generic analytics platform.

---

# 7. AI Requirements

AI is deliberately limited.

### AI receives

Structured incident context containing relevant:

* events
* evidence
* timeline
* deterministic findings

### AI produces

A structured result containing:

```text
likely_cause
explanation
supporting_evidence
recommended_resolution
confidence
```

### AI does not control

```text
authorization
policy
approval
execution
money
business-state mutation
audit history
```

The system must continue operating safely when AI is unavailable.

---

# 8. Resolution Model

The MVP supports one primary resolution:

> **Mock order-confirmation reprocess**

Example:

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
Mock Resolution Provider
       ↓
Order = CONFIRMED
```

No real payment retry, refund, or money movement is included.

---

# 9. Failure Requirements

Reviva must fail safely.

### LLM Timeout

Expected behavior:

```text
LLM unavailable
      ↓
No unsafe action
      ↓
Manual review / deterministic path
```

### Invalid AI Output

```text
LLM output
    ↓
Schema validation
    ↓
Invalid
    ↓
Reject
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
No action
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
Recover/retry
      ↓
Idempotency protection
```

### Duplicate Resolution

Repeated execution requests shall not create duplicate business effects.

---

# 10. Non-Functional Requirements

## NFR-01 — Safety

No financial or merchant business-state action shall depend solely on an AI recommendation.

## NFR-02 — Determinism

Critical decisions must be reproducible from system state, policy, and deterministic rules.

## NFR-03 — Auditability

Consequential decisions and actions must have an associated audit record.

## NFR-04 — Idempotency

Resolution operations must protect against duplicate effects.

## NFR-05 — Data Isolation

Merchant data must remain logically isolated.

## NFR-06 — Testability

Core business rules must be independently testable.

## NFR-07 — Failure Recovery

Failure of AI or background execution must not produce unsafe state transitions.

## NFR-08 — Understandability

The architecture should remain simple enough for the project team to explain and defend.

---

# 11. MVP Scope

### Included

* Merchant representation
* Payment event ingestion
* Merchant order event ingestion
* Event correlation
* State comparison
* Incident detection
* Incident lifecycle
* Evidence collection
* Timeline reconstruction
* Deterministic investigation
* AI-assisted investigation
* Structured AI output
* Resolution recommendation
* Merchant policies
* Deterministic guardrails
* Human approval
* Mock resolution worker
* Idempotency
* Audit trail
* Operator dashboard
* Failure injection
* Automated tests
* End-to-end scenario

---

# 12. Explicit Non-Goals

Reviva MVP shall **NOT** build:

* Payment gateway
* Payment processor
* Real bank integration
* Real-money movement
* Full ERP
* Full CRM
* Universal fraud engine
* Full dispute platform
* Payment retry optimization
* Payment decline prediction model
* Unrestricted autonomous financial agent
* Generic chatbot
* Multi-agent swarm
* Kubernetes deployment
* Microservice architecture without demonstrated need
* Unnecessary vector database
* Unnecessary RAG

The MVP shall use a simulated payment environment.

---

# 13. Success Criteria

The MVP is successful when the following end-to-end scenario works reliably:

```text
Payment captured
      ↓
Order failed
      ↓
Reviva detects mismatch
      ↓
Incident created
      ↓
Evidence collected
      ↓
Timeline reconstructed
      ↓
Cause investigated
      ↓
Resolution recommended
      ↓
Guardrails evaluated
      ↓
Approval obtained
      ↓
Resolution executed
      ↓
Order confirmed
      ↓
Audit recorded
```

The system must also demonstrate safe handling of:

* duplicate events
* duplicate resolution requests
* LLM timeout
* invalid AI output
* unauthorized resolution
* worker failure

---

# 14. Product Boundaries

### Reviva owns

* Incident investigation
* Event correlation
* Evidence
* Timeline
* Investigation result
* Recommendation
* Policies
* Guardrails
* Approval workflow
* Resolution orchestration
* Audit

### Reviva does not own

* Payment processing
* Banking
* Money movement
* Merchant's complete order platform
* Inventory
* CRM
* ERP
* Customer account infrastructure

---

# 15. Key Product Principle

The complete product must follow:

> **AI proposes. Deterministic software decides. The database guarantees. The audit log remembers.**

This is the architectural and product safety principle of Reviva.

---

# 16. Definition of Done — PRD

The PRD is ready to move forward when:

* The primary user is defined.
* The core incident is defined.
* Inputs and outputs are defined.
* AI boundaries are defined.
* Deterministic responsibilities are defined.
* Resolution is defined.
* Approval requirements are defined.
* Failure behavior is defined.
* MVP scope is defined.
* Non-goals are defined.
* Success criteria are measurable.
* Product boundaries are clear.

---

# 17. Next Artifact

After this PRD is accepted, the next step is:

> **Domain Model**

We will derive the domain model from the requirements rather than prematurely turning every concept into a database table.

Expected candidates will be examined rather than automatically accepted:

```text
Merchant
PaymentEvent
OrderEvent
BusinessEvent
Incident
IncidentEvidence
TimelineEvent
Investigation
ResolutionRecommendation
Policy
Approval
ResolutionAction
AuditEvent
```

The domain model must be derived from the product requirements before database tables are finalized.

---

## PRD Status

**Version:** 0.1
**Date:** August 22, 2026
**Status:** Draft for Day 0 Review
**Next Artifact:** Domain Model
