"use client";

import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";
const INCIDENT_ID = "INC-pay_demo_001-order_demo_001";

type Incident = {
  incident_id: string;
  type: string;
  status: string;
};

type Classification = {
  incident_id: string;
  recommendation: string;
};

type Eligibility = {
  eligible: boolean;
  reason?: string;
};

type Approval = {
  decision: string;
  approved_by?: string;
  reason?: string;
};

type Recovery = {
  status: string;
  resolution_type?: string;
  result?: string;
};

type AuditEvent = {
  event_type: string;
  actor_type?: string;
  description?: string;
};

export default function Home() {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [classification, setClassification] =
    useState<Classification | null>(null);
  const [eligibility, setEligibility] =
    useState<Eligibility | null>(null);
  const [approval, setApproval] =
    useState<Approval | null>(null);
  const [recovery, setRecovery] =
    useState<Recovery | null>(null);
  const [audit, setAudit] =
    useState<AuditEvent[]>([]);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] =
    useState(false);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] =
    useState("");

  async function fetchJSON<T>(
    url: string,
    options?: RequestInit,
  ): Promise<T> {
    const response = await fetch(url, options);

    if (!response.ok) {
      let detail = `API request failed: ${response.status}`;

      try {
        const body = await response.json();
        if (body.detail) {
          detail = body.detail;
        }
      } catch {
        // Keep default error message.
      }

      throw new Error(detail);
    }

    return response.json();
  }

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const incidentData =
        await fetchJSON<Incident>(
          `${API_BASE}/incidents/${INCIDENT_ID}`,
        );

      const [classificationData, auditData] =
        await Promise.all([
          fetchJSON<Classification>(
            `${API_BASE}/incidents/${INCIDENT_ID}/classify`,
            {
              method: "POST",
            },
          ),
          fetchJSON<AuditEvent[]>(
            `${API_BASE}/incidents/${INCIDENT_ID}/audit`,
          ),
        ]);

      setIncident(incidentData);
      setClassification(classificationData);
      setAudit(auditData);

      try {
        const eligibilityData =
          await fetchJSON<Eligibility>(
            `${API_BASE}/incidents/${INCIDENT_ID}/eligibility`,
            {
              method: "POST",
            },
          );

        setEligibility(eligibilityData);
      } catch {
        setEligibility(null);
      }

      try {
        const approvalData =
          await fetchJSON<Approval>(
            `${API_BASE}/incidents/${INCIDENT_ID}/approval`,
          );

        setApproval(approvalData);
      } catch {
        setApproval(null);
      }

      try {
        const recoveryData =
          await fetchJSON<Recovery>(
            `${API_BASE}/incidents/${INCIDENT_ID}/recovery`,
          );

        setRecovery(recoveryData);
      } catch {
        setRecovery(null);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to REVIVA backend.",
      );
    } finally {
      setLoading(false);
    }
  }

  async function approveRecovery() {
    try {
      setActionLoading(true);
      setActionMessage("");
      setError("");

      await fetchJSON<Approval>(
        `${API_BASE}/incidents/${INCIDENT_ID}/approval`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            approved_by: "ops_manager_001",
            reason:
              "Approved after reviewing the REVIVA eligibility evaluation.",
          }),
        },
      );

      setActionMessage(
        "Recovery approved successfully.",
      );

      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Approval failed.",
      );
    } finally {
      setActionLoading(false);
    }
  }

  async function executeRecovery() {
    try {
      setActionLoading(true);
      setActionMessage("");
      setError("");

      const idempotencyKey =
        `reviva-${INCIDENT_ID}-${Date.now()}`;

      await fetchJSON<Recovery>(
        `${API_BASE}/incidents/${INCIDENT_ID}/recovery`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            idempotency_key: idempotencyKey,
          }),
        },
      );

      setActionMessage(
        "Recovery executed successfully.",
      );

      await loadDashboard();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Recovery execution failed.",
      );
    } finally {
      setActionLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const isApproved =
    approval?.decision === "APPROVED";

  const isRecovered =
    recovery?.status === "SUCCESS";

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-950/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500 font-bold text-slate-950">
                R
              </div>

              <h1 className="text-xl font-bold tracking-tight">
                REVIVA
              </h1>
            </div>

            <p className="mt-1 text-sm text-slate-400">
              Autonomous Payment Recovery & Revenue Intelligence
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            System Operational
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-8">
        {loading && (
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-8 text-center text-slate-400">
            Loading REVIVA incident...
          </div>
        )}

        {error && (
          <div className="mb-5 rounded-xl border border-red-500/30 bg-red-500/10 p-5 text-red-300">
            <p className="font-semibold">
              REVIVA action failed
            </p>

            <p className="mt-1 text-sm">
              {error}
            </p>

            <button
              onClick={loadDashboard}
              className="mt-4 rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white hover:bg-red-400"
            >
              Retry
            </button>
          </div>
        )}

        {actionMessage && (
          <div className="mb-5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
            âœ“ {actionMessage}
          </div>
        )}

        {!loading && !error && incident && (
          <>
            <div className="mb-6">
              <p className="text-sm text-slate-400">
                Active Incident
              </p>

              <div className="mt-2 flex flex-col justify-between gap-4 md:flex-row md:items-end">
                <div>
                  <h2 className="text-2xl font-bold">
                    {incident.incident_id}
                  </h2>

                  <p className="mt-1 font-mono text-sm text-slate-400">
                    {incident.type}
                  </p>
                </div>

                <span className="w-fit rounded-full border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-400">
                  {incident.status}
                </span>
              </div>
            </div>

            <div className="grid gap-5 lg:grid-cols-3">
              <Card title="Payment">
                <StatusRow
                  label="Amount"
                  value="â‚¹500 INR"
                />

                <StatusRow
                  label="Payment status"
                  value="CAPTURED"
                  success
                />

                <StatusRow
                  label="Payment ID"
                  value="pay_demo_001"
                  mono
                />
              </Card>

              <Card title="Order">
                <StatusRow
                  label="Order ID"
                  value="order_demo_001"
                  mono
                />

                <StatusRow
                  label="Order status"
                  value="FAILED"
                  warning
                />

                <StatusRow
                  label="Correlation"
                  value="Exact match"
                  success
                />
              </Card>

              <Card title="AI Classification">
                <p className="text-xs uppercase tracking-wider text-slate-500">
                  Recommendation
                </p>

                <div className="mt-3 rounded-lg border border-blue-500/20 bg-blue-500/10 p-4">
                  <p className="text-sm font-semibold leading-6 text-blue-300">
                    {classification?.recommendation ??
                      "Unavailable"}
                  </p>
                </div>

                <p className="mt-3 text-xs leading-5 text-slate-500">
                  AI recommends only. It does not authorize
                  or execute recovery.
                </p>
              </Card>
            </div>

            <div className="mt-5 grid gap-5 lg:grid-cols-2">
              <Card title="Safety & Eligibility">
                <StatusRow
                  label="Payment captured"
                  value="PASS"
                  success
                />

                <StatusRow
                  label="Exact payment/order correlation"
                  value="PASS"
                  success
                />

                <StatusRow
                  label="Order remains failed"
                  value="PASS"
                  success
                />

                <StatusRow
                  label="Eligibility"
                  value={
                    eligibility
                      ? eligibility.eligible
                        ? "ELIGIBLE"
                        : "NOT ELIGIBLE"
                      : "EVALUATING"
                  }
                  success={eligibility?.eligible}
                  warning={
                    eligibility
                      ? !eligibility.eligible
                      : false
                  }
                />

                {eligibility?.reason && (
                  <p className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-xs leading-5 text-slate-500">
                    {eligibility.reason}
                  </p>
                )}
              </Card>

              <Card title="Operator Controls">
                <StatusRow
                  label="Approval"
                  value={
                    approval?.decision ?? "PENDING"
                  }
                  success={isApproved}
                  warning={!approval}
                />

                {approval?.approved_by && (
                  <StatusRow
                    label="Approved by"
                    value={approval.approved_by}
                  />
                )}

                <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Allowed Action
                  </p>

                  <p className="mt-2 font-semibold text-white">
                    REPROCESS_ORDER_CONFIRMATION
                  </p>

                  <p className="mt-2 text-sm leading-6 text-slate-400">
                    Mock merchant order-confirmation workflow.
                    No monetary movement.
                  </p>
                </div>

                {!isApproved && !isRecovered && (
                  <button
                    onClick={approveRecovery}
                    disabled={
                      actionLoading ||
                      eligibility?.eligible !== true
                    }
                    className="w-full rounded-lg bg-emerald-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {actionLoading
                      ? "Processing..."
                      : "Approve Recovery"}
                  </button>
                )}

                {isApproved && !isRecovered && (
                  <button
                    onClick={executeRecovery}
                    disabled={actionLoading}
                    className="w-full rounded-lg bg-blue-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {actionLoading
                      ? "Executing..."
                      : "Execute Recovery"}
                  </button>
                )}

                {isRecovered && (
                  <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
                    <p className="font-semibold text-emerald-300">
                      âœ“ Recovery completed
                    </p>

                    <p className="mt-1 text-xs text-slate-400">
                      The guarded recovery has already been
                      executed for this incident.
                    </p>
                  </div>
                )}

                <StatusRow
                  label="Recovery status"
                  value={
                    recovery?.status ??
                    "NOT EXECUTED"
                  }
                  success={isRecovered}
                  warning={!recovery}
                />

                {recovery?.result && (
                  <p className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-emerald-300">
                    {recovery.result}
                  </p>
                )}
              </Card>
            </div>

            <div className="mt-5">
              <Card title="Audit Trail">
                {audit.length === 0 ? (
                  <p className="text-sm text-slate-500">
                    No audit events available.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {audit.map((event, index) => (
                      <div
                        key={`${event.event_type}-${index}`}
                        className="flex gap-4"
                      >
                        <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
                          âœ“
                        </div>

                        <div>
                          <p className="font-medium text-slate-200">
                            {event.event_type}
                          </p>

                          <p className="mt-1 text-sm text-slate-400">
                            {event.description ??
                              "Audit event recorded"}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>

            <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="font-semibold">
                    REVIVA Safety Model
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    AI proposes. Deterministic software decides.
                    The database guarantees. The audit log remembers.
                  </p>
                </div>

                <button
                  onClick={loadDashboard}
                  disabled={actionLoading}
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-40"
                >
                  Refresh
                </button>
              </div>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

function Card({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-slate-300">
        {title}
      </h3>

      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
}

function StatusRow({
  label,
  value,
  mono = false,
  success = false,
  warning = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
  success?: boolean;
  warning?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-800 pb-3 last:border-0 last:pb-0">
      <span className="text-sm text-slate-500">
        {label}
      </span>

      <span
        className={`text-right text-sm font-medium ${
          success
            ? "text-emerald-400"
            : warning
              ? "text-amber-400"
              : "text-slate-200"
        } ${mono ? "font-mono" : ""}`}
      >
        {value}
      </span>
    </div>
  );
}

