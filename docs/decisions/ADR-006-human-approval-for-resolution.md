# ADR-006: Human Approval for Resolution

## Status

Accepted

## Date

2026-08-22

## Context

Reviva detects payment-related incidents and determines whether an incident may be eligible for resolution.

The system may use deterministic rules and optional AI assistance to explain the incident. However, automated detection and AI-generated explanations must not directly trigger a resolution.

The final resolution can change the state of an order and therefore represents a consequential operational action.

For the MVP, Reviva must demonstrate that an authorized human remains responsible for approving the resolution before the system executes the simulated order-confirmation reprocess.

## Decision

Reviva will require **explicit human approval before every resolution execution**.

The system may:

* Detect an incident automatically
* Match the payment and failed order
* Determine policy eligibility
* Generate an optional AI explanation
* Present evidence and recommended action

But the system must not automatically execute the resolution.

The required workflow is:

```text
Payment + Failed Order
        ↓
Incident Detection
        ↓
Evidence Collection
        ↓
Eligibility Evaluation
        ↓
Optional AI Explanation
        ↓
Human Review
        ↓
Manager Approval
        ↓
Idempotent Resolution
        ↓
Audit Trail
```

The human approval is therefore a mandatory state transition in the resolution lifecycle.

## Approval Invariant

A resolution must never execute unless a valid approval exists.

```text
No Approval → No Resolution
```

The backend, not only the frontend, must enforce this rule.

A client must not be able to bypass the approval step by directly calling the resolution endpoint.

## Approval Requirements

Before approving a resolution, the authorized manager must be able to see the relevant incident evidence, including:

* Payment information
* Order information
* Failure information
* Incident timeline
* Eligibility result
* Relevant policy information
* Optional AI explanation
* Recommended resolution

The manager must explicitly approve the resolution action.

Approval must be associated with:

* Incident
* Approving user
* Approval timestamp
* Resolution being approved
* Approval decision

## Approval States

The MVP will use the following conceptual states:

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

If approval is rejected:

```text
PENDING_APPROVAL
        ↓
REJECTED
```

A rejected incident must not proceed to resolution.

## Backend Enforcement

The resolution service must verify:

1. The incident exists.
2. The incident is eligible for resolution.
3. The incident has an approved decision.
4. The approval belongs to the correct incident.
5. The approval was created before the resolution attempt.
6. The incident has not already been resolved.
7. The resolution request satisfies the idempotency requirements defined in ADR-005.

Only after these checks succeed may the simulated resolution operation begin.

## AI Boundary

AI is advisory only.

AI may help explain:

* What happened
* Why the incident appears eligible
* What evidence supports the recommendation
* What action could be considered

AI must not:

* Approve the resolution
* Automatically execute the resolution
* Override deterministic eligibility rules
* Change payment or order state
* Act as the final decision-maker

Therefore:

```text
AI Recommendation ≠ Human Approval
```

The manager remains accountable for the resolution decision.

## Authorization

Only an authorized manager role may approve a resolution.

The MVP will not treat every authenticated user as capable of approving incidents.

At minimum, the system must distinguish between:

```text
Operator
Manager
```

The operator may inspect incidents, while the manager has the authority to approve the resolution.

The exact role and permission model may be expanded in a later version.

## Audit Requirements

Approval is a critical audit event and must be recorded.

The audit trail must capture:

* Incident ID
* Approving user ID
* Approval decision
* Approval timestamp
* Incident state at approval
* Relevant resolution identifier

The audit trail must make it possible to answer:

> Who approved this resolution, when was it approved, and what incident did they approve?

Approval records must be immutable from the normal application workflow.

## Alternatives Considered

### Fully Automated Resolution

Rejected.

Automated resolution would remove the human control point and create unnecessary operational risk for the MVP.

### AI-Based Approval

Rejected.

An AI explanation or recommendation cannot be treated as authorization to perform a consequential action.

### Frontend-Only Approval

Rejected.

Hiding the resolution button until approval is selected is insufficient. The backend must independently enforce approval requirements.

### Human Approval Without Audit Logging

Rejected.

A resolution without a traceable approval decision would weaken accountability and make incident investigation difficult.

## Consequences

### Positive

* Keeps a human in control of consequential actions
* Prevents accidental automated resolution
* Creates clear accountability
* Establishes a strong AI safety boundary
* Makes the workflow easier to explain and demonstrate
* Provides an auditable approval trail
* Aligns the resolution workflow with operational control principles

### Negative

* Adds an approval step to the workflow
* Requires role and authorization checks
* Requires additional database state
* Prevents completely automated resolution

## MVP Boundary

Reviva does not implement a complex enterprise approval hierarchy.

The MVP supports one clear control:

```text
Authorized Manager
        ↓
Explicit Approval
        ↓
One Idempotent Mock Resolution
```

There is no:

* Multi-level approval chain
* Automatic approval
* AI approval
* Real payment authorization
* Real-money transaction
* Production payment gateway integration

## Testing Requirements

The implementation must verify at minimum:

1. An eligible incident can enter the approval state.
2. An unauthorized user cannot approve a resolution.
3. An authorized manager can approve an eligible incident.
4. A rejected incident cannot be resolved.
5. An incident without approval cannot be resolved.
6. A resolution request with approval succeeds when all other conditions are satisfied.
7. AI output alone cannot authorize resolution.
8. Approval is recorded in the audit trail.
9. Approval cannot be silently changed after resolution.
10. Duplicate resolution attempts remain protected by ADR-005.

## Decision Summary

Reviva will use **human-in-the-loop resolution**.

The system can detect, analyze, explain, and recommend, but only an authorized human manager can approve the final action.

> **Detection can be automated. Explanation can be AI-assisted. Resolution requires human approval.**

