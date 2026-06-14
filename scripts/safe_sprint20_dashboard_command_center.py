from pathlib import Path
import subprocess
import shutil
import sys

ROOT = Path(".")
FRONTEND = ROOT / "frontend"
SRC = FRONTEND / "src"
BACKUP_DIR = ROOT / "scripts" / "_backups_sprint20_dashboard"

FILES = [
    SRC / "components" / "ThemeToggle.tsx",
    SRC / "components" / "PlatformShell.tsx",
    SRC / "app" / "dashboard" / "page.tsx",
]

def write(path, content):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n")

def backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for file in FILES:
        if file.exists():
            target = BACKUP_DIR / str(file).replace("/", "__")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)

def restore():
    for file in FILES:
        target = BACKUP_DIR / str(file).replace("/", "__")
        if target.exists():
            shutil.copyfile(target, file)

def run_build():
    return subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

backup()

write(SRC / "components" / "ThemeToggle.tsx", r'''
export function ThemeToggle() {
  return (
    <div className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-2 text-xs font-black text-violet-100">
      Mission Dark
    </div>
  );
}
''')

write(SRC / "components" / "PlatformShell.tsx", r'''
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { OpsPilotLogo } from "./OpsPilotLogo";
import { ThemeToggle } from "./ThemeToggle";
import { LanguageToggle } from "./LanguageToggle";

type PlatformShellProps = {
  children: React.ReactNode;
};

const fullNavItems = [
  ["Home", "/"],
  ["Command Center", "/dashboard"],
  ["Simulation", "/simulation"],
  ["Architecture", "/architecture"],
  ["Governance", "/admin"],
  ["Reasoning Graph", "/knowledge-graph"],
];

const pageMeta: Record<string, { title: string; subtitle: string; actions: [string, string][] }> = {
  "/dashboard": {
    title: "Command Center",
    subtitle: "Live incident lifecycle, safety gate, approval, and audit trail",
    actions: [
      ["Simulation", "/simulation"],
      ["Governance", "/admin"],
    ],
  },
  "/admin": {
    title: "Governance Console",
    subtitle: "Agent readiness, policy controls, and deployment governance",
    actions: [
      ["Command Center", "/dashboard"],
      ["Blog", "/blog"],
    ],
  },
  "/blog": {
    title: "OpsPilot Blog",
    subtitle: "AI operations and platform intelligence",
    actions: [
      ["Governance", "/admin"],
      ["Architecture", "/architecture"],
    ],
  },
  "/architecture": {
    title: "Architecture",
    subtitle: "System design and deployment model",
    actions: [
      ["Reasoning Graph", "/knowledge-graph"],
      ["Command Center", "/dashboard"],
    ],
  },
  "/simulation": {
    title: "Simulation Lab",
    subtitle: "Mission-control incident lifecycle simulation",
    actions: [
      ["Command Center", "/dashboard"],
      ["Reasoning Graph", "/knowledge-graph"],
    ],
  },
  "/knowledge-graph": {
    title: "Reasoning Graph",
    subtitle: "Evidence lineage and incident explainability map",
    actions: [
      ["Simulation", "/simulation"],
      ["Architecture", "/architecture"],
    ],
  },
};

export function PlatformShell({ children }: PlatformShellProps) {
  const pathname = usePathname();
  const isHome = pathname === "/";
  const meta = pageMeta[pathname] || {
    title: "OpsPilot Platform",
    subtitle: "AI incident command system",
    actions: [["Command Center", "/dashboard"]],
  };

  return (
    <main className="min-h-screen overflow-hidden bg-[#030712] text-slate-100 dark:bg-[#030712]">
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute left-[-10%] top-[-20%] h-[460px] w-[460px] rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-[-10%] top-[10%] h-[460px] w-[460px] rounded-full bg-violet-500/20 blur-3xl" />
        <div className="absolute bottom-[-20%] left-[30%] h-[460px] w-[460px] rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(34,211,238,0.10),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(139,92,246,0.12),transparent_30%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.045)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.045)_1px,transparent_1px)] bg-[size:42px_42px]" />
      </div>

      <div className="relative z-10">
        {isHome ? (
          <header className="sticky top-0 z-50 border-b border-white/5 bg-[#030712]/70 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4">
              <Link href="/" aria-label="OpsPilot home" className="shrink-0">
                <OpsPilotLogo />
              </Link>

              <nav className="hidden max-w-3xl flex-wrap items-center justify-center gap-1 rounded-full border border-white/10 bg-white/[0.04] p-1 text-sm text-slate-300 shadow-[0_0_40px_rgba(15,23,42,0.35)] lg:flex">
                {fullNavItems.map(([label, href]) => (
                  <Link
                    key={href}
                    className={`rounded-full px-3 py-2 transition ${
                      pathname === href
                        ? "bg-cyan-300 text-slate-950 shadow-[0_0_22px_rgba(34,211,238,0.25)]"
                        : "hover:bg-white/10 hover:text-white"
                    }`}
                    href={href}
                  >
                    {label}
                  </Link>
                ))}
              </nav>

              <div className="flex shrink-0 items-center gap-2">
                <LanguageToggle />
                <ThemeToggle />
                <Link
                  href="/dashboard"
                  className="hidden rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 shadow-[0_0_30px_rgba(34,211,238,0.12)] hover:bg-cyan-400/20 md:inline-flex"
                >
                  Launch Console
                </Link>
              </div>
            </div>

            <div className="mx-auto block max-w-7xl px-6 pb-4 lg:hidden">
              <div className="flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-white/[0.03] p-2">
                {fullNavItems.map(([label, href]) => (
                  <Link
                    key={href}
                    className="shrink-0 rounded-full px-3 py-2 text-sm text-slate-300 hover:bg-white/10 hover:text-white"
                    href={href}
                  >
                    {label}
                  </Link>
                ))}
              </div>
            </div>
          </header>
        ) : (
          <header className="sticky top-0 z-50 border-b border-white/5 bg-[#030712]/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4">
              <div className="flex items-center gap-4">
                <Link
                  href="/"
                  className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-bold text-slate-200 hover:bg-white/[0.08] hover:text-white"
                >
                  ← Home
                </Link>
                <div className="hidden md:block">
                  <OpsPilotLogo />
                </div>
              </div>

              <div className="text-center">
                <div className="text-sm font-black uppercase tracking-[0.28em] text-cyan-300">
                  {meta.title}
                </div>
                <div className="mt-1 text-xs text-slate-500">{meta.subtitle}</div>
              </div>

              <div className="flex items-center gap-2">
                {meta.actions.map(([label, href]) => (
                  <Link
                    key={href}
                    href={href}
                    className="hidden rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-400/20 md:inline-flex"
                  >
                    {label}
                  </Link>
                ))}
                <LanguageToggle />
                <ThemeToggle />
              </div>
            </div>
          </header>
        )}

        <div key={pathname} className="animate-[fadeIn_260ms_ease-out]">
          {children}
        </div>
      </div>
    </main>
  );
}
''')

