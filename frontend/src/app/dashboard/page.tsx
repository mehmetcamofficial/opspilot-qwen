"use client";

import { useEffect, useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";
import { alertStreamUrl, approveIncident, assignIncident, createIncident, createIncidentFromAlert, getIncidentTimeline, healthcheck, listAlerts, listIncidents } from "@/lib/api";

type TimelineItem = {
  agent: string;
  status?: string;
};

type IncidentState = {
  id?: string;
  incident_id?: string;
  status?: string;
  state?: string;
  service?: string;
  severity?: string;
  assignee?: string;
  triage_result?: {
    affected_service?: string;
    severity?: string;
  };
  hypothesis_result?: {
    confidence?: number;
    ranked_hypotheses?: Array<{ summary?: string }>;
  };
  risk_review?: {
    risk_level?: string;
  };
  remediation_plan?: {
    candidate_actions?: Array<{ title?: string }>;
  };
  postmortem?: {
    summary?: string;
  };
  agent_timeline?: TimelineItem[];
};

type EvidenceTab = "metrics" | "logs" | "deployments" | "runbooks";

type LiveAlert = {
  id: string;
  timestamp: string;
  service: string;
  severity: "P0" | "P1" | "P2" | "P3";
  message: string;
  signal: string;
  region: string;
  type: string;
  affected_users: number;
};

type IncidentTimelineEvent = {
  event: string;
  message: string;
  actor: string;
  timestamp: string;
  metadata?: Record<string, string>;
};

const stateMachine = ["triaging", "investigating", "hypothesis", "awaiting approval", "remediating", "monitoring", "resolved"];
const responderOptions = ["alex.chen", "maria.k", "sre-primary"];

const defaultEvidence: Record<EvidenceTab, string[]> = {
  metrics: ["p95 latency increased from 420ms to 2.8s", "cache hit ratio dropped from 91% to 41%", "database latency increased by 63%"],
  logs: ["Repeated cache-miss fallback warnings detected", "Checkout workers report increased downstream retries", "No security-related error pattern detected"],
  deployments: ["Recent cache configuration change detected", "No application code deployment in the last 30 minutes", "Rollback candidate identified: cache-config-v18"],
  runbooks: ["Runbook match: cache configuration rollback", "Validation step: confirm cache hit ratio recovery", "Rollback plan: restore previous cache TTL and routing config"],
};

function toneForStatus(status: string): "cyan" | "green" | "amber" | "violet" | "slate" {
  if (status === "resolved" || status === "completed") return "green";
  if (status.includes("approval") || status === "awaiting_approval") return "amber";
  if (status.includes("executed") || status.includes("remediating")) return "violet";
  if (status.includes("running") || status.includes("investigating")) return "cyan";
  return "slate";
}

function normalizeStatus(status?: string) {
  if (!status) return "standby";
  return status.replaceAll("_", " ");
}

function deriveLifecycleStep(status: string, incident: IncidentState | null) {
  if (!incident) return 0;
  if (status === "resolved") return 6;
  if (status.includes("monitoring")) return 5;
  if (status.includes("remediating") || status.includes("executed")) return 4;
  if (status.includes("approval")) return 3;
  if (status.includes("hypothesis")) return 2;
  if (status.includes("investigating")) return 1;
  return 3;
}

function agentDisplayName(agent?: string) {
  const labels: Record<string, string> = {
    triage_agent: "Triage",
    observability_agent: "Observability",
    runbook_agent: "Runbook",
    runbook_retrieval_agent: "Runbook",
    hypothesis_agent: "Hypothesis",
    remediation_planner_agent: "Planner",
    risk_safety_agent: "Safety",
    approval_agent: "Approval Gate",
    remediation_executor: "Executor",
    execution_review_agent: "Execution Review",
    postmortem_agent: "Postmortem",
  };

  if (!agent) return "Agent";
  return labels[agent] || agent.replaceAll("_agent", "").replaceAll("_", " ");
}

function displayTimelineStatus(agent: string | undefined, status: string | undefined, isResolved: boolean) {
  if (agent === "approval_agent" && isResolved) return "approved";
  if (status === "approval_required") return "awaiting approval";
  if (status === "completed") return "completed";
  if (status === "executed") return "executed";
  return status || "completed";
}

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function leadingHypothesis(state: IncidentState | null) {
  return state?.hypothesis_result?.ranked_hypotheses?.[0]?.summary || "Cache configuration regression introduced in the latest config change";
}

function recommendedAction(state: IncidentState | null) {
  return state?.remediation_plan?.candidate_actions?.[0]?.title || "Rollback cache configuration safely";
}

function postmortemSummary(state: IncidentState | null) {
  return state?.postmortem?.summary || "The incident was likely caused by cache config regression and mitigated with approval-gated rollback.";
}

function timelineFromState(state: IncidentState | null) {
  if (state?.agent_timeline?.length) return state.agent_timeline;
  return [
    { agent: "triage_agent", status: "waiting" },
    { agent: "observability_agent", status: "waiting" },
    { agent: "runbook_agent", status: "waiting" },
    { agent: "hypothesis_agent", status: "waiting" },
    { agent: "remediation_planner_agent", status: "waiting" },
    { agent: "risk_safety_agent", status: "waiting" },
    { agent: "approval_agent", status: "waiting" },
  ];
}

function normalizeIncidentState(data: IncidentState): IncidentState {
  if (data.incident_id || data.status) return data;

  return {
    ...data,
    incident_id: data.id,
    status: data.state,
    triage_result: {
      affected_service: data.service,
      severity: data.severity?.toLowerCase(),
    },
    agent_timeline: [
      { agent: "triage_agent", status: "created from alert" },
      { agent: "observability_agent", status: "waiting" },
      { agent: "approval_agent", status: "waiting" },
    ],
  };
}

export default function DashboardPage() {
  const [backendStatus, setBackendStatus] = useState<string>("not checked");
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [incidents, setIncidents] = useState<IncidentState[]>([]);
  const [alerts, setAlerts] = useState<LiveAlert[]>([]);
  const [incidentTimeline, setIncidentTimeline] = useState<IncidentTimelineEvent[]>([]);
  const [alertStreamStatus, setAlertStreamStatus] = useState<string>("connecting");
  const [loading, setLoading] = useState(false);
  const [evidenceTab, setEvidenceTab] = useState<EvidenceTab>("metrics");
  const [toast, setToast] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [visualStep, setVisualStep] = useState<number | null>(null);

  const status = normalizeStatus(incident?.status);
  const timeline = timelineFromState(incident);
  const isResolved = status === "resolved";
  const isAwaitingApproval = status.includes("approval");
  const lifecycleStep = visualStep ?? deriveLifecycleStep(status, incident);
  const canAssignIncident = Boolean(incident?.id);

  useEffect(() => {
    let mounted = true;

    listAlerts()
      .then((data) => {
        if (mounted) {
          setAlerts(data.alerts || []);
        }
      })
      .catch(() => {
        if (mounted) {
          setAlertStreamStatus("waiting for backend");
        }
      });

    const source = new EventSource(alertStreamUrl());

    source.onopen = () => {
      if (mounted) {
        setAlertStreamStatus("live");
      }
    };

    source.addEventListener("alert", (event) => {
      if (!mounted) return;
      const nextAlert = JSON.parse(event.data) as LiveAlert;
      setAlerts((current) => [nextAlert, ...current.filter((item) => item.id !== nextAlert.id)].slice(0, 6));
    });

    source.onerror = () => {
      if (mounted) {
        setAlertStreamStatus("reconnecting");
      }
    };

    return () => {
      mounted = false;
      source.close();
    };
  }, []);

  function notify(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 2200);
  }

  function showError(message: string) {
    setError(message);
    window.setTimeout(() => setError(null), 5000);
  }

  function extractErrorMessage(error: unknown, fallback: string) {
    if (error instanceof Error) return error.message;
    if (typeof error === "string") return error;
    return fallback;
  }

  async function loadIncidentTimeline(incidentId?: string) {
    if (!incidentId) {
      setIncidentTimeline([]);
      return;
    }

    try {
      const data = await getIncidentTimeline(incidentId);
      setIncidentTimeline(data.timeline || []);
    } catch {
      setIncidentTimeline([]);
    }
  }

  async function checkBackend() {
    setLoading(true);
    setError(null);
    try {
      const data = await healthcheck();
      setBackendStatus(`${data.status} | mock_llm=${data.mock_llm}`);
      notify("Backend healthcheck completed.");
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, "Backend check failed. Start FastAPI backend first.");
      setBackendStatus(`error: ${extractErrorMessage(error, "unknown")}`);
      showError(errorMsg);
      console.error("Backend check error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function startIncident() {
    setLoading(true);
    setError(null);
    setVisualStep(0);
    try {
      await sleep(300);
      setVisualStep(1);

      await sleep(300);
      setVisualStep(2);

      const data = await createIncident();
      setIncident(data.state ?? data);
      await loadIncidentTimeline(data.state?.incident_id ?? data.incident_id);

      await sleep(300);
      setVisualStep(3);

      notify("Investigation completed. Safety gate is waiting for human approval.");
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, "Failed to start incident. Check backend logs for details.");
      showError(errorMsg);
      console.error("Start incident error:", error);
      setVisualStep(null);
    } finally {
      setLoading(false);
    }
  }

  async function refreshIncidents() {
    setLoading(true);
    setError(null);
    try {
      const data = await listIncidents();
      setIncidents(data.incidents || []);
      notify("Stored incidents refreshed.");
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, "Failed to refresh incidents.");
      showError(errorMsg);
      console.error("Refresh incidents error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function promoteAlert(alertId: string) {
    setLoading(true);
    setError(null);
    try {
      const data = await createIncidentFromAlert(alertId);
      const normalized = normalizeIncidentState(data);
      setIncident(normalized);
      await loadIncidentTimeline(normalized.incident_id);
      setVisualStep(0);
      notify(`Incident created from alert ${alertId}.`);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, "Failed to create incident from live alert.");
      showError(errorMsg);
      console.error("Create incident from alert error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function assignActiveIncident(assignee: string) {
    if (!incident?.incident_id || !canAssignIncident) {
      notify("Create an incident from a live alert before assigning ownership.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await assignIncident(incident.incident_id, assignee);
      const normalized = normalizeIncidentState(data);
      setIncident(normalized);
      await loadIncidentTimeline(normalized.incident_id);
      notify(`Incident assigned to ${assignee}.`);
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, "Failed to assign incident owner.");
      showError(errorMsg);
      console.error("Assign incident error:", error);
    } finally {
      setLoading(false);
    }
  }

  async function approve() {
    if (!incident?.incident_id) {
      notify("Start an incident before approval.");
      return;
    }

    setLoading(true);
    setError(null);
    setVisualStep(4);
    try {
      await sleep(450);
      setVisualStep(5);

      const data = await approveIncident(incident.incident_id);

      await sleep(450);
      setIncident(data.state ?? data);
      await loadIncidentTimeline(data.state?.incident_id ?? data.incident_id);
      setVisualStep(6);
      notify("Remediation approved. Execution review and postmortem generated.");
    } catch (error: unknown) {
      const errorMsg = extractErrorMessage(error, "Failed to approve incident remediation.");
      showError(errorMsg);
      console.error("Approve error:", error);
      setVisualStep(deriveLifecycleStep(status, incident));
    } finally {
      setLoading(false);
    }
  }

  async function copyIncidentSummary() {
    const summary = {
      incident_id: incident?.incident_id || "no-active-incident",
      status,
      hypothesis: leadingHypothesis(incident),
      recommended_action: recommendedAction(incident),
      postmortem: postmortemSummary(incident),
    };
    await navigator.clipboard?.writeText(JSON.stringify(summary, null, 2)).catch(() => undefined);
    notify("Incident summary copied to clipboard.");
  }

  async function exportAuditLog() {
    const audit = timeline.map((item: TimelineItem, index: number) => ({
      step: index + 1,
      agent: item.agent,
      status: item.status || "completed",
    }));
    await navigator.clipboard?.writeText(JSON.stringify(audit, null, 2)).catch(() => undefined);
    notify("Audit log copied to clipboard.");
  }

  return (
    <PlatformShell>
      {/* demo-hardening-banner */}
      <section className="mx-auto mb-8 max-w-7xl rounded-[1.5rem] border border-cyan-400/15 bg-slate-950/70 p-4 shadow-[0_0_32px_rgba(34,211,238,0.06)]">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-[11px] font-black uppercase tracking-[0.2em] text-cyan-100">
                Operational Mode
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold text-slate-300">
                Frontend: Vercel
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-bold text-slate-300">
                Backend: Local FastAPI
              </span>
              <span className="rounded-full border border-violet-300/20 bg-violet-300/10 px-3 py-1 text-[11px] font-bold text-violet-100">
                Qwen-ready / mock-safe
              </span>
            </div>
            <p className="mt-2 max-w-5xl text-xs leading-5 text-slate-400">
              Live preview is deployed on Vercel. The interactive Command Center can run with a local FastAPI backend, while Qwen-compatible orchestration is shown through a safe mock fallback.
            </p>
          </div>

          <a
            href="/simulation"
            className="inline-flex shrink-0 items-center justify-center rounded-xl border border-cyan-300/25 bg-cyan-300/10 px-3 py-2 text-xs font-black text-cyan-50 transition hover:bg-cyan-300/20"
          >
            Run safe simulation →
          </a>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 pb-12 pt-6">
        {toast && (
          <div className="fixed right-6 top-24 z-[80] rounded-2xl border border-cyan-400/20 bg-slate-950/95 p-4 shadow-[0_0_40px_rgba(34,211,238,0.16)]">
            <div className="text-sm font-bold text-white">{toast}</div>
          </div>
        )}

        {error && (
          <div className="fixed right-6 top-40 z-[80] rounded-2xl border border-red-400/30 bg-red-950/95 p-4 shadow-[0_0_40px_rgba(239,68,68,0.16)]">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <div className="text-xs font-black uppercase tracking-wider text-red-300">Error</div>
                <div className="mt-1 text-sm text-red-100">{error}</div>
              </div>
              <button
                onClick={() => setError(null)}
                className="shrink-0 text-red-300 hover:text-red-200"
                aria-label="Close error"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <div className="grid gap-3 md:grid-cols-4">
            <SystemStripItem label="Frontend" value="Vercel / local" tone="green" />
            <SystemStripItem label="Backend" value={backendStatus} tone={backendStatus.startsWith("ok") ? "green" : backendStatus.startsWith("error") ? "amber" : "slate"} />
            <SystemStripItem label="Qwen mode" value="mock fallback" tone="amber" />
            <SystemStripItem label="Cloud billing" value="credits pending" tone="violet" />
          </div>
        </div>

        <section className="mb-5 rounded-3xl border border-cyan-400/15 bg-slate-950/70 p-5">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-2xl font-black text-white">Live alert stream</h2>
                <StatusBadge label={alertStreamStatus} tone={alertStreamStatus === "live" ? "green" : "amber"} />
              </div>
              <p className="mt-2 text-sm text-slate-400">
                Incoming operational alerts from the backend stream. Promote a signal when it needs incident command.
              </p>
            </div>
            <div className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-black uppercase tracking-[0.18em] text-cyan-100">
              SSE feed
            </div>
          </div>

          <div className="mt-5 grid gap-3 lg:grid-cols-3">
            {alerts.length === 0 ? (
              <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4 text-sm text-slate-400">
                Waiting for the first live alert...
              </div>
            ) : (
              alerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="font-mono text-xs font-black text-cyan-100">{alert.id}</div>
                      <h3 className="mt-2 truncate text-lg font-black text-white">{alert.service}</h3>
                    </div>
                    <StatusBadge label={alert.severity} tone={alert.severity === "P0" ? "amber" : alert.severity === "P1" ? "violet" : "slate"} />
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{alert.message}</p>
                  <div className="mt-3 grid gap-2 text-xs text-slate-400">
                    <div>Signal: {alert.signal}</div>
                    <div>Region: {alert.region}</div>
                    <div>Affected users: {alert.affected_users.toLocaleString()}</div>
                  </div>
                  <button
                    onClick={() => promoteAlert(alert.id)}
                    disabled={loading}
                    className="mt-4 w-full rounded-xl border border-cyan-300/25 bg-cyan-300/10 px-3 py-2 text-xs font-black text-cyan-50 hover:bg-cyan-300/20 disabled:opacity-50"
                  >
                    Create incident
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Command Center" tone="cyan" />
              <StatusBadge label={status} tone={toneForStatus(status)} />
              <StatusBadge label="human approval gated" tone="violet" />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">Incident lifecycle console</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Trace evidence, review policy decisions, approve remediation, and generate an auditable postmortem.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={checkBackend} disabled={loading} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50">Check Backend</button>
            <button onClick={startIncident} disabled={loading} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200 disabled:opacity-50">Start Incident</button>
            <button onClick={refreshIncidents} disabled={loading} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50">Refresh</button>
          </div>
        </div>

        <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <h2 className="text-xl font-black text-white">Incident state machine</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-7">
            {stateMachine.map((state, index) => {
              const active = index === lifecycleStep;
              const passed = Boolean(incident) && index < lifecycleStep;
              return (
                <div
                  key={state}
                  className={`rounded-2xl border p-3 transition-all duration-300 ${
                    active
                      ? "border-cyan-300 bg-cyan-300 text-slate-950 shadow-[0_0_28px_rgba(34,211,238,0.22)]"
                      : passed
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/[0.035] text-slate-400"
                  }`}
                >
                  <div className="text-xs font-black uppercase tracking-wider">Step {index + 1}</div>
                  <div className="mt-1 text-sm font-black">
                    {state === "awaiting approval" ? "approval gate" : state}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_390px]">
          <div className="space-y-5">
            <div className="grid items-start gap-5 lg:grid-cols-[0.82fr_1.18fr]">
              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-white">Incident summary</h2>
                    <p className="mt-1 font-mono text-sm text-slate-500">{incident?.incident_id || "No active incident yet"}</p>
                  </div>
                  <StatusBadge label={status} tone={toneForStatus(status)} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <MetricCard title="Service" value={incident?.triage_result?.affected_service || "checkout-api"} />
                  <MetricCard title="Environment" value="production" />
                  <MetricCard title="Severity" value={incident?.triage_result?.severity || "high"} />
                  <MetricCard title="Assignee" value={incident?.assignee || "unassigned"} />
                  <MetricCard title="Business impact" value="checkout degraded" />
                  <MetricCard title="Confidence" value={String(incident?.hypothesis_result?.confidence || "0.86")} />
                  <MetricCard title="Risk" value={incident?.risk_review?.risk_level || "medium"} />
                </div>

                <div className="mt-6 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
                  <h3 className="text-xl font-black text-white">Leading hypothesis</h3>
                  <p className="mt-3 leading-7 text-slate-300">{leadingHypothesis(incident)}</p>
                </div>
              </section>

              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-white">Evidence console</h2>
                    <p className="mt-1 text-sm text-slate-400">Evidence lineage behind the recommendation.</p>
                  </div>
                  <StatusBadge label="traceable" tone="green" />
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  {(["metrics", "logs", "deployments", "runbooks"] as EvidenceTab[]).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setEvidenceTab(tab)}
                      className={`rounded-full border px-4 py-2 text-sm font-bold ${
                        evidenceTab === tab
                          ? "border-cyan-300 bg-cyan-300 text-slate-950"
                          : "border-white/10 bg-white/[0.04] text-slate-300 hover:bg-white/[0.08]"
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>

                <div className="mt-5 grid gap-3">
                  {defaultEvidence[evidenceTab].map((item, index) => (
                    <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                      <div className="text-xs font-black uppercase tracking-wider text-cyan-300">source {index + 1}</div>
                      <div className="mt-2 text-sm leading-6 text-slate-300">{item}</div>
                    </div>
                  ))}
                </div>

                <div className="mt-5 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
                  <h3 className="font-black text-white">Why multi-agent?</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    Each agent owns one decision boundary: triage, evidence, hypothesis, risk, approval, execution review, and postmortem.
                  </p>
                </div>
              </section>
            </div>

            <div className="grid items-start gap-5 lg:grid-cols-[1fr_1fr]">
              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-white">Live agent timeline</h2>
                    <p className="mt-1 text-sm text-slate-400">Agent progress plus recorded incident events.</p>
                  </div>
                  <StatusBadge label={`${incidentTimeline.length} events`} tone={incidentTimeline.length ? "green" : "slate"} />
                </div>
                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  {timeline.map((item: TimelineItem, index: number) => (
                    <div key={`${item.agent}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div title={item.agent} className="text-sm font-black leading-5 text-cyan-100">
                            {agentDisplayName(item.agent)}
                          </div>
                          <div className="mt-1 text-xs text-slate-500">Agent step {index + 1}</div>
                        </div>
                        <div className="shrink-0 rounded-full border border-white/10 bg-slate-950/50 px-2.5 py-1 text-xs font-black text-slate-400">
                          {index + 1}
                        </div>
                      </div>

                      <div className="mt-3">
                        <StatusBadge
                          label={displayTimelineStatus(item.agent, item.status, isResolved)}
                          tone={toneForStatus(displayTimelineStatus(item.agent, item.status, isResolved))}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-5 rounded-3xl border border-cyan-400/15 bg-cyan-400/10 p-4">
                  <h3 className="font-black text-white">Incident event log</h3>
                  <div className="mt-4 space-y-3">
                    {incidentTimeline.length === 0 ? (
                      <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-3 text-sm text-slate-400">
                        Create an incident from the live alert stream to populate event history.
                      </div>
                    ) : (
                      incidentTimeline.map((event, index) => (
                        <div key={`${event.event}-${event.timestamp}-${index}`} className="rounded-2xl border border-white/10 bg-slate-950/40 p-3">
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <div className="text-sm font-black text-cyan-100">{event.event.replaceAll("_", " ")}</div>
                              <div className="mt-1 text-sm leading-6 text-slate-300">{event.message}</div>
                            </div>
                            <div className="shrink-0 rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[11px] font-black text-slate-400">
                              {event.actor}
                            </div>
                          </div>
                          <div className="mt-2 font-mono text-[11px] text-slate-500">{new Date(event.timestamp).toLocaleString()}</div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </section>

              <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-black text-white">Execution Review</h2>
                    <p className="mt-1 text-sm text-slate-400">What happened after approval and how the platform verified recovery.</p>
                  </div>
                  <StatusBadge label={isResolved ? "verified" : "pending"} tone={isResolved ? "green" : "amber"} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-3">
                  <MiniReview label="Action" value={isResolved ? "Rollback executed" : "Waiting approval"} />
                  <MiniReview label="Validation" value={isResolved ? "Latency recovered" : "Not started"} />
                  <MiniReview label="Risk" value={isResolved ? "Reduced" : "Medium"} />
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <MiniReview label="p95 latency" value={isResolved ? "2.8s → 480ms" : "2.8s"} />
                  <MiniReview label="Cache hit ratio" value={isResolved ? "41% → 89%" : "41%"} />
                </div>

                <div className={`mt-5 rounded-3xl border p-5 ${isResolved ? "border-emerald-400/20 bg-emerald-400/10" : "border-white/10 bg-white/[0.035]"}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-black text-white">{isResolved ? "Postmortem generated" : "Postmortem preview"}</h3>
                      <p className="mt-3 text-sm leading-6 text-slate-300">{postmortemSummary(incident)}</p>
                    </div>
                    <StatusBadge label={isResolved ? "final" : "draft"} tone={isResolved ? "green" : "slate"} />
                  </div>
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  <button onClick={copyIncidentSummary} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                    Copy incident summary
                  </button>
                  <button onClick={exportAuditLog} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                    Export audit log
                  </button>
                </div>
              </section>
            </div>
          </div>

          <aside className="space-y-5 xl:sticky xl:top-24">
            <section className="rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Ownership</h2>
                  <p className="mt-1 text-sm text-cyan-100/80">Assign a clear responder for the active incident.</p>
                </div>
                <StatusBadge label={incident?.assignee || "unassigned"} tone={incident?.assignee && incident.assignee !== "unassigned" ? "green" : "amber"} />
              </div>

              <div className="mt-5 grid gap-2">
                {responderOptions.map((assignee) => (
                  <button
                    key={assignee}
                    onClick={() => assignActiveIncident(assignee)}
                    disabled={loading || !canAssignIncident}
                    className={`rounded-2xl border px-4 py-3 text-left text-sm font-black transition disabled:cursor-not-allowed disabled:opacity-40 ${
                      incident?.assignee === assignee
                        ? "border-emerald-300 bg-emerald-300 text-slate-950"
                        : "border-white/10 bg-slate-950/40 text-cyan-50 hover:bg-white/[0.08]"
                    }`}
                  >
                    {assignee}
                  </button>
                ))}
              </div>
            </section>

            <section className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Safety Gate</h2>
                  <p className="mt-1 text-sm text-amber-100/80">Policy-aware control before production action.</p>
                </div>
                <StatusBadge label={isResolved ? "approved" : "approval required"} tone={isResolved ? "green" : "amber"} />
              </div>

              <div className="mt-5 space-y-3 text-sm">
                <PolicyItem label="Rule matched" value="production configuration rollback" />
                <PolicyItem label="Guardrail" value="human approval required" />
                <PolicyItem label="Rollback plan" value="restore previous cache config" />
                <PolicyItem label="Blocked alternative" value="database restart without evidence" />
              </div>

              <button onClick={approve} disabled={loading || !incident?.incident_id || isResolved} className="mt-5 w-full rounded-2xl bg-emerald-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40">
                {isResolved ? "Remediation approved" : isAwaitingApproval ? "Approve Remediation" : "Start incident first"}
              </button>
            </section>

            <section className="rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Approval Drawer</h2>
                  <p className="mt-1 text-sm text-violet-100/80">Operator decision package before remediation.</p>
                </div>
                <StatusBadge label={isResolved ? "closed" : "review"} tone={isResolved ? "green" : "violet"} />
              </div>

              <div className="mt-5 space-y-3">
                <ApprovalLine label="Recommended action" value={recommendedAction(incident)} />
                <ApprovalLine label="Evidence used" value="metrics + logs + deployment + runbook" />
                <ApprovalLine label="Policy triggered" value="production rollback requires approval" />
                <ApprovalLine label="Rollback safety" value="reversible config change" />
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
              <h2 className="text-2xl font-black text-white">Audit trail</h2>
              <div className="mt-5 space-y-3">
                <AuditItem label="Incident created" value={incident ? "recorded" : "pending"} />
                <AuditItem label="Evidence linked" value={incident ? "metrics/logs/runbook" : "pending"} />
                <AuditItem label="Policy evaluated" value={incident ? "approval required" : "pending"} />
                <AuditItem label="Operator approval" value={isResolved ? "approved" : "pending"} />
              </div>
            </section>
          </aside>
        </div>

        {incidents.length > 0 && (
          <section className="mt-6 rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Stored incidents</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {incidents.map((item: IncidentState) => (
                <div key={item.incident_id} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="font-mono text-sm font-black text-cyan-100">{item.incident_id}</div>
                  <div className="mt-2 text-sm text-slate-400">Status: {item.status}</div>
                </div>
              ))}
            </div>
          </section>
        )}
      </section>
    </PlatformShell>
  );
}

function SystemStripItem({ label, value, tone }: { label: string; value: string; tone: "cyan" | "green" | "amber" | "violet" | "slate" }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 truncate font-mono text-sm text-slate-200">{value}</div>
      <div className="mt-3"><StatusBadge label={tone} tone={tone} /></div>
    </div>
  );
}

function MetricCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{title}</div>
      <div className="mt-2 truncate text-xl font-black text-white">{value}</div>
    </div>
  );
}

function PolicyItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-amber-400/20 bg-slate-950/40 p-3">
      <div className="text-xs uppercase tracking-wider text-amber-200/70">{label}</div>
      <div className="mt-1 font-semibold text-amber-50">{value}</div>
    </div>
  );
}

function AuditItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-3 text-sm">
      <span className="font-semibold text-slate-200">{label}</span>
      <span className="font-mono text-cyan-200">{value}</span>
    </div>
  );
}

function ApprovalLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-violet-400/20 bg-slate-950/40 p-3">
      <div className="text-xs uppercase tracking-wider text-violet-200/70">{label}</div>
      <div className="mt-1 text-sm font-semibold leading-6 text-violet-50">{value}</div>
    </div>
  );
}

function MiniReview({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="text-xs uppercase tracking-wider text-slate-500">{label}</div>
      <div className="mt-2 font-black text-white">{value}</div>
    </div>
  );
}
