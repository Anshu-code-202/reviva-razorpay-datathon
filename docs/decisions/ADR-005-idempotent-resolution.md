# ADR-005: Idempotent Resolution

## Status

Accepted

## Date

2026-08-22

## Context

Reviva resolves a detected payment incident by allowing an authorized manager to trigger a controlled order-confirmation reprocess.

The resolution operation may be retried because of:

* User double-clicking the resolution action
* Browser refreshes or repeated requests
* Network timeouts where the client does not know whether the first request succeeded
* API retries
* Duplicate requests caused by infrastructure or frontend behavior

A resolution request must therefore never create multiple order confirmations for the same incident.

The MVP uses a simulated payment/order environment. However, the resolution workflow must model the same safety principle expected from a real payment operations system: repeating the same resolution request must not produce additional side effects.

## Decision

Reviva will make the incident resolution operation **idempotent**.

For a given incident, there may be only **one successful resolution execution**.

Every resolution request must contain or resolve to a unique idempotency key associated with the incident resolution attempt.

The backend will persist the resolution state before performing the simulated side effect and will reject or safely return the existing result for duplicate requests.

The resolution lifecycle is:

```text
INCIDENT_DETECTED
        ↓
ELIGIBLE
        ↓
APPROVAL_REQUIRED
        ↓
APPROVED
        ↓
PROCESSING
        ↓
RESOLVED
```

If the same resolution request is received again after successful resolution, Reviva must return the existing resolution result rather than executing the simulated order-confirmation operation again.

If a resolution is already being processed, another request for the same idempotency key must not start a second processing operation.

## Idempotency Invariant

For a single incident:

> One incident can produce at most one successful resolution side effect.

Therefore:

```text
same incident + same resolution
        ↓
one resolution execution
        ↓
one simulated order confirmation
        ↓
one final resolution record
```

Repeated requests must not produce:

```text
two confirmations
multiple audit events representing multiple executions
duplicate order state transitions
multiple successful resolutions
```

## Implementation Rules

### 1. Unique Resolution Identity

Each resolution operation will have a unique identifier.

The database must enforce uniqueness for the resolution identity so that application-level checks are not the only protection against duplicates.

### 2. Incident-Level Protection

An incident cannot be successfully resolved more than once.

Once an incident reaches `RESOLVED`, additional resolution requests must return the existing resolution result or a safe conflict response.

### 3. Idempotency Key

The resolution endpoint will accept an idempotency key.

The key must be stored with the resolution request and associated with the incident.

The same key must always map to the same logical resolution operation.

### 4. State Validation

The backend must validate the current incident state before executing the resolution.

A resolution is allowed only when the incident is in the expected approved state.

For example:

```text
APPROVED → PROCESSING → RESOLVED
```

The backend must not allow:

```text
RESOLVED → PROCESSING
RESOLVED → RESOLVED
CANCELLED → PROCESSING
```

### 5. Transactional Safety

The database state change and resolution record creation must be protected by a transaction.

The system must avoid a situation where the simulated order is marked as confirmed but Reviva records the resolution as failed or nonexistent.

### 6. Audit Trail

Every resolution request must be traceable.

The audit trail must distinguish between:

* First execution
* Duplicate request
* Rejected request
* Successful resolution

A duplicate request must not create another successful resolution side effect.

## Failure Handling

If processing fails before the simulated order-confirmation side effect occurs, the incident may remain eligible for controlled retry according to the defined failure state.

If the system cannot determine whether the side effect occurred, Reviva must not blindly execute the operation again.

The system must first determine the existing resolution state.

The MVP should prefer safety over automatic repeated execution.

## Alternatives Considered

### No Idempotency

Rejected.

A repeated request could create duplicate order confirmations and make the incident state inconsistent.

### Frontend-Only Prevention

Rejected.

Disabling the button after the first click does not protect against retries, refreshes, duplicate API requests, or direct API calls.

### Idempotency Only in Application Memory

Rejected.

In-memory state is not reliable across process restarts or multiple application instances.

### Database-Enforced Idempotency

Accepted.

The database provides durable uniqueness and protects the system even when multiple requests reach the backend concurrently.

## Consequences

### Positive

* Prevents duplicate resolution side effects
* Makes retries safe
* Protects against double-clicks and duplicate API requests
* Creates a deterministic resolution workflow
* Produces a stronger audit trail
* Models production-grade payment-operation behavior
* Makes the simulated environment safer and easier to test

### Negative

* Adds resolution state and idempotency data to the database
* Requires transaction handling
* Requires additional test cases for duplicate and concurrent requests
* Makes the resolution workflow slightly more complex

## MVP Boundary

Reviva does not attempt to implement a production payment gateway or distributed transaction system.

Idempotency is implemented only for the controlled MVP resolution workflow:

```text
Captured Payment
      +
Matched Failed Order
      ↓
Incident
      ↓
Eligibility
      ↓
Manager Approval
      ↓
Idempotent Mock Resolution
      ↓
Order Confirmation
      ↓
Audit Trail
```

The simulated resolution must behave as though it were a critical external side effect, even though no real payment is processed.

## Testing Requirements

The implementation must verify at minimum:

1. First valid resolution succeeds.
2. Repeating the same request does not create another resolution.
3. Repeating the same idempotency key returns the existing result.
4. A resolved incident cannot be resolved again.
5. Two concurrent resolution requests cannot both execute successfully.
6. Invalid incident states cannot trigger resolution.
7. Failed resolution does not silently create a successful audit record.
8. The final audit trail clearly records the resolution outcome.

## Decision Summary

Reviva treats idempotency as a **core safety invariant**, not an optional optimization.

The resolution endpoint must guarantee:

> **One incident → one successful resolution side effect.**

All retries, duplicate requests, and concurrent attempts must converge on the same resolution outcome without creating duplicate order confirmations.
