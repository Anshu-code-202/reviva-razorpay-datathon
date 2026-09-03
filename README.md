# REVIVA

## Autonomous Payment Recovery & Revenue Intelligence

REVIVA is a safety-first payment recovery system for a common commerce failure: **a payment is captured, but the corresponding merchant order remains failed**.

Instead of blindly retrying payments or moving money, REVIVA turns the inconsistency into a controlled operational workflow:

**Detect → Classify → Evaluate → Approve → Recover → Audit**

> **AI proposes. Deterministic software decides. The database guarantees. The audit log remembers.**

---

## Why REVIVA?

A captured payment with a failed order creates an operational gap:

- The customer may have paid successfully.
- The merchant order may still appear failed.
- A manual investigation is required.
- An unsafe retry could create duplicate financial effects.

REVIVA focuses on the recovery of the **order-confirmation workflow**, not on moving money.

### MVP safety boundary

REVIVA does **not**:

- retry a payment,
- initiate a refund,
- move or transfer money,
- autonomously authorize financial actions.

The MVP recovery action is a **mock reprocessing of the merchant order-confirmation workflow**.

---

## Core Workflow

```text
Payment + Order Events
        │
        ▼
Incident Detection
        │
        ▼
Bounded Classification
        │
        ▼
Eligibility Evaluation
        │
        ▼
Human Approval
        │
        ▼
Guarded Recovery
        │
        ├── Persist Resolution
        │
        └── Record Audit Event
```

Every recovery attempt passes through explicit gates before the recovery service executes.

---

## Canonical Incident

The primary MVP incident is:

`CAPTURED_PAYMENT_ORDER_FAILURE`

Example:

```text
Payment:  pay_test_001
Amount:   ₹500 INR
Status:   CAPTURED

Order:    order_test_001
Status:   FAILED

Result:   Payment/order inconsistency detected
```

The incident ID is deterministic for the payment/order pair:

`INC-{payment_id}-{order_id}`

This makes repeated detection idempotent at the incident level.

---

## Deterministic Classification

The current recovery path uses a bounded classifier in `app/ai/classifier.py`.

It returns a controlled recommendation rather than free-form text:

| Recommendation | Meaning |
|---|---|
| `MANUAL_REVIEW` | Evidence does not support automated recovery |
| `REPROCESS_ORDER_CONFIRMATION_CANDIDATE` | Candidate for the guarded MVP recovery workflow |
| `NO_ACTION_ALREADY_RESOLVED` | Incident is already resolved |
| `REQUEST_MISSING_EVIDENCE` | More evidence is required |

**Important:** the current implementation does not require a live LLM or external AI API to execute recovery. The classifier is deliberately bounded and deterministic for the MVP.

---

## Safety & Recovery Guardrails

The recovery service does not treat a recommendation as authorization.

Before a successful recovery, the workflow verifies the currently implemented control gates, including:

1. The incident exists.
2. The incident is in the required `DETECTED` state for eligibility.
3. The incident type is the supported canonical recovery scenario.
4. Eligibility has been evaluated successfully.
5. A human approval exists with decision `APPROVED`.
6. The approval contains a non-blank approver identity.
7. An existing resolution is not already recorded for the same idempotency key or incident.
8. A successful recovery persists a resolution and an audit event.

The implementation intentionally separates:

**recommendation → eligibility → approval → execution**

so that no single classifier decision can directly trigger recovery.

---

## Idempotency

Recovery is designed to be safe against repeated requests.

REVIVA checks for an existing resolution by:

- the supplied idempotency key, and
- the incident itself.

A repeated recovery request therefore returns the existing resolution instead of executing the recovery action again.

The resolution is persisted with a unique idempotency key in the database.

---

## Auditability

A successful recovery creates a persisted resolution and an audit event such as:

`RECOVERY_EXECUTED`

The audit trail captures the operational result of the recovery workflow so the action can be inspected after execution.

> The audit trail is persisted and queryable; production-grade immutable/WORM audit storage is outside this MVP.

---

## Architecture

```text
┌──────────────────────────┐
│ Next.js Operations UI    │
└────────────┬─────────────┘
             │ HTTP
             ▼
┌──────────────────────────┐
│ FastAPI API              │
├──────────────────────────┤
│ Incident Routes          │
│ Eligibility Routes       │
│ Approval Routes          │
│ Recovery Routes          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Domain Services          │
│                          │
│ Detection                │
│ Classification           │
│ Eligibility              │
│ Approval                 │
│ Recovery                 │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Repository Layer         │
│ + SQLAlchemy             │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ PostgreSQL               │
│                          │
│ Payments                 │
│ Orders                   │
│ Incidents                │
│ Eligibility Evaluations  │
│ Approvals                │
│ Resolutions              │
│ Evidence                 │
│ Audit Events             │
└──────────────────────────┘
```

