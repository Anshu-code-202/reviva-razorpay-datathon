# ADR-007: Auditable Resolution Workflow

## Status

Accepted

## Date

2026-08-22

## Context

Reviva is designed to resolve a specific class of payment incidents through a controlled operational workflow.

The system must not only produce the final resolution result; it must also preserve enough evidence to reconstruct what happened.

A payment incident may involve:

* Payment capture
* Order failure
* Incident detection
* Evidence collection
* Eligibility evaluation
* Optional AI explanation
* Human approval
* Resolution execution
* Final order state

Without a reliable audit trail, Reviva would not be able to answer basic operational questions such as:

* What happened?
* Why was this incident considered eligible?
* Who approved the resolution?
* When was it approved?
* Was AI involved?
* Was the resolution executed?
* Was the request retried?
* What was the final outcome?

Therefore, auditability is a core requirement of the resolution workflow.

## Decision

Reviva will maintain an **append-only audit trail** for all material incident and resolution state transitions.

Every significant action in the resolution workflow must generate an auditable event.

The audit trail will provide a chronological record of the incident lifecycle:

```text
Payment Captured
      ↓
Order Failed
      ↓
Incident Detected
      ↓
Evidence Evaluated
      ↓
Eligibility Determined
      ↓
AI Explanation Generated (optional)
      ↓
Manager Approval
      ↓
Resolution Started
      ↓
Resolution Completed / Failed
```

The audit trail is a historical record and must not be treated as the current state itself.

## Audit Invariant

The system must preserve the history of consequential actions.

> **Current state tells us where the incident is. The audit trail tells us how it got there.**

A state change without a corresponding audit event is considered an invalid workflow transition.

## Events to Record

The MVP must record at least the following events.

### Incident Detection

Records that Reviva identified a payment/order inconsistency.

Example:

```text id="5ih7w5"
INCIDENT_DETECTED
```

### Eligibility Evaluation

Records the outcome of deterministic policy evaluation.

Example:

```text id="3jyn54"
ELIGIBILITY_EVALUATED
```

The event should indicate whether the incident was eligible and reference the relevant evaluation result.

### AI Explanation

If AI assistance is used, the system should record that an AI explanation was generated.

Example:

```text id="9v8f54"
AI_EXPLANATION_GENERATED
```

The audit event should identify that AI was used without treating the AI output as an authorization decision.

### Human Approval

Records the manager's decision.

Example:

```text id="9cr4m8"
RESOLUTION_APPROVED
```

The event must identify the approving user and timestamp.

### Resolution Execution

Records when the resolution process begins.

Example:

```text id="4d5k3q"
RESOLUTION_STARTED
```

### Resolution Completion

Records the final resolution outcome.

Example:

```text id="m0g6b1"
RESOLUTION_COMPLETED
```

If the operation fails:

```text id="2u7j4p"
RESOLUTION_FAILED
```

### Duplicate Resolution Request

If an already processed resolution request is repeated, the system should record the duplicate request where useful for operational visibility.

Example:

```text id="c7h2a9"
DUPLICATE_RESOLUTION_REQUEST
```

The duplicate event must not represent another successful resolution.

## Minimum Audit Event Structure

Each audit event should contain enough information to reconstruct the action.

The MVP audit event should include:

```text id="j6u5qf"
event_id
incident_id
event_type
actor_id
timestamp
previous_state
new_state
metadata
```

Where applicable, metadata may contain:

* Resolution ID
* Idempotency key
* Eligibility result
* Approval decision
* AI usage information
* Error information
* Related order ID
* Related payment ID

Sensitive payment information must not be unnecessarily copied into audit metadata.

## Append-Only Principle

Audit records must be append-only.

Normal application operations must not:

* Delete audit events
* Rewrite historical events
* Change the actor of an event
* Change the event timestamp
* Replace a previous event with a new version

If a correction is required, the system should create a new event rather than modifying historical evidence.

For example:

```text id="6i0k5s"
APPROVAL_RECORDED
        ↓
APPROVAL_REVOKED
```

rather than modifying the original approval event.

## Separation of State and Audit History

Reviva will maintain a distinction between:

```text id="r1nqmg"
Incident State
```

and:

```text id="1qj0fa"
Audit History
```

The incident record represents the current state.

The audit trail represents the historical sequence of events.

This prevents the system from relying on mutable current-state fields to reconstruct historical behavior.

## Ordering

