# ADR-001 — REVIVA Product Boundary

* **Status:** Accepted
* **Date:** August 22, 2026
* **Decision Type:** Product Scope / System Boundary
* **Related Artifact:** `prd.md`

---

## 1. Context

REVIVA is an AI-assisted cross-system payment incident investigation and resolution platform.

The MVP addresses a specific inconsistency between:

* the payment system, and
* the merchant-owned business/order system.

The flagship incident is:

```text
Payment = CAPTURED
Order   = FAILED
```

REVIVA is intended to investigate this mismatch, reconstruct the evidence, recommend an eligible resolution, obtain approval when required, execute a controlled mock resolution, and record the resulting audit trail.

The product therefore needs an explicit boundary to prevent the MVP from expanding into a payment gateway, payment processor, ERP, CRM, fraud platform, or autonomous financial agent.

---

## 2. Decision

REVIVA will own the **incident investigation and controlled resolution orchestration layer** between the payment system and the merchant's business system.

REVIVA will **not** own payment processing, banking, money movement, or the merchant's complete business platform.

The MVP boundary is:

```text
Payment System
      │
      │ Payment Events
      ▼
┌─────────────────────────────┐
│           REVIVA            │
│                             │
│ Event Correlation           │
│ State Comparison            │
│ Incident Detection          │
│ Evidence Collection         │
│ Timeline Reconstruction     │
│ Deterministic Investigation │
│ AI-Assisted Investigation   │
│ Resolution Recommendation   │
│ Policy Evaluation           │
│ Guardrails                  │
│ Approval Workflow           │
│ Resolution Orchestration    │
│ Audit Trail                 │
└─────────────────────────────┘
      │
      │ Controlled Resolution
      ▼
Merchant Business System
(Mock Resolution Provider in MVP)
```

---

## 3. REVIVA Owns

REVIVA owns the following responsibilities:

* Payment/business event correlation
* State mismatch detection
* Incident creation and lifecycle
* Evidence collection
* Timeline reconstruction
* Deterministic investigation
* AI-assisted investigation
* Investigation results
* Resolution recommendations
* Merchant policies
* Deterministic guardrails
* Human approval workflow
* Resolution orchestration
* Idempotency protection
* Audit trail
* Operator-facing incident dashboard

---

## 4. REVIVA Does Not Own

REVIVA does not own:

* Payment processing
* Payment gateway functionality
* Payment processor functionality
* Banking infrastructure
* Real-money movement
* Real payment retries
* Merchant's complete order platform
* Inventory management
* CRM
* ERP
* Customer account infrastructure
* Universal fraud detection
* Full dispute management
* Generic payment optimization

The MVP uses simulated payment events and a mock merchant resolution provider.

---

## 5. Why This Boundary

This boundary is intentionally narrow.

The product problem is not:

> "Build another payment platform."

The problem is:

> "Investigate and safely resolve inconsistencies between payment state and merchant business state."

Keeping REVIVA at this boundary provides several benefits:

### 5.1 Focused MVP

The team can build one complete incident loop instead of attempting to reproduce an entire payment ecosystem.

### 5.2 Clear Ownership

External systems remain responsible for their own domains.

REVIVA is responsible for understanding and orchestrating the incident between them.

### 5.3 Safer AI Usage

AI can investigate and recommend without directly controlling financial or business state.

### 5.4 Easier Testing

The payment system and merchant system can be simulated deterministically.

### 5.5 Easier Demonstration

The complete workflow can be demonstrated end-to-end during the buildathon.

### 5.6 Reduced Architectural Complexity

The MVP does not require unnecessary microservices, Kubernetes, RAG, vector databases, or distributed infrastructure.

---

## 6. AI Boundary

AI is explicitly inside the investigation layer but outside the execution authority boundary.

