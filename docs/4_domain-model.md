# Reviva Domain Model

## 1. Purpose

This document defines the core business entities, relationships, states, and domain rules of Reviva.

The domain model represents the business problem independently of specific database tables, API endpoints, frameworks, or UI implementation.

Reviva is modeled around one controlled payment incident resolution workflow:

```text
Payment
   +
Order
   ↓
Incident
   ↓
Eligibility Evaluation
   ↓
Human Approval
   ↓
Resolution
   ↓
Audit Trail
```

---

## 2. Core Domain

The Reviva MVP contains the following primary domain entities:

```text
Payment
Order
Incident
Eligibility Evaluation
User
Approval
Resolution
Audit Event
```

AI explanation is treated as an optional supporting domain object rather than the authority for making a resolution decision.

---

## 3. Entity: Payment

### Purpose

Represents a payment captured by the simulated payment environment.

### Key Attributes

```text
payment_id
merchant_id
amount
currency
status
captured_at
created_at
```

### Payment Status

The MVP only requires the states necessary for the incident workflow.

```text
CAPTURED
FAILED
```

A captured payment represents the successful payment side of the incident scenario.

---

## 4. Entity: Order

### Purpose

Represents the merchant order associated with a payment.

### Key Attributes

```text
order_id
merchant_id
payment_id
status
created_at
updated_at
```

### Order Status

The MVP focuses on:

```text
FAILED
CONFIRMED
```

The important incident scenario is:

```text
Payment = CAPTURED
Order   = FAILED
```

This combination creates the candidate payment incident handled by Reviva.

---

## 5. Entity: Incident

### Purpose

Represents a detected payment/order inconsistency requiring operational investigation.

The Incident is the **central domain entity** of Reviva.

### Key Attributes

```text
incident_id
payment_id
order_id
type
status
detected_at
created_at
updated_at
```

### Incident Type

The MVP supports one primary incident type:

```text
PAYMENT_CAPTURED_ORDER_FAILED
```

### Incident Status

The lifecycle is:

```text
DETECTED
   ↓
ELIGIBLE
   ↓
PENDING_APPROVAL
   ↓
APPROVED
   ↓
PROCESSING
   ↓
RESOLVED
```

Alternative terminal states include:

```text
REJECTED
FAILED
```

### Domain Rule

An incident must reference the exact payment and order involved in the incident.

The payment and order relationship must be deterministic.

---

## 6. Entity: Eligibility Evaluation

### Purpose

Represents the deterministic evaluation used to determine whether an incident qualifies for the Reviva resolution workflow.

Eligibility is based on predefined business rules.

### Key Attributes

```text
evaluation_id
incident_id
result
reason
evaluated_at
rule_version
```

### Evaluation Result

```text
ELIGIBLE
INELIGIBLE
```

### Domain Rule

Eligibility must be determined by deterministic business rules.

AI must not override the eligibility result.

---

## 7. Entity: User

### Purpose

Represents an authenticated actor interacting with Reviva.

### Key Attributes

```text
user_id
name
role
created_at
```

### MVP Roles

```text
OPERATOR
MANAGER
```

### Role Responsibilities

#### Operator

Can:

* View incidents
* Inspect evidence
* Review incident information

Cannot:

* Approve resolution
* Execute resolution directly

#### Manager

Can:

* Review incidents
* Review eligibility
* Approve resolution
* Trigger the controlled resolution workflow

### Domain Rule

Only an authorized manager may approve a resolution.

---

## 8. Entity: Approval

### Purpose

Represents the explicit human decision authorizing a resolution.

Approval is separate from the Incident because the incident describes the problem while Approval records the human decision.

### Key Attributes

```text
approval_id
incident_id
approved_by
decision
reason
approved_at
```

### Approval Decision

```text
APPROVED
REJECTED
```

### Domain Rules

A valid resolution requires:

```text
Eligible Incident
        +
Authorized Manager
        +
Explicit Approval
```

AI output cannot substitute for approval.

---

## 9. Entity: Resolution

### Purpose

Represents the controlled attempt to resolve the incident by performing the simulated order-confirmation reprocess.

Resolution is the domain action that creates the consequential side effect.

### Key Attributes

```text
resolution_id
incident_id
approval_id
idempotency_key
status
started_at
completed_at
failure_reason
```

### Resolution Status

```text
PENDING
PROCESSING
COMPLETED
FAILED
```

### Domain Rules

A resolution:

1. Must belong to an incident.
2. Must reference a valid approval.
3. Must satisfy eligibility requirements.
4. Must have a valid idempotency identity.
5. Must not execute more than once successfully.
6. Must produce an audit trail.

### Idempotency Rule

For a single incident:

```text
One incident
     ↓
One successful resolution
     ↓
One simulated order-confirmation side effect
```