Audit events must have a reliable timestamp and relationship to the incident.

The system should preserve the logical order of events.

For example:

```text id="g8q6y1"
INCIDENT_DETECTED
        ↓
ELIGIBILITY_EVALUATED
        ↓
RESOLUTION_APPROVED
        ↓
RESOLUTION_STARTED
        ↓
RESOLUTION_COMPLETED
```

A resolution completion event must not appear as though it occurred before approval.

## Audit and Idempotency

Auditability must work together with the idempotency rules defined in ADR-005.

A repeated resolution request must not create another successful resolution.

The audit trail may record that the duplicate request occurred, but the original successful resolution remains the single resolution execution.

Therefore:

```text id="6j3k2a"
Request 1
   ↓
Resolution Executed
   ↓
RESOLUTION_COMPLETED

Request 2
   ↓
Duplicate Detected
   ↓
Existing Resolution Returned
```

## Audit and Human Approval

Auditability must also work together with ADR-006.

The system must be able to prove that human approval occurred before resolution.

The expected relationship is:

```text id="f0b3kn"
RESOLUTION_APPROVED
        ↓
RESOLUTION_STARTED
        ↓
RESOLUTION_COMPLETED
```

A resolution completion without a corresponding approval event is an invalid workflow outcome.

## Audit and AI

AI-generated explanations are advisory.

If AI is used, the audit trail should record that AI assistance occurred.

However, the audit trail must clearly distinguish:

```text id="7p8c1w"
AI_EXPLANATION_GENERATED
```

from:

```text id="q5n9m2"
RESOLUTION_APPROVED
```

This prevents the system from incorrectly representing an AI recommendation as a human decision.

## Failure Handling

If a resolution fails, the failure must be recorded.

The event should contain enough information to understand the failure without exposing unnecessary sensitive data.

Example:

```text id="m2d8x4"
RESOLUTION_STARTED
        ↓
RESOLUTION_FAILED
```

The system must not create a `RESOLUTION_COMPLETED` event when the resolution did not actually complete.

## Alternatives Considered

### Logging Only

Rejected.

Application logs are useful for debugging but are not sufficient as the business-level audit record.

Logs may be rotated, difficult to query, or disconnected from the incident lifecycle.

### Mutable Audit Table

Rejected.

Allowing historical events to be modified weakens trust in the audit trail.

### Store Only Final Incident State

Rejected.

The final state cannot explain the sequence of decisions and actions that produced it.

### Full Event-Sourcing Architecture

Rejected for the MVP.

Event sourcing would introduce unnecessary architectural complexity for the controlled incident workflow.

Reviva only requires a durable append-only audit trail, not a complete event-sourced architecture.

## Consequences

### Positive

* Provides a complete incident history
* Makes manager actions accountable
* Supports operational investigation
* Makes the AI boundary visible
* Supports idempotent resolution tracking
* Makes the MVP easier to demonstrate and verify
* Provides a foundation for future compliance and monitoring requirements

### Negative

* Requires additional database storage
* Requires audit events to be generated consistently
* Adds implementation and testing overhead
* Requires careful handling of sensitive information

## MVP Boundary

Reviva will implement auditability for the single controlled resolution workflow.

The MVP does not attempt to provide:

* Enterprise compliance reporting
* Long-term immutable archival infrastructure
* Cross-service distributed tracing
* Full event sourcing
* Legal-grade audit certification
* Advanced audit analytics

The goal is to provide a reliable, queryable record of the incident lifecycle.

## Testing Requirements

The implementation must verify at minimum:

1. Incident detection creates an audit event.
2. Eligibility evaluation creates an audit event.
3. Human approval creates an audit event.
4. Resolution execution creates an audit event.
5. Successful resolution creates a completion event.
6. Failed resolution creates a failure event.
7. Duplicate resolution attempts do not create duplicate successful resolutions.
8. Audit events preserve the correct logical sequence.
9. Historical audit events cannot be modified through normal application operations.
10. AI involvement is distinguishable from human approval.
11. A resolution cannot be considered complete without the corresponding workflow evidence.
12. Sensitive payment data is not unnecessarily duplicated in audit metadata.

## Decision Summary

Reviva will treat auditability as a **first-class property of the resolution workflow**.

Every consequential workflow action must leave a durable historical record.

> **Reviva must be able to explain not only what the final outcome was, but how, when, and by whom that outcome was reached.**