```text
Structured Incident Evidence
          ↓
     Deterministic
     Investigation
          ↓
   Ambiguity remains?
      /          \
    No            Yes
    ↓              ↓
Recommendation   AI Investigation
                     ↓
              Structured Output
                     ↓
              Schema Validation
                     ↓
             Deterministic Policy
                     ↓
              Deterministic Guardrails
                     ↓
               Human Approval
                     ↓
             Controlled Execution
```

AI must not:

* authorize itself
* bypass approval
* bypass policy
* change monetary amounts
* override limits
* execute financial actions
* directly mutate merchant business state
* modify audit history

The governing principle is:

> **AI proposes. Deterministic software decides. The database guarantees. The audit log remembers.**

---

## 7. Resolution Boundary

The MVP supports one primary resolution:

> **Mock order-confirmation reprocess**

REVIVA may orchestrate this controlled action after all applicable policies, guardrails, authorization, and approval requirements have been satisfied.

The MVP does not perform:

* real payment retries
* refunds
* real money transfers
* real banking operations

---

## 8. External System Assumptions

REVIVA assumes that external systems provide relevant events containing sufficient identifiers and state information.

For payment events, the MVP expects information such as:

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

For merchant order events, the MVP expects information such as:

* merchant ID
* order ID
* payment/reference ID
* amount
* order status
* event ID
* event type
* event timestamp
* received timestamp

REVIVA does not become the system of record for the external systems.

---

## 9. Consequences

### Positive Consequences

* Clear product identity
* Small and defensible MVP
* Strong separation of responsibilities
* Safer AI architecture
* Deterministic business decisions
* Easier automated testing
* Easier failure injection
* Easier buildathon demonstration
* Reduced infrastructure complexity

### Negative Consequences

* REVIVA cannot demonstrate real payment processing.
* The resolution provider is simulated in the MVP.
* Some real-world payment incidents will remain outside MVP scope.
* The system will not provide complete payment reconciliation.
* Future integrations will require explicit contracts with external systems.

These limitations are intentional.

---

## 10. Alternatives Considered

### Alternative A — Build a Complete Payment Platform

**Rejected.**

This would significantly expand the MVP and move REVIVA away from its core incident-investigation problem.

### Alternative B — Build a Generic Payment Reconciliation System

**Rejected.**

The MVP is specifically focused on cross-system payment/business-state inconsistencies rather than general reconciliation.

### Alternative C — Let AI Control Resolution

**Rejected.**

This conflicts with REVIVA's safety requirements.

AI output is untrusted input and cannot independently authorize or execute consequential actions.

### Alternative D — Build a Fully Autonomous Financial Agent

**Rejected.**

This would introduce unnecessary risk and complexity and violates the defined AI safety boundary.

---

## 11. Scope Rule

Any proposed feature must be evaluated against this question:

> **Does this feature directly help REVIVA investigate, explain, authorize, or safely resolve the defined payment/business-state incident?**

If the answer is **no**, the feature should not enter the MVP without an explicit scope decision.

---

## 12. Relationship to PRD

This ADR formalizes the product boundary defined in `prd.md`.

The PRD establishes that REVIVA owns:

* incident investigation
* event correlation
* evidence
* timeline
* investigation result
* recommendation
* policies
* guardrails
* approval workflow
* resolution orchestration
* audit

It also explicitly excludes:

* payment processing
* banking
* money movement
* the merchant's complete order platform
* inventory
* CRM
* ERP
* customer account infrastructure

---

## 13. Decision Outcome

**Accepted.**

REVIVA will remain a focused **cross-system payment incident investigation and controlled-resolution platform**.

The MVP will demonstrate one complete, safe incident loop:

```text
Captured Payment
      ↓
Failed Merchant Order
      ↓
Deterministic Correlation
      ↓
Incident Detection
      ↓
Evidence + Timeline
      ↓
Investigation
      ↓
Optional AI Explanation
      ↓
Resolution Recommendation
      ↓
Policy + Guardrails
      ↓
Human Approval
      ↓
Idempotent Mock Resolution
      ↓
Order Confirmed
      ↓
Complete Audit Trail
```

This boundary is binding for MVP implementation unless superseded by a later ADR.