The project is intentionally implemented as a focused application rather than a collection of unnecessary microservices.

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Validation:** Pydantic
- **Frontend:** Next.js / React
- **Testing:** pytest
- **Environment / package management:** `uv`

Python compatibility is defined by the repository's `pyproject.toml` (`>=3.14`).

---

## Repository Structure

```text
.
├── app/
│   ├── api/
│   ├── ai/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── frontend/
├── migrations/
├── scripts/
├── tests/
├── docs/
├── main.py
├── pyproject.toml
└── README.md
```

---

## Run the Demo

### 1. Backend setup

Install dependencies:

```bash
uv sync
```

Set a PostgreSQL connection string in `.env`:

```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
```

Run migrations:

```bash
uv run alembic upgrade head
```

Seed the deterministic demo data:

```bash
uv run python scripts/seed_reviva_test_data.py
```

Start the API:

```bash
uv run uvicorn app.main:app --reload
```

Health check:

```text
GET /health
```

Expected response:

```json
{"status":"ok"}
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local Next.js development server shown by the command output.

---

## Demo Sequence

For a clean judge demonstration:

1. Show the captured payment and failed order.
2. Trigger or inspect incident detection.
3. Show the bounded classification recommendation.
4. Show the eligibility result.
5. Approve the recovery as an Operations Manager.
6. Execute the guarded recovery.
7. Show the successful resolution.
8. Show the `RECOVERY_EXECUTED` audit event.
9. Repeat the same recovery request to demonstrate idempotent behavior.

The important story is not just that recovery succeeds — it is that **recovery succeeds only after deterministic checks and human approval, and repeated requests do not execute it twice**.

---

## API Surface

| Area | Endpoint | Purpose |
|---|---|---|
| Health | `GET /health` | Service health check |
| Simulator | `/simulator/*` | Demo/test event flows |
| Incidents | `/incidents/*` | Detect, classify, inspect incidents and audit history |
| Eligibility | `/incidents/{incident_id}/eligibility` | Evaluate recovery eligibility |
| Approval | `/incidents/{incident_id}/approval` | Inspect or record human approval |
| Recovery | `/incidents/{incident_id}/recovery` | Execute or inspect guarded recovery |

Exact request/response contracts are defined in the FastAPI routes and Pydantic schemas.

---

## Database Model

The MVP persists the workflow across domain entities including:

- `payments`
- `orders`
- `incidents`
- `eligibility_evaluations`
- `approvals`
- `resolutions`
- `evidence`
- `audit_events`

This allows the system to reconstruct what was detected, evaluated, approved, executed, and recorded.

---

## Testing

The repository includes unit, service, safety, API, and end-to-end workflow coverage.

Final verification:

```bash
pytest
```

Latest submission verification:

```text
31 passed
```

The recovery safety tests specifically cover controls such as eligibility requirements, approval requirements, successful recovery, idempotency, duplicate recovery prevention, and audit-event creation.

---

## What Makes REVIVA Different

REVIVA is deliberately **not** an autonomous payment bot.

Its safety model is:

```text
AI / Classifier
      │
      ▼
Recommendation
      │
      ▼
Deterministic Eligibility
      │
      ▼
Human Approval
      │
      ▼
Guarded Recovery
      │
      ▼
Persisted Resolution + Audit
```

This creates a clear separation between **what the system recommends** and **what the system is allowed to execute**.

---

## Current MVP Limitations

This repository is a hackathon MVP and intentionally has a narrow scope.

- The recovery action is a mocked merchant order-confirmation reprocessing workflow.
- It does not move money or retry payment capture.
- The current classifier is deterministic; there is no live LLM dependency in the recovery path.
- The MVP focuses on the captured-payment / failed-order incident type.
- Demo data is local/test data; this is not a production Razorpay integration.
- Production authentication/authorization infrastructure, distributed queues, external payment/order adapters, and enterprise observability are outside the current MVP boundary.
- Audit events are persisted, but production-grade immutable audit storage is outside scope.

These limitations are intentional boundaries, not hidden dependencies.

---

## Engineering Principle

> **AI proposes. Deterministic software decides. The database guarantees. The audit log remembers.**

REVIVA's goal is not to automate everything. It is to automate the **safe, repeatable part** of payment recovery while keeping authorization, financial safety, and traceability explicit.