write(SRC / "app" / "dashboard" / "page.tsx", r'''
"use client";

import { useState } from "react";
import { PlatformShell } from "@/components/PlatformShell";
import { StatusBadge } from "@/components/StatusBadge";
import { approveIncident, createIncident, healthcheck, listIncidents } from "@/lib/api";

type IncidentState = any;
type EvidenceTab = "metrics" | "logs" | "deployments" | "runbooks";

const stateMachine = [
  "triaging",
  "investigating",
  "hypothesis",
  "awaiting approval",
  "remediating",
  "monitoring",
  "resolved",
];

const incidentTemplates = [
  "Checkout API latency spike",
  "Payment error rate increase",
  "Database connection saturation",
  "Authentication failure spike",
];

const defaultEvidence: Record<EvidenceTab, string[]> = {
  metrics: [
    "p95 latency increased from 420ms to 2.8s",
    "cache hit ratio dropped from 91% to 41%",
    "database latency increased by 63%",
  ],
  logs: [
    "Repeated cache-miss fallback warnings detected",
    "Checkout workers report increased downstream retries",
    "No security-related error pattern detected",
  ],
  deployments: [
    "Recent cache configuration change detected",
    "No application code deployment in the last 30 minutes",
    "Rollback candidate identified: cache-config-v18",
  ],
  runbooks: [
    "Runbook match: cache configuration rollback",
    "Validation step: confirm cache hit ratio recovery",
    "Rollback plan: restore previous cache TTL and routing config",
  ],
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

function leadingHypothesis(state: IncidentState | null) {
  return (
    state?.hypothesis_result?.ranked_hypotheses?.[0]?.summary ||
    "Cache configuration regression introduced in the latest config change"
  );
}

function recommendedAction(state: IncidentState | null) {
  return (
    state?.remediation_plan?.candidate_actions?.[0]?.title ||
    "Rollback cache configuration safely"
  );
}

function postmortemSummary(state: IncidentState | null) {
  return (
    state?.postmortem?.summary ||
    "The incident was likely caused by cache config regression and mitigated with approval-gated rollback."
  );
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

export default function DashboardPage() {
  const [backendStatus, setBackendStatus] = useState<string>("not checked");
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [incidents, setIncidents] = useState<IncidentState[]>([]);
  const [loading, setLoading] = useState(false);
  const [evidenceTab, setEvidenceTab] = useState<EvidenceTab>("metrics");
  const [template, setTemplate] = useState(incidentTemplates[0]);

  const status = normalizeStatus(incident?.status);
  const timeline = timelineFromState(incident);
  const isResolved = status === "resolved";
  const isAwaitingApproval = status.includes("approval");

  async function checkBackend() {
    setLoading(true);
    try {
      const data = await healthcheck();
      setBackendStatus(`${data.status} | mock_llm=${data.mock_llm}`);
    } catch (error: any) {
      setBackendStatus(`error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function startIncident() {
    setLoading(true);
    try {
      const data = await createIncident();
      setIncident(data.state ?? data);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshIncidents() {
    setLoading(true);
    try {
      const data = await listIncidents();
      setIncidents(data.incidents || []);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function approve() {
    if (!incident?.incident_id) return;
    setLoading(true);
    try {
      const data = await approveIncident(incident.incident_id);
      setIncident(data.state ?? data);
    } catch (error: any) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <PlatformShell>
      <section className="mx-auto max-w-7xl px-6 pb-20 pt-10">
        <div className="mb-6 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <div className="grid gap-3 md:grid-cols-4">
            <SystemStripItem label="Frontend" value="Vercel / local" tone="green" />
            <SystemStripItem label="Backend" value={backendStatus} tone={backendStatus.startsWith("ok") ? "green" : backendStatus.startsWith("error") ? "amber" : "slate"} />
            <SystemStripItem label="Qwen mode" value="mock fallback" tone="amber" />
            <SystemStripItem label="Cloud billing" value="credits pending" tone="violet" />
          </div>
        </div>

        <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="mb-4 flex flex-wrap gap-3">
              <StatusBadge label="Command Center" tone="cyan" />
              <StatusBadge label={status} tone={toneForStatus(status)} />
              <StatusBadge label="human approval gated" tone="violet" />
            </div>
            <h1 className="text-4xl font-black text-white md:text-6xl">Incident lifecycle console</h1>
            <p className="mt-4 max-w-3xl text-slate-400">
              Investigate the incident, trace evidence, review policy decisions, approve remediation, and generate an auditable postmortem.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button onClick={checkBackend} disabled={loading} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50">
              Check Backend
            </button>
            <button onClick={startIncident} disabled={loading} className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-cyan-200 disabled:opacity-50">
              Start Incident
            </button>
            <button onClick={refreshIncidents} disabled={loading} className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08] disabled:opacity-50">
              Refresh
            </button>
          </div>
        </div>

        <div className="mb-6 rounded-3xl border border-white/10 bg-white/[0.035] p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-sm font-black text-white">Incident template</div>
              <div className="mt-1 text-sm text-slate-400">Choose a demo scenario before starting the workflow.</div>
            </div>
            <div className="flex flex-wrap gap-2">
              {incidentTemplates.map((item) => (
                <button
                  key={item}
                  onClick={() => setTemplate(item)}
                  className={`rounded-full border px-4 py-2 text-sm font-bold ${
                    template === item
                      ? "border-cyan-300 bg-cyan-300 text-slate-950"
                      : "border-white/10 bg-slate-950/50 text-slate-300 hover:bg-white/[0.08]"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mb-6 rounded-3xl border border-white/10 bg-slate-950/70 p-5">
          <h2 className="text-xl font-black text-white">Incident state machine</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-7">
            {stateMachine.map((state, index) => {
              const active =
                status === state ||
                (status === "awaiting approval" && state === "awaiting approval") ||
                (status === "standby" && index === 0);
              const passed = incident && index < 4;
              return (
                <div
                  key={state}
                  className={`rounded-2xl border p-3 ${
                    active
                      ? "border-cyan-300 bg-cyan-300 text-slate-950"
                      : passed
                      ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-100"
                      : "border-white/10 bg-white/[0.035] text-slate-400"
                  }`}
                >
                  <div className="text-xs font-black uppercase tracking-wider">Step {index + 1}</div>
                  <div className="mt-1 text-sm font-black">{state}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid gap-6 xl:grid-cols-[0.9fr_1.15fr_0.95fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-2xl font-black text-white">Incident summary</h2>
                <p className="mt-1 font-mono text-sm text-slate-500">{incident?.incident_id || "No active incident yet"}</p>
              </div>
              <StatusBadge label={status} tone={toneForStatus(status)} />
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2">
              <MetricCard title="Service" value={incident?.triage_result?.affected_service || "checkout-api"} />
              <MetricCard title="Environment" value="production" />
              <MetricCard title="Severity" value={incident?.triage_result?.severity || "high"} />
              <MetricCard title="Business impact" value="checkout degraded" />
              <MetricCard title="Hypothesis confidence" value={String(incident?.hypothesis_result?.confidence || "0.86")} />
              <MetricCard title="Operational risk" value={incident?.risk_review?.risk_level || "medium"} />
            </div>

            <div className="mt-6 rounded-3xl border border-cyan-400/20 bg-cyan-400/10 p-5">
              <h3 className="text-xl font-black text-white">Leading hypothesis</h3>
              <p className="mt-3 leading-7 text-slate-300">{leadingHypothesis(incident)}</p>
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
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

            <div className="mt-5 space-y-3">
              {defaultEvidence[evidenceTab].map((item, index) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div className="text-xs font-black uppercase tracking-wider text-cyan-300">source {index + 1}</div>
                  <div className="mt-2 text-sm leading-6 text-slate-300">{item}</div>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-3xl border border-violet-400/20 bg-violet-400/10 p-5">
              <h3 className="font-black text-white">Why multi-agent?</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Triage, evidence analysis, hypothesis ranking, risk review, approval briefing, and postmortem generation are separated for safer and more auditable reasoning.
              </p>
            </div>
          </section>

          <aside className="space-y-6">
            <section className="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-black text-white">Safety Gate</h2>
                  <p className="mt-1 text-sm text-amber-100/80">Policy-aware control before production action.</p>
                </div>
                <StatusBadge label="approval required" tone="amber" />
              </div>

              <div className="mt-5 space-y-3 text-sm">
                <PolicyItem label="Rule matched" value="production configuration rollback" />
                <PolicyItem label="Guardrail" value="human approval required" />
                <PolicyItem label="Rollback plan" value="restore previous cache config" />
                <PolicyItem label="Blocked alternative" value="database restart without evidence" />
              </div>

              <button
                onClick={approve}
                disabled={loading || !incident?.incident_id || isResolved}
                className="mt-5 w-full rounded-2xl bg-emerald-300 px-5 py-3 text-sm font-black text-slate-950 hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {isResolved ? "Remediation Approved" : isAwaitingApproval ? "Approve Remediation" : "Approve when ready"}
              </button>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
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

        <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_1fr]">
          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Live agent timeline</h2>
            <div className="mt-6 space-y-3">
              {timeline.map((item: any, index: number) => (
                <div key={`${item.agent}-${index}`} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                  <div>
                    <div className="font-mono text-sm font-black text-cyan-100">{item.agent}</div>
                    <div className="mt-1 text-xs text-slate-500">step {index + 1} · structured output recorded</div>
                  </div>
                  <StatusBadge label={item.status || "completed"} tone={toneForStatus(item.status || "completed")} />
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Outcome and postmortem</h2>
            <div className="mt-5 rounded-3xl border border-emerald-400/20 bg-emerald-400/10 p-5">
              <h3 className="font-black text-white">{isResolved ? "Postmortem generated" : "Postmortem preview"}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-300">{postmortemSummary(incident)}</p>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <button className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Copy incident summary
              </button>
              <button className="rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-3 text-sm font-bold text-white hover:bg-white/[0.08]">
                Export audit log
              </button>
            </div>
          </section>
        </div>

        {incidents.length > 0 && (
          <section className="mt-6 rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-2xl font-black text-white">Stored incidents</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {incidents.map((item: any) => (
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
      <div className="mt-3">
        <StatusBadge label={tone} tone={tone} />
      </div>
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
''')

print("Sprint 2.0 Dashboard Command Center patch applied. Running build check...")
result = run_build()
print(result.stdout)

if result.returncode != 0:
    restore()
    print("BUILD FAILED. Sprint 2.0 changes were rolled back.")
    sys.exit(result.returncode)

print("BUILD PASSED. Sprint 2.0 changes kept.")
print(f"Backups stored in {BACKUP_DIR}")
