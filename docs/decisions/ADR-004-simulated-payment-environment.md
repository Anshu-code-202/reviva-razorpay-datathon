# ADR-004 — Simulated Payment Environment

* **Status:** Accepted
* **Date:** August 22, 2026
* **Decision Type:** Architecture / MVP Scope
* **Related Artifacts:** `prd.md`, `ADR-001-reviva-product-boundary.md`, `ADR-002-mvp-incident.md`, `ADR-003-ai-safety-boundary.md`

---

## 1. Context

REVIVA investigates cross-system inconsistencies between payment state and merchant business state.

The MVP incident is:

```text
Payment = CAPTURED
Order   = FAILED
```

The complete workflow requires:

* payment events
* merchant order events
* event correlation
* incident detection
* investigation
* AI-assisted explanation
* policy evaluation
* guardrails
* approval workflow
* resolution execution
* audit trail

A key architectural decision is whether the MVP should integrate with real payment systems or use a simulated environment.

---

## 2. Decision

REVIVA MVP will use a **simulated payment environment**.

The MVP will not integrate with:

* real banks
* real payment gateways
* real payment processors
* real merchant production systems
* real money movement systems

Instead, the system will generate and process deterministic payment events that emulate realistic payment behavior.

---

## 3. Why This Decision

The purpose of the MVP is to demonstrate:

> **Incident investigation and controlled resolution.**

The purpose is not to demonstrate:

> **Payment processing infrastructure.**

Using a simulated environment allows the team to focus on the product's core value while avoiding unnecessary integration complexity.

---

## 4. Scope of Simulation

The simulated environment is responsible for producing payment-related events used by REVIVA.

Examples include:

```text
PAYMENT_CREATED
PAYMENT_AUTHORIZED
PAYMENT_CAPTURED
PAYMENT_FAILED
PAYMENT_REFUNDED
```

The MVP incident primarily uses:

```text
PAYMENT_CAPTURED
```

as the successful payment state involved in the flagship incident.

---

## 5. Merchant Order Simulation

The MVP shall also include a simulated merchant order system.

Example order states:

```text
ORDER_CREATED
ORDER_PENDING
ORDER_CONFIRMED
ORDER_FAILED
```

The flagship incident uses:

```text
ORDER_FAILED
```

as the inconsistent merchant business state.

The mock resolution process may transition:

```text
ORDER_FAILED
      ↓
ORDER_CONFIRMED
```

after successful policy evaluation, approval, and execution.

---

## 6. System Boundary

The simulated environment exists outside REVIVA's core responsibility.

Conceptually:

```text
┌─────────────────────┐
│ Simulated Payment   │
│ Environment         │
└─────────┬───────────┘
          │
          │ Payment Events
          ▼
┌─────────────────────┐
│       REVIVA        │
└─────────┬───────────┘
          │
          │ Resolution Request
          ▼
┌─────────────────────┐
│ Mock Merchant       │
│ Resolution Provider │
└─────────────────────┘
```

REVIVA consumes events but does not become a payment processor.

---

## 7. Event Model Requirements

The simulated payment environment must generate realistic event data.

Minimum payment event fields:

* merchant_id
* payment_id
* order_reference_id
* amount
* currency
* payment_status
* event_id
* event_type
* event_timestamp
* received_timestamp

Example:

```json
{
  "merchant_id": "merchant_001",
  "payment_id": "pay_123",
  "order_reference_id": "order_456",
  "amount": 1000,
  "currency": "INR",
  "payment_status": "CAPTURED",
  "event_type": "PAYMENT_CAPTURED"
}
```

---

## 8. Merchant Event Requirements

The simulated merchant system must generate realistic order events.

Minimum fields:

* merchant_id
* order_id
* payment_reference_id
* amount
* order_status
* event_id
* event_type
* event_timestamp
* received_timestamp

Example:

```json
{
  "merchant_id": "merchant_001",
  "order_id": "order_456",
  "payment_reference_id": "pay_123",
  "order_status": "FAILED",
  "event_type": "ORDER_FAILED"
}
```

---

## 9. Deterministic Incident Creation

The simulated environment must support deterministic creation of the MVP incident.

Example scenario:

```text
PAYMENT_CAPTURED
       +
ORDER_FAILED
       ↓
Correlation
       ↓
State Mismatch
       ↓
Incident Created
```

The environment should reliably reproduce this scenario during testing and demonstrations.

---

## 10. Failure Injection Support

The simulated environment shall support controlled failure generation.

Examples:

### Duplicate Events

```text
PAYMENT_CAPTURED
PAYMENT_CAPTURED
```

### Delayed Events

```text
Payment Event
      ↓
Delay
      ↓
Received Later
```

### Missing Events

```text
Expected Event
      ↓
Not Delivered
```

### Out-of-Order Events

```text
Event B Arrives
Before
Event A
```

These scenarios help validate REVIVA's robustness.

---

## 11. AI Testing Benefits

A simulated environment provides high-quality test data for AI-assisted investigation.

Benefits include:

* reproducible incidents
* controlled ambiguity
* known root causes
* repeatable demonstrations
* easier evaluation of AI outputs

AI behavior becomes easier to inspect because the ground truth is known.

---

## 12. Safety Benefits

Using simulation ensures:

* no real money movement
* no banking impact
* no merchant production impact
* no customer impact
* no regulatory exposure
* no accidental financial loss

This aligns with REVIVA's safety-first design philosophy.

---

## 13. Buildathon Benefits

The simulated environment improves buildathon execution.

Benefits include:

* fewer external dependencies
* faster implementation
* easier debugging
* predictable demos
* reduced operational risk
* easier judging and explanation

The team controls the entire workflow.

---

## 14. Consequences

### Positive Consequences

* Faster development
* Reduced integration complexity
* Safer testing
* Repeatable demonstrations
* Deterministic scenarios
* Easier automated testing
* Easier failure injection
* Easier debugging
* Stronger architectural focus

### Negative Consequences

* No production payment integration
* No live banking interaction
* No real settlement workflow
* Limited demonstration of payment infrastructure expertise
* Real-world integration challenges remain untested

These limitations are intentional.

---

## 15. Alternatives Considered

### Alternative A — Real Razorpay Integration

**Rejected.**

Adds integration complexity without improving the core investigation workflow.

### Alternative B — Bank Integration

**Rejected.**

Outside MVP scope and introduces unnecessary operational risk.

### Alternative C — Hybrid Real + Simulated System

**Rejected.**

Increases implementation effort while providing limited MVP value.

### Alternative D — Fully Simulated Environment

**Accepted.**

Provides the simplest path to demonstrating REVIVA's core capability.

---

## 16. Future Evolution

Future versions may support:

* payment gateway integrations
* webhook integrations
* merchant platform integrations
* real event ingestion
* production deployment

Such integrations must not change REVIVA's core product boundary:

> REVIVA investigates and orchestrates resolution.

It does not become a payment processor.

---

## 17. Decision Rule

Any proposed integration must satisfy:

> **Does this integration improve REVIVA's ability to investigate, explain, authorize, or safely resolve incidents?**

If the answer is no, the integration should not be added to the MVP.

---

## 18. Decision Outcome

**Accepted.**

REVIVA MVP will use a fully simulated payment environment and a mock merchant resolution provider.

The demonstration workflow is:

```text
Simulated Payment Event
          +
Simulated Merchant Event
          ↓
Deterministic Correlation
          ↓
Incident Detection
          ↓
Evidence Collection
          ↓
Timeline Reconstruction
          ↓
Investigation
          ↓
Optional AI Explanation
          ↓
Policy Evaluation
          ↓
Guardrails
          ↓
Human Approval
          ↓
Mock Resolution Execution
          ↓
Audit Trail
```

This decision is binding for the MVP unless superseded by a later ADR.