Repeated requests must not produce another successful resolution.

---

## 10. Entity: Audit Event

### Purpose

Represents an immutable historical record of a consequential domain event.

Audit events provide the historical timeline of an incident.

### Key Attributes

```text
event_id
incident_id
event_type
actor_id
timestamp
previous_state
new_state
metadata
```

### Example Event Types

```text
INCIDENT_DETECTED
ELIGIBILITY_EVALUATED
AI_EXPLANATION_GENERATED
RESOLUTION_APPROVED
RESOLUTION_REJECTED
RESOLUTION_STARTED
RESOLUTION_COMPLETED
RESOLUTION_FAILED
DUPLICATE_RESOLUTION_REQUEST
```

### Domain Rules

Audit events are append-only.

Historical events must not be modified or deleted through normal application operations.

---

## 11. AI Explanation

### Purpose

Represents optional AI-generated assistance for understanding an incident.

AI is advisory rather than authoritative.

### Possible Attributes

```text
explanation_id
incident_id
model
explanation
generated_at
```

### Domain Rules

AI may:

* Summarize evidence
* Explain the incident
* Provide a recommendation

AI may not:

* Approve a resolution
* Override eligibility
* Execute a resolution
* Change payment state
* Change order state

Therefore:

```text
AI Explanation
      ≠
Eligibility Decision
      ≠
Human Approval
      ≠
Resolution
```

---

# 12. Domain Relationships

The core relationships are:

```text
Payment 1 ───── 1 Order
   │              │
   └──────┬───────┘
          ↓
       Incident
          │
          ├──── Eligibility Evaluation
          │
          ├──── Approval ──── User
          │
          ├──── Resolution
          │
          ├──── AI Explanation
          │
          └──── Audit Events
```

More explicitly:

```text
Payment
   │
   └── associated with ── Order
                              │
                              ↓
                           Incident
                              │
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
        Eligibility       Approval         Resolution
                              │                │
                              ↓                ↓
                            User          Audit Events
```

---

# 13. Incident-to-Resolution Lifecycle

The complete domain lifecycle is:

```text
Payment CAPTURED
        +
Order FAILED
        ↓
Incident DETECTED
        ↓
Eligibility Evaluation
        ↓
┌─────────────────────┐
│ Eligible?            │
└─────────────────────┘
       │
   NO  │  YES
   ↓       ↓
INELIGIBLE  PENDING_APPROVAL
               ↓
        Manager Review
               ↓
        ┌─────────────┐
        │  Approved?  │
        └─────────────┘
          │         │
        NO│         │YES
          ↓         ↓
       REJECTED   APPROVED
                     ↓
                 PROCESSING
                     ↓
              Mock Resolution
                     ↓
                  RESOLVED
```

---

# 14. Core Domain Invariants

The following rules must always hold.

### Invariant 1 — Incident Matching

An incident must reference the exact payment and order that caused the inconsistency.

### Invariant 2 — Deterministic Eligibility

Eligibility is determined by explicit business rules.

AI cannot override it.

### Invariant 3 — Human Approval

A resolution cannot execute without explicit approval from an authorized manager.

### Invariant 4 — Idempotent Resolution

A single incident can have at most one successful resolution side effect.

### Invariant 5 — Auditability

Every consequential workflow transition must produce an audit event.

### Invariant 6 — AI Safety

AI cannot directly change payment, order, incident, approval, or resolution state.

### Invariant 7 — Resolution Ordering

The valid resolution sequence is:

```text
ELIGIBLE
   ↓
PENDING_APPROVAL
   ↓
APPROVED
   ↓
PROCESSING
   ↓
RESOLVED
```

A resolution cannot skip required authorization states.

---

# 15. What Is Outside the Domain Model

The MVP intentionally does not model:

```text
Real payment processing
Real refunds
Real money movement
Fraud detection
Chargebacks
Disputes
Subscription billing
Payouts
Settlement
Multi-level approval workflows
Complex merchant configuration
Production payment gateway integration
```

These are outside the Reviva MVP boundary defined in the PRD and ADRs.

---

# 16. Domain Model Summary

Reviva's domain can be reduced to:

```text
PAYMENT
   +
ORDER
   ↓
INCIDENT
   ↓
ELIGIBILITY
   ↓
HUMAN APPROVAL
   ↓
RESOLUTION
   ↓
AUDIT
```

With AI operating only as an optional explanation layer:

```text
             ┌───────────────┐
             │ AI Explanation│
             │   (Optional)  │
             └───────┬───────┘
                     │
                     ↓
Payment + Order → Incident → Eligibility → Approval → Resolution → Audit
```

The central principle is:

> **Reviva does not let AI or automation directly resolve a payment incident. It uses deterministic domain rules, explicit human approval, idempotent execution, and an auditable workflow to safely resolve one controlled incident type.**
